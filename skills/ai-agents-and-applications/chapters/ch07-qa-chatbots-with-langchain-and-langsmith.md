# Chapter 7: Q&A chatbots with LangChain and LangSmith

## Core Idea
A LangChain Q&A application splits cleanly into two stages — content ingestion (indexing) and retrieval-and-generation (Q&A) — and a stateless RAG chain becomes a real chatbot only once you thread chat message history through the prompt and can inspect the whole thing with LangSmith tracing.

## Frameworks Introduced
- **Two-stage Q&A object model**: the ingestion stage (Loader → Document → TextSplitter → Embeddings → VectorStore) is decoupled from the retrieval-and-generation stage (VectorStore → Retriever → Embeddings → PromptTemplate → LanguageModel); both share the `VectorStore`/`Embeddings` abstractions but run at different times.
  - When to use: any time you're building RAG — treat "get content searchable" and "answer a question" as separate pipelines you can evolve independently.
  - How: ingestion — instantiate a `BaseLoader` per source type, pass its output through a `TextSplitter` (`Document -> list[Document]`), embed the chunks, `add_documents` to a `VectorStore`. Retrieval — call `vector_db.as_retriever()`, feed retrieved context + question into a `PromptTemplate`, invoke a chat model.
- **LCEL (LangChain Expression Language) chain composition**: chains are built by piping a dict of `Runnable`s into a prompt into a model: `{"context": retriever, "question": question_feeder} | rag_prompt | chatbot`.
  - When to use: whenever you need to wire retriever + prompt + LLM (and later, memory) into one invokable pipeline instead of hand-crafting prompts per call (contrast with the manual approach in chapter 5).
  - How: every component implements the `Runnable` interface and accepts a dict; `RunnablePassthrough` feeds a value through unchanged (e.g., the raw question); `RunnableLambda` wraps a plain function (e.g., fetching chat history) as a chain step.
- **Conversational memory via ChatMessageHistory + ChatPromptTemplate**: replace the plain `PromptTemplate.from_template` with `ChatPromptTemplate.from_messages`, add a `{chat_history_messages}` placeholder, and maintain a `ChatMessageHistory` object that is appended to after every turn.
  - When to use: as soon as follow-up questions need to resolve pronouns/references ("what did *they* do next?") against prior turns.
  - How: `add_user_message()` / `add_ai_message()` after each `chain.invoke()`; feed `chat_history_memory.messages` (via `RunnableLambda`) into the chain's dict input on every call.

## Key Concepts
- **Document**: LangChain's model for text content plus metadata (e.g., `source`).
- **BaseLoader**: loads text from an external source (Wikipedia, DOCX, PDF, TXT, a whole folder) into `Document` objects.
- **TextSplitter**: a `DocumentTransformer` with signature `Document -> list[Document]`; `RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)` splits on semantic boundaries.
- **Deduplication (removing duplication)**: extracting the repeated load→split→embed→store sequence into one `split_and_import(loader)` function instead of copy-pasting it per loader.
- **DirectoryLoader**: a third-party (Unstructured) loader that ingests every matching file in a folder via a glob pattern (`**/*.{docx,pdf,txt}`) instead of instantiating one loader per file/type.
- **Retriever**: computes the query's embedding and returns the most similar stored chunks (`vector_db.similarity_search(query, k)` or `vector_db.as_retriever()`).
- **Chat message roles**: `"system"` (persona, set once at startup), `"human"` (user question), `"ai"` (LLM response); custom roles like `"context"`/`"chat_history"` carry auxiliary info but aren't persisted to history.
- **ChatMessageHistory**: LangChain class holding accumulated turns; exposes `.messages`, `add_user_message()`, `add_ai_message()`.
- **LangSmith tracing**: records inputs/outputs at every chain step (retriever, prompt formatting, LLM call) inside a "project," letting you inspect exactly what was retrieved and generated per run.
- **Project (LangSmith)**: the collection of all traces belonging to an application or part of one.

## Mental Models
- **Ingestion is offline, retrieval is online**: don't conflate "make content searchable" (batch, done once/periodically) with "answer this question" (per-request); they have different failure modes and different components to swap out (loader/splitter vs. retriever/prompt/model).
- **Everything is a Runnable dict pipeline**: think of a RAG chain as `{inputs} | prompt | model`, where each key in the input dict is itself a `Runnable` (retriever, passthrough, lambda) — memory is just one more key (`chat_history_messages`) feeding that dict.
- **A chatbot without history is just a stateless Q&A engine**: the presence/absence of `ChatMessageHistory` is the dividing line between "answers one question" and "sustains a conversation" — same retriever and model, different capability.
- **Trace before you trust**: when a chain's output looks wrong, don't guess — open the LangSmith trace and look at what the retriever actually returned versus what the prompt/model did with it.

## Anti-patterns
- **Re-implementing the same loader→split→embed→store block per source**: duplicated ingestion code drifts and is error-prone; extract a `split_and_import(loader)` helper (or use `DirectoryLoader`/a loader factory keyed by file extension) instead.
- **Feeding a stateless chain follow-up questions**: without `ChatMessageHistory`, pronouns like "they"/"it" in follow-ups resolve to nothing, producing answers from unrelated retrieved chunks (e.g., the chain answering about Sirens instead of Romans).
- **Persisting system/context messages into chat history**: only `"human"` and `"ai"` turns need tracking — system instructions and retrieved context are already reinjected fresh each call and add no information if stored.
- **Unbounded chat history growth**: letting `chat_history_memory.messages` grow every turn with no cap eventually blows the token budget; use a sliding window (last N turns) or periodic summarization instead.
- **Manually crafting prompts per call instead of using a chain**: bypasses LangChain's `PromptTemplate`/LCEL abstractions and makes it harder to swap vector stores, embedding models, or LLMs later.

## Code Examples
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=0)
embeddings_model = OpenAIEmbeddings(
    openai_api_key=OPENAI_API_KEY)
vector_db = Chroma("tourist_info", embeddings_model)

def split_and_import(loader):
    chunks = text_splitter.split_documents(loader.load())
    vector_db.add_documents(chunks)
    print(f"Ingested chunks created by {loader}")
```
- **What it demonstrates**: deduplicated ingestion — one splitter/embeddings/vector_db setup, one helper reused for every loader (Wikipedia, DOCX, PDF, TXT).

```python
rag_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """You are a helpful assistant, world-class expert in
         Roman and Greek history..."""),
        ("placeholder", "{chat_history_messages}"),
        ("assistant", "{retrieved_context}"),
        ("human", "{question}"),
    ])
retriever = vector_db.as_retriever()
question_feeder = RunnablePassthrough()
chatbot = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model_name="gpt-5-nano")
chat_history_memory = ChatMessageHistory()

def get_messages(x):
    return chat_history_memory.messages

rag_chain = {
    "retrieved_context": retriever,
    "question": question_feeder,
    "chat_history_messages": RunnableLambda(get_messages)
} | rag_prompt | chatbot

def execute_chain_with_memory(chain, question):
    chat_history_memory.add_user_message(question)
    answer = chain.invoke(question)
    chat_history_memory.add_ai_message(answer)
    print(f'Full chat message history: {chat_history_memory.messages}\n\n')
    return answer
```
- **What it demonstrates**: the complete memory-enabled RAG chain (Listing 7.4) — message-based prompt, retriever + passthrough + history all feeding the chain, and history updated on every turn.

```python
folder_path = "CilentoTouristInfo"
pattern = "**/*.{docx,pdf,txt}"
directory_loader = DirectoryLoader(folder_path, pattern)
split_and_import(directory_loader)
```
- **What it demonstrates**: bulk ingestion of a whole folder with `DirectoryLoader` instead of per-file loaders.

## Reference Tables
**Table 7.1 — Chat message roles**

| Role | Description | Sample message |
|---|---|---|
| `"system"` | Represents the chatbot application; one message created at startup to set persona | "You are a world-class expert in Roman and Greek history... recommend places to visit with knowledgeable and engaging answers." |
| `"human"` | A message from the user, typically a question | "Can you please recommend some attractions around Paestum...?" |
| `"ai"` | Synthesized response from the LLM | "The best attractions in Paestum are the three Greek temples built around 500 BC." |
| Custom | Nonstandard roles for auxiliary info, e.g., `"context"` (retrieved text) or `"chat_history"` (full history) | — |

**Table 7.2 — ChatMessageHistory convenience methods**

| Role | Convenience method |
|---|---|
| Human | `add_user_message(user_question)` |
| AI | `add_ai_message(llm_response)` |

## Worked Example
Building the Paestum Q&A chatbot end to end:

1. **Ingest**: instantiate `RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)`, `OpenAIEmbeddings`, and `Chroma("tourist_info", embeddings_model)`. Load Paestum content from Wikipedia (`WikipediaLoader`), DOCX (`Docx2txtLoader`), PDF (`PyPDFLoader`), and TXT (`TextLoader`), each run through `split_and_import(loader)`, which splits and calls `vector_db.add_documents(chunks)`.
2. **Sanity-check retrieval**: `vector_db.similarity_search("Where was Poseidonia and who renamed it to Paestum?", 4)` returns the 4 closest chunks, confirming results are pulled from multiple sources (Britannica DOCX and Wikipedia) — proof the ingestion/chunking strategy works across documents.
3. **Build the stateless RAG chain**: pull/define `rag_prompt` (context + question template), `retriever = vector_db.as_retriever()`, `question_feeder = RunnablePassthrough()`, `chatbot = ChatOpenAI(model_name="gpt-5-nano")`, then `rag_chain = {"context": retriever, "question": question_feeder} | rag_prompt | chatbot`. Asking "Where was Poseidonia and who renamed it to Paestum? Also tell me the source." returns a correct, sourced answer.
4. **Expose the memory gap**: the deliberately vague follow-up "And then, what they do?" fails — the stateless chain has no idea "they" means the Romans and answers about an unrelated Sirens passage instead.
5. **Add memory**: switch to `ChatPromptTemplate.from_messages` with a `{chat_history_messages}` placeholder, instantiate `ChatMessageHistory()`, and rebuild the chain as `{"retrieved_context": retriever, "question": question_feeder, "chat_history_messages": RunnableLambda(get_messages)} | rag_prompt | chatbot`. Wrap invocation in `execute_chain_with_memory`, which calls `add_user_message` before and `add_ai_message` after each `chain.invoke()`.
6. **Verify**: re-ask the original question (correct answer, now also recorded in `chat_history_memory.messages`), then re-ask the same vague follow-up "And then what did they do?" — this time the chain correctly resolves "they" to the Romans and answers about post-conquest development of the city, because the full turn history is now injected into the prompt.
7. **Trace it**: set `LANGSMITH_TRACING=true`, `LANGSMITH_ENDPOINT`, `LANGSMITH_PROJECT=Q & A chatbot`, and `LANGSMITH_API_KEY` as environment variables before restarting the notebook. Every chain invocation now appears as a trace in the LangSmith dashboard (Projects > Q&A Chatbot), showing left panel (all traces), middle panel (per-run steps: retriever, ChatOpenAI call, with durations), and right panel (input question / output answer) — click the Retriever run to see the exact query and retrieved documents.

## Key Takeaways
1. Separate ingestion (indexing) from retrieval-and-generation — they're different pipelines with different components and different swap points (loader/splitter vs. retriever/prompt/model).
2. Extract a shared `split_and_import(loader)` helper (or use `DirectoryLoader`) rather than duplicating load→split→embed→store per file type.
3. LCEL chains are dicts of `Runnable`s piped into a prompt into a model — memory is just another dict key, not a special mechanism.
4. A chatbot needs `ChatMessageHistory` (or equivalent) to resolve follow-up references; without it, it's a stateless Q&A engine that fails on pronouns like "they."
5. Only persist `"human"` and `"ai"` turns to history — system and context messages are reconstructed fresh each call.
6. Always sanity-check retrieval directly (`similarity_search`) before trusting the full chain's generated answer.
7. LangSmith tracing (input/output per chain step, organized into projects) is the fastest way to debug why a RAG chain retrieved or answered incorrectly.

## Connects To
- **Ch 5**: manual RAG prompt construction with the OpenAI client directly, contrasted here with LangChain's chain-based approach.
- **Ch 4**: the research summarization engine, suggested as a more complex chain to trace in LangSmith.
- **Ch 8**: advanced indexing techniques (chunk size/overlap tuning, hierarchical/multimodal indexing, multi-vector retrieval, query rewriting, routing, reranking) — the natural next step after this chapter's basic chunking and single-vector-store retrieval.
- **Vector stores**: this chapter uses Chroma; the `VectorStore` abstraction generalizes to Pinecone, FAISS, Weaviate, etc.
