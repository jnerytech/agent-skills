# Appendix C: Choosing an LLM

## Core Idea
Surveys the popular LLM families available at time of writing and lays out nine criteria — purpose, license, size, context window, language support, accuracy vs. speed, cost/hardware, benchmark suitability, and safety/bias — for picking the right one for a given project, worked through with a code-assistant example.

## Key Concepts
- **Mixture-of-Experts (MoE)**: an architecture that activates only a subset of a model's parameters per token, improving cost-efficiency versus a fully dense model of the same size (used by GPT-4, Gemini Ultra, Mixtral, DeepSeek-V3, Grok).
- **Context window**: the maximum number of input tokens a model can process at once; ranges from ~30K (Qwen) to 1M+ (Gemini 2.5/3.0, GPT-4.1, Grok 3.5), with research tests up to 10M tokens (Gemini).
- **Proprietary vs. open source**: proprietary models (OpenAI, Gemini, Cohere, Anthropic) hide architecture/training details and are billed by token via REST API; open source models (Llama, Mistral, Qwen, Falcon, DeepSeek, Phi, Gemma) expose weights, allow private deployment and fine-tuning, but shift cost to self-managed hardware.
- **Benchmark leaderboards**: Hugging Face Open LLM Leaderboard and LMSYS Chatbot Arena Leaderboard centralize cross-model benchmark comparison.
- **IFEval**: tests instruction-following via 25 types of verifiable instructions (e.g., word count, keyword mentions) across 500 prompts.
- **BIG-Bench Hard (BBH)**: 23 tasks where models historically underperform average human raters; needs multi-step/chain-of-thought (CoT) reasoning to solve well.
- **MATH (Level 5)**: 12,500 hard math problems with step-by-step solutions; low scores across models show scaling alone doesn't fix math reasoning.
- **GPQA**: 448 "Google-proof" graduate-level science questions where experts hit ~65-74% and non-experts with web access hit ~34%.
- **MuSR**: multi-step reasoning over long natural-language narratives (e.g., 1,000-word mysteries), harder and more realistic than synthetic benchmarks.
- **MMLU-Pro**: a harder version of MMLU (10 answer choices instead of 4, noisy questions removed), dropping model accuracy 16-33% versus MMLU and rewarding CoT reasoning.
- **HumanEval**: benchmark for functional-correctness of generated code, used in the chapter's practical example to rank Python code-generation accuracy.

## Mental Models
Nine-factor selection checklist (work through in roughly this order):
1. **Model purpose** — general-purpose (GPT-4, Gemini Pro) vs. specialized (Code Llama, Qwen-Coder); specialized models are usually smaller and outperform generalists on their narrow task.
2. **Proprietary vs. open source** — proprietary = convenience, no infra to manage, but prompt data leaves your organization; open source = data stays private and is fine-tunable, but you own GPU/hosting/IT costs (or use a managed platform like watsonx, Bedrock, Azure AI Studio, Vertex AI).
3. **Model size (parameters)** — more parameters generally means more capacity and accuracy, at the cost of memory, GPU needs, and latency; compression techniques can narrow this gap.
4. **Context window size** — match token capacity to task complexity; small windows suit short/simple prompts, large windows suit multi-step or document-heavy tasks.
5. **Supported languages** — match the model's strong languages (typically those with abundant training data, e.g., English/Chinese/Spanish) to your use case; rare languages may need a specialized model or fine-tuning.
6. **Accuracy vs. speed** — larger models are more accurate but slower; smaller models are faster but less precise; choose based on whether the task favors deep comprehension or real-time response.
7. **Cost and hardware requirements** — proprietary pricing scales with accuracy and token volume; open source shifts cost to GPUs, RAM, infrastructure, and skilled IT staff.
8. **Task suitability via benchmarks** — use standardized benchmarks (IFEval, BBH, MATH, GPQA, MuSR, MMLU-Pro, HumanEval) and leaderboards rather than vendor claims to compare models on the task that matters.
9. **Safety and bias** — check for filtering/monitoring against harmful or biased outputs, especially in sensitive domains like healthcare, customer service, or education.

**Worked example (Python trading code assistant)**: the decision flow was (1) specialized code-generation model over general-purpose, (2) open source required because proprietary in-house trading libraries can't be sent to external APIs, (3) medium size to balance accuracy/speed since cost wasn't a constraint, narrowing to 7 candidates, (4) pick by HumanEval score → Qwen2.5-Coder-32B-Instruct selected for the best accuracy/speed balance, with Phind-CodeLlama-34B, DeepSeek-Coder-7B, and CodeLlama-7B-Python as fallback alternatives.

**Risks to plan for regardless of model chosen**: bias inherited from training data, privacy/confidentiality of prompt data, hallucinations, unclear liability for LLM-caused errors, and IP/copyright exposure from training data.

## Reference Tables

Table C.1 — Comparison of LLMs (selected columns: developer, launch, open source):

| Model | Developer | Launch | Max tokens | Open source |
|---|---|---|---|---|
| GPT-4o / GPT-4.1 / o1 / o3 | OpenAI | 2024-25 | 128K-1M | No |
| Gemini 2.5 Pro | Google | May 25 | 1M | No |
| Gemma-3 | Google | Mar 25 | 128K | Yes |
| Claude Sonnet-3.7 | Anthropic | Feb 25 | 200K | No |
| Command R+ | Cohere | Aug 24 | 128K | No |
| Llama-4 | Meta | Sep 24 | 128K | Yes |
| Falcon3-10B-Base | TII-UAE | Dec 24 | 32K | Yes |
| Mixtral-8x22B-Instruct | Mistral AI | Mar 24 | 64K | Yes |
| Qwen2.5 72B | Alibaba Cloud | Sep 24 | 128K | Yes |
| Grok 3.5 | xAI | Feb 25 | 1M | No |
| DeepSeek-V3 / R1 | DeepSeek AI | Dec 24/Jan 25 | 128K-132K | Yes |
| Phi-4.0 | Microsoft | Dec 24 | 128K | Yes |

Table C.3 — Python HumanEval rankings (used to select the code assistant):

| Model | Python HumanEval |
|---|---|
| Qwen2.5-Coder-32B-Instruct | 83.20 |
| DeepSeek-Coder-7B-Instruct | 80.22 |
| CodeLlama-70B-Instruct | 75.60 |
| Phind-CodeLlama-34B-v2 | 71.95 |
| CodeLlama-70B-Python | 55.49 |
| CodeLlama-7B-Python | 40.48 |
| StarCoder2-7B | 34.09 |

## Key Takeaways
1. Start from purpose and privacy constraints (proprietary vs. open source) before comparing raw benchmark scores — they eliminate most candidates first.
2. Don't assume bigger is always better: match model size and context window to the task, since larger models cost more in latency, GPUs, and money.
3. Use standardized benchmarks (IFEval, BBH, MATH, GPQA, MuSR, MMLU-Pro, HumanEval) via leaderboards like Hugging Face Open LLM or LMSYS Chatbot Arena instead of trusting vendor marketing.
4. When data confidentiality is non-negotiable (e.g., proprietary in-house code or sensitive user data), open source models deployed privately are the only compliant choice, even if it means managing your own GPU infrastructure.
5. Always re-check current benchmark scores before deciding — this space moves fast enough that the tables here are already a snapshot, not a permanent ranking.
6. Plan for bias, hallucinations, privacy, liability, and IP risk as deployment concerns independent of which model you pick.

## Connects To
- **Appendix E**: compression techniques for open source models and inference engines (e.g., Ollama, OpenAI-REST-compatible engines) referenced here for narrowing the accuracy/speed and proprietary/open-source tradeoffs.
- **Ch 1**: introduces the LangChain provider integration packages (`langchain-openai`, `langchain-google-genai`, `langchain-anthropic`, `langchain-cohere`) used to actually wire in whichever model this appendix's criteria select.
