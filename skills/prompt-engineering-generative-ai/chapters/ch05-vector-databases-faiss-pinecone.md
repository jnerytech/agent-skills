# Chapter 5: Vector Databases with FAISS and Pinecone

## Core Idea
Embeddings turn text into coordinates in a latent space, so a vector database can retrieve records by *meaning* instead of exact keywords. Retrieving only the few most relevant chunks and inserting them into the prompt (RAG) cuts hallucinations and keeps you inside the context window without paying for irrelevant tokens.

## Frameworks Introduced
- **Retrieval Augmented Generation (RAG)**: search by similarity to the query, retrieve the most relevant documents, and insert them into the prompt as context.
  - When to use: open-ended scenarios where the model is asked about data it was never trained on (private docs, long chat history, product catalogs), or when the full corpus would blow the token limit or budget.
  - How (production pipeline):
    1. Break documents into chunks of text.
    2. Index chunks in a vector database.
    3. Search by vector for similar records.
    4. Insert records into the prompt as context. Add a system message telling the model to use *only* that context and to say "I don't know" otherwise.
  - Principle(s): **Give Direction**. Instead of putting static knowledge in the prompt, you insert the most relevant knowledge dynamically.
  - Why it works / failure mode: the model answers from supplied facts instead of making things up. Retrieval quality depends entirely on the embedding model and the chunking strategy. A bad chunk (cut mid-sentence, or too broad) or an embedding model that lacks domain or recent vocabulary gives you context that looks relevant but is wrong. Retrieval doesn't have to be vector search. Plain database queries or web browsing are often enough.

- **Chunking strategy (context vs. similarity trade-off)**: the chunk size and overlap you choose decide what can be retrieved.
  - When to use: every time you load documents into a vector store.
  - How: work out the token budget first. For example, gpt-4-0613's 8,192 tokens minus ~3,000 for prompt plus response leaves 5 chunks × 1,000 tokens. Split with a structure-aware splitter (`RecursiveCharacterTextSplitter` tries line breaks, then spaces) and add overlap so context survives chunk boundaries.
  - Principle(s): **Specify Format**. Short chunks without overlap may miss the answer. Long, heavily overlapping chunks return irrelevant text that confuses the LLM and costs tokens.
  - Failure mode: embedding a very large block (a whole book) causes *regression to the mean*. The vector drifts toward the average of all its tokens and loses semantic specificity. Chunks that are too small lose meaning.

- **Metadata filtering strategy**: store metadata (batch, page, title, chapter, timestamp, chatbot ID, price) next to each vector and filter queries on it.
  - When to use: to narrow where similarity is computed. Examples: only this chatbot's past conversations, recent timestamps, specific pages, products above a price.
  - How: attach metadata dicts at upsert time, then pass `filter={"batch": {"$eq": 1}}` to `index.query`. Pinecone metadata types are string, number (stored as 64-bit float), boolean, and list of strings.
  - Note: the book says the metadata strategy "can be just as important as the chunking strategy". More metadata and large, rarely retrieved chunks raise storage cost.

- **Self-Querying (SelfQueryRetriever)**: an LLM reads the user's natural-language query, pulls out structured metadata filters (and limits), and builds a new query to run against the store.
  - When to use: the query contains attributes ("books by J.K. Rowling", "2 Fantasy books") that should become exact filters rather than fuzzy similarity. The pattern also works for SQL and NoSQL databases.
  - How: define a schema of `AttributeInfo(name, description, type)` entries, give a `document_content_description`, and build `SelfQueryRetriever.from_llm(llm, vectorstore, description, metadata_field_info, enable_limit=True)`.
  - Benefits: *schema definition* (a structured picture of what users ask for) and *dual-layer retrieval* (semantic similarity plus a metadata filter).
  - Principle(s): **Evaluate Quality**. Use `temperature=0` so the generated filters are consistent rather than creative.

- **Alternative retrieval mechanisms** (pick by trade-off; see table below): MultiQueryRetriever, Contextual Compression, Ensemble Retriever, Parent Document Retriever, Time-Weighted Vector Store Retriever.

## Key Concepts
- **Vector / embedding**: a list of numbers representing text (or images) as coordinates. `text-embedding-ada-002` has 1,536 dimensions and all-MiniLM-L6-v2 has 384. Texts that co-occur in training end up close together.
- **Latent space**: the abstract multidimensional space formed by the model's parameters. Its features are learned and usually can't be interpreted by people.
- **k-nearest search**: get the query's vector and return the k closest records. Raising k widens recall: `mouse` with k=3 returns mickey mouse, cheese, trap, and k=4 adds rat.
- **Contextual vs. static embeddings**: transformer embeddings depend on context ("bank" in riverbank vs. financial bank). Vectors from different models, or different versions of one model, can't be compared.
- **Dense vs. sparse vectors**: in dense vectors almost every value is nonzero, which carries semantic meaning. Sparse vectors have 100k+ dimensions that are mostly zero, which suits keyword search. **Hybrid search** combines both.
- **Document loading vs. chunking**: loading means computing or retrieving the vectors and storing them. Chunking means splitting text into pieces. The two are usually done together.
- **TF-IDF**: term frequency offset by corpus frequency. Use it with cosine similarity for small corpora, where word2vec needs tens of millions of words.
- **Cosine similarity**: a distance measure between vectors. It approaches 1 for terms that co-occur and 0 for unrelated ones.
- **IndexFlatL2**: FAISS's brute-force index. It measures straight-line (L2) distance to every item one by one.
- **Upsert**: update the record if it exists, insert it if not. This is how Pinecone writes records.

## Mental Models
- Think of an embedding as a GPS coordinate for meaning. A relational `LIKE '%mouse%'` finds only "mickey mouse", while vector search also finds "cheese" and "trap" because they sit nearby.
- Use RAG when the knowledge you need is too big, too private or too recent for the prompt or the training data. Use static few-shot examples when the context doesn't change from query to query.
- Embeddings are only as good as the model behind them. They inherit its biases, knowledge cutoff (ada-002 stops at August 2020) and domain gaps. If your vocabulary has its own meanings (for example, the coded language of moderated online groups), train custom embeddings (word2vec/GloVe via Gensim).
- Vectors don't change unless the embedding model changes, so compute them once, persist them (`faiss.write_index`), and only re-embed new records.

## Anti-patterns
- **Stuffing the whole corpus into a huge context window**: the 2024 example is gpt-4-1106-preview with 128k context at ~10x the per-token price of gpt-3.5-turbo. Retrieving only the relevant records is cheaper and more focused.
- **Naive fixed-size splitting**: arbitrary 1,000-token cuts break sentences and paragraphs and lose meaning. Use recursive splitting with overlap.
- **Re-embedding and rebuilding the index on every query**: wastes compute, money and latency. Persist the index and reload it.
- **Merging FAISS indices and expecting IDs to survive**: `reconstruct_n` + `add` gives the vectors new IDs, and it fails for indexes without `reconstruct` (e.g. `IndexIVFFlat`) or with different configurations. Keep an external ID→data mapping, or keep the raw vectors and rebuild.
- **Training word2vec on a tiny corpus**: results only look good when cherry-picked with a seed. Use TF-IDF for small corpora.
- **Mixing embeddings from different models in one index**: their vector spaces don't match.
- **Ignoring hosted-DB risks**: overspending through misconfiguration, vendor lock-in, and the privacy and legal exposure of sending data to a third party.
- **Assuming vector search is always worth it**: it adds cost and latency. Test whether the extra context actually helps. For heavy workloads, fine-tuning may be cheaper than prompts plus embeddings plus storage.

## Code Examples
```python
from openai import OpenAI
client = OpenAI()

def get_vector_embeddings(text):
    response = client.embeddings.create(
        input=text, model="text-embedding-ada-002"
    )
    embeddings = [r.embedding for r in response.data]
    return embeddings[0]
```
- **What it demonstrates**: the basic embedding call that every later retrieval step relies on (OpenAI SDK v1 style, 2024).

```python
import numpy as np
import faiss

emb = [get_vector_embeddings(chunk) for chunk in chunks]
vectors = np.array(emb)
index = faiss.IndexFlatL2(vectors.shape[1])
index.add(vectors)

def vector_search(query_text, k=1):
    query_vector = get_vector_embeddings(query_text)
    distances, indices = index.search(np.array([query_vector]), k)
    return [(chunks[i], float(dist))
            for dist, i in zip(distances[0], indices[0])]

faiss.write_index(index, "data/my_index_file.index")   # persist
index = faiss.read_index("data/my_index_file.index")   # reload
```
- **What it demonstrates**: a minimal local vector store: index, search the k nearest, persist.

```python
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

vectorstore = FAISS.from_texts(texts=documents, embedding=OpenAIEmbeddings())
retriever = vectorstore.as_retriever()
template = """Answer the question based only on the following context:
---Context: {context}
---Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt | ChatOpenAI() | StrOutputParser()
)
chain.invoke("What is the president of the US?")  # -> "I don't know"
```
- **What it demonstrates**: RAG in a few lines of LCEL. The retriever fills `{context}` (4 documents by default) and the "only the following context" instruction makes the model answer "I don't know" for anything out of scope. Imports are from the 2024 split packages (`langchain_community`, `langchain_openai`) and may have changed since.

## Reference Tables

**Hosted (Pinecone, Chroma, Weaviate, Supabase pgvector) vs. local (FAISS)**

| Hosted advantage | What you get | Counter-risk |
|---|---|---|
| Maintenance | No setup or DBA/DevOps work | Cost, and overspend from mistakes |
| Scalability | Scales automatically as data grows | Vendor lock-in (APIs differ) |
| Reliability | SLAs, backups, disaster recovery | Privacy and legal exposure from sharing data |
| Performance | Optimized infrastructure for real-time search | |
| Support | Vendor help | |
| Security | Encryption, access control, compliance certificates (e.g. EU) | |

**Alternative retrievers**

| Retriever | Approach | Trade-off |
|---|---|---|
| MultiQueryRetriever | Generates several queries from different perspectives to widen recall | Results may contradict or overlap |
| Contextual Compression | Compresses the irrelevant parts of long docs | Hard to judge what is relevant |
| Ensemble Retriever | Combines several retrievers (hybrid) | More compute, slower |
| Parent Document Retriever | Returns the original parent doc of the matched small chunk | Larger docs, more compute |
| Time-Weighted Vector Store | Applies time decay to scores | May overlook relevant old documents |

**Embedding options**

| Option | Dims | Notes |
|---|---|---|
| OpenAI text-embedding-ada-002 | 1,536 | $0.0004 / 1K tokens (the whole KJV Bible, ~4M tokens, costs ~$1.60). Cutoff Aug 2020 |
| HF sentence-transformers/all-MiniLM-L6-v2 | 384 | Open source small BERT, tuned for sentence-level tasks |
| Gensim word2vec / GloVe (spaCy) | custom | Train on domain vocabulary. Needs a large corpus |
| TF-IDF (scikit-learn) | vocabulary size | Sparse, works on small corpora |

## Worked Example
**Chatbot long-term memory via RAG.** Mike said "My name is Mike" 3,000 messages ago, which is far outside the context window. A keyword search for "name" returns too many hits in the wrong contexts. Instead, the current user message is embedded and the top 3 similar past messages are retrieved:

```
Context
Most relevant previous user messages:
1. "My name is Mike".
2. "My dog's name is Hercules".
3. "My coworker's name is James".

Instructions
Please answer the user message using the context above.
User message: What is my name?
AI message:
```
The model answers correctly from a few dozen tokens instead of 3,000 messages.

The same flow on the "Unicorn Enterprises" employee handbook: chunk it at 100 tokens with 20 overlap. `vector_search("do we get free unicorn rides?")` returns the perks chunk ("unlimited unicorn rides…", L2 distance 0.33). `search_and_chat` then wraps the results as `Context: … Answer the question: …` under a system message that says "use only the context… if you don't know say 'I don't know'". Swap `vector_search` for `pinecone_vector_search` (`index.query(vector=xq, top_k=k, include_metadata=True)`) and the chatbot runs the same way on a hosted index (cosine score 0.84).

## Key Takeaways
1. Vector search retrieves by meaning. RAG puts those retrievals into the prompt as context, which reduces hallucinations and token cost.
2. Most of the craft is in how you load documents and chunk them. Balance specificity against preserved meaning, and use overlap.
3. Retrieval is capped by the embedding model: its dimensions, cutoff, biases and domain coverage. Never mix models within one index.
4. Persist vectors, because they only change when the model changes. FAISS works locally, and Pinecone and similar services give you managed scale at the cost of money, lock-in and privacy exposure.
5. Metadata is a second retrieval axis. Filter on it directly, or let a Self-Querying retriever (at temperature 0) extract filters from natural language.
6. Choose retrievers by trade-off and test that the added context justifies the added cost and latency.

## Connects To
- **Ch 1**: RAG applies Give Direction (dynamic context), chunking applies Specify Format, and self-query at temperature 0 applies Evaluate Quality.
- **Ch 2**: context-window limits and token pricing are why retrieval beats prompt stuffing.
- **Ch 4**: LCEL chains, prompt templates and document loaders/splitters are reused here for RAG.
- **Ch 6**: vector stores become an agent's long-term memory and a retrieval tool.
- **Ch 10**: the RAG pipeline is a core building block of production AI applications.
- **Hybrid search / BM25**: the dense+sparse combination mentioned here is standard practice in search engineering.
