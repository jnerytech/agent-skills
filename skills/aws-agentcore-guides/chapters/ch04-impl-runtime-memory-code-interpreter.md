# Chapter 4: Amazon Bedrock AgentCore Implementation Guide Part 1: Runtime, Memory, and Code Interpreter Patterns

## Core Idea
Write one `@app.entrypoint` function inside `BedrockAgentCoreApp` and AgentCore Runtime hosts it unchanged from prototype to production. Add Memory as two layers (synchronous Events, asynchronous long-term Memories). Run LLM-generated code in a session-scoped Code Interpreter sandbox. Stream NDJSON from Runtime and convert it to SSE for the browser.

## Frameworks Introduced
- **Deployment ladder**: start with `direct_code_deploy` (CLI, no Docker, no IaC). Move to `container` (CDK) for production, ZIP (Lambda Packager) for CDK without Docker, or `container` (Terraform) if you already run Terraform. The entrypoint code stays identical across all four.
- **Memory two-layer model**: Events (`create_event`/`list_events`) hold synchronous, session-scoped history with a retention minimum of 7 days. Memories (`retrieve_memories`/`list_memory_records`) are persistent and extracted asynchronously by 3 strategies.
- **Five Memory integration patterns**: Strands Hooks API (full control), `AgentCoreMemorySessionManager` (recommended start), `CompactingSessionManager` (long conversations, custom sample class), `AgentCoreMemorySaver` (LangGraph checkpointer), Direct `MemoryClient` (any framework). Start with SessionManager. Move to Hooks or Compacting when you need more control.
- **MCP-then-Code-Interpreter ordering**: the sandbox blocks outbound network. Fetch data with MCP tools first, then compute in Code Interpreter. Enforce the order in the system prompt with "NEVER call MCP tools from inside Code Interpreter".
- **Production streaming triad**: an NDJSON→SSE parser, `ThinkingFilter` (strips Nova `<thinking>` blocks and tool XML), and delta calculation (deduplicates cumulative text).

## Key Concepts
- **BedrockAgentCoreApp**: serves HTTP on port 8080, answers `/ping`, parses JSON, exposes `context.session_id`, and serializes streams as NDJSON.
- **context.session_id**: groups traces in CloudWatch and keys Memory events. It must be ≥16 characters.
- **Confused deputy protection**: the trust policy conditions `aws:SourceAccount` + `aws:SourceArn` on the `bedrock-agentcore.amazonaws.com` principal.
- **SigV4 vs Cognito JWT**: SigV4 for server-to-server, CLI and boto3 (no `authorizerConfiguration`). JWT (`customJWTAuthorizer`) for web and mobile.
- **Memory strategies**: `userPreferenceMemoryStrategy` (`/users/{userId}/preferences`), `semanticMemoryStrategy` (`/users/{userId}/facts`), `summaryMemoryStrategy` (`/summaries/{userId}/{sessionId}`).
- **Namespace**: the per-user path that scopes retrieval. It drives both accuracy and cross-user isolation.
- **Code Interpreter session**: variables and imports persist across `invoke("executeCode", ...)` calls until `stop()`.
- **NDJSON → SSE**: the backend parses Runtime NDJSON into 7 SSE event types: `message`, `tool_use`, `tool_result`, `guardrail`, `metadata`, `error`, `done`.
- **ThinkingFilter**: a stateful filter that keeps the full accumulated text and re-applies regexes, so tags split across chunk boundaries are still removed. It emits only the new suffix.
- **Incremental UTF-8 decoder**: `codecs.getincrementaldecoder('utf-8')('replace')` prevents multibyte characters from breaking at chunk edges.

## Mental Models
- Think of Runtime as "a decorator turns your function into a managed HTTPS service". Infrastructure varies, code doesn't.
- Think of Events as a transcript and Memories as notes a background LLM writes 10–30 s later.
- Use memories from the previous session in the current one rather than expecting same-turn recall.
- Think of Code Interpreter as an air-gapped calculator: bring the data in, never reach out.
- Use `CompactingSessionManager` when input tokens grow toward the context window (e.g., `token_threshold=100_000`).

## Anti-patterns
- Calling `retrieve_memories` right after `create_event` and treating empty results as a bug. Poll for up to 60 s or design around the async delay.
- Leaking Code Interpreter sessions because there is no `try/finally` or `code_session`. Leaked sessions keep consuming resources.
- Calling MCP tools from inside the sandbox.
- Relying on default boto timeouts for multi-step tool calls. Set `read_timeout=900`.
- Forwarding cumulative `stream_async` text as-is, which duplicates output. Not filtering `<thinking>`, so reasoning leaks to users.
- Letting nginx buffer SSE. Set `X-Accel-Buffering: no`.
- Session IDs shorter than 16 characters.
- Scattering env vars through the code. Centralize them in an `AgentConfig.from_env()` dataclass.

## Code Examples
```python
app = BedrockAgentCoreApp()

@app.entrypoint
async def invoke(payload, context):
    agent = Agent(model=payload.get("modelId", "us.anthropic.claude-sonnet-4-20250514-v1:0"),
                  tools=tools,
                  state={"session_id": context.session_id,
                         "user_id": payload.get("userId", "anonymous")})
    async for event in agent.stream_async(payload.get("prompt", "")):
        yield event
```
What it demonstrates: the recommended async streaming entrypoint, with session and user threaded into agent state for Memory hooks.

```python
session_manager = AgentCoreMemorySessionManager(
    agentcore_memory_config=AgentCoreMemoryConfig(memory_id=memory_id, session_id=session_id, actor_id=user_id),
    region_name="us-west-2")
agent = Agent(model=model_id, tools=tools, session_manager=session_manager)
```
What it demonstrates: zero-boilerplate automatic save and restore of conversation history.

```python
with code_session("us-west-2") as code_client:
    response = code_client.invoke("executeCode", {"language": "python", "code": "print(2 + 2)"})
# stop() automatic; result text at response["stream"][i]["result"]["content"][j]["text"]
```

CLI deploy: `agentcore configure --entrypoint ... --deployment-type direct_code_deploy --disable-memory --non-interactive`, then `agentcore deploy`, then `agentcore invoke '{"prompt": "Hello"}'`.

## Reference Tables
| Method | Docker | IaC | Best for |
|---|---|---|---|
| `direct_code_deploy` | No | No | Start here; prototypes |
| `container` (CDK) | Yes | CDK TS | Production |
| ZIP (Lambda Packager) | No | CDK | CDK without Docker |
| `container` (Terraform) | Yes | Terraform | Existing TF workflows |

| Limit | Value |
|---|---|
| Session ID min length | 16 chars (format `{user_id}_{timestamp}_{purpose}`) |
| Trace ID max | 128 chars |
| `event_expiry_days` min | 7 days (SDK) = 604,800 s (CDK `eventExpiryDuration`) |
| LTM extraction delay | 10–30 s; wait ≤60 s |
| Code Interpreter session timeout | default 3,600 s, max 28,800 s (8 h) |
| Code Interpreter libs | NumPy, Pandas, Matplotlib, SciPy, SymPy, scikit-learn; no custom installs |
| Runtime arch | ARM64 only (CodeBuild `AMAZON_LINUX_2_STANDARD_3_0` ARM) |
| Health check | `/ping` on 8080, else `FAILED` |
| BedrockModel timeouts | `read_timeout=900`, `connect_timeout=10`, retries 3 adaptive |
| IAM propagation | wait 15 s after role creation |

Troubleshooting:

| Symptom | Fix |
|---|---|
| Runtime `FAILED` | Check `/aws/bedrock-agentcore/runtimes/*` logs |
| `ImportError` | Add the package to requirements.txt |
| `uvx not found` | Add `uv` or use `find_uv_bin()` |
| Cut-off text | Use the incremental UTF-8 decoder |

## Worked Example
A cost estimator agent (`CostEstimatorAgent`):
1. The `_agent_context()` `@contextmanager` starts `CodeInterpreter(region)` and yields an `Agent` with an `execute_calculation` `@tool`. The `finally` block always calls `stop()`.
2. The system prompt enforces the order: parse services → call `get_pricing` for each, with `"output_options": {"pricing_terms": ["OnDemand"], "exclude_free_products": true}` and `max_results: 5` → run `execute_cost_calculation` in the sandbox → output a markdown cost table.
3. The rules say never to estimate prices from memory and never to call MCP from the sandbox.
4. The frontend receives this through FastAPI `StreamingResponse(media_type="text/event-stream")`. `invoke_stream` decodes chunks, splits on `\n`, runs `parse_ndjson_line` (which handles `contentBlockDelta`, `TextStreamEvent`, `tool_use`/`tool_result`, `guardrail`, and usage metrics), and emits `DoneEvent`.

## Key Takeaways
1. One entrypoint for every deploy method. Prototype with `direct_code_deploy`, then go to production with CDK `container`.
2. Session IDs must be ≥16 chars. They key Memory, CloudWatch, and traces.
3. Long-term memory is asynchronous (10–30 s). Namespace it per user for isolation.
4. Start Memory with `AgentCoreMemorySessionManager`. Escalate to Hooks or Compacting when needed.
5. Code Interpreter has no network access. Use MCP first, then compute, and always release the session.
6. Production streaming needs NDJSON→SSE conversion, ThinkingFilter, delta dedupe, an incremental UTF-8 decoder, and `X-Accel-Buffering: no`.

## Connects To
- ch01 Beginner's Guide (service overview); ch02/ch03 glossaries (Runtime, Memory, MCP terms)
- ch05 Identity/Gateway/Policy: JWT auth, Token Vault, and the anti-impersonation `sub` claim, which replaces trusting `payload.userId`
- ch06 4-stack CDK: production `container` deploy, CfnMemory with seconds-based expiry, ARM64 CodeBuild
- ch07 multi-agent (LangGraph `AgentCoreMemorySaver`, A2A); ch08 Harness managed loop; ch10 ops/cost (session leaks, timeouts)
