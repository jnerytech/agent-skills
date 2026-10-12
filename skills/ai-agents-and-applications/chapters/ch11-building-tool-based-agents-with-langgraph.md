# Chapter 11: Building tool-based agents with LangGraph

## Core Idea
Agents differ from agentic workflows in that the LLM itself decides, turn by turn, which tools to call and in what order via the tool-calling protocol — this chapter builds that loop from scratch (custom nodes and graph wiring), then collapses it into LangGraph's prebuilt `create_react_agent`.

## Frameworks Introduced
- **ReAct pattern (Reasoning and Acting)**: interleaves LLM "thoughts" with tool "actions" in a cycle — Reasoning → Act (tool call) → Reasoning → ... → Final Answer.
  - When to use: whenever the sequence/choice of tool calls can't be predetermined and must depend on evolving context (the reason to pick an agent over a fixed agentic workflow).
  - How: the LLM node examines the conversation; if it emits `tool_calls`, route to a tools-execution node, feed results back into the LLM node, and repeat until the LLM emits a plain content answer instead of tool calls.
- **Tool-calling protocol**: the mechanism by which an LLM is given a tool's name, description, and parameter JSON schema, and can respond with a structured request to invoke it instead of (or before) generating text.
  - When to use: whenever the agent must dynamically choose among external capabilities (search, APIs, code execution) rather than following a hardcoded call sequence.
  - How: register tools (`@tool` decorator or manual OpenAI schema) → bind them to the model (`llm_model.bind_tools(TOOLS)`) → model returns either `content` (final answer) or `tool_calls` (name + args + id) → application executes the call → results are appended as `ToolMessage`s and sent back to the model.
- **Prebuilt LangGraph ReAct agent**: `create_react_agent` encapsulates the LLM node, tool-execution node, conditional routing, and retry/step-limit logic that you'd otherwise hand-wire.
  - When to use: once the manual graph is understood and correct — for production/rapid development where boilerplate orchestration isn't the point.
  - How: `create_react_agent(model=llm_model, tools=TOOLS, state_schema=AgentState, prompt=system_prompt)`; no manual `bind_tools`, no custom nodes, no explicit graph wiring.

## Key Concepts
- **Function calling**: the original OpenAI mechanism letting a model request a specific function with structured arguments; evolved into the broader tool-calling protocol.
- **Tool**: any external function, service, or capability an LLM can invoke through the tool-calling protocol, passing structured inputs and receiving structured outputs.
- **Agent state**: the `TypedDict` (e.g., `messages: Annotated[Sequence[BaseMessage], operator.add]`) that accumulates the full conversation — human, AI, system, and tool messages — as the single thing flowing through the graph.
- **`tools_condition`**: LangGraph's prebuilt conditional-edge function that inspects the last message for a `tool_calls` property and routes to the `"tools"` node if present, or to `END` otherwise.
- **`ToolNode`**: LangGraph's built-in node class that executes requested tool calls and appends `ToolMessage` results, replacing a hand-written execution node.
- **System guidance**: a `SystemMessage` plus explicit per-tool `description=` text used to steer the LLM away from relying on its own pretrained "knowledge" and toward actually calling the registered tools.
- **`RemainingSteps`**: a managed state field (`langgraph.managed.is_last_step.RemainingSteps`) used by the prebuilt ReAct agent to bound how many tool-calling rounds it will run.
- **REPL (Read-Eval-Print Loop)**: the chat-loop pattern (read input → wrap as `HumanMessage` → `agent.invoke(state)` → print last message) that drives the agent interactively.

## Mental Models
- **Reasoning/Act as a state machine, not a script**: the LLM node and tools node are the only two states; the conditional edge (`tool_calls` present or not) is the only transition rule. Everything the agent "does" emerges from looping this pair, not from hardcoded branches per scenario.
- **The model only does what its knowledge of the tools allows**: an underspecified tool description (or missing system guidance) doesn't cause an error — it causes the LLM to silently fall back on its own pretraining (e.g., picking towns from memory instead of calling `search_travel_info`). Treat tool descriptions and system prompts as the actual interface contract with the model's behavior, not documentation.
- **From-scratch first, prebuilt second**: build the graph manually once so you can inspect exactly what `tool_calls`, `ToolMessage`, and routing look like in the debugger; only then swap to `create_react_agent`, so the abstraction isn't a black box.
- **Adding a tool is a data change, not a structural one**: once the graph/loop exists, adding `weather_forecast` alongside `search_travel_info` required zero changes to graph wiring — only an addition to the `TOOLS` list. The LLM's tool-selection reasoning absorbs the new capability.

## Anti-patterns
- **Under-specified tool descriptions / no system guidance**: causes the LLM to default to its own pretraining instead of calling the tool (e.g., it names Newquay/Falmouth from memory rather than running `search_travel_info`) — undermines reliability and grounding.
- **Hardcoding API calls instead of exposing tools**: defeats the purpose of an agent; if the sequence and parameters of calls can be predicted in advance, use an agentic workflow (chapter 5), not an agent.
- **Skipping the from-scratch build**: jumping straight to `create_react_agent` without understanding `tool_calls`, `ToolMessage`, and the conditional-edge mechanics makes it harder to debug when the prebuilt agent misbehaves.
- **Unbounded tool-calling loops**: without something like `RemainingSteps` (or an iteration cap), an agent stuck failing its own success condition (e.g., never finding "nice weather") could loop indefinitely.

## Code Examples
```python
class ToolsExecutionNode:
    """Execute tools requested by the LLM in the last AIMessage."""
    def __init__(self, tools: Sequence):
        self._tools_by_name = {t.name: t for t in tools}

    def __call__(self, state: dict):
        messages: Sequence[BaseMessage] = state.get("messages", [])
        last_msg = messages[-1]
        tool_messages: list[ToolMessage] = []
        tool_calls = getattr(last_msg, "tool_calls", [])
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool = self._tools_by_name[tool_name]
            result = tool.invoke(tool_args)
            tool_messages.append(
                ToolMessage(
                    content=json.dumps(result),
                    name=tool_name,
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": tool_messages}

tools_execution_node = ToolsExecutionNode(TOOLS)
```
- **What it demonstrates**: manually executing whatever tool calls the LLM requested and wrapping each result as a `ToolMessage` for the next LLM turn (LangGraph's built-in `ToolNode(TOOLS)` replaces this in practice).

```python
builder = StateGraph(AgentState)
builder.add_node("llm_node", llm_node)
builder.add_node("tools", tools_execution_node)
builder.add_conditional_edges("llm_node", tools_condition)
builder.add_edge("tools", "llm_node")
builder.set_entry_point("llm_node")
travel_info_agent = builder.compile()
```
- **What it demonstrates**: assembling the two-node ReAct-style agent graph — LLM node, tools node, conditional routing via `tools_condition`, and a loop-back edge from tools to the LLM.

```python
travel_info_agent = create_react_agent(
    model=llm_model,
    tools=TOOLS,
    state_schema=AgentState,
    prompt="""You are a helpful assistant that can search travel
    information and get the weather forecast. Only use the tools
    to find the information you need (including town names).""")
```
- **What it demonstrates**: replacing the custom `ToolsExecutionNode`, `llm_node`, and graph wiring entirely with LangGraph's prebuilt ReAct agent constructor.

## Reference Tables
| Aspect | Function calling (original) | Tool calling (current) |
|---|---|---|
| Scope | Model requests a specific user-defined function with structured args | Model can invoke functions, code interpreters, and native capabilities (e.g., web browsing) |
| API | Older Completion API | OpenAI Responses API (recommended, standardized, explicit) |
| LangChain equivalent | Manual schema dict passed to `tools=[...]` | `@tool`-decorated function + `llm_model.bind_tools(TOOLS)` |

| Build approach | What you write | What you get |
|---|---|---|
| From-scratch graph | `AgentState`, `ToolsExecutionNode`/`ToolNode`, `llm_node`, `StateGraph` wiring, `tools_condition` | Full visibility into every message/tool-call transition |
| Prebuilt ReAct agent (`create_react_agent`) | `model`, `tools`, `state_schema`, `prompt` only | Same orchestration, tool calling, and step-limit/retry logic, with far less code, plus LangSmith tracing for observability |

## Worked Example
Building the Cornwall travel assistant end to end, across three script versions (`main_01_01.py` → `main_02_0x.py` → `main_03_01.py`):

1. **Single-tool agent (`main_01_01.py`)**: load `.env` (`OPENAI_API_KEY`), build a Chroma vector store from Wikivoyage pages for `UK_DESTINATIONS` (`AsyncHtmlLoader` → `RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=128)` → `OpenAIEmbeddings`), cached via a singleton (`get_travel_info_vectorstore()`), and exposed as `ti_retriever`. Wrap it as `@tool def search_travel_info(query: str) -> str`, returning up to four results. Define `AgentState(TypedDict)` with `messages`. Register: `TOOLS = [search_travel_info]`; `llm_model = ChatOpenAI(model="gpt-5-mini", use_responses_api=True)`; `llm_with_tools = llm_model.bind_tools(TOOLS)`. Build the graph as in the Code Examples section, entry point `"llm_node"`. Wrap in a `chat_loop()` REPL. Debugging a query ("Suggest three towns with a nice beach in Cornwall") shows the LLM issuing three `search_travel_info` tool calls with rewritten queries, `ToolsExecutionNode` invoking each and collecting `ToolMessage`s, then the LLM synthesizing a grounded final answer (Newquay, St Ives, Falmouth) once no `tool_calls` remain, at which point `tools_condition` routes to `END`.

2. **Multi-tool agent (`main_02_01.py`)**: add a mock `WeatherForecastService.get_forecast(town)` returning `{town, weather, temperature}` from random choices, wrapped as `@tool def weather_forecast(town: str) -> dict`. Update `TOOLS = [search_travel_info, weather_forecast]` and rebind — no graph changes needed. Initial run on "Suggest two Cornwall beach towns with nice weather" shows a failure mode: the LLM picks towns (Newquay, Falmouth) from its own pretrained knowledge instead of calling `search_travel_info` first.

3. **Fix via system guidance (`main_02_02.py`)**: add explicit `description=` text to both `@tool` decorators, and append a `SystemMessage` inside `llm_node()` instructing the model to "Only use the tools to find the information you need (including town names)." Re-running the same query now forces the correct chain: `search_travel_info("beach towns in Cornwall")` → candidate towns from the vector store → `weather_forecast` calls per candidate → if weather is unsuitable, more `weather_forecast` calls on new candidates → final synthesized answer citing only tool-sourced towns and real (mock) weather.

4. **Refactor to prebuilt ReAct agent (`main_03_01.py`)**: copy `main_02_02.py`, import `RemainingSteps` from `langgraph.managed.is_last_step`, delete the manual `bind_tools` call, add `remaining_steps: RemainingSteps` to `AgentState`, delete `ToolsExecutionNode`, `llm_node`, and all graph-wiring code, and replace everything with a single `create_react_agent(...)` call carrying the same system prompt. Running it reproduces the same grounded, multi-step behavior (e.g., St Ives and Newquay with sunny weather) with far less code.

5. **Observability**: enabling LangSmith (`LANGSMITH_TRACING=true` plus endpoint/API key/project in `.env`) restores step-by-step visibility into the prebuilt agent — every LLM call, tool invocation, and message hand-off appears as a trace in the LangSmith UI, compensating for the reduced code-level visibility of `create_react_agent`.

## Key Takeaways
1. Build the agent loop manually at least once — `AgentState`, a tools-execution node, an LLM node, and `tools_condition` routing — before reaching for `create_react_agent`, so the abstraction never becomes a black box.
2. Tool descriptions and system prompts are behavioral contracts: vague ones cause the LLM to answer from pretrained knowledge instead of calling tools; explicit ones force grounded, tool-sourced answers.
3. Adding a new tool to a working agent is purely additive — extend the `TOOLS` list and rebind; no graph restructuring required, because the LLM handles orchestration dynamically.
4. Use `ToolNode` and `tools_condition` (LangGraph built-ins) instead of hand-rolling tool execution and routing logic once you understand what they replace.
5. `create_react_agent(model, tools, state_schema, prompt)` collapses the entire hand-wired graph into one call for production use, while `RemainingSteps` bounds runaway tool-calling loops.
6. LangSmith tracing (`LANGSMITH_TRACING=true` + project env vars) recovers the debugging visibility lost when switching from an explicit graph to a prebuilt agent.
7. Choose an agent over an agentic workflow (chapter 5) specifically when the tool sequence and parameters can't be predicted in advance and must be decided dynamically by the LLM.

## Connects To
- **Ch 5**: contrasts agentic workflows (fixed, conditional-path graphs) with agents (dynamic, LLM-driven tool selection); this chapter is the agent-side counterpart.
- **Ch 8**: reuses and streamlines the RAG vector-store techniques (chunking, embedding, Chroma) for the `search_travel_info` tool.
- **Ch 9**: references LLM query-rewriting behavior observed when the model issues multiple rewritten `search_travel_info` calls.
- **Ch 12 (Multi-agent systems)**: this chapter's multi-tool travel agent becomes the foundation for a multi-agent travel assistant combined with an accommodation-booking agent.
- **ReAct pattern**: Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models" (2022), https://arxiv.org/abs/2210.03629.
