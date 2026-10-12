# Chapter 2: Executing prompts programmatically

## Core Idea
Prompts can be sent programmatically via the OpenAI Completions API or LangChain's `ChatOpenAI`, parametrized with `PromptTemplate`, and progressively strengthened with in-context learning (zero/one/two/few-shot, chain-of-thought) when a task exceeds the LLM's zero-shot ability.

## Frameworks Introduced
- **OpenAI Completions API (`client.chat.completions.create`)**: the primary programmatic interface to OpenAI LLMs, called with `model` and a `messages` list of `{role, content}` dicts (roles: system, user, assistant).
  - When to use: direct, framework-free calls, or when you need Completions semantics (supported by many open-source LLMs too, unlike the newer Responses API).
  - How: instantiate `OpenAI(api_key=...)`, call `.create(model=..., messages=[...])`, read `response.choices[0].message.content`.
- **LangChain `ChatOpenAI`**: a wrapper around OpenAI (and other) chat models that unifies invocation behind `.invoke(prompt)`.
  - When to use: as soon as you want to build chains/apps rather than one-off calls; the book uses Completions indirectly through this wrapper throughout.
  - How: `ChatOpenAI(openai_api_key=..., model_name="gpt-5-nano")`, then `llm.invoke(prompt_input)` → `.content`.
- **LangChain `PromptTemplate`**: parametrized prompt object with `{variable}` placeholders, replacing hand-rolled f-string functions.
  - When to use: any prompt reused with varying inputs (text, tone, length, etc.).
  - How: `PromptTemplate.from_template("...{var}...")`, then `.format(var=value)` to produce the final prompt string.
- **LangChain `FewShotPromptTemplate`**: composes a list of example dicts with an `example_prompt` template and a `suffix` template, separating training examples from the prompt shell.
  - When to use: few-shot tasks where hardcoding examples inline in a single string is unmaintainable.
  - How: define `examples` (list of dicts), an `example_prompt` PromptTemplate matching those keys, and a `FewShotPromptTemplate(examples=..., example_prompt=..., suffix=..., input_variables=[...])`; format with the remaining runtime variable.
- **Chain of Thought (CoT) prompting** (Wei et al., https://arxiv.org/abs/2201.11903): few-shot examples that each include the explicit reasoning steps leading to the answer, not just the answer.
  - When to use: reasoning tasks where the model gets the right components but combines them wrong (e.g., misses a palindrome), especially when steps are deterministic.
  - How: for each example, show the input, the step-by-step reasoning, then the result; the model imitates the reasoning pattern, not just the output format.

## Key Concepts
- **In-context learning**: instructing an LLM on an unfamiliar task using examples inside the prompt itself, rather than fine-tuning; cheaper and requires no GPU/training pipeline.
- **Zero-shot learning**: no examples given; the LLM must perform the task from the instruction alone.
- **One-shot / Two-shot / Few-shot learning**: providing one, two, or several examples respectively to teach a task pattern via the prompt.
- **Chain of Thought (CoT)**: few-shot examples annotated with the logical steps used to reach each answer.
- **Tree of Thought (ToT)**: extends CoT by letting the model explore and evaluate multiple reasoning paths instead of one linear chain (https://arxiv.org/abs/2305.10601); strong on tasks needing backtracking/planning (e.g., Game of 24: 74% success vs 4% for CoT with GPT-4).
- **Thread of Thought (ThoT)**: a modular technique for filtering noise and staying focused when the context is chaotic/irrelevant-detail-heavy (https://arxiv.org/abs/2311.08734).
- **Prompt structure**: the generalized set of prompt sections — Persona, Context, Instruction, Input, Steps, Tone, Output format, Examples.
- **XML-style prompt tags**: wrapping each prompt section in tags like `<Persona>...</Persona>` to make section boundaries explicit to the model — recommended by both OpenAI and Anthropic guidelines, and backed by "The Prompt Report" (https://arxiv.org/abs/2406.06608).

## Mental Models
- **Prompt = checklist, not fixed template**: Persona/Context/Instruction/Input/Steps/Tone/Output/Examples is a menu — include only the sections a given task needs, and it's fine to leave some sections unnamed while naming others (e.g., name "Examples" but leave "Tone" implicit).
- **Escalate in-context learning only as far as needed**: try zero-shot first; if wrong, add one example; if still wrong, add a second; if still wrong, add explicit steps or full CoT. Each rung costs more tokens, so stop at the first rung that works.
- **Newer models can obsolete your prompt engineering**: a technique built to correct a model's error (e.g., the palindrome CoT prompt) may become unnecessary once a newer model version fixes the underlying weakness — don't over-invest in permanent workarounds for a model's current limitations.
- **Separate structure from data**: `PromptTemplate`/`FewShotPromptTemplate` exist so prompt shape (instructions, format) lives apart from the variable data (text, examples, numbers) — mirrors code/config separation.

## Anti-patterns
- **Hardcoding few-shot examples directly into an f-string**: works but couples training data to prompt text, making examples hard to swap/maintain — use `FewShotPromptTemplate` instead.
- **Asking for a classification without specifying output format**: produces verbose, hard-to-parse prose (e.g., a full sentence instead of just "Tech"); always add an `OUTPUT` constraint when you need a clean label.
- **Skipping steps for deterministic multi-step reasoning**: leaving the LLM to invent its own steps for tasks with a known correct procedure (like "identify palindromes, then sum them") risks it skipping edge cases (e.g., missing that 99 is a palindrome) — spell out the steps explicitly.
- **Assuming zero-shot will handle novel rule systems**: the model will say it can't classify against rules it doesn't know (e.g., the Abra/Kadabra game) rather than hallucinate — you must supply examples or a rule explanation.

## Code Examples
```python
from openai import OpenAI
import getpass
OPENAI_API_KEY = getpass.getpass('Enter your OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

prompt_input = """Write a concise message to remind users to be
vigilant about phishing attacks."""
response = client.chat.completions.create(
    model="gpt-5-nano",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt_input}
    ]
)
print(response.choices[0].message.content)
```
- **What it demonstrates**: minimal prompt execution against the raw OpenAI Completions API, including the system/user message-role convention.

```python
from langchain_core.prompts import PromptTemplate

prompt_template = PromptTemplate.from_template(
    """You are an experienced copywriter. Write a {num_words} words
summary of the following text, using a {tone} tone: {text}""")

prompt = prompt_template.format(
    text=segovia_aqueduct_text,
    num_words=20,
    tone="knowledgeable and engaging")

response = llm.invoke(prompt)
print(response.content)
```
- **What it demonstrates**: LangChain's `PromptTemplate` replacing a hand-written Python f-string function for parametrized prompts.

```python
examples = [
    {"number": 6, "reasoning": "not divisible by 5 nor by 7", "result": "None"},
    {"number": 15, "reasoning": "divisible by 5 but not by 7", "result": "Abra"},
    {"number": 12, "reasoning": "not divisible by 5 nor by 7", "result": "None"},
    {"number": 21, "reasoning": "divisible by 7 but not by 5", "result": "Kadabra"},
    {"number": 70, "reasoning": "divisible by 5 and by 7", "result": "Abra Kadabra"}
]
example_prompt = PromptTemplate(
    input_variables=["number", "reasoning", "result"],
    template="{number} \\ {reasoning} \\ {result}")
few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    suffix="Classify the following numbers as Abra, Kadabra "
           "or Abra Kadabra: {comma_delimited_input_numbers}",
    input_variables=["comma_delimited_input_numbers"]
)
prompt_input = few_shot_prompt.format(
    comma_delimited_input_numbers="3, 4, 5, 7, 8, 10, 11, 13, 35.")
response = llm.invoke(prompt_input)
print(response.content)
```
- **What it demonstrates**: `FewShotPromptTemplate` cleanly separating training examples from the prompt shell, versus hardcoding them in a single string.

## Reference Tables

**Table 2.1 — Prompt types and examples**

| Prompt type | Prompt example |
|---|---|
| Text classification | Classify the following text into one of these categories: history, tech, gardening. |
| Sentiment analysis | Classify the following text as positive, neutral, or negative. |
| Text summarization | Write a 30-word summary for the following text. |
| Composing text | Write a piece on the diver watches, mentioning the following facts: ... |
| Question answering | Read the following text, and tell me which home computers were popular in the 80s. |
| Reasoning | Add the square numbers in this sequence: 19, 13, 1, 17, 4, 64, 900. |

**Table 2.2 — In-context learning prompts**

| Technique | Explanation |
|---|---|
| Zero-shot learning | No example is provided in the prompt. |
| One-shot learning | One example is provided in the prompt. |
| Two-shot learning | Two examples are provided in the prompt. |
| Few-shot learning | A number of examples are provided in the prompt. |
| Chain of Thought (CoT) | Several examples are provided, each with the logical steps to reach the objective explained. |

**Prompt structure checklist**: Persona, Context, Instruction, Input, Steps, Tone, Output format, Examples.

## Worked Example
Goal: get an LLM to correctly sum the palindromes in `13, 1331, 121, 73, 99, 56, 232, 7` (correct answer includes 99, sums to 1790).

1. **Zero-shot** — `INSTRUCTION Sum the palindromes in this sequence: ...` → wrong: model misses 99, sums to 1691.
2. **One-shot** — add `EXAMPLE 33 is a palindrome` → still wrong, same 1691 result; one example wasn't enough signal.
3. **Two-shot** — add a second example, `44 is a palindrome` → still wrong, 99 still overlooked.
4. **Explicit steps (still few-shot)** — keep the two examples, add `Steps: 1) identify the palindromes; 2) add them up` → correct: model lists 1331, 121, 99, 232, 7 and sums to 1790.

Lesson demonstrated: when few-shot examples alone don't fix a systematic reasoning error, decomposing the task into explicit, numbered steps (a lightweight precursor to full CoT) closes the gap. The book notes that later GPT-5 versions solved this zero-shot, since the underlying model improved — illustrating that hand-tuned prompt scaffolding can become obsolete as models advance.

A related CoT worked example: classifying whether a sequence is "strange" (≥2 odd numbers whose sum is divisible by 3) fails zero-shot, but succeeds once given few-shot examples that each show the reasoning ("5 and 7 are odd; sum is 12; divisible by 3 // Strange") before the label — CoT blends few-shot examples with explicit per-example reasoning.

## Key Takeaways
1. Use the OpenAI Completions API (`messages=[{"role":..., "content":...}]`) for direct control, or LangChain's `ChatOpenAI.invoke()` when building toward chains — both return `.content`/`.choices[0].message.content` for the text.
2. Reach for `PromptTemplate` instead of Python f-string functions once a prompt needs reuse across varying inputs; use `FewShotPromptTemplate` once examples themselves need to vary or scale.
3. Escalate in-context learning incrementally: zero-shot → one-shot → two-shot → explicit steps/few-shot → full CoT — stop as soon as accuracy is acceptable, since more examples cost more tokens.
4. For deterministic multi-step reasoning, explicitly enumerate the steps in the prompt rather than trusting the model to infer them — this prevents systematic errors like missed edge cases.
5. Structure prompts from a checklist (Persona, Context, Instruction, Input, Steps, Tone, Output format, Examples); use only the sections a task needs, and consider XML-style tags (`<Persona>`, `<Instruction>`, ...) for stricter section delineation, per OpenAI/Anthropic guidance.
6. For advanced reasoning beyond CoT, Tree of Thought (multi-path exploration) suits strategic/backtracking tasks, and Thread of Thought suits noisy/chaotic contexts — both are modular extensions, not replacements, of CoT.
7. Always specify output format explicitly (e.g., "OUTPUT only the category") when you need clean, parseable results instead of verbose prose.

## Connects To
- **Ch 1**: introduces the three LLM application types (summarization engines, chatbots, AI agents) that this chapter's prompt techniques feed into.
- **Ch 3 (Summarization)**: builds LangChain Expression Language (LCEL) chains on top of the prompt/template foundations from this chapter.
- **Ch 11 (AI agents)**: returns to the Responses API, mentioned here as OpenAI's newer preferred interface for agent workflows, in contrast to the Completions API used throughout this book.
- **Fine-tuning**: the external contrasting concept to in-context learning — training a specialized model on domain data versus teaching via prompt examples at inference time.
