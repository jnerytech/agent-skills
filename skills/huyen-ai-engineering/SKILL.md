---
name: huyen-ai-engineering
description: "Knowledge base from \"AI Engineering: Building Applications with Foundation Models\" by Chip Huyen. Use when applying Huyen's frameworks for foundation-model apps, evaluation, prompt engineering, RAG, agents, finetuning, dataset engineering, inference optimization, and AI architecture — studying the book or referencing its concepts."
---

<!-- argument-hint: [topic, framework name, or chapter number] -->

# AI Engineering: Building Applications with Foundation Models
**Author**: Chip Huyen | **Pages**: ~430 (O'Reilly, 2025) | **Chapters**: 10 | **Generated**: 2026-06-26

## How to Use This Skill

- **Without arguments** — load core frameworks below for reference
- **With a topic** — ask about `RAG`, `finetuning`, `evaluation`, `inference`, `prompt injection`; I find and read the relevant chapter
- **With chapter** — ask for `ch07`; I load that specific chapter file
- **Browse** — ask "what chapters do you have?" for the full index

When you ask about a topic not in Core Frameworks below, I read the relevant chapter file before answering.

---

## Core Frameworks & Mental Models

**The Adaptation Ladder (the book's spine).** Adapt a foundation model cheap-to-expensive: **prompt engineering → +examples (few-shot) → RAG (BM25 first) → finetuning / advanced RAG → combine**. Always build an evaluation pipeline *first*. Climb only when the current rung fails to hit your usefulness threshold.

**Finetuning vs RAG — "form vs facts".** Diagnose the failure type before adapting:
- Failures are **information-based** (wrong/outdated/missing facts) → **RAG**. Finetuning can't reliably add knowledge and may worsen it.
- Failures are **behavior-based** (format, syntax, relevance, safety, style) → **finetuning**. You're tuning form, not facts.
- Both → start with RAG (no data curation/hosting, often bigger boost); combine later.

**Three Layers of the AI Stack.** Application development / model development / infrastructure. Start at the top (app) and descend only as needed.

**Evaluation-Driven Development.** Define evaluation criteria *before* building (TDD analog). Evaluation is the hardest and most underrated part of AI engineering; most failures are evaluation failures. Beware the **lamppost trap** — easy-to-measure ≠ valuable.

**Model Selection Workflow (4 steps).** Filter on hard attributes (privacy, latency, license) → narrow via public benchmarks (a filter for *bad* models, not a selector for the *best* — they saturate and are contaminated) → run your own eval pipeline → monitor in production. Iterative.

**Build vs Buy (7 axes).** Privacy, data lineage/copyright, performance, functionality (scope/control), API-vs-engineering cost, control/transparency, on-device. If AI poses an existential (business-continuity) threat → build in-house; else prefer buy.

**Sampling controls model behavior.** Outputs are *probabilistic*: temperature/top-k/top-p/min-p reshape the next-token distribution. Low temperature (→0, greedy) = consistency; ~0.7 = creativity. Hallucination is intrinsic to sampling, not a bug to fully eliminate.

**Test-time compute.** Sample N outputs (best-of-N, beam search, self-consistency majority vote) and select via logprob/verifier. A small model + verifier can rival ~30× scale — but gains reverse past a point (adversarial outputs fool the verifier).

**The Three Evaluation Approaches.**
1. **Functional correctness** (pass@k) — execute against test cases; for measurable objectives (code, SQL).
2. **Similarity to reference** — exact / lexical (BLEU, ROUGE) / semantic (BERTScore).
3. **AI-as-a-judge** — fast, cheap, reference-free, but subjective; pin model+prompt or scores become incomparable over time. Use classification/discrete scoring over continuous.
- And **comparative evaluation** (Elo / Bradley–Terry) when you only need "which model is better" — comparing is easier than scoring and never saturates.

**Prompt Engineering essentials.** In-context learning (zero/few-shot) teaches behavior with no weight update. Split **system prompt** (dev instructions, prioritized) from **user prompt**. **Chain-of-thought** and **prompt decomposition** raise accuracy and debuggability. **Instruction Hierarchy** (system > user > model > tool output) is the defense model against prompt injection. Track **both** violation rate and false-refusal rate.

**RAG retrieval.** Retriever quality is everything. **Term-based** (BM25) for exact keywords/IDs and a cheap fast baseline; **embedding-based** (ANN over a vector DB) for semantic queries; **hybrid** (sequential rerank, or parallel fused with RRF) for both. Chunk, then optionally **rerank** and use **contextual retrieval**.

**Agents.** An agent = AI planner + tools acting over an environment. **Decouple planning from execution** and validate the plan before running. Per-step errors compound (95%^10 ≈ 60%) → use stronger models for many-step tasks. **Gate write actions** (DB/email/transfer) behind human approval.

**PEFT / LoRA / QLoRA.** When memory or data is limited: freeze base weights, train tiny low-rank modules (LoRA: W' = W + (α/r)·AB; no inference latency when merged). QLoRA = 4-bit NF4 base + paged optimizers (65B on one 48GB GPU). Quantize the base, not the adapter. Serve one base + many adapters.

**Dataset Engineering: quality, coverage, quantity.** The three criteria of data curation. Data-centric beats model-centric for app builders. Synthesize data (rule-based → simulation → AI-powered) for quantity/coverage/privacy/distillation — but **mix in real data** to avoid **model collapse**. The **data flywheel** (user data → better model → more users) is the moat.

**Inference Optimization.** Separate **latency** (TTFT + TPOT×tokens) from **throughput/goodput** (requests/s meeting SLO). Classify ops **compute-bound vs memory-bandwidth-bound** (roofline) to pick the fix. Levers: quantization, **continuous batching**, **prompt caching**, **KV-cache** reduction (GQA/MQA, PagedAttention), **speculative decoding**, prefill/decode decoupling, tensor parallelism. Report p50/p90/p95/p99, never the average.

**Gradual AI Architecture (5 steps).** Onto the bare `query → model → response` baseline, add in order: **context construction → guardrails (input/output) → model router + gateway → cache (exact/semantic) → agentic patterns**. Add a component only when its problem appears. Build without an orchestrator first.

**User Feedback & the flywheel.** Design feedback collection (when + how) to be nonintrusive across the user journey. Explicit (solicited) vs implicit (inferred from action). Audit for **degenerate feedback loops** (predictions shape feedback shapes next model → sycophancy, filter bubbles) before training on it.

---

## Chapter Index

| # | Title | Key Frameworks |
|---|-------|----------------|
| [ch01](chapters/ch01-introduction-foundation-models.md) | Introduction to Building AI Applications with Foundation Models | Three Layers of the AI Stack, Adaptation Ladder, Use-Case Evaluation, Crawl-Walk-Run, last-mile challenge |
| [ch02](chapters/ch02-understanding-foundation-models.md) | Understanding Foundation Models | Chinchilla scaling, post-training (SFT→RLHF), sampling strategies, test-time compute, structured outputs |
| [ch03](chapters/ch03-evaluation-methodology.md) | Evaluation Methodology | Perplexity/cross-entropy, functional correctness (pass@k), similarity metrics, AI-as-judge, comparative eval |
| [ch04](chapters/ch04-evaluate-ai-systems.md) | Evaluate AI Systems | Evaluation-Driven Development, Model Selection Workflow, Build vs Buy, Evaluation Pipeline, SAFE/SelfCheckGPT |
| [ch05](chapters/ch05-prompt-engineering.md) | Prompt Engineering | In-context learning, system/user prompt, chain-of-thought, decomposition, Instruction Hierarchy, injection defense |
| [ch06](chapters/ch06-rag-and-agents.md) | RAG and Agents | RAG, term/embedding/hybrid retrieval, RRF, reranking, agents, ReAct, Reflexion, function calling |
| [ch07](chapters/ch07-finetuning.md) | Finetuning | Finetuning-vs-RAG, adaptation ladder, PEFT, LoRA, QLoRA, model merging, memory math |
| [ch08](chapters/ch08-dataset-engineering.md) | Dataset Engineering | Quality/coverage/quantity, data flywheel, data synthesis taxonomy, curriculum bootstrapping, model collapse |
| [ch09](chapters/ch09-inference-optimization.md) | Inference Optimization | Roofline/arithmetic-intensity, TTFT/TPOT, KV cache, continuous batching, speculative decoding, prompt caching |
| [ch10](chapters/ch10-architecture-user-feedback.md) | AI Engineering Architecture and User Feedback | Gradual AI Architecture, guardrails, model gateway, caching, feedback design, degenerate loops |

## Topic Index

- **Agents / ReAct / Reflexion** → ch06
- **AI-as-a-judge** → ch03, ch04
- **Benchmarks / leaderboards / contamination** → ch03, ch04
- **Build vs buy / model selection** → ch04
- **Caching (exact/semantic/prompt)** → ch09, ch10
- **Chain-of-thought** → ch05
- **Chinchilla / scaling laws** → ch02
- **Data flywheel** → ch08, ch10
- **Data synthesis / augmentation / model collapse** → ch08
- **Dataset curation (quality/coverage/quantity)** → ch08
- **Evaluation metrics (perplexity, BLEU, pass@k)** → ch03
- **Evaluation pipeline / criteria** → ch03, ch04
- **Finetuning vs RAG** → ch07
- **Function calling / tools** → ch06
- **Guardrails / PII masking** → ch10
- **Hallucination** → ch02, ch03
- **In-context learning (zero/few-shot)** → ch05
- **Inference optimization / latency (TTFT, TPOT)** → ch09
- **Instruction hierarchy** → ch05
- **KV cache / batching / speculative decoding** → ch09
- **LoRA / QLoRA / PEFT** → ch07
- **Model gateway / router** → ch10
- **Observability / drift / tracing** → ch10
- **Post-training / SFT / RLHF** → ch02
- **Prompt engineering** → ch05
- **Prompt injection / jailbreaking** → ch05, ch10
- **Quantization** → ch07, ch09
- **RAG / retrieval (BM25, embedding, hybrid)** → ch06
- **Reranking / RRF / contextual retrieval** → ch06
- **Sampling (temperature, top-k, top-p)** → ch02
- **Structured outputs** → ch02, ch05
- **Test-time compute / best-of-N / self-consistency** → ch02
- **Tokenization / attention / MoE** → ch02
- **User feedback (explicit/implicit, degenerate loops)** → ch10

## Supporting Files

- [glossary.md](glossary.md) — all key terms with definitions
- [patterns.md](patterns.md) — all techniques and design patterns
- [cheatsheet.md](cheatsheet.md) — decision rules, thresholds, and quick-reference tables

---

## Scope & Limits

Covers the book content only (foundation-model *application* engineering — not model pre-training from scratch). For hands-on implementation in your codebase, combine with project tools. For topics beyond this book, check related skills or ask directly.
