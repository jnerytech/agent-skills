# Chapter 2: Introduction to Large Language Models for Text Generation

## Core Idea
LLMs turn text into tokens, then into vectors. A transformer's self-attention gives those vectors context, and the model generates text one token at a time by probability. Knowing this mechanism, and the landscape of competing models (OpenAI, Google, Meta, Mistral, Anthropic), helps you choose a model and explains why the prompting principles work. Note: the model landscape is as of the 2024 edition.

## Frameworks Introduced
- **The LLM text-generation pipeline**: tokenize → embed as vectors → transformer builds contextual vectors (self-attention) → predict the most probable next token → repeat.
  - When to use: as a mental model when you need to reason about why prompt wording changes the output, or about token limits and cost.
  - How: each step is covered under Key Concepts below.
  - Why it works / failure mode: generation is probabilistic and sequential. The model can't see its whole answer in advance (this is why Ch 1 uses self-evaluation chains), and output reflects biases in the training data. Use human oversight.

- **ChatGPT's three-step fine-tuning (RLHF)**:
  1. **Collect demonstration data**: trained human labelers write the desired behavior for a distribution of prompts.
  2. **Train a supervised policy**: fine-tune pretrained GPT-3 on those demonstrations with supervised learning.
  3. **Collect comparison data + reinforcement learning**: labelers rank model outputs, a **reward model** learns to predict their preferences, and **PPO (Proximal Policy Optimization)** optimizes the policy against that reward model.
  - Result: behavior aligned with human intent, more helpful, honest, and safe than base GPT-3.

- **Cross-model comparison by running the same prompt**: the authors' practical way to judge models. Run one prompt on several models and compare instruction-following. In their Steve Jobs few-shot naming prompt, only GPT-4 got both format and style right (names starting with "i"). Claude 3 came close, and Llama 3 70b added a preamble and mixed in non-"i" names. For broader rankings, check the Chatbot Arena Leaderboard.
  - Principle(s): Evaluate Quality.

## Key Concepts
- **Token**: the basic linguistic unit (a word, a subword, or a set of characters). 100 tokens ≈ 75 words. Token counts determine model limits.
- **Tokenization (BPE, WordPiece, SentencePiece)**: splitting text into tokens. **Byte-Pair Encoding** starts from characters and merges frequent pairs (for example `a,p,p,l,e` → `appl`), which lets the model handle rare words with a manageable vocabulary.
- **Vectors / word embeddings**: multidimensional numeric representations in which semantically similar words sit close together (virtue/moral, walked/walking).
- **Transformer / self-attention**: each word "casts votes" on how important every other word is to its meaning, which produces context-rich vectors. Introduced in "Attention Is All You Need" (Google Brain). Its breakthrough was relating distant words directly, rather than processing text sequentially, which captures long-range dependencies.
- **Encoder vs decoder**: BERT uses an encoder for input understanding. GPT uses a decoder for output generation.
- **Pretraining vs fine-tuning**: pretraining gives broad language knowledge from huge corpora. Fine-tuning adapts the model to specific tasks.
- **Parameters**: the weights and biases adjusted during training. GPT-4 has an estimated 1.7T parameters and cost about $63M to train.
- **Mixture of experts**: an architecture that routes work across several expert sub-models (GPT-4, Mixtral 8x7b).
- **Quantization / LoRA**: quantization lowers parameter precision to shrink the model with little loss. LoRA (low-rank approximation) makes fine-tuning efficient. Together they make running and fine-tuning open models feasible on consumer hardware.
- **Context window**: how much text the model can consider at once (Claude 2: 100K, GPT-4 Turbo: 128K).
- **Multimodal models**: models that handle text plus images or audio in one context (GPT-4V, GPT-4o).
- **Constitutional AI**: Anthropic's alignment method, which trains the model against a list of rules or values.

## Mental Models
- Think of an LLM as **autocomplete over meaning-space**: words become points in vector space, attention bends each point toward its context, and the next token is the most probable continuation.
- Use **closed frontier models (GPT-4, Claude Opus)** when instruction-following matters most. Consider **open models (Llama, Mistral) with quantization/LoRA** when you need local deployment, fine-tuning, or cost control.
- Think of the model market as **leapfrogging**: advantages such as Claude 2's 100K window were matched within months, so choose models empirically and keep prompts portable.

## Anti-patterns
- **Trusting outputs blindly**: training data carries source biases, and models hallucinate (for example, Bard's false James Webb Space Telescope claim at launch).
- **Pasting sensitive data into models that may retrain on it**: data privacy remains a crucial concern.
- **Picking a model from reputation alone**: instruction-following varies a lot between models, so test your actual prompt on each.

## Reference Tables

| Model / family | Vendor | Notable traits (2024 edition) |
|---|---|---|
| GPT-2 | OpenAI | Released open source after a staged rollout over misuse concerns |
| GPT-3 / 3.5-turbo / ChatGPT | OpenAI | Closed and paid. 3.5-turbo is cheaper and faster. ChatGPT is RLHF-tuned for dialogue and reached 100M users by Jan 2023 |
| GPT-4 / GPT-4V / GPT-4o | OpenAI | Mixture of experts, 90th percentile on the bar exam. V adds image input. 4o (May 2024) handles text, audio, and vision in one network |
| Bard → Gemini (1.5) | Google | Rough at launch. PaLM API on GCP. Gemini 1.5 approaches GPT-4 with a 1M context. Two smaller open source models on the same architecture released too |
| Llama, Llama 2, Llama 3 | Meta | Open source, 7/8/70B sizes. Democratizes access but can be misused |
| Mistral 7B / Mixtral 8x7b | Mistral AI | Sliding window attention, Apache license. Mixtral (MoE) is about GPT-3.5 level. Base for fine-tunes such as Zephyr 7b beta |
| Claude 2 / Claude 3 (Opus, Haiku) | Anthropic | Constitutional AI. 100K window and file uploads. Opus rivals GPT-4. Haiku costs $0.25/M tokens |
| Bedrock / Titan | AWS | Managed foundation-model services (April 2023) |

## Worked Example
**The same prompt on three models:** the Ch 1 engineered prompt (Steve Jobs persona, comma-separated format, three "i"-prefixed examples) was sent to each model.
- GPT-4 → `Product names: iFit, iShoe, iFlexible` (format and style correct)
- Claude 3 → `Product names: iFit, iComfort, iSole` (format and style correct)
- Llama 3 70b → a chatty preamble, then `iFit, OneSize, iWalkFree` (broke the format, mixed the style)

Lesson: instruction-following is a key difference between models, so evaluate your real prompt on each candidate.

## Key Takeaways
1. LLMs generate text one token at a time by probability over contextual embeddings. Prompt wording shifts those probabilities.
2. Tokens (≈ 3/4 of a word) set the context limits and the cost. BPE is the common tokenizer.
3. Self-attention, which relates any word to any other, is the transformer breakthrough behind long-range coherence.
4. ChatGPT's usefulness comes from RLHF: demonstrations → supervised policy → reward model + PPO.
5. The field is competitive: closed frontier models lead on instruction-following, while open models plus quantization/LoRA make local fine-tuning possible.
6. Choose models by running your own prompt across them, and keep sensitive data out of models that may train on it.

## Connects To
- **Ch 1**: next-token prediction explains why direction, format, and examples shift outputs, and why self-evaluation in a separate call works.
- **Ch 3**: applies these models with standard ChatGPT text-generation techniques.
- **Ch 4**: context-window limits lead to chunking, map reduce, and progressive summarization in LangChain.
- **Ch 5**: embeddings and vector distance become the basis of vector databases and RAG.
- **Ch 7**: the image-side counterpart (diffusion models) to this text-model primer.
