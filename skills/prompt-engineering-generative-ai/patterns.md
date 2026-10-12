# Patterns — Prompt Engineering for Generative AI

# Text prompting

## Persona / Role Prompting
**When to use**: creative or subjective tasks; specific expertise or tone (Ch 1, Ch 3)
**How**: "in the style of <well-known person>" or "act as a <role>" in the system message; match the examples to the persona
**Trade-offs**: risk of stereotyped output; the model drifts out of role in long chats

## Prewarming (Internal Retrieval)
**When to use**: you lack domain rules for "good" output (Ch 1)
**How**: "Give me 5 tips for X based on expert advice" → "Using this advice, do X"; or paste trusted external rules into the prompt
**Trade-offs**: longer and costlier prompts

## Format Contract + Parse + Retry
**When to use**: any output consumed by code (Ch 1, Ch 3, Ch 4)
**How**: example payload + "You must follow the following principles: only valid JSON, no backticks, parsed with json.loads()"; validate with typed exceptions; retry or auto-fix on failure. YAML avoids escaping
**Trade-offs**: extra retries cost tokens; regex is only for flat structures

## Few-Shot Examples
**When to use**: format or style must be reliable (Ch 1, Ch 4)
**How**: 1–3 diverse examples; above 3–5, test count and similarity; `LengthBasedExampleSelector` (token-measured) when input length varies
**Trade-offs**: more examples give more reliability but less creativity, risk overfitting to the examples, and use up tokens

## Reference Text with Fallback
**When to use**: reducing hallucinations (Ch 3, Ch 5)
**How**: enclose sources in delimiters; "If the answer isn't found, return 'I could not find an answer'"; optionally require citations and string-match them against the source
**Trade-offs**: limited by the context window, which leads to RAG

## Ask for Context
**When to use**: decisions that need user specifics (Ch 3)
**How**: "If you need more context, please specify what would help you to make a better decision"; then re-ask with a Context block
**Trade-offs**: adds a round trip

## Style Unbundling / Meme Unbundling
**When to use**: on-brand or human-sounding text; artist-free image styles (Ch 3, Ch 8, Ch 10)
**How**: ask the LLM to describe the style's features *without naming the source*, then reuse or remix the bullets as a style guide or prompt
**Trade-offs**: works only for well-known sources; LLM output reads like instructions and needs smoothing

## Majority Vote
**When to use**: classification under nondeterminism (Ch 3)
**How**: run N times and take the modal label; constrain the output to a single word
**Trade-offs**: N× cost and latency

# Divide Labor

## Chain of Thought / Thinking Time / Inner Monologue
**When to use**: reasoning, grading, multi-factor plans (Ch 1, Ch 3, Ch 6)
**How**: "Let's think step by step"; "solve it yourself first, then compare"; hide working inside `"""` delimiters and strip it in code
**Trade-offs**: more output tokens

## Self-Evaluation Chain
**When to use**: generated quality varies (Ch 1, Ch 3)
**How**: a second call rates or critiques the first output per criterion; loop "can you improve it?" until no suggestions remain
**Trade-offs**: extra calls

## Meta Prompting / Prompt Rewriting
**When to use**: cross-model pipelines; end users who write poor prompts (Ch 1, Ch 3, Ch 8, Ch 10)
**How**: an LLM writes or rewrites the prompt for the target model ("Return only a single prompt…"); slot the result into a fixed template (medium + subject + style)
**Trade-offs**: average-quality ceiling; experts still win

## Prompt Chaining / Least to Most / Task Decomposition
**When to use**: tasks too big or varied for one prompt (Ch 3, Ch 4, Ch 10)
**How**: sub-chains joined with LCEL (`RunnableParallel`, `itemgetter`); pass summaries forward as memory; use a different model per step
**Trade-offs**: latency; errors compound; early context gets forgotten

## Query Planning
**When to use**: multi-intent queries with dependencies (Ch 4)
**How**: a Pydantic `QueryPlan` of `{id, question, dependencies}` nodes, then execute in dependency order
**Trade-offs**: planning errors propagate

## Document Chains
**When to use**: text longer than the context window (Ch 4)
**How**: Stuff (small inputs), Refine (progressive), Map Reduce (scale), Map Re-rank (confidence)
**Trade-offs**: Refine is slow; Map Reduce loses order; Re-rank needs good scoring

# Retrieval & agents

## RAG
**When to use**: private, large or recent knowledge (Ch 5, Ch 10)
**How**: chunk (recursive splitter + overlap, sized to the token budget) → embed → index → top-k search (+ metadata filter) → insert with an "only this context / I don't know" rule
**Trade-offs**: quality is capped by the embedding model and chunking; adds cost and latency

## Self-Querying Retrieval
**When to use**: queries that contain filterable attributes (Ch 5)
**How**: `AttributeInfo` schema + content description; LLM at temperature 0 emits filter + query
**Trade-offs**: depends on schema quality

## ReAct vs Function Calling
**When to use**: ReAct for sequential, reflective multi-tool tasks; functions for single or parallel definitive actions (Ch 4, Ch 6)
**How**: expressive tool names and docstrings, an `args_schema` for validation, a stop sequence for ReAct, and caps on `max_iterations` / `max_execution_time`
**Trade-offs**: ReAct is less stable; too many tools confuse the model

## Conversation Memory
**When to use**: multi-turn agents (Ch 6, Ch 10)
**How**: read before the run and write after; buffer (short chats), window K, summary, summary-buffer or token-buffer; store only AI messages when retrieval already supplies the documents
**Trade-offs**: verbatim history costs tokens; summaries lose detail

# Evaluation

## Blind A/B Test
**When to use**: before shipping any prompt change (Ch 1, Ch 10)
**How**: variants × N runs (10+ per case, several cases) → shuffle → rate thumbs-up/down → mean per variant
**Trade-offs**: manual rating is tedious and may not match the audience

## Programmatic / LLM Evals
**When to use**: scaling tests; moving to cheaper models (Ch 3, Ch 4, Ch 10)
**How**: GPT-4 references as ground truth → exact match / Levenshtein / embedding distance / pairwise judge; check the judge for false positives and negatives first
**Trade-offs**: a judge that is weak at a task grades it poorly

# Image prompting

## Modifier Stack
**When to use**: every image prompt (Ch 8)
**How**: `<format> of <subject>, in the style of <unbundled style>, <quality booster> --no <unwanted>`; tune `::` weights by grid search
**Trade-offs**: a format brings its own content with it; every word adds noise (prune with `/shorten`)

## Structure Transfer (Img2Img / ControlNet)
**When to use**: keeping composition or pose while changing style (Ch 8, Ch 9)
**How**: Img2Img with low denoising; ControlNet with a matching preprocessor and model (Canny default, OpenPose for people, Depth for layout); Ending step 0.8 frees the fine detail
**Trade-offs**: a ControlNet that is too detailed locks the output in place

## Inpainting Fix Loop
**When to use**: one bad region (Ch 8, Ch 9)
**How**: mask the region (or click it with SAM); "Whole picture" inpaint area; Original content + denoising 0.2–0.4 to fix, Latent Noise up to 0.8 to replace; one artifact at a time
**Trade-offs**: denoising above 0.4 hallucinates

## Consistent Character / DreamBooth
**When to use**: a recurring subject (Ch 8, Ch 9)
**How**: side-by-side `--ar 2:1` + Vary Region for 20 shots → DreamBooth on one concept with a rare token (`ukj`) and a class prompt
**Trade-offs**: about 1 GPU-hour and a 2 GB checkpoint per concept
