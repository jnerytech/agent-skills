# Chapter 1: Introduction to Building AI Applications with Foundation Models

## Core Idea
AI engineering—building applications on top of readily available foundation models—is a distinct discipline that, unlike traditional ML engineering, is less about developing/training models and more about *adapting* and *evaluating* someone else's model. Scale plus self-supervision made foundation models possible; "model as a service" made them accessible.

## Frameworks Introduced
- **Three Layers of the AI Stack**: application development (top), model development (middle), infrastructure (bottom).
  - When to use: orienting a build; start at the top layer and move down only as needed.
  - How: App dev = prompting, context, evaluation, interface. Model dev = modeling/training, dataset engineering, inference optimization. Infra = serving, data/compute management, monitoring.
- **Use Case Evaluation (risk/opportunity ladder)**: decide *why* (and whether) to build before building.
  - When to use: at project inception, before coding a demo.
  - How: rank motivation high→low — (1) business continuity (competitors with AI make you obsolete), (2) boost profits/productivity, (3) don't-be-left-behind R&D. Higher existential risk → favor build in-house over buy.
- **Role of AI/Humans (Apple's three axes)**: classify the feature to set the quality bar.
  - How: Critical vs complementary (more critical → higher reliability needed); Reactive vs proactive (proactive → can precompute, but needs higher quality since unsolicited); Dynamic vs static (dynamic → per-user/continual finetuning).
- **Crawl-Walk-Run (Microsoft 2023)**: gradually increase automation.
  - How: Crawl = human involvement mandatory; Walk = AI interacts with internal employees; Run = increased automation incl. external users. Advance a stage when acceptance rate is high (e.g., 95% of suggestions used verbatim).
- **Model Adaptation taxonomy**: two categories by whether weights change.
  - How: Prompt-based (prompt engineering, RAG) — no weight updates, less data, easy to start; Finetuning — updates weights, more data/complexity, needed for new tasks or strict performance.

## Key Concepts
- **Foundation model**: a large, general-purpose model (often multimodal) that can be built upon for many tasks; supersedes the LLM-only framing.
- **Self-supervision**: training where labels are inferred from the input itself (next-token prediction), bypassing the costly manual-labeling bottleneck and enabling scale.
- **Token / tokenization**: basic unit (char, word, or word-part); ~¾ word for GPT-4 (100 tokens ≈ 75 words). Vocabulary = set of all model tokens.
- **Autoregressive vs masked LM**: autoregressive predicts next token from preceding only (text generation); masked fills blanks using both sides (classification, understanding).
- **AI engineering vs ML engineering**: ML trains own models; AI engineering adapts existing ones—focus shifts to adaptation + evaluation.
- **Pre-training / finetuning / post-training**: pre-training = from scratch (random init, ~98% of compute); finetuning = continue training a trained model; post-training = finetuning done by model developers vs application developers.
- **RAG (retrieval-augmented generation)**: supplementing prompts with data retrieved from an external source.
- **Agents**: AIs that can plan and use external tools.
- **Human-in-the-loop**: involving humans in the AI's decision-making process.
- **Last-mile challenge**: the 0→60 demo is easy; 60→100 (production) is exceedingly hard.

## Mental Models
- Think of a language model as a **completion machine**: given a prompt, it predicts a continuation. Reframe tasks (translation, classification, summarization) as completion.
- Use **prompt engineering when** you need speed, low data, and broad model experimentation; use **finetuning when** the task is complex, has strict performance needs, or wasn't seen in training.
- Treat foundation-model output as **probabilistic, not guaranteed correct**—this is the source of both its power (creativity) and its frustration (hallucination).
- Think "**a model someone else trained for you**": effort moves from training to adaptation, and from modeling to evaluation.

## Anti-patterns
- **Building a cool demo and assuming it's a product**: initial foundation-model success is misleading; the last mile (60→100) takes months/years.
- **Building a thin wrapper with no moat**: if it's easy for you, it's easy for competitors—or the underlying model subsumes your layer (the "PDF-parser on ChatGPT" trap). Defend via data, distribution, or open-source-host positioning.
- **Misusing terminology**: calling prompt engineering "training" or "finetuning"—teaching via context input is prompt engineering, not weight updates.
- **Comparing models under different prompting regimes** (e.g., Gemini CoT@32 vs ChatGPT 5-shot)—creates misleading evaluation results.

## Code Examples
None in this chapter.

## Reference Tables

How model-development responsibilities change with foundation models (Table 1-4):

| Category | Traditional ML | Foundation models |
|---|---|---|
| Modeling & training | ML knowledge required (train from scratch) | ML knowledge nice-to-have |
| Dataset engineering | Feature engineering, tabular data | Dedup, tokenization, context retrieval, quality control |
| Inference optimization | Important | Even more important |

App-development importance shift (Table 1-6):

| Category | Traditional ML | Foundation models |
|---|---|---|
| AI interface | Less important | Important |
| Prompt engineering | N/A | Important |
| Evaluation | Important | More important |

## Worked Example
Customer-support chatbot. **Why build:** opportunity (boost productivity, faster responses). **Role:** AI is complementary, reactive (needs low latency), can be static or dynamic. **Human role via Crawl-Walk-Run:** start by showing AI-suggested responses to human agents (Crawl); once acceptance rate hits ~95% on simple requests, let customers interact with AI directly for those requests (Walk→Run). **Set expectations:** business metrics (% messages automated, throughput, response time, labor saved) + usefulness thresholds (quality, latency = TTFT/TPOT/total, cost per inference). **Milestone reality:** LinkedIn hit 80% in one month but needed four more months to pass 95%—plan for the last mile and hallucination cleanup.

## Key Takeaways
1. Choose adaptation deliberately: prompt engineering first (cheap, fast, low data); escalate to RAG, then finetuning only when needed.
2. Ask "should we build this?" before "how"—classify by risk/opportunity ladder and buy-vs-build (in-house if existential).
3. Set success metrics (business + usefulness thresholds) and a usefulness bar *before* shipping; budget heavily for the 60→100 last mile.
4. Evaluation is the hardest and most important AI-engineering activity—open-ended outputs have no single ground truth.
5. Always compare models under identical prompting conditions, or the comparison is meaningless.
6. Plan for maintenance: prices, models, APIs, and regulations shift fast—run continuous cost-benefit analysis and keep versioning/eval infra.
7. Defensibility comes from data, distribution, or open-source/self-host positioning—not from the model, which everyone shares.

## Connects To
- **Ch 2**: foundation models internals—probabilistic nature, sampling variables, tokenization/vocabulary efficiency.
- **Ch 3**: evaluation challenges for open-ended models (the chapter's biggest "more important" shift).
- **Ch 5**: prompt engineering. **Ch 6**: context construction and agents/tools.
- **Ch 7**: post-training/finetuning + inference optimization (quantization, distillation).
- **Ch 8**: dataset engineering and data synthesis.
- **Ch 10**: user feedback design from new AI interfaces.
