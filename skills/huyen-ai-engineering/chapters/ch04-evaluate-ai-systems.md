# Chapter 4: Evaluate AI Systems

## Core Idea
Evaluation is the biggest bottleneck to AI adoption: a model is only useful if it works for *your* application, so you must define application-specific criteria first, use them to select models, and build a custom evaluation pipeline you can trust — because public benchmarks can be contaminated and rarely match your needs.

## Frameworks Introduced
- **Evaluation-Driven Development**: define evaluation criteria *before* building (analog of test-driven development).
  - When to use: before investing in any AI application.
  - How: list criteria across four buckets — domain-specific capability, generation capability, instruction-following capability, cost & latency — then build toward measurable value (ROI), not hype.
- **Model Selection Workflow (4 steps)**: pick the best model *for your application*, not the best overall.
  - When to use: repeatedly, at every adaptation stage (prompting, finetuning).
  - How: (1) filter by hard attributes (license, privacy, size); (2) narrow using public benchmarks/leaderboards balancing quality/latency/cost; (3) run your own evaluation pipeline; (4) monitor in production. Iterative — later steps can revise earlier decisions.
- **Build vs Buy (API vs self-host) — 7 axes**: data privacy, data lineage/copyright, performance, functionality, API cost vs engineering cost, control/access/transparency, on-device deployment.
  - When to use: deciding to use commercial model APIs vs hosting open source.
  - How: weigh each axis per use case; the decision shifts over time (e.g., cost per token drops with scale when self-hosting).
- **Evaluation Pipeline (3 steps)**: design a trustworthy pipeline for open-ended tasks.
  - How: (1) evaluate all components (per task / per turn / per intermediate output); (2) create an evaluation guideline (criteria + scoring rubric with examples + tie to business metrics); (3) define evaluation methods and annotated data, then evaluate the pipeline itself and iterate.
- **SAFE (Search-Augmented Factuality Evaluator)**: knowledge-augmented factual verification.
  - How: decompose response into statements → make each self-contained → generate search queries → AI judges each against results.

## Key Concepts
- **Local vs global factual consistency**: consistency against provided context vs against open/world knowledge.
- **Hard vs soft attributes**: what you can't change (license, provider's model size) vs what you can improve (accuracy, toxicity); latency can be either.
- **Open weight vs open model**: weights public only vs weights + training data public ("open source" used loosely for both).
- **Data contamination (leakage)**: model trained on its own test data; inflates scores without real capability.
- **Textual entailment (NLI)**: classify hypothesis vs premise as entailment / contradiction / neutral — maps to consistent / inconsistent / undetermined.
- **Self-verification (SelfCheckGPT)**: sample N responses; disagreement signals hallucination.
- **Instruction-following capability**: ability to obey instructions (format, length, content), distinct from domain or generation capability.
- **Mean win rate**: HELM's aggregation — fraction of times a model beats others, averaged across scenarios (vs simple averaging).
- **Usefulness threshold**: minimum metric score for an application to be worth deploying.
- **Simpson's paradox**: model A beats B on every slice yet loses overall.
- **Pareto optimization**: optimizing multiple objectives (quality, latency, cost); fix non-negotiables first, then optimize the rest.

## Mental Models
- **Lamppost trap**: evaluation-driven development biases you toward easy-to-measure use cases; you may miss game-changing apps that are hard to evaluate. Easy to measure ≠ valuable.
- **Best overall ≠ best for you**: a leaderboard winner may fail your task; build a private leaderboard from criteria you actually care about.
- **"A benchmark stops being useful as soon as it becomes public"**: public benchmarks saturate and get contaminated; treat them as a filter for bad models, not a selector for the best.
- **Correct ≠ good**: "You are a terrible fit" can be correct yet unhelpful — define what *good* means, including what the app should NOT do.

## Anti-patterns
- **Deploying without an evaluation pipeline**: a deployed app no one can evaluate is worse than one never deployed — costs to run, costs more to take down.
- **Trusting public-leaderboard rankings blindly**: opaque benchmark selection/aggregation, likely contamination, missing capabilities you need.
- **Simple averaging of benchmark scores**: treats 80% on a hard benchmark as equal to 80% on an easy one and ignores correlation (correlated benchmarks exaggerate bias).
- **Ambiguous scoring rubric**: ambiguous guidelines yield misleading scores; if humans can't follow the rubric, AI judges can't either.
- **Skipping evaluation to cut latency/cost**: a risky bet; mix cheap (100% coverage) + expensive (1% sample) methods instead.
- **Not evaluating components independently**: you won't know *where* a multi-step system fails.

## Code Examples
AI-judge prompt for factual consistency (Liu et al. 2023, verbatim typo preserved):
```
Factual Consistency: Does the summary untruthful or misleading facts that are
not supported by the source text?
Source Text:
{{Document}}
Summary:
{{Summary}}
Does the summary contain factual inconsistency?
Answer:
```
Bootstrap to check eval-set sufficiency: draw 100 samples *with replacement* from your 100 examples, evaluate, repeat; if results vary wildly (e.g., 90% vs 70%), enlarge the set.

## Reference Tables
Samples needed for 95% confidence a system is better (OpenAI; rule: 3× smaller difference → 10× more samples):

| Difference to detect | Samples needed |
|---|---|
| 30% | ~10 |
| 10% | ~100 |
| 3% | ~1,000 |
| 1% | ~10,000 |

API vs self-host (condensed): APIs win on getting-started ease, scaling, function calling, structured outputs; self-host wins on data privacy, logprobs/interpretability, freeze/control, finetuning freedom, on-device.

## Worked Example
Resume employer-extraction app, two components: (1) PDF→text, (2) text→current employer. Evaluate end-to-end AND each step independently: step 1 by text similarity to ground truth; step 2 by accuracy given correct text. If the final employer is wrong, independent scores reveal whether OCR/extraction or reasoning failed — without them you're blind to the failure point. Then tie to business: factual consistency 80% → automate 30% of support; 90% → 50%; 98% → 90%, and set a usefulness threshold (e.g., must hit 50% to ship).

## Key Takeaways
1. Define evaluation criteria before building (evaluation-driven development); criteria span domain capability, generation, instruction-following, and cost/latency.
2. Factual consistency and safety are the central generation risks; verify with AI judges, self-verification (SelfCheckGPT), knowledge-augmented (SAFE), or NLI/entailment scorers.
3. Curate your *own* instruction benchmark — IFEval/INFOBench show methods but won't cover your prompts; "if you care about something, put a test set on it."
4. Build vs buy is a 7-axis, use-case- and time-dependent decision; re-evaluate as you scale.
5. Public benchmarks filter out bad models but won't find the best for you; they saturate fast and are likely contaminated (detect via n-gram overlap or low perplexity).
6. A clear scoring rubric with examples, validated by humans, is the backbone of a reliable pipeline; map eval metrics to business metrics and set a usefulness threshold.
7. Evaluate your evaluation pipeline: check signal, reliability/reproducibility (judge temperature 0), metric correlation, and added cost/latency.

## Connects To
- **Ch 3**: supplies the evaluation *approaches* (AI as judge, functional correctness, perplexity, similarity) this chapter applies per criterion.
- **Ch 5**: prompt sensitivity, roleplaying as a prompt technique, and additional safety/robustness concerns.
- **Ch 6**: factual consistency is central to RAG; evaluating retrieval and agentic systems.
- **Ch 8**: reuse evaluation rubrics/annotated data for synthetic training data; data quality verification.
- **Ch 9**: cost, latency, and inference-service optimization referenced under cost/latency criteria.
- **Ch 10**: production monitoring and user feedback (step 4 of the selection workflow).
