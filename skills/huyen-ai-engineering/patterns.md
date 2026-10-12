# Patterns & Techniques — AI Engineering (Chip Huyen)

## Demo-First Workflow
**When**: starting any FM application.
**How**: build the product on an off-the-shelf model first; invest in data/finetuning/own models only once it shows promise.
**Trade-offs**: fast validation; may hit a quality ceiling that later forces deeper adaptation.

## Reframe-as-Completion
**When**: mapping a task onto an LM.
**How**: express translation/classification/summarization as text completion ("continue this…").
**Trade-offs**: unlocks one model for many tasks; output needs format enforcement.

## Self-Consistency (majority vote)
**When**: exact-answer tasks (math, multiple choice).
**How**: sample N outputs at temperature > 0, take the majority answer.
**Trade-offs**: large accuracy gains; N× cost.

## Verifier Selection / Best-of-N
**When**: a cheap verifier exists.
**How**: sample N, score each (logprob / verifier / reward model), keep the best. Small model + verifier ≈ ~30× scale.
**Trade-offs**: gains reverse past ~hundreds of samples (verifier gets fooled).

## Structured-Output Enforcement (5 layers)
**When**: outputs feed downstream code.
**How**: prompting → post-processing (script-fix common errors) → test-time → constrained sampling → finetuning. Post-processing alone took LinkedIn YAML 90% → 99.99%.
**Trade-offs**: finetuning/constrained = strongest guarantee but most effort.

## Functional-Correctness Evaluation (pass@k)
**When**: measurable objectives (code, SQL, games).
**How**: execute output against test cases; report fraction solved by any of k samples.
**Trade-offs**: gold-standard signal; needs an executable spec.

## AI-as-a-Judge (done right)
**When**: open-ended outputs, no reference, production.
**How**: pin model + prompt; use classification or narrow discrete scoring (not continuous); temperature 0; few-shot judge prompts raise consistency.
**Trade-offs**: cheap and scalable; subjective; self/position/verbosity bias — swap order and keep only consistent verdicts.

## Mix Cheap + Expensive Eval
**When**: large traffic, limited eval budget.
**How**: run a cheap classifier/heuristic on 100% of data, an AI judge on ~1%.
**Trade-offs**: high-quality signal at low cost; sampling adds variance.

## Bootstrap / Data Slicing
**When**: validating eval reliability and catching bias.
**How**: resample eval set with replacement to test stability; analyze per-subset to avoid Simpson's paradox.
**Trade-offs**: more compute; surfaces hidden failures.

## Prompt Decomposition & Chaining
**When**: a prompt bloats or needs multi-step reasoning.
**How**: break into subtask prompts chained together; use cheaper models per step.
**Trade-offs**: better accuracy/debuggability; added latency and orchestration.

## Defensive Prompting
**When**: the system can execute impactful actions.
**How**: duplicate the system prompt before and after user input; end-of-input marker; sandbox code; require human approval for DELETE/DROP; track violation + false-refusal rates.
**Trade-offs**: no prompt defense is foolproof — pair with execution gates.

## Hybrid Retrieval (sequential + RRF)
**When**: queries need both keywords and semantics.
**How**: cheap term fetch (BM25) then expensive vector rerank; or run both in parallel and fuse with RRF (Score = Σ 1/(k+rank), k≈60).
**Trade-offs**: best recall; two indexes to maintain.

## Contextual Retrieval / Reranking
**When**: chunks lose meaning out of context, or candidate set is noisy.
**How**: augment chunks with AI-generated context/metadata before indexing; rerank candidates with a precise scorer.
**Trade-offs**: better precision; extra indexing/inference cost.

## Plan–Execute Decoupling
**When**: agents on risky or long tasks.
**How**: generate a plan (prefer natural-language plans, robust to API changes), validate it (heuristics / AI judge) before executing; hierarchical planning for big tasks; gate write actions behind human approval.
**Trade-offs**: avoids burning time/credits; adds a validation step.

## Tool Ablation
**When**: an agent has many tools.
**How**: drop tools one at a time; remove those with no performance loss.
**Trade-offs**: smaller attack surface and prompt; risk of removing rare-but-critical tools.

## LoRA / QLoRA / Multi-Adapter Serving
**When**: memory/data limited, or serving many tasks.
**How**: freeze base, train low-rank A,B (LoRA); 4-bit NF4 base + paged optimizers (QLoRA); keep W, A, B separate to store 1 base + many adapters and hot-swap.
**Trade-offs**: ~full quality at a fraction of memory; merging removes latency but loses swap flexibility.

## Parallel-Then-Merge (multitask)
**When**: training one model for several tasks.
**How**: finetune separately per task, then merge (summing / SLERP / layer stacking).
**Trade-offs**: avoids catastrophic forgetting; merge quality varies.

## Verifiable Synthesis (Llama 3 coding pipeline)
**When**: real data is scarce.
**How**: generate data, then programmatically verify (linters, unit tests, back-translation); keep only what passes.
**Trade-offs**: scales coverage; only works where outputs are checkable.

## Curriculum Bootstrapping
**When**: high-quality data is limited.
**How**: pre-finetune on cheaper data first (self-supervised → supervised, less-relevant → relevant, synthetic → real).
**Trade-offs**: squeezes value from cheap data; extra training stages.

## Performance-Gain Curve (data sizing)
**When**: deciding how much data to annotate.
**How**: finetune on 25/50/100% subsets and extrapolate; finetune on ~50 examples before large annotation — if no lift, more rarely helps.
**Trade-offs**: cheap sizing signal; assumes the trend extrapolates.

## Inference Optimization Toolkit
**When**: latency/cost/throughput targets unmet.
**How**: quantization (weight-only most popular) → continuous batching → prompt caching (Anthropic: up to 90% cost / 75% latency cut) → KV-cache reduction (GQA/MQA, PagedAttention) → speculative decoding / inference-with-reference → prefill/decode decoupling → tensor parallelism.
**Trade-offs**: each targets a specific bottleneck — diagnose compute- vs bandwidth-bound first (roofline).

## Gradual AI Architecture
**When**: building any FM product.
**How**: start with `query → model → response`; add context construction → guardrails → router/gateway → cache → agentic, one component per problem that appears. Build without an orchestrator first.
**Trade-offs**: avoids premature complexity; refactor as you grow.

## Feedback-Design Patterns
**When**: collecting data for the flywheel.
**How**: nonintrusive feedback across the user journey; side-by-side comparison when model is low-confidence (never force a choice users can't evaluate); explicit + implicit signals; audit for degenerate loops before training.
**Trade-offs**: rich training data; raw feedback breeds sycophancy/filter bubbles if unaudited.
