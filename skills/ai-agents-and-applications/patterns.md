# Patterns

## Prompt Templating & Few-Shot Composition
**When to use**: A prompt reused across varying inputs, or a task needing examples to fix a pattern.
**How**: `PromptTemplate.from_template("{var}")` for parametrized prompts; `FewShotPromptTemplate(examples=, example_prompt=, suffix=)` to separate examples from the prompt shell. Escalate zero-shot → few-shot → explicit steps only as needed.
**Trade-offs**: Each added example costs tokens/latency; don't keep scaffolding a newer model no longer needs.

## Chain-of-Thought Prompting
**When to use**: Deterministic multi-step reasoning where the model gets components right but combines them wrong.
**How**: Few-shot examples that show explicit reasoning steps before the answer, not just input→output.
**Trade-offs**: More tokens than plain few-shot; Tree/Thread of Thought are costlier variants for backtracking/noisy-context tasks.

## MapReduce Summarization
**When to use**: A document exceeding the context window, or many documents, when speed/cost beats per-doc fidelity.
**How**: Split into chunks (`TokenTextSplitter`), map a summary prompt over each in parallel (`RunnableParallel`/`.map()`), reduce by joining and re-summarizing.
**Trade-offs**: Faster/cheaper than Refine, but parallel chunk summaries can lose cross-chunk context.

## Refine Summarization
**When to use**: Multiple documents where each part's essence must survive into the final summary.
**How**: Maintain a running summary; feed each document plus the running summary into a refine prompt sequentially until all are processed.
**Trade-offs**: Higher latency/token cost than MapReduce — sequential, re-reads the growing summary every step.

## LCEL Chain Composition (fan-out/fan-in)
**When to use**: A multi-step LLM pipeline with independent sub-steps (N queries → N searches → N summaries).
**How**: Build small testable mini-chains (`prompt | llm | parser`), wire with `|`; `RunnableLambda` for Python glue, `RunnableParallel` for parallel branches, `.map()` to fan over a list, `RunnablePassthrough` to carry input forward.
**Trade-offs**: Parallelism cuts latency but multiplies concurrent API cost; every I/O boundary needs defensive parsing.

## LangGraph StateGraph Agent Pattern
**When to use**: Workflows needing conditional branching, cyclical retries, or explicit state beyond a linear chain.
**How**: Define state as `TypedDict`; nodes as `(state) -> partial_update` functions; wire with `add_edge`/`add_conditional_edges`; set entry point, route to `END`, `compile()`.
**Trade-offs**: More setup than a chain; uncapped cyclical edges risk infinite loops.

## RAG Design Pattern
**When to use**: Q&A over a knowledge base too large/scattered to paste into one prompt.
**How**: Ingest — chunk, embed, store in a vector store. Retrieve — embed the question, similarity-search top-k, inject as context, instruct the LLM to answer only from it or say "I don't know."
**Trade-offs**: Retrieval quality caps answer quality; naive one-embedding-per-chunk fails on both narrow and broad queries.

## Conversational Memory (ChatMessageHistory)
**When to use**: Follow-up questions need to resolve references against prior turns.
**How**: `ChatPromptTemplate.from_messages` with a `{chat_history_messages}` placeholder; maintain `ChatMessageHistory`, `add_user_message()`/`add_ai_message()` each turn; feed `.messages` in via `RunnableLambda`.
**Trade-offs**: Unbounded growth blows the token budget — cap with a window or summarization; persist only human/ai turns.

## ParentDocumentRetriever
**When to use**: Queries range narrow-to-broad and one retriever must serve both.
**How**: Split with a coarse `parent_splitter` and fine `child_splitter`; embed child chunks, store parents in `InMemoryStore`; `add_documents()` links them via metadata; retrieval returns the parent.
**Trade-offs**: Doubles storage; querying the child collection directly returns context-poor snippets.

## MultiVectorRetriever (summary / hypothetical-question embedding)
**When to use**: Coarse chunks are noisy (summary embedding) or query phrasing diverges from document phrasing (hypothetical questions).
**How**: Assign each chunk a `doc_id`; embed a generated summary or LLM hypothetical questions (`.with_structured_output`) tagged with it; store the coarse chunk in the docstore; retriever maps hits back to it.
**Trade-offs**: Extra LLM calls at ingestion; test against your data — techniques yield similar gains in practice.

## Granular Chunk Expansion
**When to use**: Need max retrieval precision from small chunks without losing surrounding context.
**How**: Index small chunks for matching; build an expanded doc (previous+current+next) keyed by a new `doc_id` in the docstore, retrieve via `MultiVectorRetriever`.
**Trade-offs**: Extra docstore storage; expansion window size is a manual tuning knob.

## Rewrite-Retrieve-Read
**When to use**: The question is poorly worded or verbose relative to the store's phrasing.
**How**: LLM rewrites the question into a search-optimized query for retrieval only; keep the original bound via `RunnablePassthrough()` for synthesis.
**Trade-offs**: One extra LLM call; doesn't help compound/broad questions — that's multi-query's job.

## Multi-Query Generation
**When to use**: A well-formed question bundles several independent implicit sub-questions.
**How**: LLM generates 3-5 alternative phrasings (`LineListOutputParser`, or `MultiQueryRetriever.from_llm`); retrieve per variant; merge/dedupe, optionally via RRF (`1/(rank+k)`).
**Trade-offs**: N retrieval calls instead of 1; only helps if variants are genuinely independent.

## Step-Back Prompting
**When to use**: The question is detailed and fine-grained chunks miss broader needed context.
**How**: LLM generates a broader "step-back question"; retrieve abstract context from it, combine with the original detailed question in one synthesis prompt.
**Trade-offs**: Two retrieval calls instead of one; abstraction quality needs a capable model.

## HyDE (Hypothetical Document Embeddings)
**When to use**: User phrasing is conceptually distant from document phrasing.
**How**: LLM writes a short hypothetical answer; embed and retrieve using that text as the query; keep the real question for synthesis.
**Trade-offs**: The fabrication must never leak into the answer path — retrieval aid only.

## Query Decomposition (single-step / multi-step)
**When to use**: Single-step for independent sub-questions (parallel); multi-step when each sub-question depends on the prior answer (sequential).
**How**: Prompt for a JSON list of `{Question, Parameter}` steps; execute each, substituting the prior answer into the next parameter; synthesize from accumulated answers.
**Trade-offs**: Multi-step latency scales with step count; no dedicated LangChain class — hand-rolled orchestration.

## Self-Querying / Metadata Enrichment
**When to use**: Chunks carry metadata and questions implicitly narrow scope by it.
**How**: `SelfQueryRetriever.from_llm(llm, vectorstore, question, metadata_field_info)`, or a custom structured call separating `content_search` from filter fields, translated to the store's native filter syntax.
**Trade-offs**: Requires metadata at ingestion; accuracy depends on clear field descriptions.

## Text-to-SQL & Semantic SQL
**When to use**: Structured/transactional data needing exact filters/joins (text-to-SQL), or fuzzy meaning-based matching in a relational schema (semantic SQL, pgvector).
**How**: `create_sql_query_chain(llm, db)` fed schema + sample rows, cleaned of markdown fences, executed via `QuerySQLDataBaseTool`; semantic SQL orders `ORDER BY column <-> embedded_query`.
**Trade-offs**: Hallucinated table/column names without schema+sample grounding; raw LLM SQL must always be cleaned before execution.

## Graph Database Query Generation (KG-RAG)
**When to use**: Relationship-heavy data needing multi-hop reasoning or explainable inference.
**How**: Few-shot prompt with graph schema + example Cypher/SPARQL; generate with a strong LLM, execute against Neo4j/Neptune, synthesize the answer with a cheaper LLM.
**Trade-offs**: More setup than vector search; trades similarity-search simplicity for explainable traversal.

## Chain Routing & Retrieval Postprocessing
**When to use**: An app spans multiple content stores, or retrieved chunks need trimming before synthesis.
**How**: Route — `llm.with_structured_output(RouteQuery)` classifies into a `Literal` datasource, dispatch to the matching retriever. Postprocess — similarity threshold, keyword filters, time decay, or RRF before synthesis.
**Trade-offs**: Router adds a classification call per query; skipping postprocessing lets low-relevance chunks dilute answers.

## ReAct Tool-Calling Agent
**When to use**: Tool sequence/choice can't be predetermined and must depend on evolving context.
**How**: LLM node examines state; if it emits `tool_calls`, route to a tools node (`ToolNode`), append results as `ToolMessage`s, loop back until plain content is returned (`tools_condition` → `END`).
**Trade-offs**: Vague tool descriptions/system prompts make the LLM answer from pretraining instead of calling tools; needs a step cap.

## ReAct Prebuilt Agent
**When to use**: The manual ReAct graph is understood and correct; ready for production.
**How**: `create_react_agent(model=llm, tools=TOOLS, state_schema=AgentState, prompt=system_prompt)` replaces manual `bind_tools`, nodes, and wiring; add `RemainingSteps` to bound rounds.
**Trade-offs**: Less code-level visibility — compensate with LangSmith tracing; build from scratch first.

## Router Agent Pattern (multi-agent)
**When to use**: A query cleanly belongs to exactly one specialist domain ("one-way ticket").
**How**: LLM classifies via structured output (`Enum` + Pydantic) into an agent type; router node returns `Command(update=state, goto=agent_name)`.
**Trade-offs**: Can't handle multi-part requests needing shared intermediate results — needs a Supervisor; add a default/confidence threshold.

## Supervisor Agent Pattern
**When to use**: Multi-part requests requiring several specialists to collaborate ("return ticket").
**How**: Give each `create_react_agent` a unique `name`; `create_supervisor(agents=[...], model=...)` wraps each as a callable tool (`transfer_to_<agent>`); use a stronger model for the supervisor.
**Trade-offs**: More LLM round-trips than a router; needs clear per-specialist capability descriptions; pass JSON, not free text, between agents.

## MCP Server/Client Integration Pattern
**When to use**: An agent needs external context (APIs, databases, services) without a bespoke wrapper per source.
**How**: Provider exposes a service as an MCP server (FastMCP 2, `@mcp.tool`, Streamable HTTP or STDIO); agent's `MultiServerMCPClient({server: {"url":..., "transport":...}})` calls `get_tools()` and merges with local tools; validate with MCP Inspector first.
**Trade-offs**: Adds network latency and an async requirement throughout the call chain; check public MCP portals before building a custom server.

## LangGraph Checkpointer for Memory
**When to use**: Multi-turn agents needing reference resolution across turns, or failure recovery / human-in-the-loop pausing.
**How**: Instantiate a saver (`InMemorySaver` dev, `SqliteSaver`/`PostgresSaver` prod), pass to `graph.compile(checkpointer=...)`, pass `thread_id` on every `invoke()`. Rewind via `get_state_history()` + `checkpoint_id`, resume with `invoke(None, config=...)`.
**Trade-offs**: `InMemorySaver` doesn't survive restarts; OpenAI Responses API needs `use_previous_response_id=True` alongside `use_responses_api=True` or duplicate-submission errors occur.

## Layered Guardrails (router-level + agent-level)
**When to use**: An agent must stay in domain/geographic scope, avoid cost abuse, or avoid unsafe output.
**How**: Router-level — classifier checks the raw query, routes off-topic ones to a no-op refusal node → `END`. Agent-level — a `pre_model_hook` re-classifies with a stricter policy, prepending a refusal `SystemMessage` to `llm_input_messages` on failure.
**Trade-offs**: Router-only checks fail to protect an agent reused/invoked directly; duplicate validation costs an extra call per turn but is the safer default.
