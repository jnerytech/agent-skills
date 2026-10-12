# Chapter 14: Productionizing AI agents: Memory, guardrails, and beyond

## Core Idea
Production readiness for an AI agent rests on two mechanisms — LangGraph checkpointers for stateful, resumable conversation memory, and layered guardrails (router-level and agent-level, pre-model and post-model) that keep the agent inside its intended scope — plus a checklist of what comes after (long-term memory, human-in-the-loop, evaluation, deployment).

## Frameworks Introduced
- **LangGraph checkpointer**: a pluggable component that snapshots the full graph state (messages, tool outputs, intermediate variables, execution metadata) after every super-step (node execution), keyed by a `thread_id` carried in `RunnableConfig`.
  - When to use: any multi-turn conversational agent that must resolve references like "same town" across turns, or any workflow needing failure recovery / human-in-the-loop pausing.
  - How: instantiate a saver (`InMemorySaver` for dev; `SqliteSaver`/`PostgresSaver`, or their async variants, for production), pass it to `graph.compile(checkpointer=...)`, and pass `config={"configurable": {"thread_id": ...}}` on every `invoke()`.
- **Guardrail layering (router-level vs agent-level; pre-model vs post-model)**: validation layers that inspect input before/after the LLM runs, or before/after routing, and redirect flow (refuse, clarify, redirect) instead of letting bad requests reach — or bad output leave — the model.
  - When to use: whenever an agent must stay within a defined domain/geographic scope, avoid cost abuse, or avoid unsafe/noncompliant output.
  - How: (1) router-level — a lightweight classifier LLM (`with_structured_output`) checks the raw user query and routes off-topic ones to a no-op `guardrail_refusal` node wired to `END`; (2) agent-level — a `pre_model_hook` function re-classifies the query with a stricter, agent-specific policy and, on failure, prepends a `SystemMessage` refusal instruction to `llm_input_messages` instead of blocking the whole graph.
- **State rewinding / time travel**: replaying a persisted graph up to a specific checkpoint using `get_state_history()` and a `checkpoint_id`, then resuming with `invoke(None, config=...)`.
  - When to use: debugging memory behavior, implementing "what if I'd chosen option B" branching, or recovering after manual intervention.
  - How: call `get_state_history(config)` to list `StateSnapshot`s newest-first, take one snapshot's `thread_id`/`checkpoint_id`, build a `new_config` pointing at it, call `get_state(new_config)` to inspect it, then `invoke(None, config=new_config)` to rehydrate before continuing.

## Key Concepts
- **Short-term memory**: context retained during a single session between user and LLM, typically in-memory or session-scoped.
- **Long-term user memory**: persistent across multiple sessions for the same user (preferences, past activity).
- **Long-term application memory**: persistent across all users and sessions (shared general knowledge, e.g., exchange rates).
- **Checkpoint**: a snapshot of graph execution state taken at a super-step (one node's execution; parallel nodes in the same step are grouped).
- **Thread**: a LangGraph session identified by a unique `thread_id`; links checkpoints to the conversation they belong to.
- **Guardrail**: an application-level mechanism (rule-based, retrieval-based, or model-based) that keeps an agent within scope, policy, and purpose by validating inputs/outputs.
- **Pre-model hook / post-model hook**: LangGraph `create_react_agent` parameters (`pre_model_hook`, `post_model_hook`) that intercept and can rewrite inputs before, or outputs after, the LLM call.
- **Human-in-the-loop**: escalating ambiguous, incomplete, or high-impact requests to a human reviewer, using a checkpoint to pause and later resume the workflow.
- **Belt-and-suspenders defense**: having both a system-wide (router) guardrail and a narrower, agent-specific guardrail so an agent stays safe even if reused or called directly.

## Mental Models
- **Guardrails as validation layers, not filters bolted on**: like input validation in traditional software, each component (router, individual agent) should validate its own inputs rather than trusting an upstream check alone — defense in depth applied to agents.
- **Checkpoints as the substrate for four use cases, not just chat memory**: state rehydration after failure, human-in-the-loop pausing, multi-turn context, and (implicitly) branching/time-travel are all the same mechanism — persisting state per super-step — applied differently.
- **Scope narrows as you go deeper into the graph**: router-level guardrails catch broad off-topic queries cheaply and early; agent-level guardrails catch narrower violations (e.g., wrong region) that only make sense to check once you know which agent would handle the request.
- **Production readiness as a checklist beyond the code you just wrote**: memory + guardrails is necessary but not sufficient — long-term memory, human-in-the-loop, post-model checks, evaluation, and deployment strategy are the remaining pillars.

## Anti-patterns
- **No guardrails at all**: lets off-topic queries (sports scores, financial tips) or unsafe/noncompliant responses through, causing hallucinations on out-of-scope topics and letting users exploit the assistant as a free gateway to an expensive LLM.
- **Relying only on a system-wide (router) guardrail**: an agent reused or invoked directly elsewhere loses protection if it doesn't also validate its own inputs — router-only checks are not "belt-and-suspenders."
- **Enabling `use_responses_api=True` without `use_previous_response_id=True`**: LangChain resends the full history every turn, which the OpenAI Responses API treats as a duplicate submission and rejects with an error.
- **Treating a `guardrail_refusal` node as doing real work**: it should be a pure no-op whose only job is providing a clean edge to `END` — putting logic there defeats the "early exit" design.
- **Skipping evaluation before production**: without functional, behavioral, performance, and regression testing, prompt/tool/model changes can silently break accuracy or safety with no way to detect regressions.

## Code Examples
```python
from langgraph.checkpoint.memory import InMemorySaver
checkpointer = InMemorySaver()

graph = StateGraph(AgentState)
graph.add_node("router_agent", router_agent_node)
graph.add_node("travel_info_agent", travel_info_agent)
graph.add_node("accommodation_booking_agent", accommodation_booking_agent)
graph.add_edge("travel_info_agent", END)
graph.add_edge("accommodation_booking_agent", END)
graph.set_entry_point("router_agent")
travel_assistant = graph.compile(checkpointer=checkpointer)
```
- **What it demonstrates**: wiring an `InMemorySaver` checkpointer into a compiled LangGraph graph so every node execution is snapshotted per `thread_id`.

```python
def pre_model_guardrail(state: dict):
    messages = state.get("messages", [])
    last_msg = messages[-1] if messages else None
    if not isinstance(last_msg, HumanMessage):
        return {}
    user_input = last_msg.content
    classifier_messages = [
        SystemMessage(content=AGENT_GUARDRAIL_SYSTEM_PROMPT),
        HumanMessage(content=user_input),
    ]
    decision = llm_guardrail.invoke(classifier_messages)
    if decision.is_travel:
        # Allow normal flow; do not modify inputs
        return {}
    return {"llm_input_messages": [SystemMessage(content=AGENT_REFUSAL_INSTRUCTION), *messages]}
```
- **What it demonstrates**: an agent-level `pre_model_hook` that classifies the latest user message and, on a scope violation, prepends a refusal `SystemMessage` instead of blocking the graph outright.

```python
last_snapshot = list(state_history_list)[0]
thread_id = last_snapshot.config["configurable"]["thread_id"]
last_checkpoint_id = last_snapshot.config["configurable"]["checkpoint_id"]
new_config = {"configurable": {"thread_id": thread_id, "checkpoint_id": last_checkpoint_id}}
retrieved_snapshot = travel_assistant.get_state(new_config)
travel_assistant.invoke(None, config=new_config)
```
- **What it demonstrates**: rewinding to a specific past checkpoint via `checkpoint_id` and resuming execution from it with `invoke(None, ...)`.

## Reference Tables
Table 14.1 — Types of memory in AI agents:

| Memory type | Scope | Persistence | Example (travel assistant) | Challenges |
|---|---|---|---|---|
| Short-term | Single user session | Until session ends | Remembering "same town" in a weather follow-up within one conversation | Limited continuity; lost when session closes |
| Long-term (user) | Across multiple sessions for one user | Weeks, months, or years | Remembering a user's preferred Cornwall destinations or accommodation types | Privacy compliance and managing the persisted data |
| Long-term (application) | Across all users and sessions | Ongoing | Storing general travel updates (e.g., Cornwall event calendar, seasonal attraction schedules) | Keeping data fresh; avoiding outdated or incorrect information |

Guardrail categories (by mechanism): rule-based (explicit conditions/regex), retrieval-based (checked against approved data sources), model-based (compact classification/moderation models).

Guardrail insertion points (by stage): pre-model checks (reject before LLM runs), post-model checks (verify generated output), routing-stage checks (decide tool/branch), tool-level checks (block unsafe/unauthorized tool actions).

## Worked Example
Building the checkpointer-enabled, guardrailed `travel_assistant` end to end:

1. **Stateless baseline**: originally each turn calls `travel_assistant.invoke({"messages": [HumanMessage(content=user_input)]})` with no session concept.
2. **Add a thread ID**: generate `thread_id = uuid.uuid1()` once per chat loop and build `config = {"configurable": {"thread_id": thread_id}}`; pass it on every `invoke(state, config=config)`.
3. **Add a checkpointer**: `checkpointer = InMemorySaver()` (swap for `SqliteSaver`/`PostgresSaver` in production), then `graph.compile(checkpointer=checkpointer)`. Now every node execution is snapshotted under the thread.
4. **Enable conversation continuity in the LLM**: `ChatOpenAI(model="gpt-5", use_responses_api=True, use_previous_response_id=True)` so only the previous response ID is resent, not the full transcript.
5. **Run it**: ask "What's the weather like in Penzance?" then follow up "What's the weather in the same town now?" — the assistant correctly resolves "same town" to Penzance because the checkpointer fed the full history back to the LLM.
6. **Manually rewind** (to understand the mechanism): after a turn, call `get_state_history(config)`, take the newest `StateSnapshot`, extract its `thread_id`/`checkpoint_id`, build `new_config`, call `get_state(new_config)` to confirm the snapshot's content, then `invoke(None, config=new_config)` to rehydrate, and ask the same follow-up ("What is the weather in the same town?") — it again resolves to Penzance, proving the rehydrated state (not just the live thread) drives context resolution.
7. **Add a router-level guardrail**: define `GuardrailDecision(BaseModel)` with `is_travel: bool` and `reason: str`; wrap the LLM with `llm_guardrail = llm_model.with_structured_output(GuardrailDecision)`; add a no-op `guardrail_refusal_node` wired to `END`. In the router, invoke `llm_guardrail` first — if `is_travel` is `False`, return `Command(update={"messages": [AIMessage(content=refusal_text)]}, goto="guardrail_refusal")`; otherwise route to the appropriate agent as before. Testing with "Can you give me the latest results of Inter Milan?" yields `is_travel=False` and a polite refusal.
8. **Add agent-level guardrails**: define a stricter `AGENT_GUARDRAIL_SYSTEM_PROMPT` that only accepts Cornwall-specific travel queries, and attach `pre_model_guardrail` as `pre_model_hook` to both `travel_info_agent` and `accommodation_booking_agent` (via `create_react_agent(..., pre_model_hook=pre_model_guardrail)`). Testing with "Can you give me some travel tips for Liverpool (UK)?" — a travel question, but out of Cornwall scope — triggers `is_travel=False` at the agent level and produces a Cornwall-specific refusal, even though it would pass a looser router-level check for "travel-relatedness" alone.
9. **Result**: two layers of defense — router-level (rejects nontravel queries fast) and agent-level (enforces Cornwall-only scope) — protect the workflow from both irrelevant and out-of-coverage requests.

## Key Takeaways
1. Use a `thread_id` + checkpointer pair to make any LangGraph agent stateful; swap `InMemorySaver` for `SqliteSaver`/`PostgresSaver` when moving to production for durability and concurrency.
2. Checkpoints capture the entire graph state per node execution, not just chat text — this is what enables failure recovery, human-in-the-loop pausing, and time-travel debugging with the same mechanism.
3. Pass `use_previous_response_id=True` alongside `use_responses_api=True` with OpenAI's Responses API, or duplicate-submission errors occur.
4. Put a fast, cheap classifier-based guardrail at the router level to reject off-topic queries before any expensive downstream agent work happens.
5. Duplicate guardrail logic at the agent level (via `pre_model_hook`) even when a router-level check exists — agents should validate their own inputs, especially if they might be reused or invoked directly.
6. Guardrails can act by rewriting `llm_input_messages` (soft redirect to a refusal) or by using `Command(goto=...)` to hard-exit the graph — pick the mechanism that matches the trust level needed.
7. Memory and guardrails are foundational but not sufficient for production: budget separately for long-term memory, human-in-the-loop, post-model output guardrails, systematic evaluation, and a deployment strategy (LangGraph Platform / Open Agent Platform).

## Connects To
- **Ch 12**: the router-based multi-agent `travel_assistant` (travel info + accommodation booking agents) built here is the same one this chapter enhances with memory and guardrails.
- **Ch 11**: tool-based `create_react_agent` agents are extended with `pre_model_hook`/`post_model_hook` for guardrail injection.
- **Ch 13**: MCP servers and enterprise data sources are the kind of components the Open Agent Platform (OAP) is designed to bridge into.
- **Human-in-the-loop**: relies on the same checkpointer/thread mechanism to pause a workflow and resume after manual review.
- **Evaluation of AI agents**: functional, behavioral, performance, and regression testing (with tools like LangSmith) form the ongoing counterpart to the guardrails built in this chapter.
