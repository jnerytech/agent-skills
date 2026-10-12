# Chapter 10: AI Engineering Architecture and User Feedback

## Core Idea
Build an AI application as a gradual architecture — start with the simplest query→model→response loop and add components (context, guardrails, routing/gateway, caching, agentic patterns, observability, orchestration) only as concrete needs arise. Then close the loop with user feedback, which for AI apps is not just product signal but the fuel of the data flywheel.

## Frameworks Introduced
- **Gradual AI Architecture (5 steps)**: Layer components onto the bare query→model→response baseline as challenges surface.
  - When to use: designing/scaling any foundation-model product; deciding what to build next.
  - How: (1) Enhance context (retrieval + tools); (2) Put in guardrails (input + output); (3) Add model router + gateway; (4) Reduce latency/cost with caches; (5) Add agent patterns (loops + write actions). Then add observability and orchestration. Follow the order that fits your app.
- **Input/Output Guardrails**: Place protection wherever there is risk exposure.
  - When to use: external APIs (leak risk), prompt-hack exposure, any failure-prone output.
  - How: Input — detect/mask sensitive data (PII), block or mask+unmask via reverse PII map. Output — catch failures (quality: malformed, hallucinated, bad; security: toxic, leaks, code-exec, brand-risk) and define handling policy (retry, parallel redundant calls, human fallback).
- **Model Gateway**: Unified, secure intermediate layer to all models (self-hosted + commercial).
  - When to use: multiple models, multiple consuming apps, central cost/access control.
  - How: one wrapper interface; centralized API keys; fine-grained access control; usage limits/cost tracking; fallback on rate-limit/API failure; logging, load balancing, sometimes caching/guardrails.
- **Feedback Design (When + How)**: Collect feedback throughout the user journey without hurting UX.
  - When to use: any conversational/AI product needing the data flywheel.
  - How — When: at signup (calibration, optional), when something bad happens (downvote/regenerate/edit/human handoff), when model has low confidence (side-by-side comparison). How: nonintrusive, easy to ignore, easy to give; incentivize; explain data use; never ask the impossible; mind position/visibility (private vs public).

## Key Concepts
- **Context construction**: "Feature engineering for foundation models" — retrieval (text/image/tabular) + tools assemble the info a model needs per query.
- **Intent classifier / router**: Small fast model predicting query intent to route to specialized/cheaper models, decline out-of-scope, or ask for clarification.
- **Next-action predictor**: A router variant deciding the agent's next step (e.g., code interpreter vs search).
- **Exact caching**: Reuse stored result only for identical requests; needs eviction policy (LRU/LFU/FIFO) and TTL judgment.
- **Semantic caching**: Reuse results for semantically similar queries via embedding similarity + threshold; high value but fragile.
- **Write actions**: Model outputs that change the environment (send email, place order); greatly expand capability and risk.
- **Observability**: Stronger than monitoring — instrument so internal state is inferable from external outputs (metrics + logs + traces) without shipping new code.
- **Trace**: End-to-end recording of one request's execution path (steps, retrieved docs, final prompt, time, cost).
- **Drift**: Silent change in system prompt, user behavior, or underlying model (API unchanged, model updated).
- **Data flywheel**: Proprietary user feedback → better models → more users → more feedback; a durable competitive moat.
- **Explicit vs implicit feedback**: Explicit = directly solicited (thumbs, stars); implicit = inferred from actions (abundant but noisy).
- **Degenerate feedback loop**: Predictions shape feedback that shapes the next model, amplifying initial bias (exposure/popularity bias, sycophancy).

## Mental Models
- **Architecture is fluid, not fixed**: A capability (e.g., guardrails) can live in the inference service, the gateway, or standalone. Separate for modularity, but expect overlap.
- **Every component is a tax**: Each addition buys capability/safety/speed but adds complexity and new failure modes — only add when a real need forces it.
- **Evaluation and monitoring are one system**: Eval metrics must translate to monitoring metrics; monitoring issues feed back into the eval pipeline. Design metrics around the failures you fear.
- **Feedback is data, with all data's hazards**: It is user data (privacy, consent) and it is biased (leniency, position, recency, randomness) — interpret before acting.

## Anti-patterns
- **Skipping guardrails for latency**: The reliability-vs-latency trade-off is real, but dropping guardrails entirely exposes users; prefer parallel/streaming-aware designs.
- **Caching user-specific or time-sensitive queries**: Causes data leaks (User X's answer served to User Y) and stale results.
- **Reaching for an orchestrator on day one**: It abstracts away how your system works, making it harder to understand/debug; start without one.
- **Asking users to do the impossible**: Forcing a preference between two answers they can't evaluate (e.g., a math question) yields noisy feedback.
- **Treating feedback design as "just product"**: Engineers ignoring it starves the data flywheel; AI engineering sits closer to product than ML engineering did.
- **Acting on raw feedback indiscriminately**: Breeds sycophancy and filter bubbles via degenerate loops.

## Code Examples
Minimal model gateway (non-functional sketch): a Flask `/model` POST endpoint reads `model_type`, dispatches to `openai_model()` or `gemini_model()` wrappers (each calling its provider SDK with `model_name`, `input_data`, `max_tokens`), and returns a unified `{"response": ...}` JSON. Point: one interface, swap providers behind it, centralize keys/control.

## Reference Tables

| Step | Component | Problem it solves | Key risk added |
|------|-----------|-------------------|----------------|
| 1 | Context construction | Model lacks info | Retrieval/tool config complexity |
| 2 | Input/output guardrails | Leaks, attacks, bad output | Latency, false refusals |
| 3 | Router + gateway | Cost, specialization, mgmt | Extra hop |
| 4 | Exact/semantic cache | Latency, cost | Data leaks, stale/wrong hits |
| 5 | Agent patterns / write actions | Complex tasks, real effects | Large new attack/error surface |

| Feedback kind | Examples | Trait |
|---------------|----------|-------|
| Explicit | thumbs, stars, A/B vote | Clear, sparse, response-biased |
| NL (content) | early termination, "No, I meant…", edits, complaints, sentiment | Rich preference data (edit = winning response) |
| Other (action) | regeneration, delete/rename/share, #turns, dialogue diversity | Abundant, ambiguous |

Observability metrics: MTTD (detect), MTTR (respond), CFR (change failure rate). Latency: TTFT, TPOT, total. Bias types: leniency, randomness, position, recency, preference.

## Worked Example
A team ships a customer-support chatbot. **v0**: query → Model API → response (no augmentation, no guards). Hallucinations appear, so **v1** adds context construction — RAG over the help center plus a web-search tool. Employees start pasting private data and attackers probe prompts, so **v2** adds input guardrails (PII mask + reverse map before external calls) and output guardrails (catch malformed JSON, toxicity; retry on empty, parallel redundant calls to bound latency, hand off to a human when sentiment turns angry). Costs and query variety grow, so **v3** adds a router (intent classifier: password→FAQ, billing→human, tech→specialized model; declines out-of-scope) and a model gateway (unified interface, centralized keys, access control, fallback on rate limits). Repeated identical questions waste money, so **v4** adds exact caching (with a trained "is this cacheable?" classifier to avoid caching user-specific answers) and selective semantic caching. Finally **v5** adds agentic loops (re-retrieve when the task isn't done) and guarded write actions (open a ticket). Throughout, observability (metrics + logs + traces, MTTD/MTTR/CFR) and an orchestrator (defined components, chained steps, parallel router+PII) tie it together. User edits and "No, I meant…" turns feed the data flywheel.

## Key Takeaways
1. Don't design the full architecture up front — grow it one justified component at a time; complexity is a cost, not a default.
2. Guardrails belong wherever risk exists, on both input and output; balance reliability against latency rather than abandoning either.
3. A model gateway centralizes access, cost, and resilience; a router cuts cost and boosts quality by sending each query to the right (often smaller) model.
4. Cache aggressively but carefully — caching user-specific or time-sensitive answers leaks data; semantic caching only pays off at high hit rates.
5. Observability (not just monitoring) means instrumenting so failures are detectable and traceable; design metrics around the failures you most fear.
6. Conversational feedback (explicit, natural-language, action-based) is proprietary training data — design collection to be nonintrusive and bias-aware.
7. Feedback is biased and can form degenerate loops (sycophancy, filter bubbles); understand it before letting it shape the model.

## Connects To
- **Ch 6**: Context construction, RAG, tools, and agentic patterns (loops, write actions) are the techniques composed in Steps 1 and 5.
- **Ch 5**: Prompt attacks, defenses, security failures, and false-refusal rate underpin the guardrails of Step 2.
- **Ch 4**: Quality failures and silent model-version drift inform output guardrails and drift detection.
- **Ch 9**: Inference serving, KV/prompt caching, and latency metrics (TTFT/TPOT) sit beneath Steps 4 and observability.
- **Ch 8**: The data flywheel that user feedback fuels; preference data (query, winning, losing) for alignment.
- **Ch 3**: Embeddings and semantic similarity power semantic caching and AI-judge metrics.
- **Ch 1**: AI engineering moving closer to product — why engineers now own feedback design.
