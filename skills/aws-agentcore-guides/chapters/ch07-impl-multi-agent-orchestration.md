# Chapter 7: Amazon Bedrock AgentCore Implementation Guide Part 4: Multi-Agent Orchestration

## Core Idea
Split a "do-everything" agent into specialized agents, each deployed as an independent AgentCore Runtime and coordinated over API; pick the coordination pattern (A2A, Supervisor, boto3, Skill System, Voice) by ownership boundary and coupling, then add Browser Use for API-less systems and Guardrails Shadow Mode for safe quality monitoring.

## Frameworks Introduced
- **Why go multi-agent (4 single-agent failures)**: system-prompt bloat (>20 tools lowers tool-selection accuracy), loss of specialization (mediocre answers everywhere), scalability limits (one LLM call, no parallelism), reduced maintainability (wide blast radius, hard to test).
- **Five orchestration patterns**: A2A Protocol / Supervisor + Sub-agent / boto3 direct invocation / Skill System / Voice Mode — see table.
  - When: choose by who owns the agents and who drives routing (LLM vs code).
- **Supervisor + Sub-agent**: parent LLM agent routes to child Runtimes via a single `invoke_sub_agent` tool.
  - How: (1) deploy each Sub-agent as its own Runtime; (2) map names→ARNs; (3) wrap `invoke_agent_runtime` in a `@tool`; (4) describe each Sub-agent's domain in the Supervisor system prompt; (5) tell it to call multiple agents in sequence when needed.
- **Generic form auto-fill (Browser Use, 3 steps)**: (1) discover fields with `page.locator("body").aria_snapshot()`; (2) LLM maps input data → JSON `{"textboxes": {...}, "radios": {...}}` using exact accessible names; (3) type via CDP in 20-char chunks with 300 ms delay, verify each field with `input_value()` before submit, re-type mismatches, check for "thank" in body text.
- **Guardrails Shadow Mode phased rollout**: (1) Shadow (log violations, don't block) → (2) analyze logs and false-positive rate → (3) switch to ENFORCE once FPs are acceptable.
- **Sub-agent error propagation strategy** (decide up front): Retry (transient) / Fallback to another agent (agent unavailable) / Report to user (unrecoverable).

## Key Concepts
- **Agent Card**: JSON self-description (name, description, capabilities, endpoint, authentication) published at `/.well-known/agent.json` for A2A discovery.
- **A2A Protocol**: Google's 2025 open standard for agent-to-agent communication; interoperable across Strands, LangGraph, custom frameworks.
- **`invoke_agent_runtime`**: boto3 `bedrock-agentcore` API taking `agentRuntimeArn`, `runtimeSessionId`, `payload`; returns a streamed `response`.
- **Skill System**: not truly multi-agent — dynamically filters one agent's tool set by user proficiency (beginner/intermediate/advanced), level read from AgentCore Memory.
- **Voice Mode**: Nova Sonic 2 (`amazon.nova-2-sonic-v1:0`) via experimental `BidiNovaSonicModel` + `BidiAgent`; needs WebSocket/WebRTC infra you host yourself.
- **`AgentCoreMemorySaver`**: LangGraph checkpointer (`langgraph-checkpoint-aws`) persisting workflow state into AgentCore Memory so graphs resume after interruption.
- **AgentCore Browser**: AWS-managed Chrome session; Playwright attaches via CDP (`connect_over_cdp`); live view in the console for debugging.
- **Shadow Mode**: guardrails evaluate and log (`GUARDRAIL_INTERVENED` → WARNING) but never block.
- **`NotifyOnlyGuardrailsHook`**: Strands `HookProvider` calling `apply_guardrail` on `MessageAddedEvent` (INPUT) and `AfterInvocationEvent` (OUTPUT).

## Mental Models
- Think of the Supervisor's system prompt as the routing table — the LLM replaces hand-written conditionals, so domain descriptions must be crisp.
- Think of `session_id` as the context-sharing dial: same ID = shared context; distinct ID per Sub-agent = isolated context.
- Use parallel invocation when tasks are independent (multi-region cost estimates); use sequential when output feeds the next step (collect → analyze → report).
- Think of Browser Use as the integration of last resort for systems without APIs — accessibility tree as the schema, LLM as the mapper.
- Every extra agent hop is at least one more LLM call: cost scales with orchestration depth.

## Anti-patterns
- One agent with >20 tools — tool selection accuracy degrades; split into Sub-agents.
- Starting with many agents — start with 2–3; validate routing accuracy beyond 5.
- Circular dependencies (A → B → A) — keep agent dependencies strictly unidirectional.
- Enabling guardrails in blocking mode directly in production — false positives block legitimate traffic; go through Shadow Mode.
- Typing long strings over CDP in one shot — dropped characters; chunk + delay + verify.
- Letting guardrail failures break the agent — wrap `apply_guardrail` in try/except and pass.
- Hyphens in `agent_runtime_name` (Terraform) — only alphanumerics and underscores.

## Code Examples
```python
@tool(name="invoke_sub_agent", description="Delegate a task to a specialized agent")
def invoke_sub_agent(agent_name: str, task: str, session_id: str = "") -> str:
    if agent_name not in SUB_AGENTS:
        return f"Error: '{agent_name}' does not exist. Available: {list(SUB_AGENTS.keys())}"
    client = boto3.client('bedrock-agentcore')
    response = client.invoke_agent_runtime(
        agentRuntimeArn=SUB_AGENTS[agent_name]["arn"],
        runtimeSessionId=session_id or f"supervisor-{agent_name}",
        payload=BytesIO(json.dumps({"prompt": task}).encode('utf-8')),
    )
    result = ""
    for chunk in response.get('response', []):
        if isinstance(chunk, bytes):
            result += chunk.decode('utf-8')
        elif isinstance(chunk, dict) and 'chunk' in chunk and isinstance(chunk['chunk'], dict):
            result += chunk['chunk'].get('bytes', b'').decode('utf-8')
    return result
```
What it demonstrates: the whole Supervisor pattern collapses to one tool; returning an error string listing valid names lets the LLM self-correct; response reader handles both bytes and dict chunks (empty response is a common bug otherwise).

```python
class NotifyOnlyGuardrailsHook(HookProvider):
    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(MessageAddedEvent, self.check_user_input)       # source="INPUT"
        registry.add_callback(AfterInvocationEvent, self.check_assistant_response)  # source="OUTPUT"
    def _evaluate(self, text, source):
        try:
            r = self.client.apply_guardrail(guardrailIdentifier=self.guardrail_id,
                    guardrailVersion=self.guardrail_version, source=source,
                    content=[{"text": {"text": text}}])
            if r.get("action") == "GUARDRAIL_INTERVENED":
                logger.warning(f"Guardrail violation (shadow): {r.get('assessments', [])}")
        except Exception:
            pass  # Guardrail failures should not affect the agent
# Agent(..., hooks=[NotifyOnlyGuardrailsHook("abc123", "1", "us-west-2")])
```
What it demonstrates: guardrails as a non-blocking hook attached to the Supervisor; 2 `apply_guardrail` calls per message.

```python
checkpointer = AgentCoreMemorySaver(memory_id=MEMORY_ID, region_name="us-west-2")
app = graph.compile(checkpointer=checkpointer)
app.invoke({"messages": [...]},
           config={"configurable": {"thread_id": session_id, "actor_id": user_id}})
```
What it demonstrates: LangGraph `StateGraph` (research → analysis, `add_conditional_edges` router looping until "complete" → `END`) made resumable with AgentCore Memory.

Terraform IaC pattern: each Sub-agent is an `aws_bedrockagentcore_agent_runtime`; the Supervisor receives Sub-agent ARNs via `environment_variables` (e.g. `MORTGAGE_CALC_ARN`), `depends_on` for readability, and an IAM policy allowing `bedrock-agentcore:InvokeAgentRuntime` on `runtime/*`.

## Reference Tables
| Pattern | Communication | Coupling | Best fit |
| --- | --- | --- | --- |
| A2A Protocol | Standardized protocol | Loose | Agents owned by different teams/orgs |
| Supervisor + Sub-agent | Hierarchical invocation | Medium | LLM-based dynamic routing (same org) |
| boto3 direct invocation | `invoke_agent_runtime` | Loose | Lightweight orchestration from Lambda/Step Functions |
| Skill System | Progressive disclosure | Medium | Unlock tools by user proficiency |
| Voice Mode | Audio stream | Medium | Call centers, voice assistants |

| Limit | Value |
| --- | --- |
| Sub-agents per Supervisor | Start 2–3; validate beyond 5 |
| Tools per agent | Accuracy degrades beyond ~20 (soft) |
| Token multiplier | Min 2x (1 Supervisor + 1 Sub-agent call) |
| Runtime session ID | Min 16 characters |
| `BedrockModel` `read_timeout` | Recommended 900 s for Code Interpreter / long multi-step tools |
| CDP input | 20 chars/chunk, 300 ms interval |
| Form field max | 50 chars (`MAX_FIELD_CHARS`) |
| `apply_guardrail` rate needed | message count × 2 (INPUT + OUTPUT) |

| Symptom | Cause | Fix |
| --- | --- | --- |
| Empty Sub-agent response | Incomplete chunk handling | Handle `text/event-stream` and JSON by `contentType` |
| Context not shared | Different `session_id` | Pass Supervisor's `session_id` |
| Throttling in parallel | Bedrock rate limits | Cross-region inference (`us.*` model IDs) |
| A2A auth errors | Expired token | Fresh token per call / shorter cache TTL |
| Supervisor never delegates | Vague tool description | More specific `@tool` `description` |

## Worked Example
Mortgage advisor Supervisor (`us.anthropic.claude-sonnet-4-20250514-v1:0`) with three Runtimes: `mortgage_calculator`, `document_reviewer`, `compliance_checker`. User asks "monthly payment for a 30M yen mortgage over 35 years?" → Supervisor routes to `mortgage_calculator` with task "30M yen, 35 years, 1.5% interest" → `invoke_agent_runtime` streams back "approximately 91,855 yen (level payment)" → Supervisor synthesizes the answer. Extended variant: a shared Code Interpreter session (`CodeInterpreter("us-west-2")`, `start()`/`stop()` in `try/finally`, `executeCode` with `clearContext: False`) gives the Supervisor a `run_code` tool alongside `invoke_sub_agent`, so it computes sales totals in code and delegates judgment to `document_reviewer`.

## Key Takeaways
1. Split agents when tool count passes ~20 or domains diverge; start with 2–3 Sub-agents.
2. Same-org routing → Supervisor; cross-team/platform → A2A Agent Cards; Lambda/Step Functions → raw `invoke_agent_runtime`.
3. `session_id` (≥16 chars) is how you share or isolate context across agents.
4. Every hop costs ≥1 LLM call — track per-agent cost with the Firehose pipeline (ch06).
5. Roll out guardrails via Shadow Mode, measure false positives, then ENFORCE.
6. Browser Use = aria snapshot + LLM mapping + chunked CDP typing + pre-submit verification.
7. Deploy each Sub-agent as its own Runtime; inject ARNs into the Supervisor via env vars; keep dependencies acyclic.

## Connects To
- ch04 (Runtime, Memory two-tier, Code Interpreter lifecycle), ch05 (Identity tokens for A2A auth), ch06 (Guardrails CDK, Firehose cost tracking)
- ch09 (Strands Agents-as-Tools/Swarm/Graph/Workflow — in-process counterparts of these cross-Runtime patterns)
- ch08 (Harness managed loop), ch10 (production ops/cost), ch11 (prompt injection defense), ch12 (Agent Registry — discovery beyond Agent Cards)
