# Chapter 3: Drafting Documentation

## Core Idea
Turn the plan into a first draft: start from audience/purpose/pattern, build an outline (the doc's "pseudocode"), flesh it out with headers/paragraphs/procedures/lists/callouts, and write for **skimming** — because readers read at most ~28% of a page.

## Frameworks Introduced
- **Audience / Purpose / Pattern header**: list these three at the top before writing to break the blank page.
  - Example: Audience = devs who know REST; Purpose = describe uploading audio files; Pattern = procedural guide.
- **Title = goal**: the title is the shortest, clearest rephrasing of the purpose from the user's view. One goal per doc; multiple goals → multiple docs. Verb-first title ("Translating dog barks to text") signals a task; noun title ("Audio encoding and sampling rates") signals reference.
- **Outline as pseudocode**: list every step/subtask in any order, then rearrange for **flow of information** (right info at the right time). Lets you validate approach cheaply before sinking time into prose.
- **The five building blocks**: headers, paragraphs, procedures, lists, callouts — each conveys info differently.
- **Callout severity ladder**: **Warning** (danger/irreversible loss) > **Caution** (unexpected consequences) > **Note** (tip/related info). Reserve for must-not-miss info to avoid alert fatigue.
- **Templates**: stable docs with placeholders for repeated patterns (release notes, bug reports, API refs, glossary entries). Consistency + faster writing; skip for unique/story content.

## Key Concepts
- **Flow of information**: ordering content to match reader knowledge and expectations.
- **Writing for skimming**: readers skim in an **"F" pattern**; help them by front-loading and breaking up text.
- **Verification step**: end every procedure with a way to confirm success — a "unit test for the documentation."
- **First draft ≠ good draft**: the draft is a judgment-free zone; get information down, polish in editing (Ch 4).

## Mental Models
- Think of an outline as pseudocode — discuss and validate before "implementing" prose.
- Use the tools you already use for code; don't learn a new toolchain. Don't get hung up on tool choice.
- Write iteratively like code: write what you know, mark `[TODO]` for gaps, fill later. Write out of sequence (intros are often written last).
- One action per procedure step — readers jump between docs and the terminal.

## Reference Tables
Skimmability strategies:

| Strategy | How |
|---|---|
| State most important info first | Answer "Will this help me?" in the first 3 paragraphs |
| Break up large text blocks | Subheaders, lists, code samples, graphics |
| Break up long documents | Split by audience, info type, feature, or format |
| Strive for simplicity | Move history/design theory out of procedural docs |

## Worked Example
**Outline for "Uploading Audio Files to Corg.ly"** evolves from a flat unordered list (install app, upload via UI/API, authenticate, verify) into a grouped, prerequisite-led structure:
```
Title: Uploading audio files to Corg.ly
Prerequisites: file size & format requirements
Uploading via the application: download → install → upload via UI → verify in UI
Uploading via the REST API: get access → call API → upload → verify via API
```
Because UI users and API users have different knowledge, the doc is then *split into two* — one per audience. Getting-unstuck tactics when drafting stalls: let go of perfectionism, ask for help, mark `[TODO]`, write out of sequence, change medium (paper/whiteboard/voice).

## Anti-patterns
- **Writing and editing at once**: rewriting sentence one for hours; separate creation from evaluation.
- **Wall of text**: readers skip it — break it up.
- **One mega-doc for many goals/audiences**: split it.
- **Callout overload**: causes alert fatigue, hides the critical warnings.

## Key Takeaways
1. Start with Audience/Purpose/Pattern; the title is the goal.
2. Outline first (pseudocode), then order for flow of information.
3. Build with headers, paragraphs, procedures, lists, callouts — one action per step, end with a verify step.
4. Write for skimming: front-load, break up text, F-pattern.
5. First drafts are allowed to be bad; get unstuck with TODOs, help, and out-of-sequence writing.
6. Templatize repeated document types.

## Connects To
- **Ch 2**: the plan supplies audience, pattern, and outline seeds.
- **Ch 4**: drafting is creation; editing is evaluation — kept separate.
- **Ch 5 & 6**: code samples and visuals are the tools for breaking up text.
- **Ch 1**: friction logs flag where callouts/notes are needed.
