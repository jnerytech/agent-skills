# Chapter 1: The Five Principles of Prompting

## Core Idea
Prompt engineering is "the process of discovering prompts that reliably yield useful or desired results." A naive prompt is fine for throwaway use. A production prompt has to be engineered against five common failures (vague direction, unformatted output, missing examples, limited evaluation, no task division), and the five model-agnostic principles map one-to-one onto those failures.

## Frameworks Introduced

- **The Five Principles of Prompting** (first published July 2022 in the blog post "Prompt Engineering: From Words to Art and Copy"; they closely match OpenAI's later Prompt Engineering Guide):
  1. **Give Direction**: describe the desired style in detail, or reference a relevant persona.
  2. **Specify Format**: define what rules to follow, and the required structure of the response.
  3. **Provide Examples**: insert a diverse set of test cases where the task was done correctly.
  4. **Evaluate Quality**: identify errors and rate responses, testing what drives performance.
  5. **Divide Labor**: split tasks into multiple steps, chained together for complex goals.
  - When to use: for any prompt you will reuse or ship to production, on any text or image model.
  - How: diagnose the naive prompt against the five failure modes (each principle fixes one), then apply them in order. Direction comes first because it is cheap and the evidence favors it.
  - Why it works: an LLM predicts the next token (about 3/4 of a word) by probability, with randomness controlled by **temperature**. Everything in the prompt shifts the probability of every generated token. "Average prompts will return average responses." The principles are conventions that work "for any level of intelligence, biological or artificial," so they outlast specific models. Prompt *templates* rarely transfer between models, but the principles do.

- **Role-playing (persona direction)**: ask for output "in the style of" a famous person or artist who is well represented in the training data (Steve Jobs gives i-prefixed names, Elon Musk gives X-names, Van Gogh gives brushstroke images).
  - When to use: subjective or creative tasks where you can't easily say what "good" means.
  - How: name the persona, and make your examples match that persona's style.
  - Principle(s): Give Direction.

- **Prewarming / Internal Retrieval** (Liu et al., 2021): first ask the model for best-practice advice on the task ("Please give me 5 tips for naming products based on expert industry advice."), then in the same chat ask it to do the task "Using this advice…". The model generates its own direction.
  - Variant: paste trusted external guidance into the prompt as rules to follow (for example, Brandwatch's 5 Golden Rules for naming a product). Quality goes up, but the prompt costs more because it is longer.
  - Principle(s): Give Direction.

- **Format specification for parseable output**: ask for JSON (or YAML) and leave the JSON *uncompleted* at the end of the prompt so the model completes it. Back this up with "Return only JSON," a system message ("You are a helpful assistant that only responds in JSON"), or model-level JSON mode (called **grammars** for Llama models). Run the result through a JSON parser (`json` library). A parse error triggers a retry.
  - Principle(s): Specify Format.

- **Zero-shot / One-shot / Few-shot**: zero, one, or several worked examples in the prompt. In the GPT-3 paper "Language Models are Few-Shot Learners," one example raised accuracy on some tasks from about 10% to nearly 50%.
  - How: 1–3 examples is easy and almost always helps. Past 3–5 examples, results become more reliable but less creative. Above 3, you must experiment with both the number of examples and how similar they are.
  - Principle(s): Provide Examples.

- **Img2Img (base image)**: in image models, the "example" is a base image URL or upload that the model generates from. Swap only the base image and the result changes radically. Check licensing first, because copyrighted base images break the providers' terms of service.
  - Principle(s): Provide Examples.

- **Blind A/B testing of prompt variants** (the evaluation workflow for this chapter):
  - When to use: when a prompt is reused or in production. Go "just one step above basic trial and error."
  - How: (1) define variants (for example zero-shot vs few-shot); (2) run each N times (N=5 here) and store variant/prompt/response in a CSV; (3) shuffle and rate *blind* with thumbs-up/down (1/0) without seeing the prompt; (4) group by variant and compare the mean score.
  - Principle(s): Evaluate Quality.
  - Failure mode: manual rating gets tedious, and your ratings may not reflect your audience's preferences. Still, "usually in less than 10 test runs of a prompt you uncover a deviation" that you would otherwise only find in production.

- **Programmatic evaluation against ground truth**: when reference answers exist (math, classification), score automatically so testing can scale. See the criteria table below.
  - Principle(s): Evaluate Quality.

- **Permutation Prompting** (image evaluation): write a prompt with `{a, b, c}` option sets. Midjourney expands it to every combination (3 formats × 2 people-counts = 6 prompts). Arrange the outputs in a grid to see the effect of each element. With API models (Stable Diffusion), fix the **random seed** for reproducibility.
  - Principle(s): Evaluate Quality.

- **Self-evaluation chain**: a second call rates the first call's output ("Rate this list of product names… out of 10, inline"). It can be split further into separate ratings per criterion (clarity, memorability, USP) that a human or code combines.
  - Why it works: while generating, the model can't see where the whole response will end up. Given the finished response, it can easily judge good vs bad. That is why it suggests names it later rates as worst (for example "OneSize Glovewalkers").
  - Principle(s): Divide Labor + Evaluate Quality.

- **Chain of Thought / "Let's think step by step"**: appending this phrase to a single prompt improves reasoning and gives an audit trail. Ratings become more consistent with the criteria. OpenAI calls this **"giving the model time to think."** It amounts to dividing labor inside one prompt.
  - Principle(s): Divide Labor.

- **Meta Prompting**: use an AI model to write a prompt for an AI model. The chapter's chain: product name → ChatGPT detailed description → "Convert this description into a short prompt for an AI image generation model such as DALL-E" → image. It works "because LLMs are human-level prompt engineers" (Zhou, 2022).
  - Principle(s): Divide Labor.

- **AI Chaining / Progressive Summarization**: chain several prompts (and models). For example, split text too large for the context window into chunks, summarize each chunk, then summarize the summaries. LangChain provides tooling for this (Ch 4).
  - Principle(s): Divide Labor.

- **ReAct (Reason and Act)**: an early agent pattern (BabyAGI, AgentGPT, Microsoft AutoGen) that chains calls to plan, observe, act, and evaluate. It was still error-prone and rare in production at the time of writing (Ch 6).
  - Principle(s): Divide Labor.

## Key Concepts
- **Prompt**: the input (usually text) that instructs a model to predict the desired response.
- **Token**: the unit LLMs predict, about 3/4 of a word. OpenAI bills by prompt plus response tokens.
- **Temperature**: the parameter that controls randomness in next-token selection.
- **Blind prompting**: trial and error with no feedback loop. Acceptable only for one-off prompts.
- **Evals**: standardized question sets with predefined answers or grading criteria, used to benchmark models (OpenAI open-sourced its evals framework). Stronger models (GPT-4) can grade weaker ones, as was done for Vicuna-13B.
- **Ground truth**: reference answers to test cases that make programmatic rating possible.
- **Elo rating**: aggregate relative ranking from side-by-side comparisons, as in lmsys Chatbot Arena. The next step up from 3/5/10-point scales.
- **Fine-tuning crossover**: rated outputs can become fine-tuning data. Fine-tuning "starts to beat prompt engineering once you can supply a few thousand examples."
- **Context window**: how much the model can take in per call (GPT-4 8,192 standard → 128K; Claude 2 100K; Gemini 1.5 1M; one Harry Potter book ≈ 185K tokens).
- **Task decomposition**: the engineering habit of splitting a problem into parts, solving each, and recombining. This is the basis of Divide Labor.

## Mental Models
- Think of a prompt as a **creative brief to an agency**: ask what context a human would need to do the task well, and put it in the prompt.
- Think of LLMs as **universal translators**: between languages, but also between formats (JSON↔YAML, natural language↔Python). The format is yours to dictate.
- Use **Give Direction before Provide Examples**: direction is cheaper, good examples are hard to collect, and there is evidence (Hsieh et al., 2023) that direction works better.
- **Direction = style; Format = output type.** "Steve Jobs" or "Van Gogh" is direction, while "JSON" or "stock photo" is format. When they clash, drop whichever matters less.

## Anti-patterns
- **Vague direction**: with no style or attributes stated, the model guesses, and subjective tasks have a low chance of matching what you want.
- **Unformatted output**: the format flips between runs (numbered list vs inline, preamble text) and breaks parsing in production.
- **Missing examples**: the output drifts to "an average of the internet," with all its bias.
- **Over-direction / conflicting constraints**: too many specifics (base image + "stock photo" + camera model + "Van Gogh") can have no consistent training samples, so the model can't satisfy all of them. Choose the most important element and drop the rest. Too *little* direction is still the more common problem.
- **Too many look-alike examples**: past 3–5 low-diversity examples, output is over-constrained (all-animal examples → only animal names), creativity drops, and edge cases are handled badly.
- **Assuming a prompt transfers across models**: there is no guarantee. Re-evaluate on every new model.
- **Bloated prompts left untested**: iteration often shows that many elements are "completely superfluous, or even counterproductive." Shorter prompts that perform as well cut cost and latency.
- **Hardcoding API keys**: use environment variables or a `.env` file (`python-dotenv`).

## Code Examples
```python
# Generate N responses per prompt variant and save for rating
# (OpenAI SDK v1 style, 2024 edition; model was gpt-3.5-turbo)
def get_response(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

responses = []
num_tests = 5
for idx, prompt in enumerate(test_prompts):
    var_name = chr(ord('A') + idx)  # prompt number as a letter
    for i in range(num_tests):
        response = get_response(prompt)
        responses.append({"variant": var_name, "prompt": prompt, "response": response})

df = pd.DataFrame(responses)
df.to_csv("responses.csv", index=False)
```
- **What it demonstrates**: the data-collection half of A/B testing. It runs each variant several times so you can see variance, such as zero-shot returning a numbered list while few-shot returns the requested inline list.

```python
# Blind rating: shuffle, then score 1/0 per response, then summarize by variant
df = pd.read_csv("responses.csv")
df = df.sample(frac=1).reset_index(drop=True)   # shuffle so ratings are blind
df['feedback'] = pd.Series(dtype='str')
# ... ipywidgets thumbs-up (1) / thumbs-down (0) buttons write df.at[i, 'feedback'] ...
summary_df = df.groupby('variant').agg(
    count=('feedback', 'count'),
    score=('feedback', 'mean')).reset_index()
```
- **What it demonstrates**: the rating half. Shuffling hides which prompt produced each response, and the group-by gives a per-variant success rate. Outside Jupyter, replace the widgets with an `input()` loop asking Y/N.

## Reference Tables

**Programmatic evaluation criteria** (from the book's non-exhaustive list):

| Criterion | What to measure |
|---|---|
| Cost | Token-heavy prompts, or prompts that only work on expensive models, may be impractical |
| Latency | More tokens or bigger models mean slower responses and worse UX |
| Calls | Multi-call loops slow the system down |
| Performance | External feedback (e.g. physics engine, model predicting real-world results) |
| Classification | How often labels are correct (via another model or rules) |
| Reasoning | Logic or math failures against reference cases |
| Hallucinations | Invention of terms not in the prompt's context |
| Safety | Unsafe output caught by a safety filter or detector |
| Refusals | Wrongful refusals, flagged by known refusal language |
| Adversarial | Robustness to known prompt-injection attacks |
| Similarity | BLEU/ROUGE word overlap or vector distance (Ch 5) to reference text |

**Naive-prompt failure → principle:**

| Failure | Principle |
|---|---|
| Vague direction | Give Direction |
| Unformatted output | Specify Format |
| Missing examples | Provide Examples |
| Limited evaluation | Evaluate Quality |
| No task division | Divide Labor |

## Worked Example
**Product name generator: naive vs engineered.**

Naive: `Can I have a list of product names for a pair of shoes that can fit any foot size?` → a long, unnumbered, inconsistently formatted list (UniFit SoleStrides, FlexiSize All-Fit Shoes, …).

Engineered (Direction + Format + Examples):
```
Brainstorm a list of product names for a shoe that fits any foot size, in the style of Steve Jobs.
Return the results as a comma-separated list, in this format:
Product description: A shoe that fits any foot size
Product names: [list of 3 product names]

## Examples
Product description: A refrigerator that dispenses beer
Product names: iBarFridge, iFridgeBeer, iDrinkBeerFridge
Product description: A watch that can tell accurate time in space
Product names: iNaut, iSpace, iTime
Product description: A home milkshake maker
Product names: iShake, iSmoothie, iShake Mini
```
Output: `Product names: iFitFoot, iPerfectFit, iShoeSize`.

The persona is swappable by the user. The format is parseable and can feed another prompt. The examples can be refreshed from user feedback so the system improves over time.

Evaluation: the A/B test of zero-shot (A) vs few-shot (B, two examples), 5 runs each and rated blind, gave **A = 0.2, B = 0.6**. Labor was then divided: a rating call scores each name /10, "Let's think step by step" makes the scores criteria-consistent, and meta prompting turns the winning name into a description and then a DALL-E/Midjourney image prompt.

## Key Takeaways
1. A naive prompt is fine for one-offs. Anything reused or shipped should be engineered against the five failure modes, because mistakes cost tokens and fix-up time.
2. Try Give Direction first (persona, rules, prewarming), then Specify Format (JSON + parser + retry), then Provide Examples (1–3 diverse examples; test before going above that).
3. Move from blind prompting to blind A/B testing. Even 5–10 runs per variant reveal large differences and edge cases before production.
4. Use evaluation to *shorten* prompts as well as improve them. Leaner prompts that perform as well cut cost and latency.
5. Models judge finished output better than they generate it, so chain a self-evaluation step, use "Let's think step by step," and use meta prompting across models.
6. Principles transfer across models and templates don't. Re-evaluate whenever you change models.

## Connects To
- **Ch 2**: tokens, next-token probability, and context windows explain *why* the principles work.
- **Ch 3**: standard text-generation techniques (lists, JSON/YAML, role prompting, chain of thought, ELI5), each tagged with these principles.
- **Ch 4**: LangChain implements AI chaining, prompt templates, and progressive summarization (Divide Labor).
- **Ch 5**: vector distance as a similarity eval, and retrieval as dynamic context (Give Direction).
- **Ch 6**: ReAct and autonomous agents as Divide Labor at scale.
- **Ch 7–9**: image-side counterparts: art-style direction, format modifiers, Img2Img, permutation grids, seeds.
- **Ch 10**: applies all five principles in one application.
- **LLM-as-judge / Elo arenas**: external evaluation practice (lmsys Chatbot Arena, OpenAI evals).
