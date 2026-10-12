# Cheatsheet

## System scoping (do this first)
- Fixed known steps, LLM only picks among options → **agentic workflow** (StateGraph, Controller-Worker/Router). Steps unpredictable, must adapt at runtime → **agent** (ReAct loop). One-shot, no memory → **engine**. Multi-turn, no autonomy → **chatbot**.
- Escalate grounding cost only as needed: prompt engineering → RAG → fine-tuning; don't skip a cheaper rung until proven insufficient. RAG often beats fine-tuning for less-popular knowledge.
- High-stakes domain (finance, healthcare) → human-in-the-loop checkpoint before finalizing any agent action.

## Summarization: stuff vs MapReduce vs Refine
| Situation | Technique |
|---|---|
| 1 doc, fits window / many docs, all fit | Stuff |
| 1 doc, exceeds window | MapReduce |
| Many docs, don't fit, speed/cost matters most | MapReduce (parallel, cheaper, some cross-chunk loss) |
| Many docs, each doc's essence must survive | Refine (sequential, slower/costlier, higher fidelity) |

## RAG failure mode → fix
| Symptom | Fix |
|---|---|
| Wrong chunks retrieved (precision vs. context tradeoff) | ParentDocumentRetriever, summary embeddings, hypothetical-question embeddings, or chunk expansion |
| Vague/poorly phrased question | Rewrite-Retrieve-Read |
| Well-formed but compound question | Multi-query generation (merge via RRF) |
| Question too narrow, missing broader context | Step-back prompting |
| Question phrasing distant from doc phrasing | HyDE (embed fabricated answer, not question) |
| Independent sub-questions | Single-step decomposition (parallel) |
| Interdependent sub-questions | Multi-step decomposition (sequential, parameterized) |
| Transactional data, exact filter/join | Text-to-SQL |
| Fuzzy match on relational columns | Semantic SQL (pgvector distance) |
| Relationship/multi-hop reasoning | KG-RAG (text-to-Cypher/SPARQL) |
| Multiple content stores | Router (structured-output classifier) |
| Irrelevant chunks reach the LLM | Postprocessing: threshold, keyword filter, time-decay, RRF |

- Always keep the *original* question bound to synthesis (`RunnablePassthrough`) — only retrieval gets the transformed query.
- Every multi-vector technique adds storage + extra LLM/embedding calls — weigh against quality gain; test against your own data rather than picking one a priori.

## Agent architecture: ReAct vs Router vs Supervisor
| Situation | Pattern |
|---|---|
| Tool sequence predictable ahead of time | Agentic workflow, not agent |
| Dynamic tool choice, single domain | Single ReAct agent |
| Query maps to exactly one specialist ("one-way ticket") | Router (`Command(goto=...)`) |
| Query needs specialists to collaborate ("return ticket") | Supervisor (specialists wrapped as tools) |
- Give the Supervisor a stronger LLM than its specialists — it alone decomposes/coordinates.
- Pass structured JSON between agents, never free-form text. Router needs a default for ambiguous queries.

## Tool vs MCP server
- Local, one-off, in-house-only capability → local `@tool`.
- External/shareable service, or you'd otherwise hand-roll a wrapper → **MCP server** (moves integration upkeep to the provider). Check official/community portals before building your own.
- Validate a new server with MCP Inspector (connect → list tools → run tool) before agent wiring.
- Vague tool `description=`/system prompt → LLM falls back on pretrained knowledge instead of calling the tool.

## Memory & checkpointer
- Stateless single-turn → no checkpointer.
- Multi-turn must resolve cross-turn references → `ChatMessageHistory` or LangGraph checkpointer (`InMemorySaver` dev, `SqliteSaver`/`PostgresSaver` prod) keyed by `thread_id`.
- Need failure recovery, human-in-the-loop pause, or time-travel debug → checkpointer (same mechanism via `get_state_history`/`checkpoint_id`).
- `use_responses_api=True` requires `use_previous_response_id=True` or duplicate-submission errors occur.
- Cap refinement loops (book's example: 3 iterations) and chat history growth (sliding window/summarization).

## Guardrails: router-level vs agent-level
- Router-level (cheap classifier, pre-downstream-work) → rejects broadly off-topic queries fast.
- Agent-level (`pre_model_hook`) → narrower/stricter re-check; needed because a reused/directly-invoked agent loses router protection. Use both (belt-and-suspenders), not either/or.
- `guardrail_refusal` node should be a pure no-op → `END`; no logic there.

## Trade-off matrices
| Vector library (FAISS) | Vector database (Chroma, Pinecone) |
|---|---|
| No original text stored, immutable, no query-during-ingest | Stores text+metadata, full CRUD, concurrent ingest — needed for changing data |

| Router | Supervisor |
|---|---|
| Single dispatch, deterministic classification, any classifier LLM | Repeated `transfer_to_<agent>` calls, dynamic decomposition, stronger LLM |

| Proprietary (OpenAI/Anthropic/Gemini) | Open source (Llama/Mistral/Qwen/DeepSeek) |
|---|---|
| Data leaves org, zero infra, pay-per-token (cheap at low volume), turnkey SLA | Private/on-prem data, GPU/hosting cost, fine-tunable, lower TCO at high volume |

| Data shape | Use |
|---|---|
| Transactional, exact filter/join | Text-to-SQL |
| Relational + fuzzy meaning match | Semantic SQL |
| Unstructured text similarity | Vector store |
| Entity relationships, multi-hop | Graph DB |

## Thresholds & defaults
- RAG retrieval `k`: start ~4, tune 2–8 by content density/context budget.
- LangGraph refinement-loop cap: 3 iterations (book's example) — always cap cyclical edges.
- RRF: `score = 1/(rank + k)`, k typically 60.
- Multi-query generation: 3–5 alternative phrasings.
- Chunking: ch3 MapReduce `chunk_size=3000/overlap=100` (tokens); ch7 basic RAG `chunk_size=500/overlap=0` (chars); ch8 parent/child `parent=3000`/`child=500`.
- In-context learning: zero-shot → one-shot → two-shot → explicit steps/CoT — stop at first rung that works.
- Mix model sizes per workflow: nano/mini for routing/fast synthesis, full-size for deep reasoning/Supervisor coordination.

## Tells & smells
- LLM invents specifics absent from context → missing "say I don't know" instruction + negative example.
- Semantically-close-but-wrong or context-poor retrieval → try ParentDocumentRetriever / summary or hypothetical-question embeddings.
- Agent answers from pretraining instead of calling an available tool → underspecified tool description/system prompt.
- Follow-up with unresolved pronouns ("they"/"it") → no memory; add `ChatMessageHistory`/checkpointer.
- LLM-generated SQL throws on execution → strip markdown fences before running.
- Conditional branching getting awkward in a plain LCEL chain → move to a LangGraph `StateGraph`.
- One-way router can't satisfy a query needing two specialists to share results → move to Supervisor.
- Local quantized LLM matches hosted quality but is much slower (esp. CPU-only) → expected; use GPU-backed engine or vLLM for production.
