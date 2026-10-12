# Chapter 2: Understanding Foundation Models

## Core Idea
Differences between foundation models trace back to four design decisions — training data, architecture, size, and post-training — and to sampling, the underrated probabilistic process that turns logits into outputs and explains hallucination, inconsistency, and many quality wins available with little effort.

## Frameworks Introduced
- **Chinchilla scaling law (compute-optimal training)**: Given a fixed compute (FLOP) budget, jointly optimize model size and dataset size.
  - When to use: Pre-training planning; deciding params vs. tokens under a budget.
  - How: Set training tokens ≈ 20× parameters (3B model → ~60B tokens); double tokens for every doubling of params; predicts optimal params/tokens and expected loss for a FLOP budget.
- **Post-training (SFT → preference finetuning)**: Two-step alignment on top of a pre-trained model.
  - When to use: After pre-training, to convert a completion model into a safe, conversational, preference-aligned one.
  - How: (1) SFT on (prompt, response) demonstration data → conversation behavior (behavior cloning); (2) preference finetuning via RLHF/DPO/RLAIF → align with human preference.
- **RLHF**: Reinforcement learning from human feedback to maximize human-preferred outputs.
  - When to use: When you need flexibility to tweak alignment beyond SFT.
  - How: (a) Train a reward model on comparison data (prompt, winning, losing) using sigmoid loss on score difference; (b) optimize the SFT model with PPO to maximize reward scores.
- **Sampling strategies (temperature, top-k, top-p, min-p)**: Shape the next-token probability distribution.
  - When to use: Tune creativity vs. determinism per task.
  - How: temperature divides logits before softmax (↑=creative, ↓=consistent, 0=greedy/argmax); top-k softmaxes over k best logits (50–500); top-p/nucleus keeps the smallest token set whose cumulative prob ≥ p (0.9–0.95); min-p sets a probability floor.
- **Test time compute (best-of-N, beam search)**: Sample multiple outputs at inference, then select the best.
  - When to use: Boost quality on hard or brittle queries when budget allows.
  - How: Generate N diverse outputs (vary sampling vars); select via highest average logprob, reward model/verifier, heuristics, or majority vote (self-consistency).
- **Structured outputs (5 layers)**: Force outputs into a required format.
  - When to use: Semantic parsing (text-to-SQL/regex), agentic tool inputs, JSON for downstream apps.
  - How (escalating): prompting → post-processing → test time compute (bandages); constrained sampling (grammar-filtered logits) → finetuning (most reliable, e.g., add a classifier head).

## Key Concepts
- **Foundation model design axes**: Training data, model architecture, model size, post-training — the root causes of model differences.
- **Attention mechanism**: Weighs importance of prior tokens via dot product of query (Q) and key (K) vectors, then weighted-sums value (V) vectors; usually multi-headed.
- **Prefill vs. decode**: Inference's parallel input-processing step vs. sequential one-token-at-a-time generation.
- **Mixture-of-experts (MoE)**: Sparse model split into expert parameter groups; only a few experts activate per token (e.g., Mixtral 8×7B: 46.7B params, 12.9B active).
- **Scale signals (3 numbers)**: Parameters (learning capacity), training tokens (how much learned), FLOPs (training cost).
- **Logit / softmax / logprob**: Raw per-token score; softmax converts logits to probabilities; logprob is log-scale probability (avoids underflow, sums for sequence probability).
- **Demonstration vs. comparison data**: (prompt, response) pairs for SFT; (prompt, winning, losing) triples for reward-model training.
- **Inverse scaling**: Cases where larger models do worse (memorization, strong priors; more alignment training reducing alignment).
- **Hallucination / inconsistency**: Ungrounded output; differing outputs for same/similar prompts — both rooted in probabilistic sampling.
- **Emergent abilities**: Capabilities present only at scale, unobservable in small models — degrade scaling extrapolation.

## Mental Models
- **Shoggoth with a smiley face**: Pre-training yields an untamed internet monster; SFT makes it socially acceptable; preference finetuning paints the smiley face.
- **Book-summary metaphor for attention**: Q = the summarizer seeking info; K = page numbers; V = page contents; high Q·K score → use more of that page.
- **Reading vs. applying knowledge**: Pre-training optimizes token-level accuracy (reading); post-training optimizes whole-response quality (using knowledge).
- **Verifier ≈ 30× model size**: A small model + verifier can match a model 30× larger — selection can substitute for scale.

## Anti-patterns
- **Translate-to-English round-trip for low-resource languages**: Needs a model that already understands the language and loses information (e.g., Vietnamese relational pronouns collapse to I/you).
- **Equating param count with capability**: Misleading for sparse/MoE models, or models undertrained on data.
- **Greedy sampling for generative tasks**: Produces boring, repetitive text; reserve for classification.
- **Trusting fixed seed/temperature for full determinism**: Hardware differences and API providers still cause variation; doesn't fix slightly-different-input divergence.
- **Over-sampling test time compute**: Beyond a point (OpenAI saw ~400) gains reverse as adversarial outputs fool the verifier; production rarely affords 400–10,000 samples.
- **Constrained sampling everywhere**: Per-format grammar is non-generalizable and adds latency; some argue invest in instruction-following instead.

## Code Examples
Text-to-regex via GPT-4o (system + user prompt → output):
```
System: Given an item, create a regex that represents all the ways the item
can be written. Return only the regex.
Example: US phone number -> \+?1?\s?(\()?(\d{3})(?(1)\))[-.\s]?(\d{3})[-.\s]?(\d{4})
User: Email address ->
GPT-4o: [a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
```

## Reference Tables
| Strategy | Param | Typical default | Effect |
|---|---|---|---|
| Temperature | T | 0.7 (creative); 0 (consistent/argmax) | Higher → creative, less coherent |
| Top-k | k | 50–500 | Smaller → predictable, cheaper softmax |
| Top-p (nucleus) | p | 0.9–0.95 | Dynamic token set; contextually appropriate |
| Min-p | min prob | — | Floor a token must reach |

| Scaling fact | Value |
|---|---|
| Compute-optimal tokens : params | ~20 : 1 |
| GPU memory (inference) | ≈ 2 bytes × params (7B → ~14 GB) |
| Verifier vs. scale | verifier ≈ 30× param increase |
| Llama training tokens | 1.4T (L1) → 2T (L2) → 15T (L3) |

## Worked Example
**Cost/time to train GPT-3-175B (3.14×10²³ FLOPs).** One H100 NVL delivers ~60 TeraFLOP/s ≈ 5.2×10¹⁸ FLOPs/day. With 256 H100s at peak: (3.14×10²³)/(256 × 5.2×10¹⁸) ≈ 236 days (~7.8 months). Peak is unrealistic — at 70% utilization (50% is "okay," >70% "great") and $2/H100/hour: $2 × 256 × 24 × 256 / 0.7 ≈ $4.14M. Takeaway: the three scale numbers (params, tokens, FLOPs) convert directly into compute time and dollars, so start from a budget and back into model/data size via the Chinchilla 20:1 rule.

## Key Takeaways
1. A model is only as good as its data; English dominates Common Crawl (~46%), so general models underperform — and run slower/costlier (Burmese needs ~10× the tokens) — on low-resource languages.
2. The transformer won by replacing RNN seq2seq's single-hidden-state bottleneck with parallelizable attention; alternatives (RWKV, SSMs: S4/H3/Mamba/Jamba) target its quadratic context cost.
3. Scale = params + training tokens + FLOPs; bigger usually wins, but MoE sparsity, undertraining, and inverse scaling break the naive "bigger is better" rule. Bottlenecks loom: usable internet data and electricity.
4. Post-training (SFT then RLHF/DPO/RLAIF) unlocks pre-trained capability — InstructGPT used only 2% of compute for it; preference finetuning trains on comparison data because absolute scores are noisy.
5. Sampling makes models probabilistic — the source of creativity, inconsistency, and hallucination; tune temperature/top-k/top-p per task and fix sampling vars + seed + cache for consistency.
6. Test time compute (best-of-N, beam search, majority vote) cheaply buys quality; a verifier can replace ~30× scale, but gains saturate and cost scales linearly.
7. Hallucination has two complementary causes: self-delusion (model can't tell given data from its own generated tokens → snowballing) and SFT knowledge mismatch (labelers use knowledge the model lacks).

## Connects To
- **Ch 1**: Pre-/post-training split, self-supervision, last-mile challenge.
- **Ch 3**: Evaluation, cross-entropy/nats, weak-model-judges-strong, AI-as-judge.
- **Ch 4**: Instruction-following capability; detecting/measuring hallucinations.
- **Ch 5 & 6**: Prompting, memory, context construction (mitigate inconsistency/hallucination); agentic tool I/O.
- **Ch 7**: Memory/KV-cache calculation, finetuning/feature-based transfer, floating-point formats.
- **Ch 8**: Dataset engineering — data quality, diversity, synthetic data, scaling-law adaptation.
- **Ch 9**: Inference optimization for prefill/decode, hardware utilization metrics.
