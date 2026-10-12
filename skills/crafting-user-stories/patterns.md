# Patterns & Techniques — The Art of Crafting User Stories

## User Story Template
**When to use**: capturing any requirement in Agile.
**How**: `As a [persona], I want [goal], so that [benefit].` Name who, what, why.
**Trade-offs**: lightweight and user-centered, but a placeholder for conversation — needs acceptance criteria to be testable.

## INVEST Quality Check
**When to use**: before accepting a story into the backlog/sprint.
**How**: confirm Independent, Negotiable, Valuable, Estimable, Small, Testable.
**Trade-offs**: strict independence can be hard with coupled features; treat as a guide, not a gate.

## Persona Creation (4 steps)
**When to use**: before writing stories, to ground the "As a..." slot.
**How**: 1) research (interviews/surveys); 2) identify common characteristics (demographic + psychographic + role); 3) write 1-page profile (name, photo, goals, challenges, behavior); 4) test & refine.
**Trade-offs**: aggregate not individual; stale personas mislead — refresh periodically.

## Empathy Mapping
**When to use**: to expose user emotions/motivations behind behavior.
**How**: pick persona → collect data → fill four quadrants **Says / Thinks / Feels / Does** → analyze for pain points.
**Trade-offs**: qualitative; combine with usage data.

## User Journey Mapping (CUJ)
**When to use**: finding friction across multi-touchpoint experiences.
**How**: define journey → identify touchpoints → identify emotions per step → map visually → analyze (include forward-looking target state).
**Trade-offs**: can sprawl; keep to key touchpoints.

## MoSCoW Prioritization
**When to use**: quick stakeholder alignment on relative importance.
**How**: bucket stories into **Must / Should / Could / Won't Have**.
**Trade-offs**: coarse; no economic ranking within buckets.

## Value-based / RICE Prioritization
**When to use**: scoring stories by impact.
**How (RICE)**: score **Reach × Impact × Confidence ÷ Effort**; rank descending.
**Trade-offs**: depends on estimate quality; confidence guards optimism.

## WSJF (Weighted Shortest Job First)
**When to use**: maximizing economic value / ROI, minimizing waste.
**How**: `WSJF = (Business Value + Opportunity Enablement + Time Criticality + Risk Reduction) / Job Size`. Highest score first.
**Trade-offs**: needs relative scoring of each factor; best with cost-of-delay thinking.

## Kano Model
**When to use**: balancing satisfaction and differentiation.
**How**: classify needs as **Basic** (must exist, taken for granted), **Performance** (more is better), **Delight** (differentiators). Cover basics, invest in delighters.
**Trade-offs**: delighters decay into expectations over time.

## Story-Point Estimation + Planning Poker
**When to use**: relative effort sizing as a team.
**How**: each member privately picks a Fibonacci card → reveal simultaneously → discuss outliers → re-vote to consensus. Track **velocity** to forecast.
**Trade-offs**: points are relative, not hours; velocity only stabilizes over several sprints.

## User Story Splitting
**When to use**: an epic/story too big for one sprint.
**How — split by**: workflow steps · business rules/conditions · data variations · operations (CRUD) · UI components · user roles/system modules. Each slice should still be independently deliverable.
**Trade-offs**: avoid horizontal (layer) splits that aren't independently valuable.

## Definition of Ready (DoR) / Definition of Done (DoD)
**When to use**: DoR gates entry to a sprint; DoD gates "complete."
**How**: DoR — clear, estimated, acceptance criteria defined, dependencies known. DoD — coded, tested, reviewed, acceptance criteria met.
**Trade-offs**: too-strict DoR stalls flow; keep lightweight.

## Story Mapping
**When to use**: visualizing the whole product against the user's workflow; release slicing.
**How**: arrange stories left-to-right by user activity, top-to-bottom by priority; slice horizontal releases.
**Trade-offs**: a planning artifact — keep it current.

## Design Sprint (GV, 5-day)
**When to use**: rapidly prototyping/testing a solution to a complex problem.
**How**: Understand → Define → Sketch → Decide → Prototype; time-box each phase; test with real users.
**Trade-offs**: resource-intensive; one sprint is a start, not the finish.
