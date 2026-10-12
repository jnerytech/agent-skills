# Chapter 1: Generating Test Ideas

## Core Idea
Before designing checks, get the team to surface *what's worth testing* — engage stakeholders in productive discussions about needs, risks and expectations. These 12 ideas are equally good for manual and exploratory testing, and feed better deterministic checks later.

## Frameworks Introduced

- **Big-picture quality pyramid** (Maslow-style): a multi-layered, multi-faceted view of quality that different groups agree on.
  - When to use: kick-off / once per milestone, to align developers, testers, analysts, business.
  - How: draw the 5 levels on a whiteboard, let people add expectations on sticky notes, then quantify each. Levels: 1. Does it work at all? 2. Does it work well (perf/security/scalability)? 3. Is it usable? 4. Is it useful (production metrics)? 5. Is it successful (business metrics)?
  - Why it works: shared visualisation prevents over-investing in already-de-risked aspects; any broken level is serious regardless of height.

- **Explore capabilities, not features**: base exploratory sessions on user *capabilities* (what a feature lets users do, or prevents), not the feature/story itself.
  - When to use: exploratory testing — story-focus causes tunnel vision (you only prove what you expect).
  - How: brainstorm what the feature allows/prevents; use impact-map actor impacts or story-map spine as starting points.

- **Always/never heuristic**: a 10-minute session listing things that should *always* happen or *never* be allowed.
  - When to use: unfamiliar domain/component, to paint the big picture fast.
  - How: split into groups, brainstorm absolutes silently, then try to *invalidate* each — one counter-example refutes it and exposes hidden assumptions.

- **"SHADED FIGS" emotional heuristic**: nine paths to stimulate test design — Scary, Happy, Angry, Delinquent, Embarrassing, Desolate, Forgetful, Indecisive, Greedy, Stressful.
  - When to use: spec workshops, exploratory sessions, designing test ideas — when you need alternatives beyond the happy path.
  - How: see Mental Models below for each path.

- **ACC matrix (Attribute-Component-Capability)**: table for organising test ideas & risk (James Whittaker, *How Google Tests Software*). Columns = quality attributes, rows = components, cells = capabilities.
  - When to use: establishing a maintainable, prioritisable test plan for frequent delivery.
  - How: capabilities go in cells; score each capability's risk with stakeholders; components & attributes change less than features, so the matrix stays stable. Capabilities = actions from a user's perspective, testable but not full test cases.

- **Risk checklists for cross-cutting concerns** (Gawande, *Checklist Manifesto*): name *key risks*, not test scenarios.
  - How: 5–9 items per list (working-memory limit); one list per concern; use "Do-Confirm" (work then review), not "Read-Do" (tick as you go).

## Key Concepts
- **Capability**: what a feature enables/prevents a user from doing; the right focus for exploration.
- **Trust boundary**: an explicit, group-agreed statement of how much you trust another team/component, setting where defensive checks are needed.
- **Activation phenomenon** (Gawande): letting people speak at the start raises participation and willingness to flag problems.
- **Black swan**: an unexpected incident no regression test would catch; mitigate by training fast reaction, not prevention.
- **Quantify even if you can't measure**: capture expectations as numbers/intervals even for hard-to-test qualities (e.g. "homepage < 2s with 50,000 concurrent users").

## Mental Models
- **Scary path** — what would most scare each stakeholder; flush out highest risks.
- **Angry path** — make the app react badly: validation errors, bad inputs, logic errors.
- **Delinquent path** — security: authentication, authorisation, permissions, confidentiality.
- **Embarrassing path** — things whose breakage causes embarrassment / credibility loss (e.g. "Qality" typo).
- **Desolate path** — zeros, nulls, blanks, missing/truncated data.
- **Forgetful path** — exhaust memory/CPU; see if data is lost.
- **Indecisive path** — back buttons, toggling, half-entered data — break last-known-state.
- **Greedy path** — select everything, max out every option.
- **Stressful path** — find the breaking point / scale limits.
- **Test benefit, not just implementation**: ask "how would you know it works *well*?" — add an overall benefit test on top of feature/regression checks.
- **Mob your test sessions**: 4–8 people generate far more diverse ideas than a pair; outsiders' ignorance enables radical test design. Don't dedup ideas too early.
- **Snoop on the competition**: cheapest mistakes to fix are ones others already made — mine regulatory reports, support forums, social media; run a *fake post-mortem* of a competitor's incident.

## Anti-patterns
- **Story-oriented exploratory testing**: leads to tunnel vision; you prove only what you expect to see.
- **Comprehensive Read-Do checklists**: grow too long, make people switch their brains off.
- **Trusting too much / too little across teams**: too much → weird untraceable bugs; too little → wasted defensive work and bulky, fragile integration tests.
- **Ignoring log/console trends**: spikes (e.g. privilege errors) are early warnings of compound failures.
- **One person holding the pen** in spec workshops: kills collaboration ("alpha dog" behaviour).

## Worked Example
**Capabilities for MindMup's contact form.** Feature: "a support request is sent when a user fills the form." Instead of testing field lengths and email formats (proving the feature works), the team framed two *capabilities*:
1. A user should be able to contact us easily *in case of trouble*; we should be able to solve their problems.
2. Nobody should be able to block/break the contact channels for others.

Exploring these surfaced two critical insights a feature-focused session would miss: (a) flaky/offline network — the top cause of support requests — meant the form couldn't connect at all, so they added a prominent alternative email shown in error messages; (b) users couldn't supply troubleshooting info, so they auto-captured and sent the last 1000 UI events with each request.

## Key Takeaways
1. Decide *what's worth testing* before *how to test it* — these activities engage stakeholders, not tools.
2. Frame exploration around capabilities and risks, not features/stories, to escape tunnel vision.
3. Use heuristics (always/never, SHADED FIGS, risk checklists) to systematically reach beyond the happy path.
4. Organise durable test knowledge in an ACC matrix; it outlives story maps and supports risk-based release decisions.
5. Quantify hard-to-test qualities anyway — a number enables design discussion and later production measurement.
6. Make trust boundaries explicit so you know where to build defences and where not to waste effort.
7. Diversity beats solo effort: mob sessions and competitor snooping inject ideas a single team can't generate.

## Connects To
- **Ch 2**: capabilities & key risks identified here become the key examples designed there.
- **Ch 4**: ACC matrix routes can drive chaos-monkey sessions ([[ch04-managing-large-test-suites]]); "test benefit" relates to "use production metrics".
- **Impact Mapping / User Story Mapping**: sources for capabilities.
- **Maslow's hierarchy of needs**: basis for the quality pyramid.
