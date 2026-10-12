# Chapter 6: Autonomous Agents with Memory and Tools

## Core Idea
An agent is an LLM used as a reasoning engine inside a loop: it picks an action (a tool call), observes the result, and decides what to do next until it reaches a final answer. Tools widen what it can do, memory carries state between steps and turns, and the framework you pick (ReAct, OpenAI functions, plan-and-execute, Tree of Thoughts) decides how it plans.

## Frameworks Introduced
- **Chain-of-Thought (CoT)**: guide the LLM through a series of steps or logical connections to reach a conclusion, by asking it to explain its decisions and to plan several steps before it gives a final answer.
  - When to use: tasks that need deep context or several factors weighed together, such as plans, strategies or multi-part problems.
  - How: give concrete context (budget, product type, audience, channels) and ask for a "step-by-step" plan. The phrase *step-by-step* is the key trigger.
  - Principle(s): Give Direction.
  - Why it works / failure mode: without CoT and context, "Create a marketing plan for a new software product" gets a generic 5-item list that fits any product. Adding the specifics ("project management software for SMBs, $20,000 budget, digital channels, step-by-step") gets a structured plan built for that product.

- **Agent components (Inputs / Goal or reward function / Available actions)**: three things govern an agent. *Inputs* are what it perceives. The *goal or reward function* is a target end state, or cumulative reward to maximize. *Available actions* are its action space.
  - When to use: designing any agent. The authors' analogy is a self-driving car (sensors; safe A-to-B navigation, where Tesla's reward is miles driven without intervention; accelerate, turn, change lanes).
  - How (LLM-specific mapping): inputs → turn everything (transcripts, data structures, readings) into **text**. Goal → **goal-driven directives** in the prompt. Actions → **functional tools**, where each new tool expands the action space. LLM agents add three more components: **memory**, **planning/execution strategies** and **retrieval** (vector similarity, SQL lookups).

- **ReAct (Reason and Act)**: the original agent framework, an improved CoT. The LLM produces observations after taking actions through tools, turns them into thoughts about which tool to use next, and loops until a "Final Answer" string appears or a maximum number of iterations is reached.
  - When to use: tasks that need several tools in sequence, introspection of earlier actions, or queries with multiple intents.
  - How (thought loop): 1. Observe the environment. 2. Interpret it with a thought. 3. Decide on an action. 4. Act on the environment. 5. Repeat until solved ("I've found the answer") or too many iterations. The prompt takes `{question}` plus `{tools}` (each tool is a function, a name and a description) and tells the model to emit `action:` / `action_input:` lines and never guess tool results.
  - Principle(s): Give Direction (step-by-step reasoning), Divide Labor.
  - Why it works / failure mode: separating thought from action lets the model ground each step in real tool output. On the downside, it is less stable than function calling and tends to call tools when a plain text reply would do. Without a stop sequence the model may hallucinate the tool result itself.

- **OpenAI Functions (function calling)**: a model fine-tuned to emit JSON function calls, with the LLM deciding at runtime whether to call one or more functions.
  - When to use: a definitive single action (simple search, data extraction), conversational agents, or parallel function calls inside one API request.
  - How: bind tools as JSON schemas (`convert_to_openai_tool`, `llm.bind_tools`) or use `create_openai_functions_agent`.
  - Principle(s): Give Direction. Each framework steers the LLM in its own way.

- **Agent Toolkits**: LangChain bundles of tools and chains for a specific domain: CSV Agent, Gmail Toolkit, OpenAI Agent, Python Agent, JSON Agent, Pandas DataFrame Agent and SQLDatabaseToolkit.
  - When to use: quickly automating a task over a known resource, such as questions over a CSV or CRUD on a SQL database.

- **Customizing standard agents**: `prefix` / `suffix` inject prompt templates into the agent. `max_iterations` (default 15 for the SQL agent) and `max_execution_time` cap cost when an agent loops forever.
  - Example: a custom `SQL_PREFIX` ("create a syntactically correct {dialect} query… limit to {top_k}… double-check your query… if unrelated return 'I don't know'") turns the SQL agent from suggesting an INSERT into actually running CRUD.

- **Memory (read before, write after)**: every LangChain memory system does two things per run. After it receives user input but *before executing*, it reads from memory and adds that to the input. After the run but *before returning*, it writes the inputs and outputs to memory.
  - How: make two design choices, (1) how to **preserve state** (an in-memory list, or a database such as `MongoDBChatMessageHistory` keyed by `session_id`) and (2) how to **query state** (last N messages, a rolling summary, or entity-specific facts).
  - Principle(s): Give Direction. Be explicit about memory parameters, such as K for a window.

- **Plan-and-Execute Agents**: split planning and tool execution into separate modules, each its own LLM with access to the objective, the current task and the completed tasks. Examples: **BabyAGI** and **AutoGPT**.
  - How (BabyAGI loop): fetch task → `execution_agent` performs it using context → enrich and store the result in a vector DB (Chroma/Weaviate) → `task_creation_agent` derives new tasks from the objective and the last result (as a list of dicts) → `prioritization_agent` reorders the list against the objective → repeat. LangChain's version is experimental.

- **Tree of Thoughts (ToT)**: goes past linear, token-level CoT by exploring several reasoning paths over coherent text chunks ("thoughts"). The model self-evaluates at each step and can plan ahead, backtrack and make global choices.
  - When to use: tasks where early decisions matter or that need strategic search, such as Game of 24, crosswords, creative writing or sudoku (LangChain's demo).
  - Evidence: GPT-4 solved Game of 24 4% of the time with CoT and 74% with ToT.

- **Callbacks**: `BaseCallbackHandler` hooks (`on_llm_start`, `on_llm_new_token`, `on_chain_error`, `on_tool_end`, `on_agent_action`, `on_agent_finish`, …) for monitoring and debugging.
  - When to use: **constructor callbacks** (`AgentExecutor(callbacks=[h], tags=[...])`) for logging or monitoring across a whole instance. **Request callbacks** (`.invoke(..., {"callbacks": [h]})`) for per-request needs such as streaming to a websocket. **`verbose=True`** for local debugging, which is the same as a console callback on the object and its children but produces a lot of logs.
  - Principle(s): Evaluate Quality.

## Key Concepts
- **Agent**: an entity that acts, perceives and decides within an environment to reach predefined objectives. It loops `get_action → run → observe` until it returns `AgentFinish`.
- **Action space**: the set of actions available at any moment. Adding tools enlarges it.
- **Tool**: a predefined function that lets the agent take a specific action. LangChain offers custom tools, prebuilt tools and AgentToolkits.
- **Stop sequence**: e.g. `stop: ["tool_result:"]`, which halts generation before the model invents a tool output.
- **agent_scratchpad**: a `MessagesPlaceholder` where the agent writes and reads its intermediate steps.
- **Long-term memory (LTM)**: the model's "library", built from vector databases, self-reflection (stored insights about users) and custom retrievers that weight relevance, recency and utility.
- **Short-term memory (STM)**: a temporary workspace for conversational history and avoiding repetition, so follow-ups ("What about clothing?") work.
- **StructuredTool / args_schema**: `StructuredTool.from_function` creates multi-argument tools. A Pydantic `args_schema` validates arguments (e.g. `file_type: Literal["pdf","txt"]`) before the tool runs.
- **get_openai_callback**: a context manager that tracks `successful_requests`, `total_cost`, `total_tokens`, `prompt_tokens` and `completion_tokens`, including across async `agenerate` calls.

## Mental Models
- Think of an **LLM agent as a reasoning engine plus tools**. The LLM only produces text, and tools are how that text becomes database writes, HTTP calls, SMS or file I/O.
- Use **OpenAI functions** when the task is one definitive action, or parallel independent calls. Use **ReAct** when the task needs sequential tool use and reflection on earlier steps (e.g. "save the interview, then email it").
- Think of **tool names, descriptions and docstrings as prompts**. The LLM picks tools from them, so expressive names and descriptions directly improve tool selection (Give Direction).
- Think of **LTM as the library and STM as the desk**. Choose a memory type by how much history you need verbatim versus summarized, and how tight the token budget is.

## Anti-patterns
- **Generic, context-free prompts for complex tasks**: "Create a marketing plan" gets boilerplate that fits any product. Add context and a step-by-step request.
- **Too many tools**: the LLM gets confused about which to use at each step. Too few limits what it can solve.
- **Trusting regex parsing of LLM output**: LLMs don't always follow the format. Handle parse errors by asking an LLM to fix the response, or by re-requesting with the previous state.
- **No iteration or time caps**: agents can loop forever and run up API and compute costs. Set `max_iterations` / `max_execution_time`.
- **Unbounded ConversationBufferMemory in long chats**: it eventually hits context-length limits, carries irrelevant history and never summarizes. Use window, summary or token-buffer memory.
- **Relying on process-local memory for continuity**: in-memory state dies with the session. Use database-backed history for long-term memory.
- **Not monitoring tool usage**: how often each tool gets called shapes agent performance. Track it (Divide Labor and Evaluate Quality: one tool per responsibility, e.g. Twilio for messaging, Requests for HTTP).

## Code Examples
```python
# Minimal ReAct pieces: extract the last action/action_input and detect the final answer
def extract_last_action_and_input(text):
    action_pattern = re.compile(r"(?i)action\s*:\s*([^\n]+)", re.MULTILINE)
    action_input_pattern = re.compile(
        r"(?i)action\s*_*input\s*:\s*([^\n]+)", re.MULTILINE
    )
    actions = action_pattern.findall(text)
    action_inputs = action_input_pattern.findall(text)
    last_action = actions[-1] if actions else None
    last_action_input = action_inputs[-1] if action_inputs else None
    return {"action": last_action, "action_input": last_action_input}

def extract_final_answer(text):
    final_answer_pattern = re.compile(
        r"(?i)I've found the answer:\s*([^\n]+)", re.MULTILINE
    )
    final_answers = final_answer_pattern.findall(text)
    return final_answers[0] if final_answers else None

chat = ChatOpenAI(model_kwargs={"stop": ["tool_result:"],})
```
- **What it demonstrates**: the ReAct loop by hand. Parse the tool call, run `tools[name]["function"](input)`, feed back `tool_result`, and use a stop sequence to block hallucinated results.

```python
# Custom agent in LCEL (OpenAI tools)
@tool
def get_word_length(word: str) -> int:
    """Returns the length of a word."""
    return len(word)

tools = [get_word_length]
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are very powerful assistant, but don't know current events "
               "and aren't good at calculating word length."),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])
llm_with_tools = llm.bind_tools(tools=[convert_to_openai_tool(t) for t in tools])
agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
            x["intermediate_steps"]
        ),
    }
    | prompt
    | llm_with_tools
    | OpenAIToolsAgentOutputParser()
)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
```
- **What it demonstrates**: building an agent from parts. Bind tools as JSON schemas, format intermediate steps into the scratchpad, and parse tool calls. Add `MessagesPlaceholder("history")` plus `memory=ConversationBufferMemory(return_messages=True)` on the executor to give it memory.

```python
def save_interview(raw_interview_text: str):
    """Tool to save the interview. You must pass the entire interview and
    conversation in here. ... Include all of the messages with the user
    and the AI, here is a good response:
    AI: some text
    Human: some text
    ...
    ---"""
    with open("interview.txt", "w") as f:
        f.write(raw_interview_text)
    return f'''Interview saved! Content: {raw_interview_text}. File: interview.txt.
    You must tell the user that the interview is saved.'''

save_interview = StructuredTool.from_function(save_interview)
```
- **What it demonstrates**: prompt engineering inside tools (Give Direction and Specify Format). The docstring sets the argument format, and the return string tells the agent what to say next.

APIs are as of the 2024 edition (`langchain.agents`, `langchain.memory`, `hub.pull("hwchase17/react")`, `create_openai_functions_agent`). Several have since been deprecated in favor of LangGraph and newer memory APIs.

## Reference Tables

**Table 6-1. Agent types (LangChain)**

| Agent type | Use it for |
|---|---|
| OpenAI Functions | Function-calling fine-tuned models (gpt-3.5-turbo-0613, gpt-4-0613); outputs JSON calls. Deprecated in favor of OpenAI Tools |
| OpenAI Tools | Newer models; can invoke one or more functions; faster in some architectures |
| XML Agent | Models good at XML, e.g. Anthropic's Claude; regular LLMs; single-string-input tools |
| JSON Chat Agent | Chat models that are good at JSON output |
| Structured Chat | Multi-input tools; structured inputs and responses |
| ReAct | ReAct logic with search/document-store tools (e.g. Tavily) |
| Self-Ask with Search | Quick factual Q&A via an Intermediate Answer tool |

**Table 6-2. OpenAI functions vs ReAct**

| Feature | OpenAI functions | ReAct |
|---|---|---|
| Runtime decision making | ✓ | ✓ |
| Single tool execution | ✓ | ✓ |
| Ease of implementation | ✓ | x |
| Parallel function calling | ✓ | x |
| Iterative thought process | x | ✓ |
| Multi-intent handling | ✓ | ✓ |
| Sequential tool execution | x | ✓ |
| Customizable prompt | ✓ | ✓ |

**LangChain memory types**

| Memory | Behavior | Use when |
|---|---|---|
| ConversationBufferMemory | Stores every message, no limit | Short chats; simplest option |
| ConversationBufferWindowMemory | Keeps only the last K interactions | Recent context matters but the buffer must stay bounded |
| ConversationSummaryMemory | Summarizes the conversation on the fly | Long conversations where verbatim history costs too many tokens |
| ConversationSummaryBufferMemory | Recent messages verbatim plus a summary of older ones; flushes by `max_token_limit` | Hybrid: recent detail and a compressed past |
| ConversationTokenBufferMemory | Keeps a recent buffer, flushed by token length | A strict token budget is vital |

**Recommended tools**: Google search (timely context), file system tools (read/write/organize files), Requests (HTTP CRUD), Twilio (SMS/WhatsApp).

## Worked Example
**Hand-rolled ReAct for "Is Jason Derulo with a partner?"**
1. The system prompt holds the ReAct pattern (observe → observation → thought → `action:` / `action_input:`), "Do not guess or assume the tool results", `{tools}` = `{"search_on_google": {...}}` and `original_problem: {question}`. The model is a `ChatOpenAI` with a stop sequence on `"tool_result:"`.
2. Model output: an observation ("We don't have any information about Jason Derulo's relationship status"), a thought ("search recent news or interviews"), then `action: search_on_google` / `action_input: "Jason Derulo current relationship status"`.
3. `extract_last_action_and_input` parses this, and the code calls `tools["search_on_google"]["function"](...)`, which returns "Jason Derulo doesn't have a wife or partner."
4. Second prompt: "You are answering this query: … Based on the provided tool result: tool_result: {tool_result}. Either provide the next observation, action, action_input, or the final answer… you must return the following pattern: "I've found the answer: final_answer"".
5. Output: `I've found the answer: Jason Derulo doesn't have a wife or partner.`, which `extract_final_answer` captures.

LangChain's `AgentExecutor` automates the same flow, adding looping for multiple tool calls and handling for parse failures. With the "Count Characters in a text string" tool, its trace reads `Action → Action Input → Observation: 34 → Thought: I now know the final answer → Final Answer`.

## Key Takeaways
1. CoT plus concrete context ("step-by-step", budget, audience) turns generic answers into specific plans.
2. An agent is a loop of action, observation and decision, defined by inputs, a goal or reward, and an action space. For LLMs, add memory, planning strategy and retrieval.
3. ReAct handles sequential, multi-intent, reflective tasks. OpenAI functions are simpler, more stable, and support parallel calls for single definitive actions.
4. Tool names, descriptions, docstrings and return strings are prompts. Write them expressively, validate arguments with `args_schema`, and don't overload the agent with tools.
5. Memory reads before the run and writes after it. Choose the storage backend and the query strategy (buffer, window, summary, token buffer) to fit conversation length and token budget.
6. For harder problems, plan-and-execute (BabyAGI/AutoGPT) separates planning from execution, and Tree of Thoughts explores and backtracks over several reasoning paths (74% vs 4% on Game of 24).
7. Instrument agents with callbacks, tags, iteration caps and `get_openai_callback` token/cost tracking.

## Connects To
- **Ch 1**: Give Direction ("Let's think step by step", tool descriptions), Specify Format (tool docstrings), Divide Labor and Evaluate Quality (one tool per job, monitored).
- **Ch 3**: task decomposition (Least to Most) and structured outputs, which agents apply inside a loop.
- **Ch 4**: LangChain/LCEL, OpenAI function calling and output parsers, which are the base of agent chains and tool binding.
- **Ch 5**: vector databases provide long-term memory and retrieval for agents (BabyAGI uses Chroma/Weaviate).
- **Ch 10**: the blog-writing app reuses custom memory (`OnlyStoreAIMemory` subclassing ConversationSummaryBufferMemory), retrieval and chained components.
- **LangGraph / modern tool calling**: the 2024 `AgentExecutor` APIs have since been superseded by graph-based agent runtimes and native multi-tool calling.
