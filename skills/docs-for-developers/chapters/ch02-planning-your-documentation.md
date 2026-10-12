# Chapter 2: Planning Your Documentation

## Core Idea
Turn user research into a **documentation plan**: choose the right **content types** for your users' **use cases**, then outline every page (title + type + description) before writing.

## Frameworks Introduced
- **Content types**: reusable patterns, each serving a specific task/user/learning preference. The core set for developers:
  - **Code comments** — document *why*, not just *what*; design decisions and trade-offs.
  - **README** — single (often Markdown) file summarizing a repo: what it does, install, troubleshooting, maintainers, license, changelog, examples, links.
  - **Getting started** — first-time experience; quickest path to a working integration. *Show, don't tell.*
  - **Conceptual** — explains ideas/how it works; opinionated but *no implementation details*; one core concept per doc.
  - **Procedural** — tutorials and how-to guides; one action per step.
  - **Reference** — cause-and-effect: API reference, glossary, troubleshooting, changelog.
- **Use case** (a.k.a. business problem / user scenario): a set of tasks to complete a goal. Derived from research; drives which content types you need.
- **Documentation plan**: a flexible outline mapping the user journey across the content you'll write.

## Key Concepts
- **Tutorial vs. how-to guide**: tutorial = *learning* in a safe environment (test data/tools, no real code); how-to = *action*, solving a real business problem with real code.
- **Escape hatch**: a cue (link, callout, note) signaling a user is in the wrong place and pointing to a better option. Prerequisites act as escape hatches.
- **Changelog vs. release notes**: changelog = terse chronological record (can be automated); release notes = rich context (what/when/why/how it was/how it'll be).
- **Content outline**: list of page titles, each with its content type and a one-line description.

## Mental Models
- Match content type to user need — different problems need different patterns.
- Keep procedures short: a user should see 2+ steps on one screen; tutorials over ~10 steps signal too-complex scope (or a too-complex *product*).
- Use docs complexity as a product signal: if a tutorial can't be shortened, the service may need simplifying — talk to the developers.
- Keep how-to guides on a single page; put links at the bottom, not mid-text, to avoid distraction (opposite of Wikipedia's link-everything style).

## Code Examples
README template skeleton:
```markdown
# README
<paragraph: what the code does at a high level>
## Installation
1. … 2. … 3. …
## Examples
## Troubleshooting
## Changelog
## Additional resources
## License information
```
- **What it demonstrates**: the minimal, concise, must-keep-current structure of a good README.

## Reference Tables
Content outline for Corg.ly (Table 2-1, abridged):

| Title | Content type | Description |
|---|---|---|
| Getting Started with Corg.ly | getting started | simple demo + links |
| Dog translation explained | conceptual | how Corg.ly works |
| Authenticating with the API | how-to | step-by-step auth |
| Corg.ly API reference | api reference | all calls + syntax |
| Troubleshooting audio issues | troubleshooting | common audio problems |
| Release notes | changelog | this release |

## Worked Example
**Planning questions** Charlotte answers before building the plan: Who is the target audience? Biggest takeaways from launch? Features in order of importance? What do users expect? Required prior knowledge? Use cases supported? Known friction points? — Her answers reveal that *getting started* docs, a strong set of *how-to* use cases, and *troubleshooting* are the priority content types, sourced from existing friction logs and interview notes.

## Anti-patterns
- **Only producing advanced docs** (how-to guides) while skipping getting-started — strands evaluators and beginners.
- **Writing before planning**: miss critical info, can't see the journey holistically.
- **FAQ sprawl**: uncurated Q&A lists with no logical flow; prefer issue→solution lists.
- **Self-documenting code as an excuse** to skip comments.

## Key Takeaways
1. Plan before writing — the plan is a flexible outline of the user journey.
2. Pick content types deliberately; each solves a different problem.
3. Distinguish tutorial (learn) from how-to (do real work).
4. Keep procedures and tutorials short; over-length signals product complexity.
5. A content outline (title + type + description) is the concrete deliverable.

## Connects To
- **Ch 1**: research and personas feed the plan's audience answers.
- **Ch 3 & 4**: plan → drafting → editing.
- **Ch 5 / Ch 6 / Ch 7**: code samples, visuals, and publishing are listed as plan line-items.
- **[[cohn-user-stories]] / [[crafting-user-stories]]**: use cases echo agile user stories.
