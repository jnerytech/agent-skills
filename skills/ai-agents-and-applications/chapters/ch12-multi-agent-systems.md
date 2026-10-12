# Chapter 12: Multi-agent systems

## Core Idea
Single agents hit a ceiling when a request spans multiple specialized domains; splitting capability across dedicated agents and coordinating them — first via a deterministic Router, then via a more flexible Supervisor — lets a system answer both simple, single-domain queries and complex, multi-part queries in one conversation.

## Frameworks Introduced
- **Router agent pattern**: an LLM classifies the incoming user message into one of a fixed set of agent types (via structured output), then a graph `Command` hands off the unchanged state to that agent node.
  - When to use: queries that cleanly belong to exactly one specialist domain — a "one-way ticket" through the workflow.
  - How: (1) enumerate agent types (`Enum`), (2) define a Pydantic structured-output model for the classification, (3) bind it with `llm.with_structured_output(...)`, (4) write a classification system prompt, (5) implement a router node that reads the last `HumanMessage`, invokes the classifier, and returns `Command(update=state, goto=agent_name)`, (6) wire specialist agents as graph nodes with edges to `END`.
- **Supervisor pattern**: a higher-level "agent of agents" that wraps each specialist agent as a callable tool and can invoke them repeatedly, in any order, combining intermediate results before responding.
  - When to use: multi-part requests that require several specialists to collaborate and share intermediate results — a "return ticket" interaction, not a single dispatch.
  - How: (1) give each `create_react_agent` a unique `name`, (2) `pip install langgraph-supervisor` and import `create_supervisor`, (3) call `create_supervisor(agents=[...], model=...)` instead of passing a tool list, (4) prefer a more powerful LLM for the supervisor since it must decompose tasks and coordinate multiple agents, (5) invoke it exactly like a ReAct agent (`travel_assistant.invoke(state)`).

## Key Concepts
- **Router agent**: classifies incoming queries with an LLM and delegates each one, once, to a single specialist agent.
- **Supervisor agent**: orchestrates multiple specialist agents as tools, deciding which to activate — possibly several times — to decompose and answer complex requests.
- **Agent handoff**: the transfer of control from one agent to another; in the router this is a single `Command(goto=...)` dispatch, in the supervisor it's a `transfer_to_<agent_name>` tool call.
- **One-way ticket vs. return ticket**: the router routes each query to exactly one agent and ends; the supervisor can revisit agents multiple times in a session to collect and combine results.
- **Structured routing output**: a Pydantic model (`AgentTypeOutput`) constrains the LLM's classification decision to a fixed enum, avoiding string parsing.
- **Agent-as-tool**: under the Supervisor pattern, each specialist `create_react_agent` is wrapped and exposed to the supervisor as an invocable tool rather than being wired as a fixed graph edge.
- **current_agent / agent_history state fields**: recommended state fields for tracking which agent handled each step of a multi-agent workflow, for observability and debugging.
- **Hybrid architecture**: the router/supervisor layer is workflow-driven (deterministic dispatch logic), while each specialist agent underneath still runs its own flexible, tool-based ReAct decision loop.

## Mental Models
- **One-way ticket vs. return ticket**: think of the router as issuing a single, non-refundable ticket — one classification, one agent, done. The supervisor issues open return tickets — it can send the conversation back to any agent as many times as needed until the full request is satisfied. Reach for a supervisor the moment a query can't be answered by exactly one destination.
- **Agents as tools, recursively**: a ReAct agent treats functions as tools it can call; the Supervisor pattern treats whole agents as tools. The orchestration mechanism doesn't change — only what's being invoked does. This makes multi-agent systems a natural extension of tool-calling agents rather than a separate paradigm.
- **Two layers of decision-making**: in both patterns, there's a deterministic/classification layer on top (router logic or supervisor planning) and a dynamic, tool-based reasoning layer underneath (each specialist's own ReAct loop). Debugging means figuring out which layer made the wrong call.

## Anti-patterns
- **Unstructured natural-language inter-agent communication**: when agents pass data between each other, use structured formats (e.g., JSON), not natural language — parsing unstructured inter-agent communication increases error rates.
- **Routing without a default or confidence threshold**: a router without explicit handling for ambiguous queries (a default route, or a request for clarification below a confidence threshold) will misroute edge cases.
- **Supervisor with no visibility into specialist capabilities**: the supervisor's planning prompt needs each specialist agent's tool list and capability description, or it can't decompose tasks correctly.
- **Forcing multi-domain requests through a router**: a query that inherently needs two specialists to share intermediate results (e.g., "find a town with good weather, then check hotel availability there") cannot be answered by a one-way-ticket router — it needs a supervisor.
- **Loosely scoped agent prompts**: each agent needs a clearly defined scope, tools list, and example queries it should handle; vague prompts blur which agent should own a given request.

## Code Examples
```python
class AgentType(str, Enum):
    travel_info_agent = "travel_info_agent"
    accommodation_booking_agent = "accommodation_booking_agent"

class AgentTypeOutput(BaseModel):
    agent: AgentType = Field(..., description="Which agent should handle the query?")

llm_router = llm_model.with_structured_output(AgentTypeOutput)

def router_agent_node(state: AgentState) -> Command[AgentType]:
    """Router node: decides which agent should handle the user query."""
    messages = state["messages"]
    last_msg = messages[-1] if messages else None
    if isinstance(last_msg, HumanMessage):
        user_input = last_msg.content
        router_messages = [
            SystemMessage(content=ROUTER_SYSTEM_PROMPT),
            HumanMessage(content=user_input)
        ]
        router_response = llm_router.invoke(router_messages)
        agent_name = router_response.agent.value
        return Command(update=state, goto=agent_name)
    return Command(update=state, goto=AgentType.travel_info_agent)
```
- **What it demonstrates**: a router node that classifies the last human message via structured output and hands off state to the chosen agent node with `Command(goto=...)`, defaulting to `travel_info_agent` when there's no human message.

```python
travel_info_agent = create_react_agent(
    model=llm_model,
    tools=TOOLS,
    state_schema=AgentState,
    name="travel_info_agent",
    prompt="""You are a helpful assistant that can search travel information
    and get the weather forecast. Only use the tools to find the information
    you need (including town names).""",
)
accommodation_booking_agent = create_react_agent(
    model=llm_model,
    tools=BOOKING_TOOLS,
    state_schema=AgentState,
    name="accommodation_booking_agent",
    prompt="""You are a helpful assistant that can check hotel and BnB room
    availability and price for a destination in Cornwall. You can use the
    tools to get the information you need. If the user does not specify the
    accommodation type, you should check both hotels and BnBs.""",
)
```
- **What it demonstrates**: giving each specialist agent a unique `name`, a prerequisite for wrapping them as tools under a Supervisor.

## Reference Tables
| Aspect | Router pattern | Supervisor pattern |
|---|---|---|
| Interaction shape | One-way ticket — single dispatch per query | Return ticket — agents can be revisited multiple times |
| Coordination unit | Graph node + `Command(goto=...)` | Specialist agent wrapped as a tool |
| Best for | Single-domain queries | Multi-part, cross-domain queries needing shared intermediate results |
| Setup | `Enum` of agent types + Pydantic structured output + router node | `create_supervisor(agents=[...], model=...)` from `langgraph-supervisor` |
| Recommended LLM | Any classification-capable model | A more powerful model (e.g., GPT-5) to handle decomposition/coordination |
| Handoff mechanism | Explicit `Command` to a fixed next node | Dynamic `transfer_to_<agent_name>` tool calls |

## Worked Example
Building the UK travel assistant end to end, from two isolated agents to a Supervisor-coordinated system:

1. **Leaf agents already exist** (from earlier in the chapter): a `travel_info_agent` (search + weather tools) and an `accommodation_booking_agent` combining a SQL toolkit over `cornwall_hotels.db` (`SQLDatabaseToolkit`) with a `check_bnb_availability` tool backed by a mocked `BnBBookingService`. Both are ReAct agents built with `create_react_agent`.

2. **Router version** (`main_05_01.py`): import `StateGraph`, `END`, `Command`. Define `AgentType` enum and `AgentTypeOutput` Pydantic model; bind `llm_router = llm_model.with_structured_output(AgentTypeOutput)`. Write `ROUTER_SYSTEM_PROMPT` instructing the LLM to classify a message as a travel-information question or an accommodation-booking question and respond with the matching agent name. Implement `router_agent_node` (shown above) as the graph's entry node, with `travel_info_agent` and `accommodation_booking_agent` as downstream nodes, each edged to `END`. The router-to-specialist connection isn't a static edge — it's resolved at runtime by the `Command` the router returns.
   - Try: "What are the main attractions in St Ives?" → routed to `travel_info_agent`.
   - Try: "Are there any hotel or BnB rooms available in Penzance this weekend?" → routed to `accommodation_booking_agent`.
   - Limitation surfaced: "Can you find a nice seaside Cornwall town with good weather right now and find availability and price for one double hotel room in that town?" cannot be answered — it needs both agents to collaborate and share intermediate results, which a one-way router can't do.

3. **Supervisor version** (`main_06_01.py`): `pip install langgraph-supervisor`; `from langgraph_supervisor.supervisor import create_supervisor`. Re-create both leaf agents, this time each with a unique `name` ("travel_info_agent", "accommodation_booking_agent"). Build `travel_assistant = create_supervisor(agents=[travel_info_agent, accommodation_booking_agent], model=llm_model, ...)` — configuration mirrors a ReAct agent, but a list of agents replaces the list of tools. Use a stronger model for the supervisor's own reasoning since it must decompose multi-step requests. Wire the chat loop to `result = travel_assistant.invoke(state)`.

4. **Run the multi-part query** through the supervisor. The LangSmith trace shows: `travel_assistant` calls `transfer_to_travel_info_agent` → `travel_info_agent` calls `search_travel_info` then `weather_forecast` → control returns to `travel_assistant`, which calls `transfer_to_accommodation_booking_agent` → `accommodation_booking_agent` calls `check_bnb_availability` and `sql_db_query`. The supervisor coordinated both specialists, and each specialist's own tool-based ReAct loop ran underneath — a hybrid, two-layer architecture (deterministic supervisor dispatch on top, dynamic tool reasoning below).

## Key Takeaways
1. Start with a router when queries map cleanly to one specialist; move to a Supervisor only when requests genuinely need multiple agents to collaborate and share intermediate results.
2. Use structured output (a Pydantic model over an `Enum`) for routing decisions instead of parsing free-text LLM responses.
3. A Supervisor is configured almost identically to a ReAct agent — the key difference is passing a list of named agents instead of a list of tools.
4. Give the supervisor a stronger model than the specialists, since it alone is responsible for task decomposition and multi-agent coordination.
5. Track `current_agent` and `agent_history` in state so you can audit which agent handled each step, and use LangSmith traces to see the full decision tree (agents, tools called, handoffs).
6. Pass structured data (JSON), never free-form natural language, between agents to keep inter-agent communication reliable.
7. Validate routing quality with a labeled dataset of queries and correct agent assignments, measuring classification accuracy and refining the router prompt from the error analysis.

## Connects To
- **Ch 5**: the router and supervisor graphs are both built on the `StateGraph`/node/`Command` foundations from LangGraph's agentic workflow model.
- **Ch 11**: the hotel and B&B booking tools (SQL toolkit, custom `@tool`-decorated `check_bnb_availability`) built here are the same tool-based ReAct agent techniques introduced for single-agent tool use.
- **LangSmith tracing**: used throughout to inspect router decisions, supervisor handoffs, and each specialist agent's tool calls step by step.
