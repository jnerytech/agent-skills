# Chapter 3: Summarizing text using LangChain

## Core Idea
When a document or document set exceeds an LLM's context window, split it into chunks/Documents, summarize the pieces, then combine those partial summaries — via MapReduce (parallel) or Refine (sequential) — into one final summary.

## Frameworks Introduced
- **MapReduce summarization chain**: split → map → reduce, built from three LCEL sub-chains composed with `|`.
  - When to use: a single document bigger than the context window, or many documents where parallel speed and lower token cost matter more than preserving every contextual link.
  - How: (1) split the text into Document/chunk objects with a tokenizer (`TokenTextSplitter`, chunk_size + chunk_overlap); (2) map — run a summarization prompt independently over every chunk, in parallel via `RunnableParallel`; (3) reduce — join the chunk summaries into one string and run a second summarization prompt over that combined text.
- **Refine strategy**: progressively build one running summary by folding in one document at a time.
  - When to use: multiple documents where you want the essence of each part fully captured in the final summary, and sequential latency/token cost is acceptable.
  - How: maintain `current_refined_summary` (starts empty); for each document, call a refine prompt with `{current_refined_summary, text}`; the LLM either merges the new content in or returns the current summary unchanged if the document isn't useful; loop until all documents are processed.
- **Summarization decision flowchart**: pick a technique by two questions — one document or many? does it/they fit the context window?
  - When to use: as a triage step before writing any summarization chain.
  - How: single doc + fits window → stuff into one prompt. Single doc + doesn't fit → MapReduce. Multiple docs + all fit → stuff together. Multiple docs + don't fit → MapReduce (speed/cost) or Refine (per-document fidelity).

## Key Concepts
- **Context window**: the maximum text (instructions + content) an LLM can accept in one prompt, measured in tokens (~1 token ≈ 1 word); varies hugely by model (GPT-3.5: 16K, GPT-4/Claude 3: 100K, GPT-5/Gemini: 1M+).
- **Tokenizer / TokenTextSplitter**: reads text and breaks it into tokens, then groups tokens into chunks of a target size so each chunk fits the LLM's prompt limit; from the `tiktoken`-backed `langchain_text_splitters` package.
- **Document object**: LangChain's wrapper for a piece of text plus metadata (source, page number, timestamp, etc.) that preserves provenance through a processing pipeline; produced by any `DocumentLoader`.
- **Runnable / RunnableLambda / RunnableParallel**: `Runnable` is the abstract interface every chain component implements (takes input, processes, returns output). `RunnableLambda` wraps a plain Python callable as a chain step. `RunnableParallel` applies its wrapped logic to every element of a sequence concurrently — used for the map step.
- **LCEL pipe operator (`|`)**: chains components by passing one's output as the next's input, e.g. `prompt | llm | StrOutputParser()`.
- **DocumentLoader**: source-specific loader that returns a list of Document objects; examples: `WikipediaLoader`, `Docx2txtLoader`, `PyPDFLoader`, `TextLoader`, `WebBaseLoader`, `UnstructuredLoader`, `DirectoryLoader`.
- **StrOutputParser**: converts an LLM's raw response object into a plain text string.

## Mental Models
- **Split → Map → Reduce as three independently testable sub-chains**: build and reason about the chunking chain, the per-chunk summarization chain, and the combine chain separately, then compose them with `|` — mirrors classic MapReduce (map over a key, reduce/aggregate by key).
- **Fidelity vs. throughput trade-off**: MapReduce trades some cross-chunk context/completeness for parallelism and lower token cost; Refine trades speed and total token cost for preserving each document's essence, since every step re-reads the growing summary.
- **Decision-tree triage before coding**: always resolve "one doc or many?" then "fits the window or not?" before picking stuff/MapReduce/Refine — avoids over-engineering a MapReduce chain for text that would simply fit in one prompt.

## Anti-patterns
- **Reading a fixed set of documents with a raw file reader instead of a DocumentLoader**: manual token-splitting (as done for `Moby-Dick.txt`) is only needed when you must split one long text into chunks yourself; existing discrete documents (Word/PDF/TXT/Wikipedia) should go through the matching `DocumentLoader`, which already returns a `Document` list with metadata.
- **Choosing MapReduce when per-document fidelity matters**: MapReduce's parallel chunk summaries can lose connections between chunks; if the goal is to guarantee each source document's core content survives into the final summary, use Refine instead.
- **Ignoring cost/rate limits when testing**: repeatedly invoking `map_reduce_chain.invoke()` on the full book (or any large corpus) racks up per-call LLM charges and can trigger `RateLimitError: 429` on free-tier accounts; test on a trimmed sample first.

## Code Examples
```python
text_chunks_chain = (
    RunnableLambda(lambda x: [
        { 'chunk': text_chunk, }
        for text_chunk in TokenTextSplitter(chunk_size=3000,
            chunk_overlap=100).split_text(x)
    ])
)
```
- **What it demonstrates**: the split step — turning a raw string into a list of chunk dicts sized to fit under the model's context window.

```python
summarize_chunk_prompt_template = """
Write a concise summary of the following text, and include the main details.
Text: {chunk}
"""
summarize_chunk_prompt = PromptTemplate.from_template(summarize_chunk_prompt_template)
summarize_chunk_chain = summarize_chunk_prompt | llm
summarize_map_chain = (
    RunnableParallel(
        { 'summary': summarize_chunk_chain | StrOutputParser() }
    )
)

summarize_summaries_prompt_template = """
Write a concise summary of the following text, which joins several summaries,
and include the main details.
Text: {summaries}
"""
summarize_summaries_prompt = PromptTemplate.from_template(summarize_summaries_prompt_template)
summarize_reduce_chain = (
    RunnableLambda(lambda x: {
        'summaries': '\n'.join([i['summary'] for i in x]),
    })
    | summarize_summaries_prompt
    | llm
    | StrOutputParser()
)

map_reduce_chain = (
    text_chunks_chain
    | summarize_map_chain.map()
    | summarize_reduce_chain
)

summary = map_reduce_chain.invoke(moby_dick_book)
```
- **What it demonstrates**: the full MapReduce chain assembly — split chain piped into `.map()` over the map chain, piped into the reduce chain — and its invocation.

```python
def refine_summary(docs):
    intermediate_steps = []
    current_refined_summary = ''
    for doc in docs:
        intermediate_step = \
            {"current_refined_summary": current_refined_summary, "text": doc.page_content}
        intermediate_steps.append(intermediate_step)
        current_refined_summary = refine_chain.invoke(intermediate_step)
    return {"final_summary": current_refined_summary, "intermediate_steps": intermediate_steps}

full_summary = refine_summary(all_docs)
```
- **What it demonstrates**: the Refine loop — each document is combined with the running summary via `refine_chain`, and the summary updates one document at a time.

## Reference Tables
| Aspect | MapReduce | Refine |
|---|---|---|
| Processing order | Parallel (chunks/documents processed independently) | Sequential (one document at a time) |
| Context preservation | Some content loss acceptable | Preserves more context/each document's essence |
| Speed | Faster (parallel map step) | Slower (sequential, increasing latency) |
| Token cost | Lower | Higher (total tokens increase with each refine step) |
| Best for | Large volumes / large corpora, when speed matters most | When each part's essence must be captured in the final summary |

## Worked Example
Goal: summarize `Moby-Dick.txt` (~18,000 tokens), too big to "stuff" into gpt-5-nano's simulated small context window.

1. **Setup**: create `ch03` folder, venv, install `tiktoken`, `notebook`, `langchain`; read the file into `moby_dick_book` with a plain Python file read (needed here because the source is one long string, not discrete documents); instantiate `llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model_name="gpt-5-nano")`.
2. **Split**: `text_chunks_chain` uses `RunnableLambda` + `TokenTextSplitter(chunk_size=3000, chunk_overlap=100).split_text(x)` to turn the book string into a list of `{'chunk': ...}` dicts (~3,000-token pieces with 100-token overlap).
3. **Map**: `summarize_map_chain` wraps `summarize_chunk_prompt | llm | StrOutputParser()` in `RunnableParallel`, so every chunk gets its own "write a concise summary" prompt run independently.
4. **Reduce**: `summarize_reduce_chain` joins all chunk summaries with `'\n'.join(...)`, feeds the combined text into a second "summary of summaries" prompt, and parses the output to a string.
5. **Combine**: `map_reduce_chain = text_chunks_chain | summarize_map_chain.map() | summarize_reduce_chain` — the `.map()` call is what fans the map chain out over every item in the chunk list produced by the split step.
6. **Run**: `summary = map_reduce_chain.invoke(moby_dick_book)` — output is a coherent multi-paragraph summary (Ishmael's melancholy, arrival in New Bedford, meeting Queequeg, etc.), built entirely from independently-summarized chunks reduced into one narrative.
7. **Extension to multiple sources (section 3.2)**: for the Paestum example, four sources (Wikipedia via `WikipediaLoader`, `.docx` via `Docx2txtLoader`, `.pdf` via `PyPDFLoader`, `.txt` via `TextLoader`) are each loaded into `Document` lists and concatenated: `all_docs = wikipedia_docs + word_docs + pdf_docs + txt_docs`. Because these are already discrete documents (not one long text), no splitting step is needed — MapReduce or Refine can run directly against `all_docs`. The chapter then demonstrates Refine on `all_docs`, iterating the running summary through each document until `final_summary` captures Paestum's history end to end.
8. **Decide** (flowchart, section 3.3): one document that fits → stuff it; one document too big → MapReduce; many documents that all fit → stuff them together; many documents too big → MapReduce for speed, Refine for per-document fidelity.

## Key Takeaways
1. Always chunk with a tokenizer-aware splitter (`TokenTextSplitter`) sized to your model's context window, not an arbitrary character count.
2. Build MapReduce as three composable LCEL sub-chains — split, map (`RunnableParallel` + `.map()`), reduce — so each stage can be tested independently.
3. Use `Document` objects (with metadata) for anything loaded via a `DocumentLoader`; reserve manual chunking/`Document` construction for cases where you must split one long text yourself.
4. Choose MapReduce for throughput and lower cost on large corpora; choose Refine when each document's essence must survive into the final summary, accepting higher latency and token cost.
5. Run the one-doc-vs-many, fits-window-vs-doesn't decision tree before writing any summarization code — it directly picks stuff vs. MapReduce vs. Refine.
6. Test summarization chains on a trimmed sample first; every LLM call in a MapReduce/Refine chain is billed, and full-book runs (or repeated test runs) add up fast.
7. Explore `UnstructuredLoader` and `DirectoryLoader` to load mixed-format folders (Word/PDF/TXT) in one operation instead of wiring a separate loader per file type.

## Connects To
- **Ch 1**: Document object model and the catalog of `DocumentLoader` types referenced here (Wikipedia, Word, PDF, TXT, web).
- **Ch 2**: basic `PromptTemplate`-based summarization of small documents, which this chapter extends to documents/corpora exceeding the context window.
- **Ch 4**: research summarization engine — builds directly on these summarization techniques plus deeper LCEL (parallel processing) for a multi-chain application.
- **Ch 8**: chunking strategies in more depth (chunking by size vs. content structure).
- **LCEL (LangChain Expression Language)**: the `|` pipe composition and `Runnable` interface used throughout to assemble split/map/reduce and refine chains.
