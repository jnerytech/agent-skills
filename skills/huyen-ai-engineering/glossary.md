# Glossary — AI Engineering (Chip Huyen)

**AI engineering** — building applications by *adapting* existing foundation models; focus is adaptation + evaluation, not training from scratch (Ch 1).
**AI-as-a-judge** — using a model+prompt to score outputs; fast, cheap, reference-free, but subjective (Ch 3, 4).
**ANN (approximate nearest neighbor)** — vector search (LSH/HNSW/IVF/PQ/Annoy) underlying embedding retrieval (Ch 6).
**Arithmetic intensity / roofline** — FLOPs-per-byte; classifies an op as compute-bound vs memory-bandwidth-bound (Ch 9).
**Attention** — Q·K dot products weight V vectors over prior tokens (Ch 2).
**Autoregressive vs masked LM** — predict next token (generation) vs fill blanks both sides (classification) (Ch 2).
**Back-translation** — translate output back and compare to verify synthetic data (Ch 8).
**Backpropagation** — forward + backward pass (loss → gradient → optimizer) (Ch 7).
**Behavior cloning** — SFT on (prompt, ideal response) pairs (Ch 2).
**BLEU / ROUGE** — lexical n-gram similarity to reference text (Ch 3).
**BPC / BPB** — bits-per-character / -byte; cross-entropy normalized for cross-tokenizer comparison (Ch 3).
**Catastrophic forgetting** — sequential multitask training erases earlier tasks (Ch 7).
**Chain-of-thought (CoT)** — prompt the model to reason step by step before answering (Ch 5).
**Chinchilla scaling law** — compute-optimal training: tokens ≈ 20 × params (Ch 2).
**Chunking** — splitting documents into retrievable units (Ch 6).
**Comparative evaluation** — rank models from pairwise win rates (Elo / Bradley–Terry / TrueSkill) (Ch 3).
**Completion machine** — mental model of an LM as a prompt-continuation predictor (Ch 1).
**Constrained sampling** — restrict tokens during generation to guarantee output format (Ch 2).
**Context construction** — "feature engineering for FMs": retrieval + tools assemble per-query info (Ch 5, 10).
**Context precision / recall** — % retrieved that is relevant / % relevant that is retrieved (Ch 6).
**Continued pre-training** — self-supervised finetuning on cheap in-domain data (Ch 7, 8).
**Continuous batching** — finished responses return immediately; new requests fill freed slots (Ch 9).
**Contextual retrieval** — augment chunks with metadata/AI context before indexing (Ch 6).
**Cross entropy** — difficulty of predicting data: H(P,Q) = H(P) + KL (Ch 3).
**Data augmentation** — new data derived from real data (Ch 8).
**Data contamination** — model trained on test/benchmark data (Ch 4).
**Data flywheel** — proprietary feedback → better model → more users → moat (Ch 8, 10).
**Data lineage** — provenance of data; obscured by AI generation (Ch 8).
**Data synthesis** — generating non-real data that mimics real properties (Ch 8).
**Deduplication** — removing whole/intra/cross-document duplicates (Ch 8).
**Degenerate feedback loop** — predictions shape feedback that shapes the next model, amplifying bias (Ch 10).
**Demonstration vs comparison data** — (prompt, response) for SFT vs (prompt, win, lose) for reward model (Ch 2).
**Drift** — silent change in prompts, user behavior, or the underlying model (Ch 10).
**Embedding-based retrieval** — semantic ranking via vector similarity / ANN (Ch 6).
**Entropy** — average information (bits) per token (Ch 3).
**Exact vs semantic caching** — reuse identical requests vs semantically-similar ones via embedding threshold (Ch 9, 10).
**Evaluation-driven development** — define eval criteria before building (TDD analog) (Ch 4).
**Few-shot / zero-shot** — in-context learning with / without examples (Ch 5).
**Finetuning** — adapting a model by updating weights (Ch 7).
**Foundation model** — large, general-purpose, often multimodal model built upon for many tasks (Ch 1).
**Full vs partial finetuning** — update all params vs some layers (Ch 7).
**Functional correctness (pass@k)** — execute output against test cases; fraction solved by any of k samples (Ch 3).
**Function calling** — model invoking declared tools (required / none / auto) (Ch 6).
**Goodput** — requests/s that meet the SLO (Ch 9).
**Guardrails (input/output)** — protection placed at each risk exposure; mask/block inputs, catch outputs (Ch 10).
**Hallucination** — ungrounded output arising from probabilistic sampling (Ch 2, 3).
**Hard vs soft attributes** — unchangeable (license, privacy) vs improvable model attributes (Ch 4).
**Hybrid search** — combine term + embedding retrieval (sequential rerank or parallel RRF) (Ch 6).
**Human-in-the-loop** — humans included in the AI decision process (Ch 1).
**In-context learning** — learning behavior from in-prompt examples, no weight update (Ch 5).
**Instruction hierarchy** — priority system > user > model > tool output; injection defense (Ch 5).
**Intent classifier / router** — small fast model routing queries to specialized/cheaper models (Ch 10).
**KV cache** — stored key/value vectors of prior tokens to skip recompute in decode; grows with seq len × batch (Ch 9).
**Last-mile challenge** — 0→60 is easy, 60→100 exceedingly hard (Ch 1).
**Logit / softmax / logprob** — raw score → probability → log-probability (Ch 2).
**LoRA** — W' = W + (α/r)·AB; freeze W, train low-rank A,B; no inference latency when merged (Ch 7).
**MoE (mixture of experts)** — sparse model, few experts active per token (Ch 2).
**MFU / MBU** — model FLOPs / memory-bandwidth utilization vs theoretical peak (Ch 9).
**Mixed precision** — high-precision weight copy with low-precision grads/activations (Ch 7).
**Model adaptation** — adjusting a model with or without weight updates (Ch 1).
**Model collapse** — recursive training on AI-generated data degrades models irreversibly (Ch 8).
**Model gateway** — unified secure layer to all models: central keys, access control, fallback, logging (Ch 10).
**Model merging** — combining models via summing (linear/SLERP), layer stacking, concatenation (Ch 7).
**Needle in a haystack (NIAH)** — long-context recall test; the middle is recalled worst (Ch 5).
**Observability** — inferring internal state from external outputs (metrics + logs + traces) (Ch 10).
**Open weight vs open model** — weights only vs weights + training data (Ch 4).
**Ossification** — pre-training freezing weights so they resist later finetuning (Ch 8).
**PEFT** — parameter-efficient finetuning: near-full quality, far fewer trainable params (Ch 7).
**Perplexity** — exp(cross entropy); effective branching factor; proxy for capability (Ch 3).
**Post-training** — SFT → preference finetuning that turns a completion model into an aligned assistant (Ch 2).
**Prefill / decode** — parallel input processing vs sequential token generation (Ch 2, 9).
**Prompt caching** — reuse overlapping prompt segments (e.g. system prompt) processed once (Ch 9).
**Prompt injection / jailbreaking** — injecting malicious instructions / subverting safety (Ch 5).
**Prompt perturbation / robustness** — output sensitivity to small prompt tweaks (Ch 5).
**Quantization** — converting weights/activations to fewer bits; PTQ is most common (Ch 7, 9).
**RAG (retrieval-augmented generation)** — supplement the prompt with retrieved external data (Ch 6).
**ReAct** — interleave Thought / Act / Observation until Finish (Ch 6).
**Reflexion** — separate evaluator + self-reflection to regenerate an agent trajectory (Ch 6).
**Reranking** — reorder/trim retrieved candidates with a precise scorer (Ch 6).
**RLHF** — train a reward model on comparisons, then PPO-optimize the SFT model (Ch 2).
**RRF (reciprocal rank fusion)** — fuse parallel rankings: Score = Σ 1/(k+rank), k≈60 (Ch 6).
**Sampling strategies** — temperature / top-k / top-p / min-p reshape the next-token distribution (Ch 2).
**Self-consistency** — majority vote across sampled outputs for exact-answer tasks (Ch 2).
**Self-supervision** — labels inferred from the input (next-token), enabling scale (Ch 1, 2).
**Simpson's paradox** — wins each slice yet loses overall; why you slice data (Ch 4).
**Speculative decoding** — fast draft model proposes K tokens; target verifies in parallel (Ch 9).
**Structured outputs** — guaranteeing output format via prompting/post-processing/constrained sampling/finetuning (Ch 2, 5).
**System vs user prompt** — dev instructions (prioritized) vs user input, joined by chat template (Ch 5).
**Task vector / delta parameters** — finetuned minus base weights; enables task arithmetic (Ch 7).
**Temperature** — scales logits before softmax; →0 deterministic, higher = more random (Ch 2).
**Tensor parallelism** — partition operator tensors across devices (intra-operator) (Ch 9).
**Test-time compute** — sample N outputs then select via verifier/logprob/vote (Ch 2).
**Textual entailment (NLI)** — entail / contradict / neutral relation (Ch 4).
**Token / tokenization** — basic unit (~¾ word for GPT-4); vocabulary = all model tokens (Ch 1).
**Transfer learning** — reusing knowledge across related tasks (Ch 7).
**TTFT / TPOT** — time to first token (prefill latency) / time per output token; total = TTFT + TPOT × tokens (Ch 9).
**Usefulness threshold** — minimum score worth shipping (Ch 4).
**Write actions** — outputs that change the environment; high capability and high risk (Ch 6, 10).
