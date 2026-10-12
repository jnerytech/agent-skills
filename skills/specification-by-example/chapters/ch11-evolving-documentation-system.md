# Chapter 11: Evolving a documentation system

## Core Idea
A living documentation system is more than a directory of executable specification files: to deliver its benefits it must be organized so the specs make sense together and carry the context needed to understand each part. Aim for three properties — easy to understand, consistent, and organized for easy access — and continuously refine the system to keep them.

## Frameworks Introduced

### Property 1 — Easy to understand

- **Don't create long specifications**: A long spec is a symptom, not just a length problem; the longer it is, the harder to understand.
  - When to use: A specification grows large as functionality is added.
  - How: Diagnose the underlying cause — (a) concepts are at the wrong abstraction level ("What are we missing here?" → find an implied concept, ch7); (b) it describes several similar functions, not one → split into focused specs (ch8); (c) it's a script, not a spec → restructure around *what* not *how* (ch8); (d) it carries unnecessary context → trim to the attributes that illustrate this test's goal.

- **Don't use many small specifications to describe a single feature**: The inverse failure — over-fragmentation. If someone must read ~10 specs to understand one feature, reorganize/merge.
  - When to use: Domain understanding evolves; concepts that started apart converge, or split concepts start resembling existing ones.
  - How: Merge multiple specs that describe the same feature into one. (Sky Network Services broke specs down so far that a single spec no longer described a whole feature — too many files to track.)

- **Look for higher-level concepts**: Replace a set of near-duplicate specs with one spec focused only on the differing attributes.
  - When to use: You end up with similar specs differing only in minor details.
  - How: Step back; view what the specs describe from a higher abstraction level; identify the unifying concept; collapse the set. (Can trigger design breakthroughs, like "implied concepts," ch7.)

- **Avoid using technical automation concepts in tests**: Specs in technical language are ineffective as a communication tool.
  - When to use: Stakeholders aren't technical.
  - How: If business users care about a spec, write it in their language; if they don't care, capture it with a technical test tool instead. Technical wording (SQL, DOM ids, "wait until time T") is acceptable only when stakeholders are technical — but even then it describes *how* something is tested, not *what* the function is, and tends to cause long-term maintenance pain. Technical concepts leaking into docs also signal underlying design problems (see "Listen to your living documentation").

### Property 2 — Consistent

- **Evolve a language**: Grow a set of reusable patterns/phrases for specifications — a mini DSL — to cut automation-layer maintenance and keep wording uniform.
  - When to use: Automation/fixture code grows wordy and one-off (a maintenance issue); duplication appears across step/fixture files.
  - How: Boil very specific, single-test fixtures down to generic, reusable phrases; share one step/fixture file across the stories of a business function rather than per-story. Because the docs are automated and connected to software, evolving this language creates and maintains the ubiquitous language (ch8).

- **Base the specification language on personas**: Derive spec language from the activities different personas can perform.
  - When to use: Web projects / heavy user interaction.
  - How: Name personas (e.g., "Boris the borrower," "Carrie the co-signer"); express specs from each persona's motivations and actions; personas can double as automation entry-point helpers. Do NOT use for low-interaction batch/data-processing systems — switch to a process-flow model with Given-When-Then instead.

- **Collaborate on defining the language**: Catch consistency problems as specs are written, not in a later review pass.
  - When to use: You choose NOT to run big specification workshops.
  - How: Have developers and testers write specs in pairs (pilot/co-pilot) so problems are flagged immediately — like pairing vs. after-the-fact code review. Alternatively (stable language), let BAs/business users write specs and have developers review anything structurally different from existing specs and advise on consistency/automability.

- **Document your building blocks**: Make reusable spec components discoverable so people reuse them and keep the language consistent.
  - When to use: Always, as a system grows; new members ask how to write a good spec.
  - How: Build a separate area listing building blocks (e.g., a personas page generated from automation code — a "living dictionary"); and/or extract good representative examples from existing specs (guaranteed accurate because executable). Keep evolving language back-propagated into older specs so no part stays in three-year-old jargon.

### Property 3 — Organized for easy access

- **Organize current work by stories**: Group all in-progress specs together.
  - When to use: Work currently in progress (current iteration).
  - How: Use the tool's hierarchy (sections/dirs) to gather all specs for active stories into a "Current Iteration" branch so they run as one test pack (ch10's iteration pack) and give a clear story-done definition. One story spans several functional areas, each with its own focused spec.

- **Reorganize stories by functional areas**: Once implemented, move specs out of story-based grouping into a business-function hierarchy.
  - When to use: A story is done; stories are a planning tool, not a way to organize existing functionality.
  - How: Move the spec into the relevant Feature Set (PayPal integration → Payments; back-office report → User Management). Navigate by business function to find any feature. Keep story linkage via cross-references/tags if needed (e.g., regulatory traceability) — see figure 11.1.

- **Organize along UI navigation routes**: Replicate the UI navigation structure in the docs.
  - When to use: Documenting user interfaces with clearly defined navigation (e.g., back-office apps).
  - How: Make each doc page mirror a UI page like a help page — "here's everything I can do on this page," with links to dialog pages (Beazley/Ian Cooper). Risk: high maintenance if UI routes change often.

- **Organize along business processes**: Structure docs by use-case hierarchy.
  - When to use: End-to-end use-case traceability required (e.g., regulated pharmaceutical research).
  - How: Top-level use case = system goal = end-to-end business process; it refers to lower-level (sub-process) use cases. Keep the requirements doc's table of contents identical to the tests' — yielding direct requirement-to-test traceability. (Help-system/user-guide chapters are another valid organizing axis.)

- **Use tags instead of URLs**: Refer to specs by freeform tags/keywords, not by location.
  - When to use: You need traceability of specifications.
  - How: Assign story/case numbers as tags and link to *search results* for the tag, so specs can be moved/merged/split without breaking links from issue trackers or planning tools. Works even outside web tools, via a simple script over a project directory (Bekk: tag Cucumber tests, link from Confluence/Subversion).

- **Listen to your living documentation**: Treat documentation/automation pain as a signal about the system itself.
  - When to use: Specs are complex, brittle, or hard to automate.
  - How: Incidental complexity in a spec → simplify the system (Walton: "if a test is too complicated, it's telling you something about the system" — UBS workflow over-complication surfaced and was reduced). Hard-to-automate specs / long setups → client APIs are hard to use → simplify the API (Gärtner, Mestdach). Many tests broken by one small domain change → shotgun surgery → wrong architecture (Cooper). Duplicated concepts in docs → duplication in the domain model.

## Key Concepts
- **Living documentation system**: An organized, automated set of executable specifications plus contextual information that together explain what the system does — the longest-living project artifact.
- **Specification language / mini DSL**: An evolved set of reusable phrases and patterns for writing specs; its evolution maintains the ubiquitous language.
- **Persona**: A named user archetype whose motivations and activities drive spec language and can serve as an automation entry point.
- **Building blocks**: Reusable spec components (steps, personas, fixtures), documented via a living dictionary or representative extracted examples.
- **Functional area / Feature Set**: A business-function bucket (Payments, User Management) used to organize completed specs for retrieval.
- **Tag**: A freeform textual attribute on a page/file used for resilient traceability and external links instead of location-based URLs.
- **Listen to your tests**: Reading test/spec complexity as a diagnostic of design, API, and architecture problems.

## Mental Models
- Use **higher-level concepts / merging** when many small specs each cover a feature; use **splitting** when one spec covers many functions — both pathologies point at a missing or wrong abstraction.
- Use **story-based grouping while work is in progress**, then **functional-area (or UI/business-process) grouping once done** — planning structure and reference structure are different jobs.
- Use **tags + search links** (not URLs/static hierarchy) whenever you need traceability, because the docs will be reorganized over time.
- Use **complex/brittle specs as a warning light**: the living documentation is an alternative UI to your system — if it's hard to write and maintain, so is the real UI.

## Anti-patterns
- **Long, unfocused specifications**: Hard to understand; usually hide a missing concept, a script-in-disguise, or several merged functions.
- **Over-fragmentation**: Needing ~10 specs to grasp one feature is as bad as one giant spec.
- **Technical acceptance tests as communication tools**: Cryptic to business, slow, duplication-heavy (Link rewrote them as JUnit; Vogel's DbFit tests became too brittle).
- **Personas where there's little user interaction**: Blank stares from business; use process/Given-When-Then instead.
- **Defining language only via after-the-fact review**: Lets inconsistencies pile up that must be reworked — pair instead.
- **Stale jargon left in old specs**: Forces human translation, defeating the documentation's purpose.
- **No high-level structure / adding tests ad hoc**: Can't find which tests cover which functionality (Cowans) — you "might as well read the code."
- **Linking specs by URL / static hierarchy**: Breaks the moment you reorganize.

## Worked Example
A team building a website starts each story in a **Current Iteration** branch. Story #128, "enhanced registration," touches several functional areas, so it spawns separate focused specs: a back-office user report, age verification, and new PayPal and Gmail integrations — all grouped under the story so the whole story runs as one pack and has a clear "done."

Early on they wrote one Gherkin file per story card, with five or six cards per feature, and one fixture/step file each. Duplication appeared immediately across the near-identical one-liner steps, so they **evolved a language**: a single shared step file per business function, and generic reusable phrases replacing wordy single-test fixtures — cutting fixture code sharply.

Once #128 ships, story numbers become irrelevant for navigation, so they **reorganize by functional area**: the PayPal spec moves into Payments, the back-office report into User Management, and so on (figure 11.1's Feature Sets branch). Now anyone discussing a MasterCard change can navigate Payments and find every related example. Story traceability is preserved not by location but by **tags** (#128 attached as metadata, links pointing to tag-search results), so future moves/merges/splits don't break references from the issue tracker. Specs awaiting clarification sit in a separate holding place. Had they been documenting a back-office UI, they might instead have mirrored UI navigation routes (Beazley); a regulated pharma team instead mirrored its use-case hierarchy so the requirements TOC equals the tests' TOC.

## Key Takeaways
1. Living documentation has three goals — easy to understand, consistent, organized for access — and only continuous refinement keeps them.
2. Watch both extremes: split long unfocused specs, and merge many tiny specs that describe one feature; both signal a missing higher-level concept.
3. Keep specs in business language; technical automation wording belongs in technical test tools and signals possible design problems.
4. Evolve a reusable specification language (mini DSL) — it cuts automation maintenance and is how you grow/maintain the ubiquitous language.
5. Organize current work by stories, then reorganize finished specs by functional area (or UI routes / business processes) so features are findable.
6. Use tags and search links, never location-based URLs or rigid hierarchies, for traceability that survives reorganization.
7. Listen to your living documentation: complex, brittle, or hard-to-automate specs are diagnostics for system, API, and architecture problems.

## Connects To
- **Ch 3**: Introduced *why* living documentation matters; this chapter supplies the *how* of building and organizing it.
- **Ch 7**: "Look for implied concepts" — the same abstraction-finding move that breaks apart long specs and unifies near-duplicates.
- **Ch 8**: Refining specs to be focused and self-explanatory, "scripts aren't specifications," and the ubiquitous language that the evolving spec language maintains.
- **Ch 10**: The "current iteration pack" that story-based grouping enables for fast execution.
