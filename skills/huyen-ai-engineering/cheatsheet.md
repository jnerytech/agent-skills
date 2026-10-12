# Cheatsheet — AI Engineering (Chip Huyen)

## The one decision that matters most: how to adapt

| Symptom | Diagnosis | Do this |
|---|---|---|
| Wrong / outdated / missing **facts** | information-based failure | **RAG** (start BM25) |
| Bad **format / syntax / style / safety / relevance** | behavior-based failure | **Finetuning** |
| Both | — | RAG first (easier, often bigger boost), combine later |
| "Prompting doesn't work" | usually unsystematic prompting | Re-run **systematic prompt experiments** before anything |

**Adaptation ladder (cheap → expensive):** prompt → +few-shot → RAG → finetune/advanced-RAG → combine. Build the **eval pipeline first**. Climb only on failure.

## Sampling defaults

| Goal | Temperature |
|---|---|
| Consistency / extraction / classification | 0 (greedy) |
| Balanced | ~0.7 |
| Creativity | higher (watch incoherence) |
| AI-judge / reproducible eval | 0 |

- Multi-sample selection gains **reverse** past ~hundreds of samples (verifier fooled).
- Inference memory ≈ **2 bytes × params** (7B → ~14 GB).

## Evaluation

- Public benchmarks = filter for **bad** models, not selector for the **best** (saturated + contaminated).
- Executable objective → **functional correctness (pass@k)**.
- Open-ended, no reference → **AI-as-judge** (pin model+prompt; discrete scoring; temp 0).
- Only need "which is better" → **comparative** (Elo) — never saturates.
- Factual question → judge by **correctness**, not preference.
- Detecting a 3× smaller score gap → **10× more eval samples** (≈√10).
- Don't trust **perplexity** after post-training/quantization.
- **Lamppost trap**: easy-to-measure ≠ valuable.

## Build vs Buy / Model Selection

- Existential (business-continuity) risk → **build in-house**; else prefer **buy**.
- Data privacy forbids external data → **self-host** or privately-deployed API only.
- Pareto: fix non-negotiables (e.g. latency) as hard filters first, optimize the rest.

## RAG retrieval

| Need | Use |
|---|---|
| Exact keywords/IDs, cheap fast baseline | **BM25 / term-based** |
| Semantic, natural-language, finetunable | **embedding-based (ANN)** |
| Both | **hybrid** (sequential rerank or parallel RRF, k≈60) |
| Knowledge > context window, or per-user | **RAG** (long context is used poorly + costs tokens) |

## Agents

- Many steps → **stronger model** (errors compound: 95%^10 ≈ 60%).
- Risky/long task → **decouple plan from execution, validate before running**.
- Write action (DB/email/transfer) → **human approval gate**.
- Prefer **natural-language plans** (robust to tool-API changes).

## Finetuning memory levers

| Lever | Effect |
|---|---|
| Full FT (7B) | ~56 GB → exceeds consumer GPU |
| **LoRA** | train tiny low-rank modules; no inference latency when merged |
| **QLoRA** | 4-bit NF4 base + paged optimizers → 65B on one 48 GB GPU |
| Quantize **base, not adapter** | adapter memory is negligible |

- Little data → **PEFT/LoRA on a stronger model**. Large data → **full FT on a smaller model**.

## Dataset engineering

- Judge every dataset on **quality, coverage, quantity**.
- Synthetic data → **mix in real data** (pure recursion → model collapse).
- AI preference judge → ask twice with **swapped order**, keep consistent only (position bias).
- Distilling reasoning → **improve the base**, don't imitate (imitation = answer-shaped hallucinations).
- Annotate big? Finetune on **~50 examples first**; no lift → more rarely helps.

## Inference optimization

| Metric | Meaning | Report |
|---|---|---|
| **TTFT** | time to first token (prefill) | p50/p90/p95/p99 (never average) |
| **TPOT** | time per output token | total = TTFT + TPOT × tokens |
| **Goodput** | requests/s meeting SLO | the real throughput target |

- **Compute-bound** → more/faster chips. **Bandwidth-bound** → higher-bandwidth chips + quantization + KV-cache reduction.
- MFU already maxed → **skip speculative decoding** (no idle FLOPs).
- TPOT only needs to beat reading speed (~120 ms/token, 6–8 tok/s) → don't overspend.
- Long context → prioritize **KV-cache** opt (GQA/MQA, PagedAttention, windowed attention).
- Prefill/decode split ratio: 2:1–4:1 favors TTFT; 1:2–1:1 favors TPOT.

## Architecture & feedback (Ch 10)

- Build order: **context → guardrails → router/gateway → cache → agentic**. One component per problem.
- Start **without an orchestrator** (it hides internals, complicates debugging).
- **Don't cache** user-specific or time-sensitive queries (leak + staleness).
- Fear a specific failure → **design a metric for it** (untargeted metrics miss it).
- Latency tempting you to drop guardrails → **parallelize/stream**, don't remove.
- Comparative feedback → **never force a choice users can't evaluate**.
- Feedback drives updates → **audit for degenerate loops / bias first** (sycophancy, filter bubbles).
