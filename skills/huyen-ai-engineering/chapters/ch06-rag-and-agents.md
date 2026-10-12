# Chapter 6: RAG and Agents

## Core Idea
Both RAG and agents are patterns for constructing the query-specific *context* a model needs (instructions are common to all queries; context is per-query). RAG retrieves relevant info from external memory; agents use tools to perceive and act on an environment — going beyond context construction to interacting with the world.

## Frameworks Introduced
- **RAG (Retrieval-Augmented Generation)**: retrieve-then-generate; a *retriever* fetches relevant info from external memory, a *generator* produces the answer from it.
  - When to use: knowledge exceeds context window; per-user/per-query data; reduce tokens, cost, hallucination. (Long context does *not* kill RAG — long context is used poorly and data always outgrows it.)
  - How: index (chunk → optionally embed → store) → query (retrieve top-k chunks) → join with prompt → generate.
- **Term-based (lexical/sparse) retrieval**: rank by keyword overlap via TF-IDF / BM25.
  - When to use: fast/cheap baseline; exact keywords (error codes, product names, IDs).
  - How: inverted index (term→docs); score = Σ IDF(t)×TF(t,D); BM25 normalizes TF by doc length.
- **Embedding-based (semantic/dense) retrieval**: rank by meaning via vector similarity.
  - When to use: natural-language queries, semantic match, room to finetune for gains.
  - How: embed chunks → vector DB → embed query → ANN search (k-NN exact only for tiny data).
- **Hybrid search**: combine term-based + embedding-based, in sequence (cheap fetch → expensive rerank) or parallel (ensemble fused with RRF).
- **Agent**: anything that perceives an environment and acts on it; defined by its *environment* + *set of actions (tools)*; AI is the *planner/brain*.
  - When to use: multi-step tasks needing tools/world-interaction; needs powerful model (compound errors, higher stakes).
  - How: plan → validate/reflect → execute (function calls) → reflect on outcomes → repeat.
- **ReAct**: interleave reasoning (Thought) and action (Act) then observe (Observation), looping until Finish.
- **Reflexion**: separate evaluator + self-reflection modules; agent proposes a new trajectory after each failure.

## Key Concepts
- **Indexing vs querying**: preprocessing data for fast lookup vs sending a query to fetch relevant data.
- **Chunking**: splitting docs into retrievable units (fixed-size, recursive, by structure; with overlap).
- **Reranking**: reordering/trimming retrieved candidates with a more precise (or time-weighted) scorer.
- **Vector database / ANN**: store embeddings; approximate nearest-neighbor search (LSH, HNSW, IVF, product quantization, Annoy) trading accuracy for speed.
- **Context precision / context recall**: % of retrieved docs that are relevant / % of relevant docs that were retrieved.
- **Query rewriting**: reformulate an ambiguous query (often via another model) to be self-contained.
- **Contextual retrieval**: augment each chunk with metadata, answerable questions, or AI-generated situating context before indexing.
- **Tool inventory**: the set of tools an agent can use — knowledge augmentation, capability extension, write actions (read-only vs write).
- **Function calling**: model API turns tools into callable functions; tool_choice = required / none / auto.
- **Planning vs execution**: roadmap of actions vs running them; decouple so only validated plans run.
- **Reflection / error correction**: self-critique to detect failures and regenerate plans.
- **Memory tiers**: internal knowledge (weights), short-term (context), long-term (external/retrieval).

## Mental Models
- **Context construction = feature engineering** for foundation models — give the model exactly the info it needs per input.
- **RAG is a special case of an agent** where the retriever is one tool the model can call.
- **Planning is search** — explore paths, predict each action's outcome, pick the most promising; backtracking is possible even for autoregressive models.
- **Compound error math**: 95% per-step accuracy → ~60% over 10 steps → ~0.6% over 100. More steps demand stronger models.
- **Indexing/querying trade-off**: a richer index (HNSW) = accurate + fast queries but slow/heavy to build; simple (LSH) = cheap build, slower/less accurate queries.

## Anti-patterns
- **Assuming long context replaces RAG**: models focus on wrong parts of long context; every token adds cost/latency.
- **Naive whole-document retrieval**: blows up context length — chunk instead.
- **Embedding everything blindly**: embeddings obscure exact keywords (error codes, product names) — keep term-based/hybrid.
- **Coupling planning with execution unsupervised**: a bad 1,000-step plan burns hours/API credits before you notice — validate plans first.
- **Too many tools**: more tools = harder to use well + bloated descriptions; do ablation, drop unused.
- **FIFO memory eviction blindly**: early messages often state the task's purpose — dropping them loses critical info.
- **Trusting reflection over reality**: agent declares success when it hasn't (e.g., placed 40 of 50 people and insists it's done).
- **Unrestricted write actions**: don't let an unreliable agent run bank transfers / delete prod — gate with human approval.

## Code Examples
Function-calling response (pseudocode, multi-API representative):
```python
response = ModelResponse(
    finish_reason='tool_calls',
    message=chat.Message(
        content=None, role='assistant',
        tool_calls=[ToolCall(
            function=Function(arguments='{"lbs":40}', name='lbs_to_kg'),
            type='function')]))
# then: lbs_to_kg(lbs=40) -> feed output back to generate final answer
```
RRF score: `Score(D) = Σ_i 1/(k + r_i(D))`, typical k=60.

## Reference Tables
| Dimension | Term-based | Embedding-based |
|---|---|---|
| Query speed | Much faster | Slower (embed + vector search) |
| Performance | Strong out-of-box, hard to improve; term ambiguity | Can win with finetuning; natural queries |
| Cost | Cheap | Embedding + storage + search costly |

Control flows: **sequential** (B after A), **parallel** (A & B together), **if** (B or C on output), **for loop** (repeat until condition).

## Worked Example
Agent loop for "Project Fruity Fedora sales for next 3 months" (Kitty Vogue, tools: response gen, SQL gen, SQL exec):
1. **Reason**: to project, need last 5 years of sales.
2. **SQL gen** → query for 5-yr sales. 3. **SQL exec** → results.
4. **Reflect**: numbers insufficient (missing values) → also need past marketing campaigns.
5. **SQL gen** → campaign query. 6. **SQL exec**.
7. **Reason**: data now sufficient → generate projection.
8. **Reflect**: task complete → finish.
This is ReAct in practice: interleaved Thought/Act/Observation until the agent judges the goal met.

## Key Takeaways
1. Context is per-query; RAG and agents both build it, but agents also act on the world.
2. RAG quality is bounded by retriever quality — evaluate retrieval, embeddings, AND end-to-end output.
3. Start with BM25/Elasticsearch as a strong cheap baseline; add embeddings/hybrid where semantics or finetuning pays off.
4. Chunk size is a tunable trade-off (diversity vs lost context vs compute) — no universal best; experiment.
5. Decouple planning from execution and add reflection (ReAct/Reflexion) — cheap to add, large quality gains, at latency/cost.
6. Tool selection drives agent success; choose via ablation and tool-call distribution analysis.
7. Memory (internal / short-term context / long-term retrieval) lets RAG and agents handle info beyond the context limit.

## Connects To
- **Ch 2**: text-to-SQL is semantic parsing; FM vs RL planners.
- **Ch 3**: embeddings, embedding evaluation (MTEB), vector search.
- **Ch 4**: lexical similarity (n-gram overlap), evaluating generative outputs.
- **Ch 5**: prompting/instructions (this chapter does context); defensive prompt engineering for tool/code-execution security; chain-of-thought, structured outputs.
- **Ch 7**: RAG/agents are prompt-based (no model change); next chapter modifies the model itself (finetuning).
