# Chapter 3: Standard Practices for Text Generation with ChatGPT

## Core Idea
A toolkit of simple, repeatable text-prompting techniques: shape output into parsable formats (lists, JSON, YAML, CSV, Mermaid), transform text (ELI5, translation, style unbundling, summarization), manage length with chunking and token counting, and raise reliability with role prompting, reference text, thinking time, self-evaluation, majority vote, LLM-as-evaluator and meta prompting. Each technique applies one or more of the Five Principles.

## Frameworks Introduced
- **Optimized List Generation**: state the list size, the filter (e.g. "male"), the item format ("only the name, never the film"), "never include any commentary", and add an example list.
  - When to use: any list that downstream code will split or parse.
  - How: fix the count, the bullet style and the per-item content, ban preamble, and show 3–5 example items.
  - Principle(s): Provide Examples, Specify Format.
  - Why it works / failure mode: a naive "Generate a list of Disney characters" returned 30 numbered items with preamble and mixed "(The Jungle Book)" suffixes, which breaks a parser expecting bullets. LLMs also don't guarantee counts (ask for 10, get 8), so validate the length or tolerate variation in code.
- **Hierarchical List Generation + Regex Parsing**: ask for a "hierarchical and incredibly detailed" outline with an example of the nesting, then parse it with `re`.
  - When to use: nested output such as article outlines.
  - How: "Hierarchical" makes the model nest items. "Incredibly detailed", "very long" or "include at least 10 top-level headings" makes the output longer. Parse with `r'\* (.+)'` for headings and `r'\s*([a-z]\..+)'` for subheadings, going line by line into a dict.
  - Note (When to Avoid Using Regular Expressions): regex control flow gets complicated fast. Switch to JSON or YAML once the structure grows.
- **Generating JSON**: give the task, the format and an example JSON payload, plus explicit guardrails.
  - How: add "You must follow the following principles: Only return valid JSON. Never include backtick symbols such as: `. The response will be parsed with json.loads(), therefore it must be valid JSON."
  - Principle(s): Give Direction, Provide Examples.
  - Failure modes: a "Sure here's the JSON:" preamble, a ```json fence, invalid payloads (unescaped characters, truncation from size).
- **YAML Generation & Filtering YAML Payloads (LLM as reasoning engine)**: give a YAML schema, let the model update quantities from a free-text User Query, filter out items not in the schema, and return `"No Items"` if nothing is left.
  - When to use: cleaning or validating user input, and handing control-flow decisions to the LLM instead of code (Fig. 3-1).
  - How: write the rules as bullets, then the `# schema:`, then "return only a valid .yml… Do not provide any commentary." Three possible outcomes: valid, filtered, `No Items`.
  - Why YAML over JSON: no character escaping (indentation replaces braces and commas), better readability, and comments are supported.
- **Handling Invalid Payloads**: defensive parsing in code. Define custom exceptions (`InvalidResponse`, `InvalidItemType`, `InvalidItemKeys`, `InvalidItemName`, `InvalidItemQuantity`, `InvalidItemUnit`), run `yaml.safe_load`, and check the type, keys, value types, schema membership, max quantity and allowed units before passing the result downstream.
  - Principle(s): Evaluate Quality.
- **Diverse Format Generation**: ask for Mermaid flowcharts (`graph TD …`), mock CSV, code, conversations or scripts. Name the format explicitly, because the format name carries conventions (CSV means comma separators).
- **Explain It like I'm Five (ELI5)**: "Explain the following text as if I was 5 years old. Explain it like I'm 5. Text: …"
  - When to use: turning technical documents (e.g. a cancer-research abstract) into summaries anyone can read.
- **Universal Translation Through LLMs**: chain transformations (simple text → complex → simple Spanish → English). Some meaning is lost but most of the intent survives. It works well only for languages, and programming languages, with plenty of training data.
- **Ask for Context**: let the model either answer or ask for what it needs.
  - How: (1) ask the question; (2) ask "Provide a list of requirements that would help you to make an informed and high-quality decision"; (3) re-ask with a `Context:` block that answers those requirements. Default key phrase: **"If you need more context, please specify what would help you to make a better decision."**
  - Related: AutoGPT's self-evaluation step is an actor-critic check on whether the context is enough before acting.
- **Text Style Unbundling**: extract a document's textual features (tone of voice, length, vocabulary and phrasing, structure, content) into a style guide, then generate new content with it.
  - How: use a meta prompt such as "Analyze the following text and identify core features that will allow further documents to imitate the same style… Provide all of the features as a style writing guide", then "Write a new blog post on [topic] using the same tone of voice, length, vocabulary, and structure as the previously analyzed text." Combine with **reference text** to get branded content that is grounded in facts.
  - Benefits: brand consistency, faster content creation, adaptability. The same approach covers **extracting specific textual features** such as entities and sentiment.
- **Summarization (incl. under context window limits)**: chunk → summarize each chunk → combine into a final summary (Fig. 3-4). Tailor summaries to the reader: A = key insights, B = decision-making info, C = collaboration. Steer the focus with something like "Provide a concise, abstractive summary of the above text. Only summarize the advantages: …"
- **Chunking Text**: split by sentence, paragraph, topic, complexity, length or tokens (see table).
  - Principle(s): Divide Labor, Evaluate Quality. Define the granularity, then tune the token count and temperature.
  - Good chunking keeps whole words (ideally whole sentences and points), handles sentences that cross page breaks, and keeps each chunk within the context window.
- **Sliding Window Chunking**: overlapping windows of `window_size` characters that advance by `step_size`. A small step means more duplication but less information lost between chunks. Use a larger overlap when accuracy and semantic context matter more than token cost or request count.
- **Least to Most**: a chain of prompts where each builds on the previous answer, going from general to detailed. Example: Flask "Hello World" architecture outline → route code → unit test.
  - Benefits: progressive exploration, flexibility, better comprehension, collaborative learning.
  - Challenges: the chat history overflows the context window so early tasks are forgotten, and every step depends on the quality of the step before.
  - Principle(s): Divide Labor, Evaluate Quality (check each prior response before the next step).
- **Role Prompting**: "I want you to act as a tech reviewer… My first suggestion request is: MongoDB." Put the role in the **System Message** for chat models. See the Awesome ChatGPT Prompts list.
  - When to use: to get specific expertise, set a style or tone, encourage creative output, explore other perspectives, or make the interaction more engaging.
  - Challenges: bias or stereotyping from the role, and the model drifting out of role in long conversations. Principle(s): Give Direction, Evaluate Quality.
- **GPT Prompting Tactics (OpenAI-recommended)**:
  - **Avoiding Hallucinations with Reference**: "Refer to the articles enclosed within triple quotes… If the answer isn't found, return 'I could not find an answer'." A variant asks for citations (`{"citation": …}`) or "Insufficient information." Citations can be checked automatically by string-matching them against the source. With limited context windows this needs dynamic retrieval (leads to ch05). Principle(s): Give Direction, Specify Format.
  - **Give GPTs "Thinking Time"**: "First, try to solve the problem on your own. Then, see if your answer matches the proposed solution. Don't judge the given answer until you've tried solving it yourself."
  - **Inner Monologue Tactic**: the model writes its working, its comparison with the user's answer and its hint plan inside `"""` delimiters, and only the final `Hint:` is shown to the user. Strip the delimited parts in code. Use for tutoring, where showing the reasoning would give the answer away.
  - **Self-Eval LLM Responses**: send the previous output back with "can you improve it again… Perhaps defaults or type hints?" You can repeat this until the model stops suggesting improvements.
- **Classification with LLMs**: zero-shot (no examples) or few-shot (a few labeled examples, which also fixes the output format). Fast way to prototype and get a baseline accuracy. Traditional ML may still win on some problems. Use cases: reviews, email intent, social sentiment, news topics, résumé screening. Sending sensitive data to the API carries a leakage risk.
- **Majority Vote for Classification**: run the same classification several times and take the most frequent label. This reduces variance and outliers, at the cost of extra latency and spend.
- **Criteria Evaluation (LLM-as-evaluator / synthetic evaluation)**: use a stronger model (GPT-4) to grade a weaker one's outputs (GPT-3.5-turbo) on one criterion, e.g. "You only respond with a 1 if the response is concise, and a 0 if it is not."
  - **Evaluate the evaluator**: build test cases with and without a known issue, then count false positives (issue hallucinated) and false negatives (issue missed).
  - Costs about 10× less than human rating and takes minutes instead of days. Run cheap programmatic checks first (e.g. response length). Principle(s): Evaluate Quality.
- **Meta Prompting**: prompts that write other prompts. Example: write a children's book with GPT-4, then have it write Midjourney or Stable Diffusion prompts for each scene (Fig. 3-8).
  - Uses: image prompts from product descriptions, style/feature prompts (copywriting guides), and **optimizing Prompt A to reach Goal 1**.
  - How: "Act as a GPT Prompt Engineer… Return only a single prompt, never return the output of a prompt… Bullet point out any important features." Then critique and refine it, optionally adding web pages as extra examples.

## Key Concepts
- **Few-shot prompting**: adding examples to the prompt. Even a small rephrase with examples changes the output a lot.
- **LLM as reasoning engine**: the LLM makes control-flow decisions (filter, validate, route) that you would otherwise code.
- **Reference text**: documents given as ground truth so the model answers from them, not from memory.
- **Context length**: `maximum_context_length = input_tokens + output_tokens`. Overflow causes truncated output or rejected requests.
- **Chunking**: breaking text into units (sentence, paragraph, topic, complexity, length, tokens) to fit the context, cut cost, speed up processing and allow per-chunk work.
- **Sentence detection (sentence boundary disambiguation)**: finding where sentences start and end, e.g. with spaCy `en_core_web_sm`.
- **Tiktoken / BPE**: OpenAI's fast byte pair encoding tokenizer. Encodings: `cl100k_base`, `p50k_base`, `r50k_base`. Tokens can be one character or a whole word and often include a leading space.
- **Chat message roles**: `system` (instructions and persona; optional, the default behaves like "You are a helpful assistant"), `user`, `assistant`. Few-shot examples can be sent as `system` messages with `name: example_user` / `example_assistant`.
- **Sentiment analysis**: classifying a text's tone (positive, negative, neutral). Its known weak spots are sarcasm/irony and context-specific jargon.
- **Synthetic evaluation**: LLM-based grading as a cheaper, faster stand-in for human raters.

## Mental Models
- Use **JSON/YAML over regex** once structure is nested. Regex is fine for a flat or two-level list but its control flow becomes fragile as the format grows.
- Think of the prompt's **"You must follow the following principles:" bullet block** as a format contract. It shows up everywhere in this chapter (JSON, classification, meta prompts).
- Use **sentence/paragraph chunking** when meaning matters and **token chunking** when hitting the limit exactly matters. Use a **sliding window** to keep context across cut points.
- Think of a **single classification as one noisy sample**. Majority vote and evaluator testing turn it into a measured estimate.

## Anti-patterns
- **Leaving size, format and commentary unspecified**: output varies between runs and breaks parsers.
- **Trusting requested counts**: "10 headings" may come back as 8.
- **Parsing raw JSON without guardrails**: preamble text and ```json fences make `json.loads` fail.
- **Word-level chunking / naive fixed-character splits**: loses context, cuts words and sentences in half, and raises processing load.
- **Vague classification prompts**: "Is this text positive or negative?" returns "mixed tone" prose. Specify the labels, examples, a single-word output, and how to handle mixed cases.
- **Long role-play or least-to-most chains without checks**: role drift, forgotten early context, and errors that compound.
- **Using an LLM evaluator unvalidated**: it may report problems that aren't there or miss real ones. Test it on known cases first.
- **Sending emails, résumés or other sensitive data**: risk of leakage into future training data.

## Code Examples
```python
# Parse hierarchical list into a dict (Example 3-2)
section_regex = re.compile(r"\* (.+)")
subsection_regex = re.compile(r"\s*([a-z]\..+)")
result_dict = {}
current_section = None
for line in openai_result.split("\n"):
    section_match = section_regex.match(line)
    subsection_match = subsection_regex.match(line)
    if section_match:
        current_section = section_match.group(1)
        result_dict[current_section] = []
    elif subsection_match and current_section is not None:
        result_dict[current_section].append(subsection_match.group(1))
```
- **What it demonstrates**: going line by line with a "current section" state to turn LLM text into nested data.

```python
def sliding_window(text, window_size, step_size):
    if window_size > len(text) or step_size < 1:
        return []
    return [text[i:i+window_size]
            for i in range(0, len(text) - window_size + 1, step_size)]

import tiktoken
def count_tokens(text_string: str, encoding_name: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(text_string))
count_tokens("Hello world! This is a test.", "cl100k_base")  # 8
```
- **What it demonstrates**: overlapping chunking, and exact token counts for checking budget against the context window. (`num_tokens_from_messages` extends this to chat payloads: about 3 tokens per message, +1 per name, +3 to prime the reply. These per-model constants are for 2023-era models.)

```python
responses = []
for i in range(0, 3):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": base_template.format(content=text)}])
    responses.append(response.choices[0].message.content.strip())

def most_frequent_classification(responses):
    count_dict = {}
    for classification in responses:
        count_dict[classification] = count_dict.get(classification, 0) + 1
    return max(count_dict, key=count_dict.get)
```
- **What it demonstrates**: majority vote over repeated few-shot classifications (OpenAI SDK v1 style, as of the 2024 edition).

## Reference Tables
**Table 3-1. Chunking strategies**

| Splitting strategy | Advantages | Disadvantages | Good for |
|---|---|---|---|
| Sentence | Preserves context, suits many tasks | Inefficient for very long content | Summarization, translation, sentiment |
| Paragraph | Handles longer content, cohesive units | Less granular, may miss subtle links | Document analysis, topic modeling, extraction |
| Topic/section | Identifies main themes | Needs topic identification, misses fine detail | Classification, recommendations, clustering |
| Complexity | Groups by reading level, adaptive | Needs a complexity measure | Readability, content adaptation, personalized learning |
| Length | Handles very long content efficiently | Loses context, more preprocessing | Large-scale analysis, indexing, preprocessing |
| Tokens (tokenizer) | Exact counts, stays within limits | Tokenization overhead | Fitting prompts to the context window |

**When to chunk / not chunk**: chunk large documents (over the token limit), complex analyses and multi-topic documents. Don't chunk short documents, simple analyses or single-topic documents.

**Tiktoken encodings (2024)**: `cl100k_base` for GPT-4, GPT-3.5-turbo and text-embedding-ada-002. `p50k_base` for Codex, text-davinci-002/003. `r50k_base` (gpt2) for GPT-3 davinci.

**Sentiment preprocessing**: remove special characters (emojis, hashtags, punctuation), lowercase, correct spelling, and include domain-specific content in the prompt.

## Worked Example
**Sentiment prompt, before and after.**
Before: "Is this text positive or negative? I absolutely love the design of this phone, but the battery life is quite disappointing." The model returns a paragraph about a "mixed tone". The prompt has three gaps: no output format, no examples, and no rule for mixed sentiment.

After:
```
Using the following examples as a guide:
positive: 'I absolutely love the design of this phone!'
negative: 'The battery life is quite disappointing.'
neutral: 'I liked the product, but it has short battery life.'
Only return either a single word of:
- positive
- negative
- neutral
Please classify the sentiment of the following text as positive, negative, or neutral: I absolutely love the design of this phone, but the battery life is quite disappointing.
```
Output: `neutral`. The fixed prompt states the task, gives an example for each class (including how to label mixed text), and specifies a single-word output, so the result can be parsed and aggregated, e.g. with majority vote.

## Key Takeaways
1. Specify count, item format, filters and "no commentary", and add examples. That alone makes list and structured output parsable.
2. Prefer JSON or YAML (YAML: no escaping, readable, comments allowed) over regex. Always validate the parsed result in code with typed exceptions.
3. The LLM can make control-flow decisions (filter against a schema, ask for more context) that you would otherwise write by hand.
4. Choose the chunking strategy for the task: semantic splits keep meaning, token splits keep you within limits, and sliding windows keep context across chunk boundaries. Count tokens with tiktoken.
5. Reliability tactics: reference text with a fallback answer, thinking time, inner monologue, self-evaluation, majority vote.
6. Use a stronger LLM as a cheap evaluator, but measure its false positive and false negative rates first, and run programmatic checks before any LLM call.
7. Meta prompting (prompts that write prompts) is behind style unbundling, image-prompt generation and prompt optimization.

## Connects To
- **Ch 1**: every technique here applies one of the Five Principles. Criteria evaluation automates Ch1's thumbs-up/down rating.
- **Ch 2**: tokens, context windows and BPE tokenization explain why chunking and tiktoken are needed.
- **Ch 4**: LangChain replaces the hand-rolled output parsers, text splitters, prompt chains (least to most) and summarization pipelines.
- **Ch 5**: "dynamically retrieving relevant information" for reference-text prompts becomes RAG with FAISS/Pinecone, which relies on chunking.
- **Ch 6**: ask-for-context, self-evaluation and the AutoGPT actor-critic step lead into autonomous agents.
- **Ch 7–9**: meta prompting produces the Midjourney and Stable Diffusion prompts.
- **Ch 10**: style unbundling, chunked summarization and LLM evaluation come together in a full application.
