# Appendix A: An Overview of Extreme Programming

## Core Idea
User stories originated in Extreme Programming (XP), where they are the primary unit of requirements: the customer writes them, developers estimate them, and they flow through the Planning Game into iterations and releases. The story practice only works inside XP's surrounding web of practices (on-site customer, testing, small releases) — the twelve practices are synergistic and interdependent, not a menu to pick from.

## Frameworks Introduced

- **The Twelve Practices**: adopt all of them; they support and enable each other (refactoring is made safe by pair programming, simple design, collective ownership, continuous integration, and testing). Customize only after mastering standard XP.
  - When to use: at project start; choose the full set rather than favorites.

- **Small Releases**: progress in fixed timeboxed iterations (1–3 weeks, never >4). A feature (story) is fully delivered within one iteration — never half a feature, never full feature at half quality. Iteration ends on its scheduled day; scope (not quality, not duration) flexes.
  - How: pick the shortest iteration length that still delivers tangible business value; when undecided, choose the shorter.

- **The Planning Game**: XP's name for collaborative release + iteration planning where developers and customer predict the future.
  - How: customer pre-writes stories on cards; developers estimate cost on each card; developers state how much work fits one iteration; customer selects highest-priority stories summing to (not exceeding) that capacity, fills iteration 1, then 2, etc. Enough iterations = a release plan (a hypothesis, re-planned each iteration).

- **Refactoring**: restructure/rewrite code to improve it without changing external behavior. Programmer is *required* (not encouraged) to refactor code she touches that needs it. Replaces big upfront design.

- **Testing / Test-Driven Development**: developers write automated unit tests; customers write (often automated) acceptance tests. TDD = write a failing test first, verify it fails, then write only enough operational code to pass. No operational code except in response to a failing test; cycle is minutes, not hours.

- **Pair Programming**: two programmers, one keyboard/monitor, two brains; one types and thinks ahead, the other thinks broadly. Switch roles/partners often. ~15% more programming time buys lower defects, less code, faster solutions, shared understanding, higher satisfaction — and enforces the discipline the other practices demand.

- **Sustainable Pace**: brisk but consistent pace beats unsustainable bursts; ~6 hrs/day of pairing, team sets its own pace; coach watches for burnout.

- **Team (Collective) Code Ownership**: all code owned by everyone; any pair can change any code. Coherence is protected by the unit-test suite (TDD), not by individual gatekeepers.

- **Coding Standard**: shared naming/formatting conventions — required because everyone edits everything; keep it brief and essential.

- **Simple Design** (Beck's 4 constraints): code+tests fully convey intent; no duplication; fewest classes; fewest methods. Do the simplest thing that could possibly work.

- **Metaphor**: a single system-wide frame of reference (e.g., "the system is a chalkboard") that gives a simple, shared way to think about behavior, supporting simple design without a master architecture.

- **Continuous Integration**: integrate at least daily, in practice continuously — check in a small change, an automated build + test suite runs, failures emailed immediately; integration problems fixed in tiny batches as they occur.

- **On-Site Customer**: customer sits with the team, writes stories and acceptance tests, answers questions as they arise. Essential to the story approach because stories depend on many customer–developer conversations; an absent customer causes delays.

## Key Concepts
- **The Customer**: role responsible for writing and prioritizing stories and writing/executing acceptance tests; may be a user, product/project manager, or analyst; may be a customer team speaking "with one voice."
- **The Programmer**: broad technical role (no programmer/designer/DBA distinction); works as a team; unit-tests everything.
- **Coach**: monitors adherence to XP practices and nudges the team back on track; watches for burnout.
- **Project Manager**: more leader than manager; shelters the team from bureaucracy and removes obstacles.
- **Iteration**: firm 1–3 week timebox delivering working, tested, usable code.
- **Release**: a set of iterations whose stories collectively define a shippable plan (a revisable hypothesis).
- **Acceptance test**: customer-defined test per story; replaces waterfall requirements documents.
- **Spike**: (referenced in story estimation context) a short experiment to learn enough to estimate.

## Mental Models
- **Think of the release plan as a hypothesis, not a contract** — it is re-planned each iteration as priorities shift and velocity becomes known.
- **Use scope as the flex variable** — when an iteration runs short on time, cut work, never extend the date or lower quality.
- **Think of TDD as putting code in maintenance mode from day one** — well-factored and testable by construction.
- **Use pairing to enforce discipline** — alone it's too tempting to skip "just this once" a refactor or test.

## Worked Example
A story flows through XP like this: the customer writes "A user can reset her password" on a card; developers estimate it (say, 3 points) and write that on the card. In the **Planning Game**, developers declare they can do ~20 points per 2-week iteration; the customer selects her top-priority cards up to 20 points for iteration 1, then fills later iterations, defining a **release**. At **iteration planning**, the team takes the highest-priority stories for this iteration and breaks each into tasks. During the iteration, a pair practices **TDD** (failing acceptance/unit test → code), **refactors** freely under **collective ownership**, and **integrates continuously**. By the firm end date, the story is **fully delivered**, passing the customer's **acceptance tests** — or it's dropped to a later iteration, but never shipped half-done.

## Key Takeaways
1. User stories are an XP artifact; they presuppose XP's surrounding practices — especially the on-site customer and acceptance testing.
2. The Planning Game is the engine that turns estimated story cards into iteration and release plans.
3. Iterations are firm timeboxes; flex scope, never date or quality.
4. The twelve practices are interdependent — refactoring, TDD, pairing, collective ownership, and CI mutually reinforce.
5. XP's four values — communication, simplicity, feedback, courage — and five principles (rapid feedback, assume simplicity, incremental change, embrace change, quality work) define XP even more than any single practice.

## Connects To
- **Ch 1**: introduces what a user story is — here we see its native XP habitat (cards written by the customer, estimated by developers).
- **Ch 6**: acceptance testing — the XP customer's responsibility for per-story acceptance tests, replacing requirements docs.
- **Ch 9–10**: release planning and iteration planning — direct elaboration of XP's Planning Game (estimating velocity, prioritizing cards into iterations, breaking stories into tasks).
