# Chapter 13: Why User Stories?

## Core Idea
Among all requirements methods, user stories win because they shift the focus from a shared *document* to a shared *understanding* — emphasizing verbal communication, comprehensibility, right-sized planning units, iterative/opportunistic development, deferred detail, participatory design, and accumulated tacit knowledge — while honestly acknowledging a few drawbacks.

## Frameworks Introduced
- **Adequate stories + frequent conversations** (vs. "perfect requirements"): the goal is not perfect written requirements but good-enough placeholders backed by ongoing talk.
  - When to use: always, as the governing philosophy of stories.
  - How: write terse placeholding sentences; defer detail to conversations near implementation.
  - Why it works: written words are imprecise and gain false finality; "100 perfect left shoes ≠ one perfect pair" (Poppendieck) — perfect parts don't sum to a perfect whole.
- **Opportunistic development** (Guindon; Parnas & Clements): real developers don't work top-down; they move freely between requirements, scenarios, and design at varying abstraction levels.
  - How: write/rewrite stories at any level of detail; shift focus as opportunities appear.
  - Failure mode it avoids: rigid top-down specification, which fails because users don't fully know needs, details emerge during build, humans can't hold all details, and change happens.
- **Participatory (vs. empirical) design**: engage users *as members* of the design team rather than merely studying them.
  - How: accessible, jargon-free stories pull users in; they help prototype the UI from the start.

## Key Concepts
- **Verbal communication**: stories force talk; conversations give a short feedback loop and mutual learning, with no false precision and no "sign-off."
- **Comprehensibility**: terse, value-focused stories are readable by both business and developers; IEEE 830 buries both in jargon.
- **Right size for planning**: stories are larger than IEEE 830 statements, smaller than use cases/scenarios — usable directly for release planning, programming, and testing.
- **Epic**: a large story (e.g., "the user can compose and send email") later split into smaller stories.
- **Deferring detail**: a goal-level placeholder is written now, fleshed out only when details matter.
- **Tacit knowledge**: face-to-face talk accumulates shared, unwritten understanding across the team.
- **Completism (Fowler)**: the compulsion to fill in every field of a template — a use-case hazard stories escape (no story template exists).
- **Empirical design**: designers decide by studying/interviewing users who never become true participants.

## Mental Models
- Stories are the *right* size: IEEE 830 items are too small to prioritize (everything becomes "mandatory"); use cases/scenarios are too big (priorities not useful).
- Think of an IEEE 830 spec as implying "if it doesn't say 'shall,' the system shall NOT" — so you can't tell a missing requirement from an unwritten one. Stories add detail progressively without that trap.
- Use stories when you need a *virtuous cycle*: accessible stories → engaged users → developers engage users more.

## Anti-patterns
- **Chasing "perfect requirements"**: even perfect sentences fail — users refine opinions, and perfect parts don't make a perfect whole.
- **Treating written words as precise**: ambiguity ("soup or salad and bread"; "should," "prominently display"; "name can be 127 characters") only resolves in conversation.
- **Prioritizing thousands of nested "shall" statements**: nesting (4.6.1.1 under 4.6.1) makes independent prioritization impossible.

## Worked Example
Cohn's lunch-menu ambiguity: the menu read "Entrée comes with choice of soup or salad and bread." Does it mean *Soup or (Salad and Bread)* or *(Soup or Salad) and Bread*? The written sentence can't say. The waitress's spoken "Would you like soup or salad?" — plus dropping a bread basket on the table before taking the order — removed all ambiguity instantly. This is the whole argument for stories: shift the focus from precise writing to a short verbal feedback loop.

## Key Takeaways
1. Stories shift focus from a shared document to a shared understanding via conversation.
2. They are comprehensible to everyone and the right granularity for planning.
3. They suit iterative development — start with an epic, split as needed.
4. They encourage deferring detail and opportunistic, participatory design, and build tacit knowledge.
5. Drawbacks: hard to see relationships among many stories on large projects; may need light extra docs for traceability; tacit-knowledge approach doesn't scale to very large teams.

## Connects To
- **Ch 12**: provides the contrasts (IEEE 830/use cases/scenarios) this chapter argues against.
- **Ch 14**: drawbacks here (lost relationships, too much detail) recur as story smells.
- **Ch 16**: traceability and large-project concerns handled via constraints and light documents.
- **Agile / XP communication values**: external link to high-bandwidth, face-to-face communication.
