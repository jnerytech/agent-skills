# Chapter 5: Agentic workflows with LangGraph

## Core Idea
LangGraph extends LangChain from linear chains to a graph-based execution model — typed state, nodes, and edges — enabling conditional branching and cyclical workflows that plain chains can't express cleanly.

## Frameworks Introduced
- **Agentic workflow vs. agent (design pattern distinction)**: a workflow guides the app through a fixed sequence where the LLM only selects among predefined options; an agent reasons, decides, and dynamically determines next steps based on tools and evolving context.
  - When to use: pick workflows when the task decomposes into a bounded set of known steps/routes; pick agents when the system must adapt paths in real time to new information.
  - How: workflows commonly implement Controller-Worker (controller orchestrates workers in sequence) or Router (LLM routes to the right worker) patterns.
- **LangGraph StateGraph (node/edge/state model)**: a framework for building stateful, multi-step AI applications as a directed graph — nodes are processing functions, edges define transitions, and a typed state object flows through and accumulates updates.
  - When to use: when an app needs decisions based on prior results, explicit state tracking, branching, or repeated/cyclical steps — things LangChain's linear `chain = (prompt | llm | parser)` composition can't handle well.
  - How: (1) define state as a `TypedDict`, (2) implement each processing step as a node function `(state) -> dict` returning partial updates, (3) wire nodes with `add_edge` / `add_conditional_edges`, (4) set an entry point and route terminal nodes to `END`, (5) `compile()` and `invoke()`.

## Key Concepts
- **State**: a strongly typed object (Python `TypedDict`) that defines the data structure flowing through the entire graph; enforced explicitly, unlike chains' implicit/loosely typed state.
- **Node**: a processing unit, usually a Python function, that receives the current state and returns a partial state update (not a full replacement).
- **Edge**: a directed connection between two nodes defining the flow of data/execution.
- **Conditional edge**: an edge governed by a router function that inspects runtime state and returns a string naming the next node, enabling dynamic branching.
- **Entry point**: the node where graph execution begins, set via `graph.set_entry_point(...)` (or the `START` constant).
- **END condition**: the built-in `END` marker that terminates execution when an edge routes to it.
- **Compile**: `graph.compile()` validates the graph structure and produces an executable application (`app`).
- **Controller-Worker pattern**: an LLM-driven controller assigns tasks to workers in a defined sequence.
- **Router pattern**: an LLM simply directs a task to the appropriate worker/processor based on context.

## Mental Models
- **Chains vs. graphs**: a chain is a straight pipe — data flows one direction, once, through fixed stages. A graph is a map with junctions — the same "stages" become nodes, but execution can branch, loop back, or terminate conditionally based on what the state currently holds. Moving from chain to graph is a shift from "what happens next is fixed in code" to "what happens next is decided at runtime by the state."
- **LangGraph as blueprint, LangChain as building blocks**: LangChain supplies components (LLMs, embeddings, retrievers); LangGraph supplies the structure that organizes those components into a stateful, controllable system. LangGraph is not a replacement — it's an orchestration layer on top.
- **State as the single source of truth**: instead of each step implicitly threading its output into the next step's input (as in a chain), every node reads from and writes to one explicit, typed state object. This makes "what does this step need" and "what does this step change" inspectable and testable in isolation.
- **Conditional routing as an explicit decision function**: a router function is just `state -> next_node_name (str)`. Treat branching logic as a pure function you can reason about and test independently of the graph wiring.

## Anti-patterns
- **Forcing dynamic/conditional logic into a linear LangChain chain**: works initially but becomes cumbersome — e.g., "redirect to regenerate queries if <50% of summaries are relevant" is hard to express in `prompt | llm | parser`-style composition; this is exactly the signal to move to LangGraph.
- **Leaving state implicit or loosely typed**: makes it hard to track data across steps, complicates debugging, and obscures which part of a pipeline failed — LangGraph's typed `TypedDict` state exists specifically to prevent this.
- **Unbounded refinement loops**: a conditional edge that loops back (e.g., regenerate queries) without a hard iteration cap risks infinite loops; the chapter's example caps iterations at 3 and forces progression to report writing once the cap is hit.
- **Node functions returning full state instead of partial updates**: nodes should return only the fields they change (e.g., `return {"search_queries": queries}`), not reconstruct/overwrite the entire state object.

## Code Examples
```python
from langgraph.graph import StateGraph
from typing import TypedDict

class ResearchState(TypedDict):
    input_query: str
    intermediate_result: str
    final_output: str

graph = StateGraph(ResearchState)
```
- **What it demonstrates**: defining a typed state and instantiating a `StateGraph` around it.

```python
def generate_search_queries(state: dict) -> dict:
    """Generate search queries based on user question."""
    question = state["user_question"]
    queries = llm_generate_queries(question)
    return {"search_queries": queries}

graph.add_node("generate_queries", generate_search_queries)
graph.add_edge("generate_queries", "perform_searches")

def should_refine_queries(state: dict) -> str:
    if len(state["search_results"]) < 2:
        return "refine_queries"
    else:
        return "summarize_results"

graph.add_conditional_edge("perform_searches", should_refine_queries)
```
- **What it demonstrates**: a node function returning a partial state update, a simple linear edge, and a conditional edge whose router returns the next node name based on state.

```python
graph.set_entry_point("parse_question")

from langgraph.graph import END
graph.add_edge("write_final_report", END)
```
- **What it demonstrates**: setting the graph's entry point and terminating a path at `END`.

## Reference Tables
| Aspect | LangChain chain | LangGraph graph |
|---|---|---|
| Flow | Linear, fixed sequence (`prompt \| llm \| parser`) | Directed graph with branching and cycles |
| State | Implicit/loosely typed, threaded step to step | Explicit, strongly typed (`TypedDict`), shared and accumulated |
| Branching | Cumbersome to express conditional paths | Native via `add_conditional_edges` with a router function |
| Repetition | Hard to repeat steps based on new information | Native via cyclical edges (loop back to earlier node) |
| Parallelism | Falls short for multiple concurrent processes | Supported by the graph structure |
| Debugging | Unclear which part of the chain failed | Modular nodes/edges make failure points traceable |
| Error handling | Difficult without explicit state | Each node can implement its own error handling |

## Worked Example
Transforming the chapter 4 web research assistant (LangChain sequential chains) into a LangGraph agentic workflow:

1. **Original LangChain shape**: `assistant_instructions_chain | web_searches_chain | search_and_summarization_chain.map() | RunnableLambda(...) | RESEARCH_REPORT_PROMPT_TEMPLATE | get_llm() | StrOutputParser()` — a single rigid pipeline: select assistant → generate queries → search → summarize → write report. Limitations: rigid/linear (can't redirect based on intermediate relevance), no explicit state, hard error handling, hard debugging.

2. **Identify nodes** (one per responsibility): Assistant Selector, Query Generator, Web Searcher, Content Summarizer, Relevance Evaluator (new), Report Writer. The new element is a conditional branch: after evaluating relevance, either proceed to Report Writer or loop back to Query Generator, capped at 3 iterations.

3. **Step 1 — Define the state**: compose typed dicts (`AssistantInfo`, `SearchQuery`, `SearchResult`, `SearchSummary`, `ResearchReport`) into one `ResearchState(TypedDict)` holding `user_question`, `assistant_info`, `search_queries`, `search_results`, `search_summaries`, `research_summary`, `final_report`, `used_fallback_search`, `relevance_evaluation`, `should_regenerate_queries`, `iteration_count`.

4. **Step 2 — Convert components to node functions**: e.g. `select_assistant(state)` calls the LLM with the assistant-selection prompt, parses the response, returns `{"assistant_info": assistant_info}`; `generate_search_queries(state)` builds a prompt from `assistant_info` and `user_question`, calls the LLM, parses queries, returns `{"search_queries": search_queries}`. Every node follows this read-state → process → return-partial-update pattern.

5. **Step 3 — Define the graph structure**: `graph = StateGraph(ResearchState)`; add all six nodes with `graph.add_node(...)`; wire the linear portion with `add_edge` (select_assistant → generate_search_queries → perform_web_searches → summarize_search_results → evaluate_search_relevance); define `route_based_on_relevance(state)`, which increments `iteration_count`, forces `"write_research_report"` once `iteration_count >= 3`, otherwise returns `"generate_search_queries"` if `should_regenerate_queries` else `"write_research_report"`; wire it with `graph.add_conditional_edges("evaluate_search_relevance", route_based_on_relevance, {"generate_search_queries": "generate_search_queries", "write_research_report": "write_research_report"})`; route `write_research_report` to `END`; set entry point to `"select_assistant"`.

6. **Step 4 — Compile and run**: `app = graph.compile()`; build an `initial_state` dict with all fields populated (most `None`, `iteration_count: 0`, `used_fallback_search: False`) and a real `user_question`; run `result = app.invoke(initial_state)`; extract `result["final_report"]`.

7. **Outcome**: the Relevance Evaluator node checks whether ≥50% of summaries are relevant. If not, and under the 3-iteration cap, the flow loops back to regenerate queries; otherwise it proceeds to write the report — dynamic behavior that would be cumbersome to build with plain LangChain chains.

## Key Takeaways
1. Reach for LangGraph specifically when a task needs conditional branching, cyclical retries, or explicit state — not for simple, one-direction pipelines where a LangChain chain still suffices.
2. Model state as a `TypedDict` up front; it's the contract every node reads from and writes to, and it's what makes the workflow debuggable.
3. Node functions should be near-pure: take state in, return only the fields they change, not the whole state.
4. Conditional edges are just router functions (`state -> str`) mapped to a dict of `{return_value: next_node_name}` — keep branching logic isolated and testable.
5. Always cap cyclical/refinement loops (e.g., max iterations) to avoid infinite loops in agentic workflows.
6. LangGraph doesn't replace LangChain — LangChain components (LLMs, prompts, parsers) still do the work inside each node; LangGraph only supplies the orchestration.
7. Converting a chain to a graph is a mechanical process: identify component boundaries as nodes, define the shared state schema, wire linear edges for the fixed path, add conditional edges for the decision points, set entry point and `END`.

## Connects To
- **Ch 4**: the original LangChain-based web research summarization engine that this chapter converts step by step into a LangGraph agentic workflow.
- **Ch 11–14 (Part 5)**: multi-tool agents and multi-agent systems build on the StateGraph/node/edge foundations introduced here.
- **Anthropic's "Building Effective Agents"**: referenced in the chapter as further reading on when to choose workflows vs. agents.
