# Chapter 4: Editing Documentation

## Core Idea
Editing is to writing what testing/refactoring is to code: a separate, analytical pass that makes content actually meet user needs. Edit in **focused passes**, build a repeatable **editing process** with peer + technical reviews, and give/receive feedback constructively.

## Frameworks Introduced
- **The four editing passes** (in this order): **Technical accuracy → Completeness → Structure → Clarity & brevity**.
  - Why this order: start with what you (the developer) know best, work toward what the user wants.
  - **Technical accuracy**: do the instructions produce the promised result? Run them yourself; reconcile inconsistent terms (e.g. "encryption" vs "hashing"); add warnings for failure/data-loss/injury.
  - **Completeness**: no gaps, no leftover `[TODO]`/`[TBD]`; account for other OSes/versions; note expiration dates. *Completeness ≠ telling everything* — too much info loses readers too.
  - **Structure**: title, headers, ToC are signposts; consistent/logical order; correct prerequisites and next steps; follows the template.
  - **Clarity & brevity**: line-by-line — "code refactoring for documentation." Cut words, fix grammar/tone, remove idioms/bias.
- **Editing process**: self-review → peer review → technical review → integrate feedback → second round. Mirrors code review; shares load and sets team standards.
- **Plussing** (Pixar): *you may only criticize an idea if you also add a constructive suggestion.* Focus on the idea, not the person; be specific; give time to respond.

## Key Concepts
- **Peer review**: a teammate familiar with the product checks usefulness/relevance — like a code review.
- **Technical review**: a targeted review by a domain expert, vital when documenting an integration of two technologies where you only know one.
- **Editing checklist**: keeps self-review on track (title specific, headers ordered, purpose in para 1, procedures tested, links work, spell-check run, prereqs/next steps defined).
- **Agile prime directive** (Norm Kerth): everyone did the best job they could given what they knew — the mindset for receiving feedback.

## Mental Models
- Editing = code testing/review; grammatically perfect docs can still "fail to compile" for users (fail to help).
- Read like a first-time reader to surface assumptions.
- Make distance: review with a fresh mind, not immediately after writing.
- Consider every piece of feedback; you need not accept all of it — resolve contradictions by asking "what does the user need?"

## Reference Tables
The four passes at a glance:

| Pass | Key question |
|---|---|
| Technical accuracy | Will following this yield the promised result? |
| Completeness | Any gaps, TODOs, untested OS/versions? |
| Structure | Do title/headers/order signpost correctly? |
| Clarity & brevity | Is every line as short and clear as possible? |

## Worked Example
**Karthik reviews Charlotte's Corg.ly draft** much like a code review. He channels their customer Mei's likely questions — "Which steps are required?", "How do I tweak these API calls?", "What common errors will I hit?" — and leaves comments: add detail here, add headers there, fix a link, add next steps. He plans a second feedback round before showing it to Mei. To integrate feedback efficiently: start with the reviewer who left the *most* comments (preempts later ones), handle one reviewer at a time, acknowledge all help, and run a second review on the changes (like reviewing follow-up commits on a PR).

## Anti-patterns
- **Writing and editing simultaneously**: slow, gets you stuck.
- **Editing everything at once**: overwhelming; use focused passes.
- **Mistaking grammar-perfect for user-effective**: passes the linter, still has bugs.
- **Criticism without a suggestion**: violates plussing; demoralizes without helping.

## Key Takeaways
1. Separate writing (creation) from editing (evaluation).
2. Edit in four focused passes: accuracy, completeness, structure, clarity.
3. Build an editing process with peer and technical reviews using your existing code-review tools.
4. Consider all feedback; you decide what to accept — optimize for the user.
5. Give feedback by plussing, and call out what you *like*.

## Connects To
- **Ch 3**: drafting produces the raw material this pass refines.
- **Ch 1**: friction logs feed the technical-accuracy and completeness passes.
- **Ch 2**: structure pass verifies you followed the documentation plan/templates.
- **Ch 8**: external user feedback extends this internal review loop after publishing.
