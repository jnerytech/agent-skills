# Chapter 3: Evaluation Methodology

## Core Idea
Evaluation is the biggest hurdle to shipping foundation-model applications, and it is harder than traditional ML eval because models are open-ended, increasingly intelligent (so outputs are costly to verify), black-boxed, and saturate benchmarks fast. The fix is systematic automatic evaluation — language-modeling metrics, exact evaluation, AI-as-a-judge, and comparative ranking — rather than "eyeballing" or word-of-mouth.

## Frameworks Introduced
- **Language modeling metrics (cross entropy, perplexity, BPC, BPB)**: four interrelated measures of predictive accuracy on next-token prediction; know one and you can derive the others.
  - When to use: model selection, guiding training/finetuning, data deduplication, contamination detection, anomaly detection.
  - How: train to minimize cross entropy H(P,Q) = H(P) + D_KL(P‖Q); report perplexity = exp of cross entropy (base 2 for bits, base e for nats). Lower = better predictor.
- **Functional correctness**: evaluate whether the system actually performs the intended task.
  - When to use: tasks with measurable/executable objectives — code generation, text-to-SQL, game bots, optimization.
  - How: run output against test cases; for code use pass@k = fraction of problems where any of k samples passes all tests.
- **Similarity measurements against reference data**: score outputs against ground-truth (canonical) responses.
  - When to use: open-ended tasks lacking executable correctness (translation, summarization, captioning) where references exist.
  - How: pick one of four — human/AI judgment, exact match, lexical similarity (BLEU/ROUGE/METEOR/TER/CIDEr via n-gram overlap or edit distance), semantic similarity (BERTScore/MoverScore via embedding cosine similarity).
- **AI as a judge (LLM as a judge)**: use an AI model + prompt to score outputs.
  - When to use: open-ended, reference-free, production eval; fast/cheap/flexible; sometimes the only automatic option.
  - How: prompt specifies task + criteria + scoring system (classification > discrete numeric > continuous). Three modes: score alone, compare to reference, compare two responses. A judge = model + prompt + sampling params.
- **Comparative evaluation**: rank models from pairwise match outcomes rather than independent (pointwise) scores.
  - When to use: subjective quality where "which is better" is easier than absolute scoring; never saturates.
  - How: collect matches → win rates → feed a rating algorithm (Elo, Bradley–Terry, TrueSkill) to compute scores → rank. Ranking is correct if higher-ranked model wins >50% of matches.

## Key Concepts
- **Entropy**: average information per token; lower entropy = more predictable language.
- **Cross entropy H(P,Q)**: how hard it is for model Q to predict data from true distribution P; equals H(P) when learning is perfect (KL divergence = 0). Not symmetric.
- **Perplexity (PPL)**: exponential of cross entropy; the effective number of options the model is choosing among. Lower for structured data, smaller vocab, longer context.
- **BPC / BPB**: cross entropy normalized per character / per byte, for cross-tokenizer comparison; ties to compression efficiency.
- **Exact vs subjective evaluation**: exact produces unambiguous judgment (functional correctness, exact match); subjective depends on judge/prompt (AI judge, essay grading).
- **pass@k**: functional-correctness score; fraction of problems solved by any of k generated samples.
- **Reference-based vs reference-free**: metrics that require ground-truth responses vs those that don't.
- **Self-bias / first-position bias / verbosity bias / recency bias**: systematic AI-judge (and human) preference distortions.
- **Reward / reference-based / preference model**: three types of small, specialized AI judges.
- **Transitivity**: ranking assumption that A>B and B>C implies A>C — questionable for human preference.

## Mental Models
- **Perplexity = branching factor.** A perplexity of 3 means the model behaves as if choosing among ~3 equally likely next tokens — impressive when vocab is 10,000s+.
- **A judge is a system, not a model.** Change the model, prompt, or sampling and you have a different judge whose scores aren't comparable to the old one's — so judges make poor longitudinal benchmarks.
- **Judging is easier than generating.** Anyone can say which song is better without writing one — why comparative eval and weaker/specialized judges can work, and why comparative eval survives super-human models.
- **Perplexity as a memory probe.** Low perplexity on benchmark data signals contamination; high perplexity on new data signals novelty (use for dedup/anomaly detection).

## Anti-patterns
- **Eyeballing / vibe checks / word of mouth**: ad hoc go-to prompts not tied to application needs; fine to bootstrap, insufficient for iteration.
- **Optimizing for BLEU/lexical overlap**: high lexical similarity ≠ correctness; on HumanEval correct and incorrect solutions had similar BLEU.
- **"Contains reference" exact match**: accepts factually wrong outputs ("September 12, 1929" contains the right year but wrong date).
- **Trusting an opaque AI judge**: never trust a judge whose model + prompt you can't see; criteria like "faithfulness" aren't standardized across tools.
- **Comparing scores across tools/judges**: MLflow relevance ≠ Azure relevance; faithfulness is 1–5 vs 0/1 vs YES/NO across tools.
- **Preference voting on correctness questions**: "is there a link between phone radiation and tumors?" must be answered by correctness, not preference; preference voting only works when voters are knowledgeable.
- **Using perplexity on post-trained/quantized models**: SFT/RLHF "collapses entropy" and raises perplexity even as task ability improves.

## Code Examples
HumanEval-style functional correctness: a problem ships with a checker; each `assert` is a test case. Model passes if any of k samples passes all asserts.
```python
def check(candidate):
    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.3) == True
    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.05) == False
    # ... pass@k = fraction of problems solved by any of k samples
```
Cosine similarity for semantic eval: `sim(A,B) = (A·B) / (‖A‖·‖B‖)`, range −1..1 (1 = identical meaning).

## Reference Tables

| Approach | Type | Needs reference? | Best for | Main weakness |
|---|---|---|---|---|
| Cross entropy / perplexity | exact (proxy) | no | model capability proxy, dedup, contamination | misleading after SFT/RLHF/quantization |
| Functional correctness (pass@k) | exact | no (tests) | code, SQL, games, optimization | only measurable-objective tasks |
| Exact match | exact | yes | trivia, math, short answers | fails on open-ended |
| Lexical similarity (BLEU/ROUGE) | exact | yes | translation, captioning | overlap ≠ quality; needs exhaustive refs |
| Semantic similarity (BERTScore) | exact-ish | yes | meaning overlap | depends on embedding quality; compute cost |
| AI as a judge | subjective | optional | open-ended, production | inconsistent, biased, non-standard, cost/latency |
| Comparative evaluation | relative | no | ranking models, preference | scales quadratically; no absolute score |

| Scoring system | AI-judge reliability |
|---|---|
| Classification (good/bad) | best |
| Discrete numeric (1–5) | good (narrower range better) |
| Continuous (0–1) | worst |

## Worked Example
Five models, pairwise win rates over 1,000 matches each (Table 3-6 style): M1>M2=90%, M1>M3=40%, M1>M4=15%, M1>M5=10%, M2>M3=60%, M2>M4=80%, M3>M4=70%, M3>M5=10%, M4>M5=20%. Raw numbers don't reveal an order. You feed these comparative signals to a rating algorithm (Bradley–Terry — LMSYS switched from Elo because Elo was sensitive to evaluator/prompt order) which fits a latent score per model, then ranks by score. The ranking is validated predictively: it's correct if, for every pair, the higher-ranked model wins >50% of future matches. Note this tells you M-better-than-N but not whether either is good enough — if M_A resolves 70% of support tickets and M_B beats it 51%, you still don't know M_B's resolution rate, so you'd add functional-correctness eval before swapping (especially if M_B costs 2x).

## Key Takeaways
1. Pick the evaluation method by task shape: executable → functional correctness; reference exists → similarity; open-ended/production → AI judge; "which model" → comparative.
2. Perplexity is a cheap, powerful proxy for capability and a tool for dedup/contamination/anomaly detection — but distrust it after post-training or quantization.
3. AI-as-a-judge is the de facto production method (fast, cheap, reference-free) but is inconsistent, biased, and non-standardized — always pin and disclose model+prompt, and supplement with exact and/or human eval.
4. Prefer classification or narrow discrete scoring over continuous scoring for AI judges; add few-shot examples to boost consistency (GPT-4 65%→77.5%) at the cost of longer/pricier prompts.
5. Comparative evaluation captures human preference and never saturates, but scales quadratically, may violate transitivity, and gives no absolute "good enough" signal.
6. Not every question is a preference question — use correctness for factual ones, and only collect preference votes from knowledgeable voters.
7. Evaluation lags the rest of the AI stack in tooling and investment; treat it as first-class, designed around where your system fails.

## Connects To
- **Ch 1**: language modeling roots (Shannon 1951), tokens, entropy.
- **Ch 2**: logprobs needed to compute perplexity; SFT/RLHF, sampling variables, preference/test-time compute that consume judge/preference signals.
- **Ch 4**: turning these methods into an evaluation pipeline and model selection; spot-checking cost/confidence trade-offs.
- **Ch 5**: prompt engineering best practices (applies directly to writing judge prompts).
- **Ch 6**: embeddings power vector search/RAG.
- **Ch 7**: quantization and its effect on perplexity.
- **Ch 8**: embedding-based data deduplication.
