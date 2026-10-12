# Chapter 1: Changing Software

## Core Idea
All software change is, technically, **behavioral change** — and the hard part isn't the small thing you change, it's *preserving* the vast amount of behavior you must keep. Understanding is the key to changing safely.

## Frameworks Introduced
- **Four Reasons to Change Software**: every change is one (or more) of: 1) Adding a feature, 2) Fixing a bug, 3) Improving design (refactoring), 4) Optimizing resource usage.
  - When to use: to cut through "is it a bug or a feature?" arguments and focus on what *technically* changes.
  - How: classify the change by what it holds invariant vs. alters (structure / functionality / resource usage).
- **The Invariance Matrix**: what each change type alters vs. preserves.
  - When to use: deciding how much behavior is at risk.

## Key Concepts
- **Behavior**: the most important thing about software — what users depend on. Adding behavior builds trust; changing/removing depended-on behavior (a bug) destroys it.
- **Refactoring**: improving structure *without* changing behavior, verified by tests, in small steps. Differs from cleanup (low-risk reformatting) and rewriting (high-risk).
- **Optimization**: hold functionality invariant, change a *resource* (time/memory) instead of structure.
- **Legacy code**: (book's working definition) code without tests. Code without tests is bad code, however well written — you can't know if it's getting better or worse.

## Mental Models
- Think of every change as "change a little, preserve a lot." The risk lives in the *preserved* part you might break unknowingly.
- Refactoring and optimization are twins: both freeze functionality and let *something else* move.

## Anti-patterns
- **Minimizing changes to manage risk** ("if it's not broke, don't fix it"): existing classes/methods grow larger and harder to understand; skills atrophy; fear compounds daily.
- **Inlining instead of extracting "to be safe"**: fewer edits feels safer but rots structure.

## Reference Tables
Typical change profile (— = held invariant):

|                   | Add Feature | Fix Bug | Refactor | Optimize |
|-------------------|-------------|---------|----------|----------|
| Structure         | Changes     | Changes | Changes  | —        |
| New Functionality | Changes     | —       | —        | —        |
| Functionality     | —           | Changes | —        | —        |
| Resource Usage    | —           | —       | —        | Changes  |

## Worked Example
A manager asks to move the company logo from left to right, and animate it next release. Bug fix or feature? Irrelevant at the people level. Technically: we *add* behavior (logo on right) and *remove* behavior (logo on left) — it's behavioral change either way. Contrast: adding a `replaceTrackListing()` method to `CDPlayer` changes *nothing* until something calls it. Adding code + calling it = adding behavior; modifying existing code = risking existing behavior.

## Key Takeaways
1. Stop arguing bug-vs-feature; ask what behavior changes and what must be preserved.
2. Preserving existing behavior is one of the largest challenges in development.
3. The big risk isn't the change — it's not knowing *how much* behavior is at risk.
4. Three questions of risky change: (1) What changes must we make? (2) How will we know we did them correctly? (3) How will we know we haven't broken anything?
5. Avoiding change breeds bigger classes, rusty skills, and fear.

## Connects To
- **Ch 2**: Cover and Modify answers all three risk questions with tests.
- **Ch 3 & 4**: sensing/separation and seams are *how* you preserve behavior under test.
