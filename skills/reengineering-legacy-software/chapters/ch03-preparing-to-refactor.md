# Chapter 3: Preparing to Refactor

## Core Idea
Before touching code, win the social and political battle: get your team communicating and aligned, get the organization to fund the work with explicit business value, then triage which refactorings are worth doing and decide where you sit on the refactor → incremental-rewrite → full-rewrite spectrum (default to refactoring).

## Frameworks Introduced

- **Three axes of refactoring (value / difficulty / risk)**: every candidate refactoring is scored on three dimensions. *Value* = usefulness to team/org. *Difficulty* = effort to perform. *Risk* ≈ number of dependents (more dependents → higher chance of a side-effect regression). (The skill brief calls this "value/cost/risk"; the book's middle axis is **difficulty** = cost-to-do.)
  - When to use: triaging a backlog of possible refactorings; deciding where the Iconoclast should aim.
  - How: plot each refactoring on the three axes; target two named categories →
    - **Low-hanging fruit** (risk = low, difficulty = low): start here.
    - **Pain points** (value = high): fix enough and you're a hero. Use chapter-2 data (FindBugs warnings, build/CI signals) to find both.

- **Refactor → Incremental rewrite (The Third Way) → Full rewrite spectrum**: a risk/power continuum at three altitudes — code-level (refactor), module/component-level (incremental rewrite), system-level (Big Rewrite).
  - When to use: deciding how to revitalize a legacy system.
  - How: prefer the lowest-risk option that achieves the goal. Refactor by default; reach for rewrite only when two necessary conditions both hold (below); use incremental rewrite as the middle path.

- **Necessary conditions for a (full) rewrite** — BOTH must hold:
  1. **Refactoring tried and failed**: you spent considerable time/effort refactoring with no noticeable quality improvement. (Even a doomed refactoring teaches you the codebase and informs the rewrite design.)
  2. **Paradigm shift**: a fundamental tech change is needed (most commonly a language/framework change — e.g. COBOL→Java because COBOL engineers are rare; Spring MVC→Rails for productivity).

- **The Third Way (incremental rewrite)**: split the rewrite into phases, two hard rules — (a) each phase delivers business value on its own; (b) you can stop after any phase and still keep the gains.
  - When to use: you want to rewrite parts but a big-bang cutover is too risky / delivers nothing until the end.
  - How: divide the legacy system into logical components (ideally along existing feature boundaries), give each a well-defined public interface (a preliminary refactoring phase), then go component-by-component deciding per-component whether to refactor or rewrite. Often pairs with re-architecting a monolith into services (ch. 5).

- **Value proposition (make it official)**: write down specific, measurable goals tied to *named* features before starting, e.g. "make feature X possible" / "improve feature Y performance by 20%."
  - When to use: securing resources/approval from business stakeholders for any large refactoring.
  - How: state concrete goals (not "improve maintainability"); they fix scope, justify budget, and act as a guardrail against feature creep. Keep it visible.

- **Secret 20% Project (Plan B)**: for small refactorings (rule of thumb: one developer, < 1 week), skip the approval process — just do it.
  - When to use: small, uncertain, or over-discussed changes where a prototype answers questions faster than meetings.
  - How: (1) start without seeking authorization; (2) spend < 20% of your time on it so it doesn't disrupt real work; (3) once results are worth sharing, open it for team review; (4) refine on feedback. Not real secrecy — the point is a working prototype beats endless pre-fact debate.

## Key Concepts
- **Technical debt**: Ward Cunningham's metaphor — accumulated unresolved issues (quick hacks, copy-paste, good-enough fixes) that you pay "interest" on via slower development and reduced flexibility.
- **Traditionalist**: developer averse to all change; "if it ain't broke, don't fix it"; sees refactoring as risk/distraction.
- **Iconoclast**: developer who can't bear others' code and over-refactors; risks regressions, unreviewable diffs, and team resentment.
- **Strangler pattern (Fowler)**: build the new system around the outside of the old one, intercepting inputs/outputs and assuming more responsibility until the original quietly dies — close cousin of the incremental rewrite.
- **God class**: a giant (e.g. 3,000-line) class of static utility methods that surrounding code is forced to depend on; design gravity makes it grow.
- **Greenfield doesn't stay green**: fresh rewrites quickly re-accumulate the same complexity, because "implementation cruft" is usually "complicated spec" in disguise.
- **Regression (rewrite-specific risk)**: existing source encodes every business rule and years of bug fixes; miss one and behavior changes for a user.
- **Demarcating code**: agreeing as a team which areas are high-value and which are high-risk, so effort lands where it pays.

## Mental Models
- Use **refactoring** when the existing system is a trustworthy production foundation and a disciplined sequence of small behavior-preserving steps can lift quality — verify after each step with reviews + tests.
- Use **incremental rewrite** when you genuinely need to replace modules but cannot accept the risk/zero-interim-value of a big bang — and the system splits cleanly into value-delivering phases.
- Use **full rewrite** only when refactoring has demonstrably failed AND a paradigm/technology shift is required.
- Use **replace (third-party/OSS)** before writing anything: "the best code is no code at all" — every line you write you maintain for years.
- Use the **Secret 20% Project** when a refactoring is < 1 dev-week or when discussion has stalled into "meetings about meetings."

## Anti-patterns
- **Full ("Big Bang") rewrite**: almost always a bad idea — high risk, large overhead (boilerplate, ops, environments), invariably overruns, delivers zero value until done, and silently reintroduces old bugs/regressions.
- **Refactoring without business value or sign-off**: zero new features by definition; stakeholders won't fund it and will cancel it when deadlines loom unless value is pre-justified.
- **Lone-wolf / unreviewed refactoring**: large unreviewable diffs breed regressions; the Iconoclast's rogue rewrites also corrode team morale and knowledge sharing.
- **Mandatory pair programming**: forcing it on the unwilling "ends in failure"; offer it, don't enforce.
- **No clear goals on a big project**: scope balloons (the author's own The Site rewrite stretched past a year across multiple teams).
- **Rewrite disguised as refactoring**: transplanting huge swaths of legacy code into the "new" system means you're doing a roundabout, inefficient refactoring.

## Reference Tables

Refactoring triage (two recommended target categories on the value/difficulty/risk axes):

| Category | Profile | Why |
|---|---|---|
| Low-hanging fruit | risk = low, difficulty = low | Safe, cheap; good place to start |
| Pain points | value = high | Big payoff; team treats you as a hero |

Refactor vs. full rewrite:

| Dimension | Refactor | Full rewrite |
|---|---|---|
| Risk | Lower; works against proven foundation | High; new project, regression risk |
| Behavior preservation | Small steps preserve behavior | Must re-discover every rule & bug fix |
| Interim value | Incremental — stop anytime, keep gains | None until the final cutover |
| Overhead | Low | High (boilerplate, ops, multi-env) |
| Estimation | Hard but task-sized | Very hard ("how many iPhones in a cinema screen?") |
| Upside | Limited | Freedom; build-in testability |

## Worked Example
**Incremental rewrite of Orinoco.com** (monolithic Java servlet e-commerce site). Because the site already has self-contained features (Listings, Search, Recommendations, Checkout, My Page, Authentication), split it into one JAR per feature, then phase the work so each phase ships value:

| Phase | Description | Business value |
|---|---|---|
| 0 | Preliminary refactoring: define component interfaces, split into separate JARs | Clear interfaces increase maintainability |
| 1 | Rewrite Authentication; change password storage | Better data-security compliance |
| 2 | Rewrite Search; switch search engine | Better search results; users find products |
| 3 | Refactor Recommendations | Test recommendation algorithms faster |

Per-component, you decide refactor vs. rewrite based on each component's condition; phases can be reordered by business priority; stakeholders can stop whenever value runs out. (Often this is also the moment to re-architect the monolith into services — deferred to ch. 5.)

## Key Takeaways
1. Improving legacy code is a team sport: secure communication and shared goals (code review, optional pairing, Tech Talks / special events) before you start.
2. Refactoring must justify itself in business terms — write specific, feature-named, measurable goals, make it official, and expect to defend it more than once.
3. Triage everything by **value, difficulty, risk**; start with low-hanging fruit and high-value pain points.
4. Consider options in order: **replace (buy/OSS) → refactor → rewrite**. Default to refactoring.
5. A full rewrite is almost always wrong; only justified when refactoring has tried-and-failed AND a paradigm shift is required — both conditions.
6. When you must rewrite, prefer the **incremental "Third Way"**: phase it so each phase delivers value and stopping early still leaves you ahead (cf. Strangler pattern).
7. Manage the social side: channel the Iconoclast with code review + mandatory tests + sized diffs; convert the Traditionalist with pairing and a concrete demonstration of technical debt.

## Connects To
- **Ch 2**: Reuse the continuous-inspection data (FindBugs warnings, CI/build signals) to locate low-hanging fruit and pain points.
- **Ch 4**: Disciplined small transformations plus automated tests are what make refactoring lower-risk than rewriting; ch. 4 covers testing while refactoring legacy code.
- **Ch 5**: Re-architecting a monolith into a service-oriented architecture — the natural extension of component-splitting in the Orinoco incremental-rewrite example.
- **Strangler pattern (Martin Fowler)**: external analog of the incremental rewrite — wrap and gradually replace the old system.
- **Working Effectively with Legacy Code (Feathers)**: the "refactor under tests / break dependencies" discipline underpinning the case against rewriting.
