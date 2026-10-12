# Chapter 9: Strands Agents Multi-Agent Pattern Selection Guide - Agents-as-Tools, Swarm, Graph, and Workflow

## Core Idea
Choosing a Strands multi-agent primitive is choosing how much control flow you delegate to model judgment vs pin down in code; decide by two questions in order — is the execution path known in advance, and if not, who routes (a central orchestrator or the peers). (Verified against strands-agents Python SDK 1.42.x, June 2026; Python 3.10+.)

## Frameworks Introduced
- **Pattern Selection Decision Path (4 questions)**:
  1. Can a better single agent meet the need? (sharper tool descriptions, fewer overlapping tools, restructured prompt) → yes: stay single-agent.
  2. Is the execution path known in advance (drawable on a whiteboard before seeing input)?
  3. Known → need conditional routing, loops, or per-step agent identity? Yes → **Graph**; No → **Workflow**.
  4. Discovered → who decides the next actor? Central coordinator → **Agents-as-Tools**; the peers → **Swarm**.
- **Six signals that justify multi-agent**: tool-selection accuracy degrades; system prompt accumulates contradictory personas; one context window must hold everything; steps need different operating envelopes (model/timeout); independent subtasks could run in parallel; team ownership boundaries.
- **Composition rule — determinism outside, autonomy inside**: Graph is the outer skeleton (`add_node` accepts a multi-agent system); nest a Swarm as one bounded exploratory stage. Never an outer Swarm over inner Graphs.
- **Upgrade path**: single agent → Agents-as-Tools → Graph-with-nested-patterns. Designs starting at maximum autonomy rarely climb down gracefully.
- **Pre-commit checklist**: name the forcing signal; whiteboard test; name the bounds on worst-case run; decide where `node_history`/`execution_order` get stored; outcome vs unit-test strategy; upgrade path.

## Key Concepts
- **Layering of the surface**: Swarm and Graph = SDK orchestrator classes in `strands.multiagent`; Agents-as-Tools = design pattern using `@tool`; Workflow = `workflow` tool from `strands-agents-tools`; A2A = interoperability protocol (`A2AServer`/`A2AAgent`), orthogonal to the four.
- **Agents-as-Tools**: specialist agent wrapped in a `@tool`; orchestrator routes per call, control always returns to it; specialists see only their tool input.
- **Swarm**: flat peer team; SDK injects `handoff_to_agent(agent_name, message, context)` into every member; shared working context; emergent order; one active agent at a time.
- **Graph**: developer-declared nodes + directed edges with optional condition functions over `GraphState`; supports bounded cycles; most auditable/testable.
- **Workflow**: orchestrates tasks (description + `system_prompt` + `priority` + `dependencies`), not agents; auto-parallel from dependencies; state persisted to disk by `workflow_id` (re-`start` resumes); `pause`/`resume` not implemented (return error).
- **Handoffs (1.0 sense)**: in the 1.0 announcement "handoffs" meant agent→human (HITL), distinct from Swarm agent→agent handoffs.
- **Durable session management**: persist agent state to backends such as Amazon S3 — matters more for long Swarm/Graph runs.
- **Invocation state**: request-scoped context `graph(task, invocation_state={"role": "admin"})`; as of 1.42.x condition functions receive only `GraphState`, so don't route per-caller in conditions.
- **Result objects**: Swarm `result.status`, `result.node_history`; Graph `status`, `execution_order`, `results`, `execution_time`, `accumulated_usage`.

## Mental Models
- Think of "who decides the next step" as the master row: it determines determinism, auditability, token behavior, and failure mode.
- Think of the specialist docstring as the routing table — treat it like an API contract.
- Think of every LLM-routed step as a paid model invocation on top of the work; Graph edges and Workflow dependencies route at ~zero marginal cost and cap invocations by construction.
- Use Workflow when every step is "a task needing the output of these other tasks"; the moment you need "only if…" or "go back and redo", use Graph.
- Agents-as-Tools vs Swarm = where control returns: hierarchy (back to orchestrator) vs lateral (between peers).
- Topology is for process structure; prompts are for behavior.
- Specialist lifetime: construct inside the tool = fresh, stateless, concurrency-safe; hoist to module level = persistent history, shared state, growing context.

## Anti-patterns (8 pitfalls)
1. **Over-decomposition** — five mediocre agents instead of one good one; merge back if no named signal.
2. **Context fragmentation** — specialists only see what crosses the boundary; use Swarm `message`/`context` deliberately.
3. **Unbounded autonomy** — Swarm without repetitive-handoff detection, cyclic Graph without `set_max_node_executions` = "unbounded loop with a billing meter".
4. **Swarm for a procedural task** — paying handoff-reasoning tokens to rediscover steps you could write as edges (most common selection mistake).
5. **Encoding behavior in topology** — nodes like `apologize_if_frustrated`.
6. **Fragile condition functions** — phrase-matching that silently returns `False`; downstream nodes never run (truncated result). Have upstream emit explicit markers.
7. **Vague specialist docstrings** ("handles data tasks") — inconsistent routing.
8. **Testing emergent systems deterministically** — assert outcomes/invariants, not paths.
Also: orchestrator context bloat from verbose specialists (return tight structured answers); nesting deeper than 2 levels of Agents-as-Tools; treating Workflow tasks as multi-turn conversations.

## Code Examples
```python
@tool
def research_assistant(query: str) -> str:
    """Process and respond to research-related queries.

    Args:
        query: A research question requiring factual information.
    """
    try:
        research_agent = Agent(system_prompt=RESEARCH_ASSISTANT_PROMPT)
        return str(research_agent(query))
    except Exception as e:
        return f"Error in research assistant: {e}"

orchestrator = Agent(system_prompt="Route each query to the most appropriate specialized tool: "
    "use research_assistant for research questions; answer simple questions directly without delegation.",
    tools=[research_assistant])
```
What it demonstrates: docstring = routing rule; return error strings so the orchestrator adapts; orchestrator answers trivia itself to avoid delegation round trips.

```python
swarm = Swarm([researcher, coder, reviewer], entry_point=researcher,
              max_handoffs=20, max_iterations=20,
              execution_timeout=900.0, node_timeout=300.0)
result = swarm("Build a Python CLI tool that deduplicates files in a directory")
print(result.status, [n.node_id for n in result.node_history])
```
What it demonstrates: `Agent(name=...)` names are handoff addresses; each prompt defines specialty *and* handoff etiquette ("Hand off to the reviewer when the implementation is complete").

```python
def analysis_complete(state):
    analysis = state.results.get("analysis")
    return analysis is not None and "complete" in str(analysis.result).lower()

builder = GraphBuilder()
builder.add_node(researcher, "research"); builder.add_node(analyst, "analysis"); builder.add_node(reporter, "report")
builder.add_edge("research", "analysis")
builder.add_edge("analysis", "report", condition=analysis_complete)
builder.set_entry_point("research")
# bounded cycle:
builder.set_max_node_executions(10); builder.set_execution_timeout(300); builder.reset_on_revisit(True)
builder.add_edge("review", "draft", condition=needs_revision)
graph = builder.build()
```
What it demonstrates: quality gate as code with an explicit marker; feedback loop whose existence, exit and trip count are code-reviewable. Async: `await graph.invoke_async(task)`, streaming: `async for event in graph.stream_async(task)`.

```python
agent = Agent(tools=[workflow])   # from strands_tools import workflow
agent.tool.workflow(action="create", workflow_id="report_pipeline", tasks=[
  {"task_id": "data_extraction", "description": "...", "system_prompt": "...", "priority": 5},
  {"task_id": "trend_analysis", "dependencies": ["data_extraction"], "system_prompt": "...", "priority": 3}])
agent.tool.workflow(action="start", workflow_id="report_pipeline")
agent.tool.workflow(action="status", workflow_id="report_pipeline")
```
What it demonstrates: dependency list is the entire parallelism model — tasks sharing one dependency run in parallel.

```python
app = BedrockAgentCoreApp()          # pip install bedrock-agentcore (starter toolkit deprecated)
graph = builder.build()              # build once at module load, not per request
@app.entrypoint
def invoke(payload):
    result = graph(payload.get("prompt", ""))
    return {"status": str(result.status)}
```
What it demonstrates: AgentCore Runtime is pattern-agnostic — any pattern sits behind one entrypoint; CLI: `agentcore create` / `dev` / `deploy` / `invoke`.

## Reference Tables
| | Agents-as-Tools | Swarm | Graph | Workflow |
| --- | --- | --- | --- | --- |
| Form | `@tool` pattern | `strands.multiagent.Swarm` | `GraphBuilder`/`Graph` | `workflow` tool (`strands-agents-tools`) |
| Who decides next | Orchestrator LLM | Agents via handoffs (LLM) | Edges + condition functions (code) | Task dependencies (code) |
| Structure | Hierarchy | Flat peer team, shared context | Directed graph, DAG + optional cycles | Dependency-ordered task list |
| Determinism | Topology fixed, routing per request | Low (emergent) | High | High |
| Parallelism | Multi-tool turns only | One agent at a time | Independent branches | Automatic for independent tasks |
| Fits | Triage, Q&A dispatch, hierarchical decomposition | Open-ended cross-discipline collaboration | Staged processes, gates, bounded loops | Repeatable fan-out/fan-in pipelines |
| Safety rails | Your own per-tool error handling | `max_handoffs`, `max_iterations`, timeouts, repetitive-handoff detection | Timeouts, `set_max_node_executions`, `reset_on_revisit` | Status tracking, state persisted by ID |

**Swarm defaults**: `entry_point` = first agent; `max_handoffs` 20; `max_iterations` 20; `execution_timeout` 900.0 s; `node_timeout` 300.0 s; `repetitive_handoff_detection_window` 0 (disabled); `repetitive_handoff_min_unique_agents` 0 (disabled) — enable both for production.

**Workflow vs Graph**: unit = task vs agent (or nested system); tool vs core class; no branching vs conditional edges; no loops vs capped loops; lifecycle create/start/status/list/delete by ID vs build once, invoke per request (sync/async/stream).

**Tiebreakers**: parallelism → Workflow, then Graph; auditability/compliance → Graph; predictable token/latency → Graph or Workflow; welcome surprising solutions → Swarm; simple testing → Graph/Workflow; single conversation owner → Agents-as-Tools; human-in-the-loop checkpoints → Graph (gate = node + condition).

## Worked Example
Four scenarios mapped through the decision path: **customer support front door** (unpredictable categories, one conversation owner) → Agents-as-Tools; **production incident response** (first finding decides next specialist; DB/network/app build on each other) → Swarm with repetitive-handoff detection; **contract intake** (extract clauses → validate against policy → revise on failure at most twice → summary for legal; audit needed) → Graph with conditional edge and bounded cycle; **weekly multi-document report** (same structure weekly, parallel sources, merge) → Workflow.

## Key Takeaways
1. Exhaust single-agent remedies first; split only on a named signal — every boundary adds a model call, latency, and a context leak point.
2. Path known → code it (Graph if branching/loops/per-node config, else Workflow); path discovered → Agents-as-Tools (central owner) or Swarm (peers).
3. Set bounds day one: Swarm handoff/iteration caps + repetitive-handoff detection; cyclic Graph `set_max_node_executions`; timeouts everywhere.
4. Compose with Graph outside, Swarm inside.
5. Test emergent patterns on outcomes/invariants; unit-test Graph conditions and Workflow tasks without a model.
6. On AgentCore Runtime, build the system once at module load, prefer `stream_async` for long runs, and ship `node_history`/`execution_order`/`accumulated_usage` to observability.
7. Per-agent model choice (cheap triage, strong analysis) is often where multi-agent pays for its overhead.

## Connects To
- ch07 (AgentCore-side multi-agent: cross-Runtime Supervisor, A2A, boto3 — the deployment-level counterpart)
- ch08 (Harness can't express graph/workflow patterns; export to Strands code lands here)
- ch02 (orchestrator/handoff/supervisor terminology), ch04 (Runtime entrypoint, Memory), ch05 (Policy/Cedar for per-agent authorization), ch06/ch10 (observability, cost, evaluations), ch12 (Agent Registry for cross-team discovery alongside A2A)
