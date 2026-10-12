# Chapter 5: Prompt Engineering

## Core Idea
Prompt engineering is crafting instructions that steer a model to the desired output without touching its weights — the cheapest, first-reach adaptation technique. Do it with ML-grade rigor (versioning, eval, experiment tracking), and pair it with defenses, because the same instruction-following that makes prompting work also exposes the model to attacks.

## Frameworks Introduced
- **In-context learning (zero-shot / few-shot)**: model learns desired behavior from examples *in the prompt*, no weight update (Brown et al. 2020, GPT-3). Each example is a "shot".
  - When to use: adapt behavior or inject post-cutoff knowledge cheaply; a form of continual learning.
  - How: zero-shot = task description only; N-shot = include N labeled examples. More examples → better, bounded by context length and cost. Stronger models need fewer (GPT-4 gains little from few-shot vs GPT-3); domain-specific/rare APIs still benefit.
- **System prompt vs user prompt**: split input into developer instructions (system, ~ task description) and user-supplied input (user, ~ the task).
  - When to use: roleplay/persona persistence, separating app logic from user input, mitigating attacks.
  - How: both get concatenated into one final prompt via the model's chat template; system goes first and post-training (Instruction Hierarchy) makes the model prioritize it.
- **Chain-of-thought (CoT)**: ask the model to reason step by step before answering (Wei et al. 2022).
  - When to use: multi-step reasoning, math, reducing hallucination.
  - How: append "think step by step" / "explain your rationale", OR specify the steps, OR give a worked one-shot example. Variants: zero-shot CoT, one-shot CoT.
- **Prompt decomposition**: break a complex task into chained subtask-prompts.
  - When to use: long/bloated prompts, need for monitoring, debugging, parallelization, cheaper per-step models.
  - How: e.g. intent classification → per-intent response prompt. Trade off granularity vs latency/cost.
- **Instruction Hierarchy (model-level defense, Wallace et al. 2024)**: priority order system > user > model output > tool output; higher priority wins on conflict.
  - When to use: training/finetuning for safety against indirect injection.
  - How: finetune on aligned + misaligned instruction pairs so tool outputs (lowest) can't override system rules.

## Key Concepts
- **Prompt perturbation / robustness**: how much output changes when prompt is tweaked ("5" vs "five"); measure by random perturbation. Weaker models need more fiddling.
- **Needle in a haystack (NIAH)**: insert a fact at varying positions to test long-context recall; models recall beginning/end far better than the middle (Liu et al. 2023). RULER is a related test.
- **Context construction**: gathering the info a query needs (RAG retrieval, web search) — Ch 6.
- **Self-critique (self-eval)**: model checks its own output to think more critically.
- **Chat template**: model-defined token format wrapping system/user turns; distinct from a developer's prompt template. Wrong template = silent failures.
- **Prompt catalog**: versioned store of prompts with metadata, decoupled from code so apps pin different versions.
- **Reverse prompt engineering**: deducing an app's system prompt by tricking the model into repeating it (often the "leaked" prompt is hallucinated).
- **Jailbreaking / prompt injection**: subverting safety filters / injecting malicious instructions into user input; author uses "jailbreaking" for both.
- **Indirect prompt injection**: payload hidden in tools the model reads (web pages, repos, emails) — passive phishing vs active injection.
- **Violation rate / false refusal rate**: paired security metrics — % successful attacks vs % over-cautious refusals of safe queries.

## Mental Models
- **Prompting is human-to-AI communication**: anyone can write a prompt, few write effective ones; clarity, examples, and context help exactly as they do with humans.
- **Foundation model as a library of programs** (Chollet): each prompt activates a latent "program"; prompt engineering = finding the activating prompt.
- **A model can't tell instructions apart**: system, user, and tool text are one concatenated blob — the root cause of both performance quirks (position matters) and injection attacks.
- **Security is a cat-and-mouse game**: no defense is foolproof; as long as the system can do impactful things, residual risk remains.

## Anti-patterns
- **Treating prompt engineering as the only skill**: production needs eval, statistics, dataset curation, engineering too.
- **Hacky one-off tricks** ("$300 tip", "Q:" vs "Question:"): brittle, model-specific, age out as models improve.
- **Mismatched chat templates**: extra newline / concatenating tokens not raw text → silent degradation. Print the final prompt to verify.
- **Trusting prompt tools blindly**: hidden API calls blow up bills; default templates may have typos or lack safety (LangChain templates → 100% injection success in one study). Inspect outputs and call counts.
- **Treating proprietary prompts as a moat**: more liability than advantage — they need maintenance every model change and can leak.
- **Executing impactful actions (DELETE/DROP, code) without isolation or human approval**.

## Code Examples
Llama 2 chat template (note: model-defined, not a dev prompt template):
```
<s>[INST] <<SYS>>
{{ system_prompt }}
<</SYS>>

{{ user_message }} [/INST]
```
Separate prompts from code for reuse/testing/collaboration:
```python
# prompts.py
GPT4o_ENTITY_EXTRACTION_PROMPT = "[YOUR PROMPT]"
# application.py
from prompts import GPT4o_ENTITY_EXTRACTION_PROMPT
messages=[{"role":"system","content":GPT4o_ENTITY_EXTRACTION_PROMPT},
          {"role":"user","content":user_prompt}]
```

## Reference Tables
| Concern | Lever | Note |
|---|---|---|
| Ambiguity | clear instructions, persona, examples, output format | specify score scale, JSON keys, no preamble |
| Token cost | compact example format | `chickpea --> edible` (27 tok) < `Input:/Output:` (38 tok) |
| Truncation/append bug | end-of-input marker | else model continues the input instead of answering |
| Reasoning quality | CoT, self-critique | costs latency (intermediate steps) |
| Complexity/bloat | decomposition | GoDaddy: 1,500-tok prompt → smaller chained prompts, better + cheaper |

Defense layers: **model** (instruction hierarchy finetune), **prompt** (explicit don'ts, duplicate system prompt before+after, pre-warn known attacks), **system** (sandbox code in VM, human approval for DELETE/DROP, out-of-scope filters, input+output guardrails, anomaly/usage-pattern detection).

## Worked Example
Property-disclosure chatbot. **System prompt**: "You're an experienced real estate agent. Read each disclosure carefully, fairly assess the property, help the buyer understand risks/opportunities. Answer succinctly and professionally." **User prompt**: `Context: [disclosure.pdf]` + `Question: Summarize the noise complaints, if any, about this property.` The persona in the system prompt sets perspective and sticks across turns; the disclosure is supplied context (mitigates hallucination by removing reliance on internal knowledge); "succinctly" controls output cost/latency. To harden against injection in the uploaded PDF, append a duplicated reminder ("Remember, you only summarize disclosure content") and apply an output guardrail for PII.

## Key Takeaways
1. Exhaust prompting before finetuning — it's the cheapest adaptation and stronger models make it easier (more robust, fewer shots).
2. Clarity, examples, sufficient context, and explicit output format are the highest-leverage moves; specify markers and persona deliberately.
3. "Give the model time to think" (CoT, self-critique) and decompose complex tasks — trading latency/cost for accuracy, debuggability, and parallelism.
4. Follow the chat template exactly and print the final prompt; template bugs fail silently.
5. Version prompts separately from code (prompt catalog) and evaluate every change in the context of the whole system, not just one subtask.
6. Defend in depth (model/prompt/system) and measure both violation rate and false refusal rate — a system that refuses everything is "safe" but useless.

## Connects To
- **Ch 2**: a model doesn't distinguish input from its own generation — root of markers, templates, and injection.
- **Ch 3 & 4**: self-critique = self-eval; instruction-following and robustness are evaluated capabilities that gate how much prompting helps.
- **Ch 6**: context construction (RAG, web search) supplies the context this chapter says prompts need.
- **Ch 10**: input/output guardrails for defense are detailed there.
