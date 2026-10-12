# Chapter 3: Amazon Bedrock Glossary - A Reference for AI Engineers and Architects

## Core Idea
Read Amazon Bedrock as six layers: Foundation Models → Inference → API Surface → Higher-level Surfaces (Knowledge Bases, Guardrails, Agents, Flows) → AgentCore (a parallel bring-your-own-agent runtime) → Customization and Evaluation. Most design decisions come down to choosing the right inference mode, API, retrieval knobs, and safety layer, and to knowing which surfaces are being retired.

## Frameworks Introduced
- **Six-layer component map**: the typical request path is *Application → API Surface → Inference → Foundation Model*, with Knowledge Bases, Guardrails and Agents attached to the same `Converse` call. AgentCore is reached when a custom agent built outside Bedrock Agents calls back into the same API surface. Customization and Evaluation is offline tooling. MCP, A2A and Watermark span layers.
- **Cost-control levers**: Provisioned Throughput (higher idle cost for lower per-token cost at steady high utilization), Application Inference Profile (tag traffic for cost allocation), Batch Inference (give up real-time latency for discounts), Prompt Caching (cache a stable prefix), `maxTokens` (hard cap on runaway generation), Model Distillation (cheaper student model).
- **Production grounded-answer recipe**: Knowledge Base (RAG) + **Reranker** (retrieval precision) + **Contextual Grounding Check** in a Guardrail (reject ungrounded output).
- **Chunking ladder**: start fixed-size (~300 tokens, ~20% overlap). Move to semantic when there are clear semantic boundaries, to hierarchical when retrieval must span fine and coarse granularity (long manuals), and to no-chunking only for short, self-contained docs. Always pair the choice with an evaluation set.

## Key Concepts
- **Foundation Model / Base Model / Custom Model**: every model reachable via `InvokeModel`/`Converse` is an FM. A base model has provider weights. A custom model carries your weights, produced either by a customization job (served via Provisioned Throughput) or by **Custom Model Import** (on-demand).
- **Model Lifecycle**: Active → Legacy → EOL. **Ignoring a deprecation notice is the most common cause of Bedrock production outages**.
- **Inference Profile**: an identifier that enables **Cross-Region Inference** while keeping data inside the profile's geography (a US profile stays in US Regions).
- **TPM / RPM**: per-model, per-Region account quotas. TPM is the dominant constraint for high-traffic LLM workloads. RPM bites first on small requests such as classification and embeddings.
- **Converse API**: the model-agnostic chat API (messages, `system`, tool use, multimodal `content` blocks of type `image`/`document`/`video`). It is the recommended default because you can swap models without rewriting code.
- **Tool Use** = Bedrock's name for function calling. The model returns a structured `toolUse` block, the app executes the tool and returns the result.
- **Metadata Filter**: a boolean constraint on chunk metadata (`equals`, `greaterThan`, `in`, `stringContains`, `startsWith`; combined with `andAll`/`orAll`). It is the standard mechanism for multi-tenant RAG, recency-aware retrieval, and document-class access control. **Implicit Metadata Filtering** lets Claude generate the filter from a metadata schema.
- **Guardrail**: a named, versioned bundle of content filters, denied topics, word filters, sensitive-information (PII and regex) filters, contextual grounding check, and prompt-attack filter. It checks both input and output in one round trip.
- **Bedrock Agent**: model + Action Groups (an OpenAPI schema or function definitions bound to Lambda or Return of Control) + optional KB + orchestration loop, invoked via `InvokeAgent`. **Renamed Amazon Bedrock Agents Classic on 2026-06-30 and closed to new customers since 2026-07-30**. AWS points to AgentCore instead.
- **AgentCore Identity**: brokers on-behalf-of-user and machine-to-machine credentials (e.g., Cognito JWT → downstream OAuth token, scoped temporary AWS credentials), so no secrets live in agent code.

## Mental Models
- **`InvokeModel` vs `Converse`**: use `Converse`/`ConverseStream` for chat (one schema across Claude, Llama, Nova, Mistral). Use `InvokeModel` for provider-specific parameters and for non-chat models (image, video, embedding). Opt into streaming with `InvokeModelWithResponseStream`/`ConverseStream` to reduce perceived latency.
- **Inference Profile vs Application Inference Profile**: the first is AWS-defined and used for cross-region routing. The second is customer-defined and tagged so cost can be allocated per app or tenant in Cost Explorer and Budgets.
- **Bedrock Agents vs AgentCore Runtime**: managed orchestration (Action Groups + OpenAPI + an out-of-the-box loop, now Classic and closed to new customers) vs bring-your-own framework, planner and long-running stateful agents on managed microVMs.
- **Multi-Agent Collaboration vs A2A**: the first is a managed Supervisor → Collaborators pattern inside Bedrock (only the Supervisor receives `InvokeAgent`, and Collaborators are opaque to users). A2A extends collaboration across team, vendor and organization boundaries.
- **Content Filter vs Word Filter**: probabilistic harm categories with adjustable strength vs deterministic exact-match lists (brand names, product codes, profanity).
- **Guardrails vs model refusals**: Guardrails are an independent, customer-controlled layer that survives model swaps, so put application-specific rules there. Provider refusals still apply on top.
- **Customization choice**: use **fine-tuning** when you have curated prompt/completion pairs of the exact output you want. Use **continued pre-training** for a large domain-vocabulary gap (more data, heavier). Use **distillation** when a validated expensive model must get cheaper. Use **Custom Model Import** when training already happened elsewhere and you only need Bedrock for inference.
- **Embedding model choice fixes vector dimensionality**: changing it means re-embedding the whole corpus.

## Anti-patterns
- Pinning a model ID without tracking lifecycle and deprecation dates.
- Hard-coding production prompts in source code. Use **Prompt Management** (versioned, parameterized, A/B-testable without redeploy).
- Treating a wrong Action Group OpenAPI schema as a minor issue. It is the most common cause of failing Agent tool calls.
- A RAG app that still hallucinates while no Contextual Grounding Check is enabled.
- "Related-but-not-right" retrieval left unfixed. Adding a reranker is the most common single fix.
- Running steady high-volume traffic on On-Demand when it is throttled, or buying Provisioned Throughput for spiky low-volume traffic.

## Code Examples
Metadata filter shape for KB retrieval (operators named in the source):
```json
{"andAll": [
  {"equals": {"key": "category", "value": "policy"}},
  {"greaterThan": {"key": "epoch_modification_time", "value": 1700000000}}
]}
```
*What it demonstrates*: combining tenant or document-class scoping with recency inside a single `Retrieve`/`RetrieveAndGenerate` call.

## Reference Tables

**Six layers**
| Layer | Components | Role |
|---|---|---|
| 1 Foundation Models | Nova, Claude, Llama, Mistral, Cohere, AI21, Marketplace | provider weights behind one API |
| 2 Inference | On-Demand, Provisioned Throughput, Inference Profile (Cross-Region/Application), Batch | capacity and routing |
| 3 API Surface | `InvokeModel`/`InvokeModelWithResponseStream`, `Converse`/`ConverseStream` | runtime entry points |
| 4 Surfaces | Knowledge Bases, BDA, Guardrails, Agents, Flows/Studio/IDE/Prompt Management | managed retrieval, safety, orchestration, authoring |
| 5 AgentCore | Runtime, Memory, Gateway, Code Interpreter, Browser Tool, Identity, Observability | BYO-agent runtime |
| 6 Customization & Eval | Continued Pre-training, Fine-tuning, Distillation, Model Evaluation, LLM-as-a-Judge | offline adapt and benchmark |

**On-Demand vs Provisioned Throughput**
| Choose | When |
|---|---|
| Provisioned Throughput (terms: No commitment/hourly, 1 month, 6 months) | invoking a customization-job Custom Model; steady high utilization; need a guaranteed ceiling with no throttling |
| On-Demand | spiky, unpredictable or low-volume traffic |
| Batch (S3 in/out, async) | nightly summarization, evaluation runs, offline analytics |
| Latency-Optimized | interactive chat/voice; prioritizes TTFT and tokens/sec on selected models |

**Inference parameters**: `temperature` (typically 0.0–1.0, via `inferenceConfig`; low for extraction and structured output), `top_p`, Top-K (not on every model; use the model body or `additionalModelRequestFields`), `stopSequences`, `maxTokens` (input + `maxTokens` > context window → error).

**Knowledge Bases**: APIs are `Retrieve` and `RetrieveAndGenerate`. Data sources: S3, web crawler, Confluence, SharePoint, Salesforce, refreshed by asynchronous **Sync Jobs**. Vector stores: OpenSearch Serverless/Managed, S3 Vectors, Aurora PostgreSQL pgvector, Neptune Analytics, Pinecone, Redis Enterprise Cloud, MongoDB Atlas. Embedding models: Titan Embeddings, Cohere Embed. Rerankers: Amazon Rerank 1.0, Cohere Rerank 3.5. Chunking options: fixed, semantic, hierarchical, none. **BDA** turns documents, images, audio and video into structured JSON (IDP) as preprocessing ahead of KB ingestion.

**Custom Model Import**: architectures Llama, Mistral, Mixtral, Flan, GPTBigCode, Qwen2/2.5/3, GPT-OSS, Mllama. Served on demand via `InvokeModel` in `us-east-1`, `us-east-2`, `us-west-2`, `eu-central-1`.

**Model Evaluation**: automatic metrics (accuracy, F1, ROUGE, BERTScore), human evaluation, and LLM-as-a-Judge.

**Retired or moving surfaces**: Bedrock Studio is no longer available, and its capabilities moved to Amazon Bedrock in SageMaker Unified Studio. Bedrock IDE boundaries are still shifting. Bedrock Agents is now Classic and closed to new customers.

## Worked Example
**A hallucinating RAG app**: (1) check chunking against an evaluation set, starting from ~300-token fixed chunks with 20% overlap; (2) add a Reranker (Cohere Rerank 3.5 / Amazon Rerank 1.0) for related-but-wrong hits; (3) scope retrieval with a metadata filter (tenant, recency); (4) attach a Guardrail with a Contextual Grounding Check, which scores *grounding* and *relevance* and blocks low scores; (5) add a Prompt Attack Filter plus network-layer WAF for injection.

## Key Takeaways
1. Default to `Converse`. Drop to `InvokeModel` only for provider-specific parameters or non-chat models.
2. Use cross-region inference profiles to relieve TPM throttling, and application inference profiles to allocate cost.
3. Chunking strategy is the single largest determinant of RAG quality. A reranker is the highest-impact single fix.
4. Guardrails are model-independent policy. Encode application rules there, not only in prompts.
5. Track model lifecycle. Deprecations break `InvokeModel`/`Converse` calls outright.
6. For new agent work, use AgentCore. Bedrock Agents (Classic) is closed to new customers as of 2026-07-30.

## Connects To
- ch01 Beginner's Guide: the AgentCore layer in depth, and Bedrock Agent vs AgentCore.
- ch02 Agent Eng Glossary: vendor-neutral RAG, guardrail and evaluation terms.
- ch04 Impl Pt1 (Runtime/Memory/Code Interpreter) and ch05 Impl Pt2 (Identity/Gateway).
- ch07 Impl Pt4: multi-agent beyond Bedrock's Supervisor/Collaborator.
- ch10 Production ops: cost levers, quotas, DR. ch11 WAF: complements the Prompt Attack Filter.
