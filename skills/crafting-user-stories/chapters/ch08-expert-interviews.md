# Chapter 8: Expert Interviews

## Core Idea
Four practitioners (Sean Mack, Bob Galen, Michael Spayd, Lyssa Adkins) converge on one message: a user story is not a requirement document but a deliberately incomplete placeholder for a future conversation — its power lies in collaboration, emergence, and traceability to business value, not in upfront completeness.

## Frameworks Introduced
- **Story-as-placeholder (Spayd / Adkins)**: A user story is "a placeholder for a future conversation," not a detailed spec — a game piece you pull down off the wall when it's time to build.
  - When to use: at backlog creation and refinement, whenever teams pressure themselves to fully specify upfront.
  - How: write a headline plus a couple of notes; leave acceptance criteria as a stub; defer detail to a live conversation with the customer present.
- **The 30–40% completeness curve (Galen)**: A story only needs to be ~30–40% defined when it enters a sprint; it reaches complete definition by sprint's end.
  - When to use: to calibrate how much detail to write before estimating.
  - How: define only the key bits needed to picture, estimate, and de-risk the work; flesh out the rest iteratively. The number isn't magic — the point is "terse to begin with."
- **Three Amigos (Galen)**: Co-create stories with multiple perspectives — typically development, testing/QA, and product — adding architecture or DevOps "amigos" when the story warrants.
  - When to use: during story creation and refinement, especially for stories with architectural or operational implications.
  - How: bring the right people together to shape the story collaboratively (not write-and-handoff); they act as shepherds of value, not a writing authority. Avoid meetings for meetings' sake.
- **Objective-to-story traceability (Mack)**: Maintain an unbroken line from annual business objectives down to individual stories.
  - When to use: annual/quarterly planning in objective-driven organizations.
  - How: map objectives and measures → break into program increments → deliver via stories; review progress against objectives quarterly so daily work's impact is visible.

## Key Concepts
- **Placeholder for a future conversation**: the defining metaphor — the story exists to trigger collaboration, not to contain the answer (attributed variously to Phil Wait).
- **Embracing ambiguity**: stories are intended to carry built-in uncertainty that resolves over time; discomfort with this is normal and expected.
- **Interrupt pattern (Adkins)**: Agile/story practices deliberately interrupt the unconscious learned habit of handing detailed requirements down to a team.
- **Risk-based testing via acceptance criteria (Galen)**: value-oriented acceptance criteria signal to testers where the critical business value sits, guiding where to test hardest.
- **Teardrop metric (Galen)**: an outcome measure of customer delight — "That's exactly what I envisioned" — ranging from negative to high.
- **Flow metrics (Mack)**: lead time, cycle time, throughput, WIP — give visibility into how work flows and what kind of work gets done.
- **Collaborative ownership / "everyone a chef" (Galen)**: teams of collaborators who take ownership, not order-takers implementing handed-down tasks.

## Mental Models
- Use the **placeholder mindset** when teams freeze trying to specify everything upfront — write less, force a "bad" first draft, let detail emerge.
- Use **risk-based testing** when test capacity is finite — let value-driven acceptance criteria tell you what to hammer on.
- Use **objective-to-story traceability** when you need to prove daily work moves business goals.
- Use the **interrupt-pattern lens** when an org reflexively reverts to Waterfall-style detailed handoffs — the formulaic brevity of stories is itself the corrective.

## Anti-patterns
- **Writing too much upfront**: the biggest anti-pattern for new teams; carried over from Waterfall training that conflates rigor with volume. It blocks emergence and customer collaboration.
- **Requirements as a signed contract**: an arm's-length document written by an intermediary (BA) who never talks to the developer; breeds "you should have known" / "how could we have known" finger-pointing.
- **Throw-in-the-kitchen-sink requirements**: when customers fear they get only one chance to speak, they list everything they could want — Adkins cites ~70% of features rarely or never used.
- **Checkbox acceptance criteria**: criteria that exist only because the template demands them, or so many they obscure what's actually valuable.
- **Order-takers, not collaborators**: a team that just implements handed-down specs instead of co-owning and problem-solving.

## Key Takeaways
1. Write less to start — a headline and a few notes is enough; deliberately write a "bad," terse, incomplete story and let detail unfold over time.
2. Treat every story as a placeholder for a future conversation with the customer who is present and ready to collaborate, not a finished spec.
3. Aim for only ~30–40% completeness at sprint entry — just enough to picture, estimate, and de-risk before executing.
4. Co-create stories with multiple perspectives (Three Amigos: dev, QA, product — plus architecture/DevOps when relevant); shape requirements together rather than handing them off.
5. Keep customers and stakeholders engaged continuously — not just at sprint reviews but during refinement and whenever appropriate — to close the communication gap.
6. Invest in value-oriented acceptance criteria: they tell testers where to focus risk-based testing and signal to developers which areas (e.g., performance) are critical.
7. Measure outcomes, not output — prioritize customer-delight ("teardrop") and outcome-based value over story-completeness counts; pair with flow metrics (lead/cycle time, throughput, WIP).
8. Trace stories to business objectives through planning so the impact of daily work on goals stays visible.
9. Close the feedback loop — ask customers "do you care about what we built, will you use it, how should we change it?" — to avoid building the unused majority.
10. Use facilitation tricks (e.g., proposing a deliberately weak story to provoke "I can do better") to pull the team into collaborative ownership.

## Worked Example
Galen's "write a nonsensical story on purpose" tactic: he sometimes drafts an absurd user story specifically so the team will call it out — "This is absurd" — letting him reply, "Okay, who can write it better?" The provocation converts passive order-takers into collaborators and produces a story the team owns. The lesson: collaborative definition often needs a catalyst, and a deliberately imperfect draft is a cheaper, faster catalyst than a polished one.

## Connects To
- **Ch 1–2**: grounds the foundational definition of a user story as a placeholder/conversation rather than a requirement.
- **Acceptance-criteria / testing chapters**: Galen's risk-based use of acceptance criteria operationalizes how criteria drive both testing and design priorities.
- **Estimation/planning chapters**: the 30–40% completeness curve sets how much detail must exist before a story can be estimated and pulled into a sprint.
- **Metrics chapter / Example scenario**: Mack's flow metrics (lead time, cycle time, throughput, WIP) and objective traceability feed directly into measuring story impact.
