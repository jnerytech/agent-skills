# Chapter 6: RAG fundamentals with ChromaDB

## Core Idea
Retrieval Augmented Generation (RAG) solves the problem of Q&A over large knowledge bases by splitting the work into an ingestion stage (embed and store content in a vector store) and a retrieval stage (semantically search that store, then feed the result to an LLM as context) — instead of stuffing everything into one prompt.

## Frameworks Introduced
- **RAG design pattern (retrieve-then-generate)**: a two-stage architecture — content ingestion (indexing) and question-answering (retrieval + generation).
  - When to use: the knowledge base is too large or too scattered (multiple documents/formats) to paste into a single prompt.
  - How: (1) ingestion — extract text from sources, split into chunks, embed each chunk, store chunk + embedding (+ metadata) in a vector store; (2) Q&A — embed the user's question with the same model, run a similarity search against the vector store, retrieve top-k chunks, insert them as "context" into a prompt template, send to the LLM, return the synthesized answer.
- **Hallucination-safe Q&A prompting**: constrain the LLM to answer only from the retrieved context and explicitly say "I don't know" otherwise.
  - When to use: whenever the retrieved context may not contain the answer — the default assumption in any RAG system.
  - How: instruct the model to use only the given context, cap answer length, and give explicit permission (and an example) to say "I do not know" rather than guess.

## Key Concepts
- **Semantic search**: searching by meaning rather than exact keyword match — the query and result need not share any words.
- **Embedding**: a numerical vector representation of text (or image/audio/video) that captures meaning in its dimensions; used to index content for similarity search.
- **Vector store**: a storage system optimized for holding and querying high-dimensional embeddings; returns the closest vector(s) to a query vector via similarity search.
- **Vector library vs. vector database**: a library (e.g., FAISS) only stores embeddings in memory with no updates and no query-during-ingest; a database (e.g., Pinecone, Chroma) also stores the original text/metadata, supports full CRUD, and allows querying while ingesting.
- **Context**: the text/information supplied in the prompt alongside the user's question, used to formulate the answer — either a full document or retrieved chunks.
- **Synthesize**: to generate an answer from the question and the supplied context.
- **Chunk (text fragment/node)**: a small piece of a document; documents are split into chunks because embedding models work on finite input sizes and because search should target focused, relevant pieces rather than large mixed-relevance sections.
- **Similarity search**: measuring distance between query and stored embeddings (e.g., cosine, Euclidean, Hamming distance; ANN algorithms) to find the semantically closest chunks.
- **Chroma collection**: a named bucket in ChromaDB where documents and their embeddings are stored together.

## Mental Models
- **ChatGPT-chatbot-over-one-document as RAG's training wheels**: the single-document Q&A pattern (paste text + question, then refine via follow-up turns in a stateful session) is structurally identical to RAG, except RAG replaces "the whole pasted document" with "chunks retrieved from a vector store." Understanding one clarifies the other.
- **Distance = relevance signal**: lower vector distance between query and chunk means higher semantic relevance; this is the mechanism the retriever uses to rank and select context, not a magic black box.
- **Less-but-focused beats more-but-loose**: narrowing context to the most relevant chunks improves speed, cost, and accuracy versus overloading the prompt with everything — a rebuttal to the instinct to just retrieve more.
- **Retrieval never generates**: the vector store's job ends at returning the closest raw text chunks; it never produces prose answers. Answer synthesis is strictly the LLM's job, downstream of retrieval — conflating the two stages is a common misunderstanding.

## Anti-patterns
- **Trusting an LLM's unconstrained answer over supplied text**: when a chatbot can't find the answer in the provided text, it may fall back on its own (possibly wrong or made-up) knowledge — hallucination. Example in the chapter: ChatGPT invented "94 columns" and specific per-temple counts that were factually wrong.
- **Pasting the entire knowledge base into the prompt**: doesn't scale — exceeds the model's context window and degrades speed/cost/accuracy versus retrieving only relevant chunks.
- **Using immutable vector libraries (FAISS-style) for frequently changing data**: they can't be updated in place and don't support concurrent query-during-ingest, making them a poor fit for intraday-changing knowledge bases.
- **Loose prompt wording ("answer the question")**: without an explicit "say you don't know" instruction and a concrete negative example, the LLM will still guess when context is insufficient — as shown by the plain prompt vs. the LangChain Hub-style safe prompt.

## Code Examples
```python
import chromadb
chroma_client = chromadb.Client()

tourism_collection = chroma_client.create_collection(
    name="tourism_collection")

tourism_collection.add(
    documents=[
        "Paestum, Greek Poseidonia, …[shortened] … Greek temples.",
        "Poseidonia was probably …[shortened] … in the 18th century.",
        "The ancient Greek part of …[shortened] … from the site."
    ],
    metadatas=[
        {"source": "https://www.britannica.com/place/Paestum"},
        {"source": "https://www.britannica.com/place/Paestum"},
        {"source": "https://www.britannica.com/place/Paestum"}
    ],
    ids=["paestum-br-01", "paestum-br-02", "paestum-br-03"]
)

results = tourism_collection.query(
    query_texts=["How many Doric temples are in Paestum"],
    n_results=1
)
print(results)
```
- **What it demonstrates**: creating a Chroma collection, ingesting text with metadata and IDs (Chroma auto-generates embeddings via its default model), and running a semantic similarity query that returns the closest chunk plus its distance and metadata.

```python
def query_vector_database(question):
    results = tourism_collection.query(
        query_texts=[question],
        n_results=1
    )
    results_text = results['documents'][0][0]
    return results_text

def prompt_template(question, text):
    return f'Use the following pieces of retrieved context to '
    f'answer the question. Only use the retrieved context to '
    f'answer the question. If you don\'t know the answer, or '
    f'the answer is not contained in the retrieved context, '
    f'just say that you don\'t know. Use three sentences '
    f'maximum and keep the answer concise. \nQuestion: '
    f'{question}\nContext: {text}. Remember: if you do not '
    f'know, just say: I do not know. Do not make up an '
    f'answer. For example do not say the three temples have '
    f'got a total of three columns. \nAnswer:'

def execute_llm_prompt(prompt_input):
    prompt_response = openai_client.chat.completions.create(
        model='gpt-5-nano',
        messages=[
            {"role": "system", "content": "You are an assistant "
                "for question-answering tasks."},
            {"role": "user", "content": prompt_input}
        ])
    return prompt_response
```
- **What it demonstrates**: the retrieval function (wraps the Chroma query), the hallucination-safe prompt template (context + explicit "say I don't know" instruction with a negative example), and the LLM-invocation function using the OpenAI chat completions API.

```python
def my_chatbot(question):
    results_text = query_vector_database(question)   # Retrieves content from the vector store
    prompt_input = prompt_template(question, results_text)  # Creates the LLM prompt
    prompt_output = execute_llm_prompt(prompt_input)  # Executes the LLM prompt
    return prompt_output
```
- **What it demonstrates**: the full RAG loop collapsed into one function — retrieve, build prompt, generate — the minimal shape every later LangChain abstraction (Ch. 7) will wrap.

## Reference Tables

**Vector libraries vs. vector databases**

| Capability | Vector library (e.g., FAISS) | Vector database (e.g., Pinecone, Chroma) |
|---|---|---|
| Stores original text | No — external sync via unique ID required | Yes, alongside embeddings and metadata |
| Updates | No — immutable data structures | Full CRUD (create, read, update, delete) |
| Querying during ingestion | Not supported (read/write conflict risk) | Supported |
| Extra features | Minimal, in-memory | Caching, sharding, partitioning |

**Most popular vector stores (table 6.1, abridged)**

| Vector store | Type | Website |
|---|---|---|
| FAISS | Vector library | github.com/facebookresearch/faiss |
| Milvus | Vector database | milvus.io |
| Qdrant | Vector database | qdrant.tech |
| Chroma | Vector database | trychroma.com |
| Weaviate | Vector database | weaviate.io |
| Pinecone | Vector database | pinecone.io |
| Vald | Vector database | vald.vdaas.org |
| ScaNN | Vector library | (Google) |
| Elasticsearch | Search engine | elastic.co |
| PgVector | PostgreSQL extension | github.com/pgvector/pgvector |
| MongoDB Atlas | MongoDB extension | mongodb.com |

## Worked Example
Building RAG from scratch against ChromaDB and an OpenAI model (GPT-5-nano), reproducing the earlier ChatGPT-vs-Paestum comparison:

1. **Set up clients.** Create an in-memory Chroma client (`chromadb.Client()`) and a collection (`create_collection`); create an OpenAI client with an API key.
2. **Ingest.** Split the Paestum source text manually into chunks and `add()` them to the collection with `documents`, `metadatas` (source URL), and `ids`. Chroma embeds each chunk with its default embedding model.
3. **Retrieve.** Wrap `collection.query(query_texts=[question], n_results=1)` in `query_vector_database(question)`, returning `results['documents'][0][0]` — the single closest chunk.
4. **Prompt, first pass.** Build a plain prompt template combining question + retrieved context and call `execute_llm_prompt`. Test with the trick question "How many columns have the three temples got in total?" — the retrieved chunk doesn't contain that number. GPT-5-nano correctly replies it lacks the information (unlike GPT-3.5-turbo previously, which hallucinated "24 columns").
5. **Prompt, hardened.** Adopt the LangChain Hub's hallucination-safe RAG prompt pattern: instruct the model to use only the retrieved context, say "I do not know" if the answer isn't there, cap the answer at three sentences, and give a concrete negative example ("do not say the three temples have got a total of three columns"). Rerun the trick question — response: "I do not know."
6. **Assemble the chatbot.** Combine the three pieces into `my_chatbot(question)`: retrieve → build prompt → call LLM → return response.
7. **Validate end-to-end.** Ask the original multi-part question ("how many temples … who constructed them … what architectural style"). The chatbot answers temple count and architectural style correctly from retrieved context, and — because the retrieved chunk doesn't mention builders — honestly states "I do not know who constructed them," rather than inventing an answer as plain ChatGPT initially risked doing.

Outcome: a working, non-hallucinating Q&A chatbot built from three small functions (`query_vector_database`, `prompt_template`, `execute_llm_prompt`) plus one orchestrator (`my_chatbot`), with no framework beyond the ChromaDB and OpenAI SDKs.

## Key Takeaways
1. RAG splits Q&A into ingestion (chunk → embed → store) and retrieval (embed query → similarity search → inject context → generate) — treat these as separate, independently testable stages.
2. Chunking matters as much as retrieval: mid-sentence splits or orphaned context degrade answer quality even when the retriever finds the "right" chunk.
3. The vector store never writes prose — it only returns the closest raw chunks; always pair it with an LLM call for synthesis.
4. Explicitly instruct the LLM to refuse when the context is insufficient (with a concrete negative example) — this is the cheapest, most effective anti-hallucination lever available.
5. Vector libraries and vector databases converge in practice, but pick based on need: libraries for simple, static, in-memory similarity search; databases when you need persistence, updates, metadata, or concurrent ingestion.
6. Start k (number of retrieved chunks) around 4 and tune between roughly 2–8 based on content density and context-window budget.
7. Embedding dimensionality must stay consistent between ingestion and retrieval — switching embedding models requires re-embedding the whole corpus.

## Connects To
- **Ch 7**: Q&A chatbots with LangChain and LangSmith — reimplements this same RAG pipeline using LangChain's object model and adds tracing.
- **Vector store client-server mode**: `chromadb.PersistentClient` (on-disk) and `chromadb.HttpClient` (client/server) as alternatives to the in-memory client used here.
- **Prompt engineering**: the hallucination-safe prompt pattern here is a specific application of general safe-prompt-design principles referenced throughout the book.
