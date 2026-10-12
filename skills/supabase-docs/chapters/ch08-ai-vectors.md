# Chapter 8: AI & Vector Embeddings

## Core Idea
"The best vector database is the database you already have." Supabase turns Postgres into a vector store via **pgvector**, so embeddings live next to your relational data — sharing the same SQL, RLS, indexes, migrations, and joins. You generate embeddings with a model (OpenAI, Hugging Face/Transformers.js, `gte-small`), store them in a `vector(N)` column, then rank rows by distance to a query embedding. Because it's just Postgres, you also get keyword search (`tsvector`), hybrid fusion, fine-grained access control (RLS), and async embedding pipelines — without bolting on a separate Pinecone-style service.

## Frameworks Introduced
- **pgvector**: Postgres extension adding the `vector` type and distance operators (`<->`, `<#>`, `<=>`) plus HNSW/IVFFlat ANN indexes.
- **Semantic search**: search by meaning using embedding similarity instead of exact keywords; embeds both stored content and the query, then ranks by cosine/inner-product distance.
- **Hybrid search (RRF)**: fuse full-text (`tsvector` + GIN) and semantic (`pgvector` + HNSW) result lists via Reciprocal Ranked Fusion, scoring each row `1/(k+rank)` per list.
- **RAG with permissions**: chunk documents into `document_sections`, embed each chunk, and let RLS policies transparently filter similarity results to rows the user may see.
- **Automatic embeddings**: trigger → `pgmq` queue → `pg_cron` → `pg_net` → Edge Function pipeline that generates/refreshes embeddings asynchronously on insert/update.
- **vecs (Python client)**: manages *unstructured* collections, auto-creating SQL tables with a `jsonb` metadata column.

## Key Concepts
- **Embedding**: a list of floats capturing "relatedness" of text/image/video; similar concepts sit close together in vector space (used for search, recommendations, classification, clustering).
- **Dimensions**: the `vector(N)` size must match the model's output (`gte-small`=384, OpenAI `text-embedding-3-large`=up to 3072, shortenable). Fewer dimensions generally perform best.
- **Same-model rule**: only compare embeddings produced by the *same* model — cross-model comparisons are meaningless.
- **Similarity vs distance**: `similarity = 1 - cosine_distance`. Cosine (`<=>`) is the safe default; inner product (`<#>`) is fastest when vectors are normalized (e.g. OpenAI).
- **ANN tradeoff**: indexes give approximate nearest-neighbor results — trading a little recall for large speedups vs sequential scan.
- **PostgREST limitation**: `supabase-js` cannot call distance operators directly; wrap similarity queries in a SQL function and invoke via `rpc()`.
- **Structured vs unstructured metadata**: dedicated columns (SQL filtering, constraints, throughput) vs a flexible `jsonb` column (rapid prototyping, user-defined fields).

## Mental Models
- **Embeddings as coordinates**: meaning becomes geometry; "find similar" becomes "find nearest point."
- **The index is a shortcut, not the truth**: HNSW/IVFFlat skip comparisons, so results are approximate — tune for recall vs latency.
- **Filter inside the function, not after**: pushing a `where` into the SQL function lets the planner combine it with the vector predicate; `.eq()` chained after `rpc()` filters *post-ranking* and can starve `match_count`.

## Anti-patterns
- Chaining `.eq()`/metadata filters onto `rpc()` results instead of parameterizing the filter into the SQL function (kills index use, returns too few rows).
- Ordering by the computed `similarity` alias instead of the raw distance expression — the index gets ignored, causing slow scans.
- Building an **IVFFlat** index on an empty/tiny table (clusters need representative data); HNSW is safe immediately.
- Comparing embeddings from different models, or storing the wrong dimension count.
- Connecting the MCP server to production data, or running it without read-only/project scoping.

## Code Examples
```sql
-- Enable extension, create vector column, index, and similarity query
create extension vector with schema extensions;

create table documents (
  id bigint primary key generated always as identity,
  content text,
  embedding extensions.vector(512)
);

-- Index for cosine distance (HNSW is the recommended default)
create index on documents using hnsw (embedding vector_cosine_ops);

-- Similarity search wrapped in a function (callable via rpc)
create or replace function match_documents (
  query_embedding extensions.vector(512),
  match_threshold float,
  match_count int
)
returns setof documents
language sql
as $$
  select *
  from documents
  where documents.embedding <=> query_embedding < 1 - match_threshold
  order by documents.embedding <=> query_embedding asc
  limit least(match_count, 200);
$$;
```
- **What it demonstrates**: the full vector lifecycle — enable pgvector, declare a fixed-dimension column, build an HNSW cosine index, and expose ANN search through a SQL function whose `order by` uses the raw distance operator (so the index is honored) and whose `match_threshold`/`match_count` bound result quality and size.

## Reference Tables

**HNSW vs IVFFlat**

| Aspect | HNSW | IVFFlat |
| --- | --- | --- |
| Algorithm | Hierarchical proximity graph (skip-list layers + navigable small world) | Inverted file: clusters vectors into `lists`, probes nearby cells |
| Build timing | Safe immediately after table creation | Build only after table has representative data |
| Changing data | Robust; index stays optimal as rows added | Rebuild when data distribution shifts |
| Tuning knob | `hnsw.iterative_scan` (`off`/`strict_order`/`relaxed_order`), `m`, `ef_construction` | `lists` (build), `ivfflat.probes` (query) |
| Best for | High accuracy, read-heavy, low-latency, recall > memory | Large sets (100k–10M), lower memory, fast approximate |
| Recommendation | **Default choice** | Special cases only |

**Distance operators** (each pairs with an operator class for indexing)

| Operator | Meaning | Operator class | Use when |
| --- | --- | --- | --- |
| `<->` | Euclidean (L2) distance | `vector_l2_ops` | geometric/spatial similarity |
| `<#>` | Negative inner product | `vector_ip_ops` | normalized vectors (fastest, e.g. OpenAI) |
| `<=>` | Cosine distance | `vector_cosine_ops` | safe default; magnitude-independent |

Index dimension limits (pgvector ≥ 0.7.0): `vector` ≤ 2,000; `halfvec` ≤ 4,000; `bit` ≤ 64,000. For >2,000 dims, index a cast: `using hnsw ((embedding::halfvec(3072)) halfvec_cosine_ops)`.

## Worked Example
Store embeddings and run end-to-end semantic search from an Edge Function:

```ts
// 1. Generate a one-time embedding for the user's query
const openai = new OpenAI({ apiKey: openaiApiKey })
const { data } = await openai.embeddings.create({
  model: 'text-embedding-3-large',
  input: query,
  dimensions: 512,
})
const [{ embedding }] = data

// 2. Search via the SQL function (RLS still applies if using user JWT)
const { data: documents } = await supabase.rpc('match_documents', {
  query_embedding: embedding,
  match_threshold: 0.78,
  match_count: 10,
})
```

For RAG with access control, chunk into `document_sections` with an `owner_id` on the parent `documents`, then add an RLS policy — every similarity `select` then implicitly filters to the caller's rows:

```sql
create policy "Users can query their own document sections"
on document_sections for select to authenticated using (
  document_id in (select id from documents where owner_id = (select auth.uid()))
);
```

## Key Takeaways
- pgvector makes Postgres a first-class vector DB: embeddings + relational data + RLS + SQL in one place.
- HNSW is the default index; IVFFlat only for special large/low-memory cases and only after data exists.
- Pick the distance operator to match your model (cosine default, inner product for normalized) and index with the matching operator class.
- Always wrap similarity in a SQL function called via `rpc()`; order by the raw distance and push filters *into* the function.
- Combine keyword + semantic via RRF for the best recall; automate embedding upkeep with triggers + pgmq + pg_cron + Edge Functions.
- The Supabase MCP server lets AI tools query your project — use read-only, project-scoped, non-production settings to limit prompt-injection blast radius.

## Connects To
- Ch: Edge Functions (embedding generation, hybrid_search invocation, automatic-embeddings pipeline)
- Ch: Auth & RLS (RAG-with-permissions access control)
- Ch: Database extensions (pgmq, pg_net, pg_cron, hstore, full-text GIN/`tsvector`)
- Ch: AI editor tools / MCP (`ai-prompts` for IDE rules, MCP server tool groups and security)
