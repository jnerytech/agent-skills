# Chapter 4: Building a research summarization engine

## Core Idea
Automate manual "search, read, summarize" research by chaining web search, scraping, and LLM summarization into a pipeline, then reimplement it in LCEL so the independent steps run in parallel instead of sequentially.

## Frameworks Introduced
- **Query rewriting (multiple query generation)**: use the LLM to turn one ambiguous research question into several targeted search queries before hitting the search engine.
  - When to use: the original question is short, ambiguous, complex, or has grammar issues that would confuse a search engine.
  - How: prompt the LLM with the question and a desired number of queries, requesting a JSON list; feed each query independently into web search.
- **LangChain Expression Language (LCEL) chain composition**: compose `Runnable` components with the `|` pipe operator into sequential/parallel pipelines.
  - When to use: any multi-step LLM workflow where steps have clear input/output boundaries and some steps are independent of each other.
  - How: build mini-chains per step (prompt → LLM → parser), wire them with `|`, use `RunnableLambda` for custom Python transforms, `RunnableParallel` for simultaneous branches on the same input, and `.map()` to fan a chain out over a list.
- **Mini-chain composition strategy**: build one small chain per processing step, then assemble them into a master chain.
  - When to use: any pipeline complex enough that a single monolithic chain becomes hard to test or reason about.
  - How: name and test each mini-chain in isolation (Assistant Instructions, Web Searches, Search Result URLs, Search Result Text and Summary, Search and Summarization, Web Research), then compose into the top-level chain.

## Key Concepts
- **Runnable protocol**: the interface LCEL components implement — `invoke()`, `stream()`, `batch()`, plus async variants — enabling uniform composition.
- **RunnableLambda**: wraps an arbitrary Python function (often a lambda) so it can participate in an LCEL pipe chain.
- **RunnableParallel**: runs multiple operations concurrently against the same input, returning a dict keyed by branch name.
- **`.map()` operator**: fans a chain out to run once per item in an input list, in parallel, producing a list of results.
- **RunnablePassthrough**: forwards the original input unchanged into a named field of a dict, so later steps (and the final report) can still reference the raw user question.
- **Assistant Instructions chain**: selects the best-fit "research assistant" persona (e.g., finance analyst, tour guide, sport expert) and generates its system-style instructions from the user's question, via a few-shot JSON-output prompt.
- **Web Searches chain**: rewrites the user question into N targeted search queries (query rewriting) using the assistant instructions as context.
- **Search and Summarization chain**: per query, fetches result URLs, scrapes each page, and summarizes it — composed from Search Result URLs, Search Result Text and Summary, and Joined Summary sub-chains.
- **Web Research chain**: the master chain — Assistant Instructions → Web Searches → Search and Summarization (mapped per query, parallel) → merge → Research Report prompt → LLM → parsed string.
- **`to_obj()` utility**: converts LLM JSON text output into a Python dict/list, returning `{}` on malformed JSON — a defensive parsing boundary between LLM text and downstream code.

## Mental Models
- **Sequential-first, then parallelize**: build the naive, easy-to-follow sequential pipeline first to understand the data flow; only then reimplement in LCEL to unlock parallel execution — don't optimize for speed before the shape of the pipeline is understood.
- **Fan-out / fan-in**: the recurring shape in this chapter is "one input produces N independent items (queries, then URLs) → process each item independently and in parallel → join results back into one text block for the next stage." This appears twice, nested (queries fan out to URLs, URLs fan out to page summaries).
- **Persona-conditioned prompting**: letting the LLM pick a specialized assistant persona (finance analyst vs. tour guide vs. sport expert) before generating queries/report produces more targeted, domain-appropriate output than a single generic prompt.
- **Cost-as-a-dial**: `NUM_SEARCH_QUERIES` × `NUM_SEARCH_RESULTS_PER_QUERY` directly multiplies both LLM token spend and wall-clock time (in the sequential version) — treat these constants as an explicit accuracy/cost/latency trade-off, not an afterthought.

## Anti-patterns
- **Sequential processing of independent web requests**: summarizing pages one-by-one means total latency scales linearly with the number of searches × results — this is why the chapter moves to LCEL `.map()`/parallel execution.
- **Sending raw scraped HTML text straight to the report prompt**: skips the per-page summarization step, wasting context and letting irrelevant boilerplate (nav menus, footers) pollute the final report; instead summarize each page first, keeping only source URL + summary.
- **Ignoring User-Agent headers when scraping**: sites like Wikipedia will block the request (via `requests.get`) without a browser-like `User-Agent` and `Accept-Language` header, so scraping silently fails.
- **Not guarding malformed LLM JSON output**: parsing LLM-returned JSON directly with `json.loads` without a fallback (as `to_obj()` provides) will crash the pipeline on any malformed response.

## Code Examples
```python
import requests
from bs4 import BeautifulSoup

def web_scrape(url: str) -> str:
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            page_text = soup.get_text(separator=" ", strip=True)
            return page_text
        else:
            return f"Could not retrieve the webpage: Status code {response.status_code}"
    except Exception as e:
        print(e)
        return f"Could not retrieve the webpage: {e}"
```
- **What it demonstrates**: web scraping with `requests` + `BeautifulSoup`, with spoofed headers to avoid being blocked and defensive error handling that returns a string instead of raising.

```python
search_and_summarization_chain = (
    search_result_urls_chain
    | search_result_text_and_summary_chain.map()  # parallelize for each url
    | RunnableLambda(lambda x: {
        'summary': '\n'.join([i['summary'] for i in x]),
        'user_question': x[0]['user_question'] if len(x) > 0 else ''
    })
)

web_research_chain = (
    assistant_instructions_chain
    | web_searches_chain
    | search_and_summarization_chain.map()  # parallelize for each web search
    | RunnableLambda(lambda x: {
        'research_summary': '\n\n'.join([i['summary'] for i in x]),
        'user_question': x[0]['user_question'] if len(x) > 0 else ''
    })
    | RESEARCH_REPORT_PROMPT_TEMPLATE
    | get_llm()
    | StrOutputParser()
)
```
- **What it demonstrates**: LCEL composition with `.map()` for two nested levels of parallel fan-out (per web search, then per URL within each search) and `RunnableLambda` join steps that merge mapped results back into a single dict before the next stage.

```python
assistant_instructions_chain = (
    {'user_question': RunnablePassthrough()}
    | ASSISTANT_SELECTION_PROMPT_TEMPLATE
    | get_llm()
    | StrOutputParser()
    | to_obj
)
```
- **What it demonstrates**: minimal LCEL chain pattern — `RunnablePassthrough` binds raw input to a named prompt variable, `StrOutputParser` extracts `.content`, and a plain function (`to_obj`) is used directly in the pipe without wrapping (functions are runnables by duck-typing when used as the last/middle link here via `|`).

## Reference Tables
| Mini-chain | Input | Output | Parallelized via |
|---|---|---|---|
| Assistant Instructions chain | user question (str) | dict: assistant_type, assistant_instructions, user_question | — |
| Web Searches chain | dict from above | list of dicts: search_query, user_question | — |
| Search Result URLs chain | dict: search_query, user_question | list of dicts: result_url, search_query, user_question | — |
| Search Result Text and Summary chain | dict: result_url, search_query, user_question | dict: summary, user_question | `RunnableParallel` inside; instantiated per URL |
| Search and Summarization chain | dict: search_query, user_question | dict: summary (joined), user_question | `.map()` over URLs |
| Web Research chain (master) | user question (str) | final Markdown research report (str) | `.map()` over search queries |

## Worked Example
Question: `'What can I see and do in the Spanish town of Astorga?'`, with `NUM_SEARCH_QUERIES = 2`, `NUM_SEARCH_RESULTS_PER_QUERY = 3`.

1. **Assistant Instructions chain** (`chain_1_2.py`): `assistant_instructions_chain.invoke(question)` runs the question through `ASSISTANT_SELECTION_PROMPT_TEMPLATE` (a few-shot prompt with 3 worked examples of question → assistant persona) and the LLM picks "Tour guide assistant," returning `{'assistant_type': 'Tour guide assistant', 'assistant_instructions': 'You are a world-travelled AI tour guide assistant...', 'user_question': 'What can I see and do in the Spanish town of Astorga?'}`.
2. **Web Searches chain** (`chain_2_1.py`): takes that dict, injects `NUM_SEARCH_QUERIES` via `RunnableLambda`, runs `WEB_SEARCH_PROMPT_TEMPLATE` through the LLM, and returns a list like `[{'search_query': 'Astorga attractions', ...}, {'search_query': 'Astorga history', ...}]`.
3. **Search and Summarization chain**, run once per query via `.map()`:
   - **Search Result URLs chain** (`chain_3_1.py`) calls `web_search(web_query=..., num_results=3)` (DuckDuckGo via `DuckDuckGoSearchAPIWrapper`) and returns 3 `{result_url, search_query, user_question}` dicts.
   - **Search Result Text and Summary chain** (`chain_4_1.py`), run once per URL via `.map()`: scrapes the page with `web_scrape()`, truncates to `RESULT_TEXT_MAX_CHARACTERS` (10,000), runs `SUMMARY_PROMPT_TEMPLATE` through the LLM inside a `RunnableParallel` (alongside passthrough lambdas for `result_url`/`user_question`), then formats `'Source Url: {url}\nSummary: {summary}'`.
   - The Joined Summary step (embedded `RunnableLambda`) joins all per-URL summaries for that query with `'\n'.join(...)`.
4. **Web Research chain** (`chain_5_1.py`) runs step 3 once per query (again via `.map()`, so both search-level and URL-level work parallelize), joins all per-query summaries with `'\n\n'.join(...)` into `research_summary`, then feeds `{research_summary, user_question}` into `RESEARCH_REPORT_PROMPT_TEMPLATE | get_llm() | StrOutputParser()`.
5. Result: `web_research_chain.invoke(question)` returns a Markdown report (≥1,200 words, APA-style source list) starting with `# Introduction`, covering history and top attractions of Astorga, generated end-to-end without manual copy-pasting into ChatGPT.

The sequential version (`research_engine_seq.py`, section 4.6) performs the identical steps as plain imperative Python (list comprehensions and `llm.invoke()` calls in a loop) — useful for understanding the data flow before converting each step into an LCEL mini-chain.

## Key Takeaways
1. Break a multi-stage LLM pipeline into small, independently testable mini-chains (one prompt/transform per responsibility) before assembling a master chain — each was validated in this chapter with its own `chain_try_*.py` script and mock input.
2. Use query rewriting (LLM-generated multiple search queries) instead of sending the raw user question straight to a search API — it disambiguates, fixes grammar, and adds context.
3. `RunnableLambda` bridges plain Python logic (like calling `web_search()` or `web_scrape()`) into an LCEL pipe chain; `RunnableParallel` and `.map()` are the two tools for concurrency — the former for parallel branches on one input, the latter for parallel instances over a list.
4. Always summarize scraped page text before feeding it to a downstream report prompt; keep the source URL attached to each summary so the final report can cite sources (APA format required at the prompt level).
5. Guard every external-I/O boundary defensively: `web_scrape()` catches exceptions and returns a string instead of raising; `to_obj()` returns `{}` on JSON parse failure instead of crashing the chain.
6. Treat `NUM_SEARCH_QUERIES` and `NUM_SEARCH_RESULTS_PER_QUERY` as explicit cost/latency/accuracy dials — more queries and results improve report depth but multiply both token cost and (in a sequential design) runtime.
7. LCEL's `.map()` converts an O(n) sequential loop into parallel execution with no change to the underlying mini-chain code — the same `search_result_text_and_summary_chain` used for a single URL becomes the per-item worker for a whole list.

## Connects To
- **Ch 3**: reuses summarization chain patterns and `RunnableParallel` introduced there; this chapter is the first full end-to-end LCEL application built from those primitives.
- **Ch 5**: the closing note reframes this pipeline as a fixed, non-adaptive "agentic workflow" and previews rebuilding it with LangGraph for state management and more autonomous agent behavior.
- **GPT Researcher (external)**: the engine's design is explicitly adapted from the open-source GPT Researcher project (github.com/assafelovic/gpt-researcher), reimplemented here in LCEL for pedagogical clarity.
- **Retrieval-Augmented Generation (RAG)**: query rewriting/multiple query generation is described as the same technique used to improve RAG retrieval, covered in later chapters.
