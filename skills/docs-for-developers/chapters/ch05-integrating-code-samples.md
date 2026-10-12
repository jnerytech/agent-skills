# Chapter 5: Integrating Code Samples

## Core Idea
Code is the gold readers hunt for — they skim prose to find it. A good sample must be **Explained, Concise, Clear**, and (if executable) **Usable/extensible** and **Trustworthy**. One broken sample destroys trust in the docs *and* the product.

## Frameworks Introduced
- **Two types of samples**:
  - **Executable** — runnable; copy-paste-and-personalize (e.g. a `curl` request).
  - **Explanatory** — not meant to run; outputs/blocks to learn from or compare (e.g. an API JSON response). Must match what the reader actually sees so copy-pasting an error into search returns relevant hits.
- **The five principles of good samples**:
  - **Explained**: accompanied by prose/comments giving the *why*, not the *what*; state prerequisites, version limits, odd conventions.
  - **Concise**: exact info needed, nothing else; only the feature being documented; short lines (no horizontal scroll).
  - **Clear**: follows the language's conventions/style guide; descriptive names; no clever tricks, deep nesting, or local aliases.
  - **Usable (& extensible)**: clear where to substitute data; use descriptive placeholders like `replace_with_actual_bark`, **not** `foo`/`bar`/gibberish; say where replacement data comes from.
  - **Trustworthy**: production-ready, tested, consistent; mark alpha/beta clearly.

## Key Concepts
- **Colon convention**: when prose introduces a sample, end the line with a colon.
- **Ellipsis + line wrap**: wrap long lines (~80 chars, per Google's style guide) and use `...` to mark omitted parts of large samples.
- **Range of complexity**: provide a simple "hello world" for newcomers and richer use-case samples for the comfortable — but only **one use case per page**; never mix newcomer and advanced.
- **Presentation**: make code visually pop (box, fixed-width font, distinct background); use backticks/`<code>`.

## Mental Models
- Text and code are different languages; the reader cares about the code. A sample can say more than the prose around it.
- If a sample needs a long explanation, the *code* may be too complex — refactor it, or tell the engineers the use case is confusing.
- "Think before you automate": autogeneration/sandboxes cost maintenance; that time might serve readers better in writing, IA, or the product.

## Code Examples
Descriptive placeholder marks where the reader substitutes their own data:
```shell
# Provide code comments that tell users what to update or replace
$ curl 'https://corgly.example.com/api/v1/translate' -i -X POST \
  -H 'Content-Type: application/json' \
  -d '{"query": "replace_with_actual_bark"}'
```
- **What it demonstrates**: usability — the reader sees exactly what to replace and why, with no `foo`/`bar`.

## Reference Tables
Tooling for code samples (three types):

| Tool type | Use when | Trade-off |
|---|---|---|
| Testing | Always for runnable samples | Store samples in a repo, test, then embed |
| Sandboxing | Risky/sensitive software needing lots of customization | High build + maintenance cost; often excessive |
| Autogeneration | API outputs/errors via OpenAPI etc. | Auto-reflects API changes, but still needs human review of comments |

## Worked Example
**Matching a Corg.ly API request to its exact response.** The doc shows a `POST /translate` with body `{"query": "woof woof arf woof"}`, then the *exact* `HTTP/1.1 200 OK` JSON response listing translations with confidence scores (0.99, 0.90, …). Pairing request to real output — including common error samples — is what makes the reference trustworthy; a mismatched error code would leave users unable to diagnose problems.

## Anti-patterns
- **`foo`/`bar`/acronyms** as placeholders — opaque to nontraditional-background devs.
- **Irrelevant/overcomplicated code** that hides the intent and resists copy-paste.
- **Untested or out-of-date samples** — one break loses reader trust.
- **Screenshotting code** instead of providing copy-pastable text (see Ch 6).

## Key Takeaways
1. Readers seek code first; make samples specific, useful, maintainable.
2. Every sample: Explained, Concise, Clear; executable ones also Usable and Trustworthy.
3. Explain the *why*; use descriptive placeholders; one use case per page.
4. Test samples relentlessly; mark alpha/beta.
5. Automate (autogen/sandbox) only when the maintenance payoff is real.

## Connects To
- **Ch 2**: API reference content type relies on these samples.
- **Ch 4**: samples go through the same editing/accuracy passes.
- **Ch 6**: don't screenshot code — keep it copy-pastable.
- **Ch 11**: regular sample reviews are part of maintenance.
