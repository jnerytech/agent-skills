# Chapter 6: Specifying collaboratively

## Core Idea
Specification by Example fails if specifications are written in isolation; building a shared understanding requires business users and the delivery team to collaborate, but the *form* of that collaboration varies by context — from big all-team workshops to informal ad hoc conversations, usually structured as a preparation phase followed by a discussion.

## Frameworks Introduced

- **Try big, all-team workshops**: Intensive, hands-on domain/scope exploration with the whole team — implementation team, business stakeholders, domain experts — to build a consistent shared understanding and produce examples that illustrate a feature.
  - When to use: Starting out with Specification by Example; team is new or testers/developers lack solid domain knowledge.
  - How: Schedule on the calendar up front (regularly scheduled meetings beat the logistical nightmare; call senior stakeholders' secretaries). Whole team explores obscure routes and business rules up front. Can be folded into Scrum PBR (Product Backlog Refinement) workshops (5–10% of each iteration) — split top backlog items, draw examples on a whiteboard, identify technical/usability risk, then planning-poker estimate; split the story if no agreement.

- **Try smaller workshops ('Three Amigos')**: A focused meeting of one developer, one tester, one business analyst. (a.k.a. "The Power of Three" — Crispin/Gregory; formerly "Acceptance Testing Threesomes".)
  - When to use: Domain requires frequent clarification (single test-writer + review isn't enough).
  - How: Three people around one large screen; no up-front scheduling needed. Output is the actual feature file (Given-When-Then) the group agrees is complete in content before coding — placeholders/notes for imprecise values are fine. If domain knowledge is imbalanced, let the less-knowledgeable prepare beforehand so they aren't dominated.

- **Pair-writing**: A developer and an analyst (or tester) write the executable specification together on one keyboard/monitor.
  - When to use: Mature products where developers know enough to skip big workshops but a single viewpoint still risks misunderstanding.
  - How: Analyst supplies correct behavior; developer shapes the test to be easy to automate and to fit the living documentation (e.g., factoring shared workflow into its own test to kill duplication). Tester-developer pairing works when BAs are a bottleneck or absent — gives testers an overview of what's covered so they know what to check separately.

- **Have developers frequently review tests before an iteration**: Business users write the acceptance tests (e.g., Cucumber) themselves, then ask a senior developer to review before the iteration.
  - When to use: Analysts/business users are writing the tests.
  - How: Reviewer gives hints on writing steps and suggests extensions to the domain language. Frees developers to implement more, but increases the risk that specs miss implementation detail or are hard to automate.

- **Try informal conversations**: Ad hoc, on-demand chats among only the people who will work on a story, just before implementation starts.
  - When to use: Business stakeholders sit close by and are readily available.
  - How: "Anyone who has a stake" (analyst, programmer, tester, business stakeholder/user) briefly meets to establish a common baseline — enough to start, not every acceptance criterion. Decide per story whether the chat suffices or whether a full workshop is needed (small increment to known functionality → conversation is enough).

### Preparation patterns (preparing for collaboration)

- **Hold introductory meetings** (a.k.a. pre-planning) — When: project has many stakeholders. Run several days before the iteration to gather initial feedback and filter out stories too vague to accept; define high-level acceptance criteria as bullet points, not detailed examples. Not the planning meeting.
- **Involve stakeholders** — Actual stakeholders (not just product owner / BA proxies) must join; they make real decisions. Distinguish *prioritization* (one person) from *clarification* (the team). A single product owner can't know everything.
- **Undertake detailed preparation and review up front** — When: remote stakeholders. One person (analyst/tester) works one step ahead with stakeholders to structure examples and capture key values; a developer reviews early for technical gaps. Assign to a dedicated member to avoid dragging the whole team into pre-iteration analysis.
- **Have team members review stories early** — When: analysts/domain experts are a bottleneck. Form a "cell" (e.g., one tester + two developers) to first-pass review stories, spot common problems, and prep questions for the product owner.
- **Prepare only initial examples** — When: stakeholders are readily available. Don't over-prepare; just identify enough initial examples to get the basic structure in place so discussion runs efficiently.

## Key Concepts
- **Specification workshop**: Intensive whole-team domain/scope exploration producing shared understanding and illustrative examples.
- **Three Amigos**: Dev + tester + BA examining a story from three perspectives.
- **PBR workshop**: Scrum Product Backlog Refinement; a natural host for example-illustration in mature Scrum teams.
- **Preparation phase**: Up-front analysis (by one person or a few seniors) that feeds, but never replaces, collaboration.
- **Clarification vs. prioritization**: Prioritization belongs to one person; clarification can be done by the team.
- **Cell**: A small standing sub-group that reviews stories early to offload a bottlenecked role.

## Mental Models
- Use **big workshops** when the product is immature, the team is new, or domain knowledge is thin — they transfer knowledge to everyone at once (but cost the most time).
- Use **smaller/Three Amigos or pair-writing** once the team has built domain knowledge — cheaper, more flexible, three people fit around one screen.
- Use **more up-front preparation** when business users are remote or changes need heavy analysis; use **less** when stakeholders sit close and changes are small and well-understood.
- Use the **bottleneck** to assign prep work: if testing is the bottleneck, pull developers/BAs into up-front work; if BAs/SMEs are the bottleneck, pull testers in.

## Anti-patterns
- **Writing specs in isolation**: Developer-only specs get tied to software design and are hard to understand; tester-only specs are organized in a way that's costly to maintain and hard to automate.
- **Single test-writer (even with reviews) in a complex domain**: Leads to too many overlapping, duplicated tests that are painful to refactor when anything changes.
- **Funneling all specification through one product owner**: Fine for prioritization, but one person can't clarify everything; you still must talk to real stakeholders.
- **Overpreparing**: Fully prescribed examples kill creativity and make teams skip the discussion, reintroducing the analyst-to-developer handoff and leaving functional gaps unfound. Aim for "just enough" — enough "I'm not quite sure" to force a conversation.
- **Drafting semiformal docs in an all-hands workshop**: Doesn't encourage everyone to get involved; reserve file-writing for small groups around one monitor.
- **Excluding stakeholders because "we know the domain"**: Subtleties neither team nor customer anticipated slip through and can't be caught from the tests.

## Worked Example
A team at a U.S. insurance provider runs a **Three Amigos** session for an upcoming loan story. Because the domain needs frequent clarification, they don't rely on a single test-writer. One developer, one tester, and one business analyst gather around a single large monitor with a keyboard — no advance scheduling needed.

The BA frames the story's intended behavior. As they talk, the developer says how he'll implement a field using TDD ("for the telephone field, I'll use an integer"); the tester immediately probes edge cases ("what if I put `++`, brackets, or leading zeros?"). The trio drafts the actual **feature file in Given-When-Then** directly on screen — the acceptance criteria *is* the output. They don't touch fixtures or layers beneath. Where a value is imprecise (a realistic policy number), they drop a placeholder note flagging a little cleanup later. The hard requirement: every test is agreed **complete in content before any code is written**.

Producing this semiformal artifact collaboratively prevents information distortion during later automation and teaches everyone how to write specs that are easy to automate. The result feeds the rest of the team; if domain knowledge had been imbalanced, the quieter participant would have prepared beforehand so the domain expert couldn't dominate the conversation.

## Key Takeaways
1. Collaboration is non-negotiable — Specification by Example won't work on isolated documents no matter how well other patterns are applied.
2. Specification responsibility is shared: programmers contribute implementation/automation insight, testers contribute validation and edge-case thinking, business contributes correct behavior.
3. Most teams work in two phases — someone prepares initial examples up front, then stakeholders discuss and extend them; balance the two by maturity, domain knowledge, change complexity, bottlenecks, and stakeholder availability.
4. Match the model to context: big workshops for starting out/immature; Three Amigos for clarification-heavy domains; pair-writing for mature products; developer review for analyst-written tests; informal conversations when stakeholders are close.
5. Preparation must feed collaboration, never replace it — overprepared, complete-looking examples cause teams to skip discussion and miss functional gaps. Prepare "just enough."
6. Involve actual stakeholders, not just product owners or BA proxies; separate one-person prioritization from team-wide clarification.
7. Put preparation work wherever the bottleneck *isn't* — and keep pre-iteration analysis assigned to a dedicated person so it doesn't swallow the whole iteration.

## Connects To
- **Ch 7**: Illustrating using examples — the core technique these collaboration models run on; Ch 7 walks through a specification workshop end to end.
- **Ch 5**: Deriving scope from goals — collaboration clarifies *what* to build once scope and priority are set.
- **Ch 9 (Living documentation)**: Pair-writing and developer review exist to keep specs easy to automate and maintain over the long term.
- **Ch 12**: uSwitch close-stakeholder model — informal conversations in practice.
