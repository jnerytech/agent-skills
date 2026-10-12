# Chapter 8: Advanced indexing

## Core Idea
Naive RAG (one embedding per chunk, one fixed chunk size) breaks on either detailed or broad queries; advanced indexing fixes this by storing *multiple* embeddings per document (child chunks, summaries, hypothetical questions) that all resolve back to a richer chunk for synthesis.

## Frameworks Introduced
- **ParentDocumentRetriever**: index small child chunks for precise vector matching, but return their large parent chunk for LLM synthesis.
  - When to use: queries range from narrow/detailed to broad/contextual and you want a single retriever to serve both.
  - How: split with a coarse `parent_splitter` and a fine `child_splitter`; store parent chunks in an `InMemoryStore` (docstore) and child chunk embeddings in a vector store (e.g. Chroma); call `add_documents()` — child embeddings are generated automatically and linked to their parent via metadata.
- **MultiVectorRetriever (child chunks)**: manual equivalent of ParentDocumentRetriever with explicit control over ID linking.
  - When to use: you need custom logic for building the "retrieval vector" (not just smaller chunks of the same text) — this is the base pattern reused for summaries and hypothetical questions.
  - How: split into coarse chunks, assign each a UUID (`doc_id`), split each coarse chunk into granular child chunks tagged with that `doc_id` in metadata, `vectorstore.add_documents(child_chunks)`, and `docstore.mset(zip(ids, coarse_chunks))`.
- **Embedding document summaries**: embed an LLM-generated summary of each coarse chunk instead of (or alongside) the raw chunk, since raw large chunks dilute embedding relevance with filler content.
  - When to use: coarse chunks contain a lot of low-signal text (e.g., travel guide prose) that weakens the embedding's semantic focus.
  - How: run each coarse chunk through a summarization chain (`{"document": ...} | prompt | llm | StrOutputParser()`), store the summary as the vector-store document (tagged with `doc_id`), store the original coarse chunk in the docstore.
- **Hypothetical Document Embeddings for indexing (embedding hypothetical questions)**: generate several questions each chunk could answer, embed those questions, and link them back to the chunk.
  - When to use: user queries are phrased very differently from the document's own wording, so direct chunk/question semantic similarity is weak.
  - How: use `.with_structured_output(HypotheticalQuestions)` (a Pydantic model with a `questions: List[str]` field) to force the LLM to return a clean list; create one `Document` per question tagged with the source chunk's `doc_id`; store questions in the vector store and coarse chunks in the docstore.
- **Granular chunk expansion (sentence/context window expansion)**: index small granular chunks for precision, but at retrieval time return an "expanded" chunk containing the previous, current, and next chunk concatenated.
  - When to use: you want maximum retrieval precision from small chunks without sacrificing the surrounding context needed for a complete answer.
  - How: split into granular chunks, for each chunk build `expanded_chunk_text` = previous + current + next chunk content, store expanded text in the docstore keyed by a new UUID, tag the granular chunk's metadata with that `doc_id`, ingest granular chunks into the vector store via `MultiVectorRetriever`.
- **Semi-structured / multimodal indexing via MultiVectorRetriever**: treat tables (and, for multimodal RAG, images) like text chunks — summarize them, embed the summary, store the raw table/image in the docstore, and return the raw artifact on a match.

## Key Concepts
- **Synthesis chunk**: the (usually larger) chunk actually fed to the LLM to generate the answer.
- **Retrieval chunk**: the smaller/derived representation (child chunk, summary, or hypothetical question) whose embedding is used only for search precision.
- **Two-layer chunk structure**: the general pattern behind all multi-vector strategies — a retrieval layer for matching, a synthesis layer for context.
- **Document hierarchy splitting**: splitting along the document's natural structure (headers, sections) via `HTMLHeaderTextSplitter`/`MarkdownHeaderTextSplitter`; preserves semantic meaning but produces uneven chunk sizes.
- **Absolute-size splitting**: splitting by fixed character/token/sentence count via `CharacterTextSplitter`/`RecursiveCharacterTextSplitter`/`TokenTextSplitter`; consistent sizes but risks mid-sentence cuts.
- **InMemoryStore / InMemoryByteStore**: key-value stores used as the docstore side of a multi-vector retriever; the former holds serializable Python objects, the latter raw bytes.
- **doc_id metadata key**: the linking field written into each retrieval-layer Document's metadata so `MultiVectorRetriever` can map a vector hit back to its parent/synthesis document in the docstore.
- **Chunk expansion (context window retrieval)**: fetching N chunks before/after a matched chunk at retrieval time to restore context lost by small chunk size.

## Mental Models
- **Precision vs. context tradeoff**: small chunks win on precision (detailed queries) but lose context; large chunks win on context (broad queries) but lose focus. Every technique in this chapter is a way to get both without picking one chunk size.
- **Two layers, one retriever**: rather than tuning a single chunk size, decouple "what gets embedded" (retrieval layer) from "what gets returned" (synthesis layer) — `MultiVectorRetriever` is the general mechanism, and ParentDocumentRetriever/summary embeddings/hypothetical questions are just different choices for what goes in the retrieval layer.
- **Test, don't assume**: the author explicitly says the various multi-vector techniques "usually yield similar performance improvements" and to test each against your own data/content structure rather than picking one a priori.
- **Semi-structured and multimodal content is just another retrieval layer**: a table summary or an image summary is embedded exactly like a hypothetical question or chunk summary — the raw table/image lives in the docstore and is returned on a match.

## Anti-patterns
- **Using a single fixed chunk size for all query types**: small chunks fail broad questions, large chunks fail detailed ones — pick chunk size (and technique) based on expected query type, not convenience.
- **Splitting mid-sentence with fixed-size splitters**: `CharacterTextSplitter`/`TokenTextSplitter` can cut sentences, reducing semantic value of the resulting embeddings.
- **Embedding raw large chunks directly**: filler/irrelevant content in a coarse chunk dilutes its embedding, making retrieval less focused — summarize or use child chunks instead.
- **Searching the retrieval-layer collection directly (child chunks / summaries / hypothetical questions alone)**: as shown repeatedly in the chapter's "compare with direct semantic search" sections, this returns concise but context-poor results — you must go through the `MultiVectorRetriever`/`ParentDocumentRetriever` to get the linked synthesis chunk.
- **Ignoring storage/compute overhead**: parent-child and multi-vector retrieval store both layers and require extra LLM calls (for summaries/hypothetical questions) or extra embedding calls (for `SemanticChunker`) — benchmark quality gain against this cost before deploying.

## Code Examples
```python
parent_splitter = RecursiveCharacterTextSplitter(
    chunk_size=3000)
child_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500)
child_chunks_collection = Chroma(
    collection_name="uk_child_chunks",
    embedding_function=OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY),
)
child_chunks_collection.reset_collection()
doc_store = InMemoryStore()
parent_doc_retriever = ParentDocumentRetriever(
    vectorstore=child_chunks_collection,
    docstore=doc_store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter
)
```
- **What it demonstrates**: wiring `ParentDocumentRetriever` with separate parent/child splitters, a vector store for child embeddings, and an `InMemoryStore` for parent documents.

```python
class HypotheticalQuestions(BaseModel):
    """A list of hypotetical questions for given text."""
    questions: List[str] = Field(...,
        description="List of hypothetical questions for given text")

llm_with_structured_output = ChatOpenAI(
    model="gpt-5-nano", openai_api_key=OPENAI_API_KEY).with_structured_output(
    HypotheticalQuestions
)
```
- **What it demonstrates**: forcing structured LLM output (a Pydantic schema) so generated hypothetical questions come back as a clean list ready to embed.

```python
expanded_chunk_text = ""
if previous_chunk_num:
    expanded_chunk_text += granular_chunks[previous_chunk_num].page_content
    expanded_chunk_text += "\n"
expanded_chunk_text += granular_chunks[this_chunk_num].page_content
expanded_chunk_text += "\n"
if next_chunk_num:
    expanded_chunk_text += granular_chunks[next_chunk_num].page_content
    expanded_chunk_text += "\n"
expanded_chunk_id = str(uuid.uuid4())
expanded_chunk_doc = Document(page_content=expanded_chunk_text)
```
- **What it demonstrates**: building the expanded (previous + current + next) chunk that gets stored in the docstore and returned instead of the bare granular chunk.

## Reference Tables
**Table 8.2 — Splitting strategies**

| Splitting strategy | Pros | Cons | LangChain classes |
|---|---|---|---|
| Document hierarchy | More accurate semantic meaning | Chunk size varies significantly | `HTMLHeaderTextSplitter`, `MarkdownHeaderTextSplitter` |
| By size: number of tokens | Consistent chunk size | Incomplete sentences at boundaries | `TokenTextSplitter` |
| By size: number of characters | Consistent chunk size | Incomplete sentences may reduce semantic value | `CharacterTextSplitter` |
| By sentence, paragraph, or word | Retains semantic meaning in most cases | Small chunks may lack enough context | `RecursiveCharacterTextSplitter` |

**Table 8.1 — Naive RAG issues and solutions (Q&A stage)**

| Issue | Solution |
|---|---|
| Retrieval returning the wrong content chunks | Advanced document indexing techniques |
| Poor question formulation | Question transformations |
| Ineffective question for retrieval | Question transformations |
| Limited data relevance in content store | Routing to multiple content stores |
| Limited querying capabilities for structured data | Content store query generation |
| Irrelevant retrieved results fed to LLM | Retrieval postprocessing |

## Worked Example
Goal: retrieve rich context for the query "Cornwall Ranger" from UK travel-guide pages, using `ParentDocumentRetriever`.

1. Set up splitters and stores:
   ```python
   parent_splitter = RecursiveCharacterTextSplitter(chunk_size=3000)
   child_splitter = RecursiveCharacterTextSplitter(chunk_size=500)
   child_chunks_collection = Chroma(collection_name="uk_child_chunks",
       embedding_function=OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY))
   child_chunks_collection.reset_collection()
   doc_store = InMemoryStore()
   parent_doc_retriever = ParentDocumentRetriever(
       vectorstore=child_chunks_collection, docstore=doc_store,
       child_splitter=child_splitter, parent_splitter=parent_splitter)
   ```
2. Ingest content per destination URL — load HTML with `AsyncHtmlLoader`, transform to text with `Html2TextTransformer`, then `parent_doc_retriever.add_documents(text_docs, ids=None)`. Internally this splits into 3000-char parent chunks (stored in `doc_store`) and 500-char child chunks (embedded into `child_chunks_collection`, each tagged with its parent's id).
3. Verify ingestion: `list(doc_store.yield_keys())` shows the stored parent chunk IDs.
4. Query: `retrieved_docs = parent_doc_retriever.invoke("Cornwall Ranger")`. The retriever matches the query against child-chunk embeddings, then returns `retrieved_docs[0]`, the full parent chunk — several paragraphs covering trains, roads, buses, spanning far more than just the ticket mention.
5. Contrast: searching `child_chunks_collection.similarity_search("Cornwall Ranger")` directly returns only the short child chunk that literally mentions "Cornwall Ranger" (ticket price, no surrounding travel context).
6. Conclusion: the parent-child structure gives precise matching (via child embeddings) *and* rich synthesis context (via the returned parent chunk) — exactly the two-layer pattern this chapter builds on for summaries and hypothetical questions.

## Key Takeaways
1. Decouple what you embed (small, focused retrieval chunks) from what you feed the LLM (large, context-rich synthesis chunks) using `MultiVectorRetriever`-family retrievers.
2. Match splitting strategy to content: use document-hierarchy splitters (`HTMLHeaderTextSplitter`, `MarkdownHeaderTextSplitter`) for structured content, absolute-size splitters (`RecursiveCharacterTextSplitter`) when structure is weak or absent.
3. `ParentDocumentRetriever` is the turnkey option for child-chunk embedding; `MultiVectorRetriever` is the general-purpose building block for summaries, hypothetical questions, and chunk expansion.
4. Summary embeddings reduce noise from filler content in large chunks; hypothetical-question embeddings close the gap between how users phrase queries and how documents phrase answers.
5. Granular chunk expansion (previous + current + next) gives small chunks the surrounding context they lack, without embedding large chunks directly.
6. Tables and images can be indexed the same way as text: summarize, embed the summary, store the raw artifact in a docstore, and return it via `MultiVectorRetriever` on a match — this is the same pattern used for multimodal RAG.
7. Every multi-vector technique adds storage and compute cost (extra LLM/embedding calls); benchmark retrieval-quality gains against that overhead before adopting one in production.

## Connects To
- **Ch 7**: RAG fundamentals — the naive single-embedding architecture this chapter improves on.
- **Ch 9**: Question transformations — the next stage in the Q&A pipeline (table 8.1), addressing poor question formulation and ineffective retrieval queries.
- **Vector store metadata filtering**: `doc_id` linking pattern depends on metadata support (e.g., ChromaDB `where` filters), which varies by vector store.
- **SemanticChunker**: an alternative to fixed-size/hierarchy splitting that detects natural breakpoints via embedding similarity (`langchain_experimental.text_splitter`).
