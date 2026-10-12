# Patterns & Techniques — Docs for Developers

## User Research (break the curse of knowledge)
**When to use**: before writing anything, to understand real user needs.
**How**: sketch users → define their goal → list characteristics → outline their questions → validate via 3–5 interviews (open questions), surveys (closed questions), and support tickets grouped by theme.
**Trade-offs**: quality over quantity; good research is time-consuming but high ROL.

## Friction Log
**When to use**: to feel your users' pain firsthand and find doc vs. product gaps.
**How**: pick one user + one tightly-scoped scenario; number each step; record expected vs. actual; color-code positive/negative; file product issues, write docs for doc gaps.
**Trade-offs**: tight scope or it sprawls into the unactionable.

## Personas / User Stories / Journey Maps
**When to use**: to condense research into durable artifacts.
**How**: persona = characteristics + goals; story = `As a [user], I want [activity] so that I can [goal]`; journey map = define task → list channels → steps → experience per step → connect into a flow.
**Trade-offs**: focus on the larger, less-expert persona, not the advanced outlier.

## Content-Type Selection
**When to use**: planning what to write for each use case.
**How**: match need to type — code comments, README, getting started, conceptual, procedural (tutorial=learn / how-to=do), reference (API ref, glossary, troubleshooting, changelog).
**Trade-offs**: don't only write advanced docs; cover getting-started too.

## Documentation Plan
**When to use**: before drafting, to map the user journey.
**How**: answer audience/takeaways/features/expectations/prereqs/use-cases/friction; produce a content outline (title + type + description).
**Trade-offs**: skipping it risks missing critical content.

## Outline-First Drafting
**When to use**: confronting the blank page.
**How**: list Audience/Purpose/Pattern; title = goal (one per doc); dump all steps in any order ("pseudocode"); reorder for flow of information; expand with headers/paragraphs/procedures/lists/callouts.
**Trade-offs**: first draft is allowed to be bad — separate from editing.

## Writing for Skimming
**When to use**: always — readers consume ≤28% of a page in an F-pattern.
**How**: state most important info in first 3 paragraphs; break up text with subheaders/lists/code/graphics; split long docs by audience/info-type/feature; one action per procedure step; end with a verify step.

## Getting Unstuck
**When to use**: drafting stalls.
**How**: let go of perfectionism; ask for help; mark `[TODO]`; write out of sequence (intro last); change medium (paper/whiteboard/voice).

## Templates
**When to use**: multiple similar docs (release notes, bug reports, API refs, glossary entries).
**How**: extract the consistent sections into a placeholder skeleton.
**Trade-offs**: skip for unique/story content.

## Four-Pass Editing
**When to use**: turning a draft into publishable content.
**How**: Technical accuracy → Completeness → Structure → Clarity & brevity, one pass at a time; read as a first-time reader.
**Trade-offs**: completeness ≠ telling everything.

## Review Process + Plussing
**When to use**: collaborative editing.
**How**: self-review (checklist) → peer review → technical review (domain expert) → integrate (start with the heaviest reviewer, one at a time) → second round. Give feedback by plussing: only criticize an idea with a constructive suggestion; focus on idea not person.
**Trade-offs**: consider all feedback; you decide what to accept.

## Code Sample Design (ECCUT)
**When to use**: every sample readers will copy.
**How**: **E**xplained (the why), **C**oncise (only what's needed, ~80-char lines + ellipsis), **C**lear (follow style guides), **U**sable (descriptive placeholders like `replace_with_actual_bark`, never foo/bar), **T**rustworthy (production-ready, tested). One use case per page; provide a range of complexity (hello-world → advanced).
**Trade-offs**: long explanation = code too complex; refactor it.

## Code Sample Tooling
**When to use**: scaling sample maintenance.
**How**: Testing (always; store in repo, test, embed) → Sandboxing (risky software needing customization) → Autogeneration (OpenAPI for API outputs).
**Trade-offs**: "think before you automate" — that time may serve readers better elsewhere.

## Visual Content (CAP)
**When to use**: when words aren't enough (architecture, processes).
**How**: judge on **C**omprehension, **A**ccessibility, **P**erformance; start on paper; one idea per diagram ("simplify to amplify"); consistent shapes/colors/labels; describe in body text; publish SVG; 4.5:1 contrast. Diagram types: boxes-and-arrows, flowcharts, swimlanes.
**Trade-offs**: beware video — expensive, decays fast; usually a doc+images is cheaper.

## Content Release Process
**When to use**: publishing.
**How**: define when/who/where/tools/announce; build a Gantt timeline inside the software release; coordinate docs with the code release; assign one final approver; test procedures and samples; push a test doc through new toolchains; meet users where they are; announce; iterate.
**Trade-offs**: publish and iterate — no doc is perfect at release.

## Feedback Channels + Triage
**When to use**: post-publish, at scale.
**How**: build a focused few channels (page feedback w/ issue template, support monitoring, sentiment widget, surveys→CSAT, user council); triage each item — valid? actionable (original+reproducible+scoped)? priority (P0–P3)?; follow up with users.
**Trade-offs**: don't build every channel; respect users' time.

## Measuring Quality
**When to use**: "is my documentation any good?"
**How**: a doc is good when it fulfills its purpose; weigh functional (Accessible/Purposeful/Findable/Accurate/Complete) over structural (3 Cs); define org/reader/doc goals; make a plan, baseline, contextualize, use metric clusters, mix qual+quant; track TTHW.
**Trade-offs**: more metrics ≠ more answers.

## Information Architecture
**When to use**: doc set grows and findability drops.
**How**: combine sequences/hierarchies/webs; assess existing content (Keep/Remove/Review/Merge/Split + find gaps); card-sort a new map (Consistent/Relevant/Findable); migrate with redirects + validation checklist; document the IA.
**Trade-offs**: not too deep, not too shallow; reuse sparingly — link instead.

## Maintenance & Deprecation
**When to use**: keeping docs in sync with code.
**How**: run a user impact analysis per change; release docs with the feature (Kubernetes model); assign owners (CODEOWNERS); automate toil (freshness checks, link checkers, prose linters/Vale, ref generators/OpenAPI); deprecate with callouts + migration guide (publish first), then delete with notice + redirects.
**Trade-offs**: good automation kills toil; bad automation compounds it.
