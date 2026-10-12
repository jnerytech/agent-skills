# Chapter 10: Building AI-Powered Applications

## Core Idea
Apply the Five Principles of Prompting end to end by breaking one naive "write a blog post" prompt into a chain of LangChain components: topic research, expert interview, outline, retrieval-augmented section writing, style rewrite, title optimization and image generation. The result is human-sounding content built on the user's own opinions and experience, and every step can be tested, logged and improved on its own.

## Frameworks Introduced
- **Five Principles as a prompt-audit checklist**: score an existing prompt against Direction, Format, Examples, Evaluation and Division before you build on it.
  - When to use: before productionizing any "long, sophisticated" prompt.
  - How (applied to the typical SEO blog prompt: tone, transition words, active voice, 1000+ words, 9 sections × 2 paragraphs, keywords, slug, meta description):
    - *Direction*: some instructions exist, but the output still sounds like AI rather than the user.
    - *Format*: count-based rules (9 sections, word counts) get ignored, because LLMs are bad at math.
    - *Examples*: there are none, so reliability suffers across topics and runs. Even one-shot would help a lot.
    - *Evaluation*: this is **blind prompting** (instructions added without testing). Some may do nothing except cost tokens, and some may hurt quality.
    - *Division*: one prompt does everything, so you can't tell which part succeeds or fails.
  - Principle(s): all five.
  - Why it works / failure mode: the naive prompt ("Write a blog post on {blogPostTopic}") gives short, generic content with no unique opinions or experience, which won't rank on Google. Adding more instructions to a single prompt doesn't fix that.

- **AI Blog Writing pipeline**: a chain of separate LangChain components, each maintainable and logged.
  1. **Topic Research**: SERP API → scrape the top 3 URLs (async Chromium/Playwright) → split (`RecursiveCharacterTextSplitter.from_tiktoken_encoder`, chunk 1500 / overlap 400) → summarize into Pydantic `DocumentSummary` objects.
  2. **Expert Interview**: `InterviewChain` makes the LLM generate 5 open-ended questions that target **information gain** beyond the SERP summaries. The user answers them through `input()`.
  3. **Generate Outline**: `BlogOutlineGenerator` turns topic + summaries + Q&A into a `BlogOutline` (title + `sub_headings`) through `prompt | ChatOpenAI() | PydanticOutputParser`.
  4. **Text Generation**: `ContentGenerator` vectorizes the scraped pages into Chroma, then writes each subheading with retrieval, custom memory and interview insights.
  5. **Writing Style**: rewrite the draft with a tested style-guide prompt (GPT-4).
  6. **Title Optimization**: generate options and A/B them with thumbs-up/down ratings.
  7. **AI Blog Images**: meta-prompt an image idea, then call Stable Diffusion XL in Corporate Memphis style.
  8. **User Interface**: a Gradio prototype for feedback.
  - Principle(s): Divide Labor (the chain), Give Direction (interview answers as unique context), Specify Format (Pydantic parsers), Evaluate Quality (style tests, title A/B, human feedback).
  - Why it works / failure mode: each stage adds a different kind of context (SERP facts, personal insight, structure, relevant snippets, prior sections). Splitting the work also lets you find and fix the weak step. The authors say the style rewrite is the hardest step and the only one that needed GPT-4.

- **Expert interview for information gain**: role prompt the LLM ("You are a content SEO researcher…"), give it the SERP summaries, and require exactly 5 open-ended (not yes/no) questions for insights *not already covered* in `{document_summaries}`, plus `{format_instructions}`.
  - Principle(s): Give Direction. Unique answers give the model unique context, which leads to fresher, more nuanced articles.

- **Writing-style extraction and Meme Unbundling**: ask the model to describe a known writer's style as bullet points ("Do not mention the writer or source, and respond only with bullet points: -", ending on `-` to force the format). Then mix and match the bullets from several writers (e.g. Harry Dry + Mike Taylor) into a target style.
  - When to use: making AI drafts sound human and on-brand, which cuts editing time. You should still disclose AI assistance.

- **Prompt optimization by embedding distance**: run each candidate prompt several times on several test cases and score the outputs by cosine distance to a hand-written reference (`text-embedding-ada-002`, LangChain's embedding evaluator). Lower is better.
  - Variants tested: A Control; B One-shot writing sample (describe the style from one sample); C Three-shot rewriting example (3 input/rewritten pairs → describe the style); D Three-shot writing sample (3 final samples only).
  - Rules: test across multiple cases with **10+ runs per case**, because nondeterminism can mislead you. Testing doesn't have to be systematized; even GitHub Copilot's evals were "haphazard and messy". Next steps are fine-tuning (OpenAI recommends ≥50 samples) or **DSPy**, which searches over instruction and few-shot combinations against your metric.
  - Principle(s): Evaluate Quality.

- **Meta-prompting for images**: one model writes the prompt for another. ChatGPT describes an image for the article or title, and that text is wrapped in a fixed style template and sent to Stability AI.
  - Principle(s): Give Direction. A named style ("Corporate Memphis") is often enough to steer Stable Diffusion, so you don't need to train a DreamBooth model.

- **Prototype UI first**: before you build NextJS + Tailwind + servers + a database, ship a **Gradio** (or Streamlit) prototype for feedback. `demo.launch(share=True)` gives a public link, and Hugging Face Spaces hosts demos for free.
  - Principle(s): Evaluate Quality. Human feedback is the most valuable evaluation data (it drove alignment breakthroughs such as ChatGPT).

## Key Concepts
- **Blind prompting**: adding instructions to a prompt without testing whether they help.
- **Information gain**: insight that the existing top-ranking content doesn't already contain. The interview questions aim for it.
- **Bespoke context**: a section prompt that combines interview insights, what has already been written (memory) and retrieved web snippets.
- **OnlyStoreAIMemory**: a `ConversationSummaryBufferMemory` subclass that stores **only AI messages**, so retrieved documents don't bloat memory while the model still knows what it already wrote and summarizes once over the limit.
- **Graceful retrieval backoff**: start with k=5 retrieved docs, decrement k on errors (e.g. context overflow), and fall back to no docs.
- **Embedding distance (cosine similarity)**: an evaluation metric for style closeness to a reference text.
- **A/B testing prompts**: compare prompt versions by average human rating (thumbs up/down) and token usage.
- **Corporate Memphis**: a B2B illustration style (vibrant palettes, bold asymmetric shapes, organic and geometric forms). It started as costly signaling, and AI can reproduce it cheaply while keeping the trust associations.
- **Subclassing LangChain classes**: e.g. overriding `AsyncChromiumLoader.load` to scrape several URLs asynchronously.

## Mental Models
- Think of a production AI app as **a chain of small, testable prompts**, not one mega-prompt. Each link adds one kind of context and can be evaluated separately.
- Use **the user's own answers** when you need content that is unique and not generic. The LLM writes and the human supplies the opinions, so the LLM acts as "an informed coauthor".
- Spend your **expensive model and testing budget on the strategically hardest step** (here, the style rewrite). Cheaper models handle the rest.
- Use **a throwaway Gradio UI** to validate an unproven idea before you invest in a full stack.

## Anti-patterns
- **"Write a blog post on {topic}"**: produces short, generic, unoriginal content that won't rank.
- **Numeric format constraints** (exact section or word counts): LLMs often ignore them.
- **Blind prompting**: untested instructions waste tokens and can lower quality.
- **One prompt for the whole task**: you can't diagnose which part fails.
- **Judging a prompt from one run or one case**: nondeterminism inflates or deflates the apparent performance. Use 10+ runs across several cases.
- **Storing retrieved documents in conversation memory**: bloats context. Store only the AI's outputs.
- **Copying retrieved documents verbatim**: plagiarism. The section prompt explicitly forbids it and allows ignoring unhelpful docs.
- **Building the full production stack before you get feedback**: slow and risky for an unproven idea.

## Code Examples
```python
class OnlyStoreAIMemory(ConversationSummaryBufferMemory):
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        input_str, output_str = self._get_input_output(inputs, outputs)
        self.chat_memory.add_ai_message(output_str)
```
- **What it demonstrates**: custom memory that remembers prior sections (to avoid repetition) without storing the large retrieved context.

```python
for subheading in self.outline.sub_headings:
    k = 5  # Initialize k
    while k >= 0:
        try:
            relevant_documents = (self.chroma_db.as_retriever() \
                .invoke(subheading.title, k=k))
            section_prompt = f""" ...prompt_excluded_for_brevity... Section text: """
            result = self.blog_post_chain.predict(section_prompt)
            blog_post.append(result)
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            k -= 1
        if k < 0:
            relevant_documents = ""
```
- **What it demonstrates**: per-section RAG generation with backoff on how many docs to retrieve so each prompt fits the context window.

```python
def create_image(title) -> str:
    chat = ChatOpenAI()
    # 1. Generate the image prompt:
    image_prompt = chat.invoke([SystemMessage(content=f"""Create an image prompt
        that will be used for Midjourney for {title}.""")]).content
    # 2. Generate the image:
    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",  # stable-diffusion-xl-1024-v1-0
        headers={..., "Authorization": f"Bearer {api_key}"},
        json={"text_prompts": [{"text": f'''an illustration of {image_prompt} in the style of
            Corporate Memphis, white background, professional, clean lines, warm pastel colors'''}],
              "cfg_scale": 7, "height": 1024, "width": 1024, "samples": 1, "steps": 30},
    )
    # 3. base64-decode data["artifacts"], save as uuid PNG, return paths
```
- **What it demonstrates**: meta-prompting (an LLM writes the image prompt) plus a fixed style suffix for a consistent brand look (condensed). The APIs are the 2024 Stability v1 REST and `langchain_openai`.

## Reference Tables

**Five Principles audit of the "sophisticated" blog prompt**

| Principle | Status in the naive long prompt | Fix in the pipeline |
|---|---|---|
| Direction | Tone/voice rules, but sounds like AI | Interview answers + style-guide rewrite |
| Format | Section/word counts ignored | Pydantic `BlogOutline`; per-section `.md` output |
| Examples | None | Few-shot style samples in the style prompt |
| Evaluation | Blind prompting | Embedding-distance tests, title A/B, user feedback |
| Division | One prompt | Research → interview → outline → sections → style → title → image |

**Style-prompt experiment (scored by embedding distance to a manual rewrite; lower is better)**

| Variant | Approach |
|---|---|
| A | Control: the bullet-point style prompt |
| B | One-shot writing sample → GPT-4 describes the style |
| C | Three-shot rewriting example (input + rewritten pairs) → describe the style |
| D | Three-shot writing sample (final samples only) → describe the style |

The test cases were memetics, skyscraper technique and value-based pricing. The winning prompt was a 7-point style description: Informative & Analytical; Structured & Organized; Conversational Tone with Professionalism; Practical & Actionable; Balanced Perspective; Examples & Analogies; Direct & Clear.

## Worked Example
**Context-rich section prompt (Text Generation step)**
```
You are currently writing the section: {subheading.title}
---Here are the relevant documents for this section: {relevant_documents}.
If the relevant documents are not useful, you can ignore them.
You must never copy the relevant documents as this is plagiarism.
---Here are the relevant insights that we gathered from our interview questions
and answers: {self.questions_and_answers}. You must include these insights where
possible as they are important and will help our content rank better.
---You must follow the following principles:
- You must write the section: {subheading.title}
- Render the output in .md format
- Include relevant formats such as bullet points, numbered lists, etc.
---Section text:
```
End to end with `TOPIC = "Neural networks"`: the top 3 Google results are scraped and summarized → `InterviewChain` asks 5 open-ended questions, which the user answers → `BlogOutlineGenerator` returns a title and subheadings → for each subheading, Chroma retrieves up to 5 snippets, `OnlyStoreAIMemory` supplies a summary of what has been written, and the prompt above writes the section → GPT-4 rewrites the draft in the tested style → `create_image(outline_result.title)` produces a Corporate Memphis header. In the Gradio UI the whole flow is two buttons: "Summarize and Generate Questions" and "Generate Blog Post & Image".

## Key Takeaways
1. Audit every prompt against the Five Principles. Long instruction lists without examples, tests or task division are blind prompting.
2. Unique, human-sounding content needs unique input. Interview the user for information gain that the SERP doesn't have.
3. Build the app as a chain of LangChain components with Pydantic parsers, so each step is structured, logged and replaceable.
4. Write long content section by section with retrieval, memory of what's been written (AI messages only) and a context-rich, anti-plagiarism prompt.
5. Test the hardest prompt (style rewrite) quantitatively: several variants, several cases, 10+ runs each, scored by embedding distance. Escalate to fine-tuning or DSPy if needed.
6. Use meta-prompting plus a named art style for consistent, cheap brand imagery. A DreamBooth model is only needed for a truly custom style.
7. Ship a Gradio prototype early. Human feedback is the most valuable evaluation data.

## Connects To
- **Ch 1**: the Five Principles are used here as an audit checklist and then as the design of the whole pipeline.
- **Ch 3**: meta prompting (one model writes another's prompt) and role prompting in the interview system message.
- **Ch 4**: LCEL chains, `PydanticOutputParser`, text splitters and document loaders.
- **Ch 5**: Chroma vector store and retrieval of scraped pages per section.
- **Ch 6**: custom memory (`ConversationSummaryBufferMemory` subclass) to avoid repetition.
- **Ch 8**: Meme Unbundling (mixing writer styles) and naming art styles to steer image models.
- **Ch 9**: Stable Diffusion XL via the Stability AI API, with DreamBooth as the upgrade path for a custom house style.
- **DSPy / LLM evals**: automated prompt optimization against a defined metric. Hugging Face Spaces for hosting demos.
