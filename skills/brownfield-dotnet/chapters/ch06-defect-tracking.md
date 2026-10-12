# Chapter 6: Defect Tracking

## Core Idea
On a brownfield project you inherit a backlog of stale defects, and the real fix is process, not tooling — you can stay on top of defects without a tool, but never without a process. The chapter drives toward a culture of quality anchored by a **Zero Defect Count** policy.

## Frameworks Introduced

- **Zero Defect Count**: A policy that carrying *any* open defect is unacceptable; every reported defect becomes the highest-priority work item.
  - When to use: After the inherited backlog has been fully cleared; as the permanent steady-state discipline.
  - How: Fix defects as fast as they are reported. A developer needn't drop everything mid-task — finish to a safe check-in point (hours, at most a day). Use developer leads to assign a few defects between feature tasks; consider a short daily defect-only standup, or a single defect supervisor for non-self-organizing teams. Deny "give it to whoever wrote it" hand-offs (reinforces collective ownership over blame).
  - Why it works / failure mode: Reframes defects as accumulating *debt/risk* — if one open defect is OK, why not 500? Fails if any team layer (dev, test, mgmt, client) won't commit, or if defects linger past half a week (culture needs reinforcement).

- **The Initial Defect Triage**: A fast first-pass meeting to either *close* or *assign* every inherited defect.
  - When to use: At project start, to baseline code health from open *and* closed defects.
  - How: Decide three things per defect — (1) what can/can't be done, (2) who does it, (3) how important. Two outcomes only: close (usually only spurious/duplicate/already-fixed ones) or assign. Assignable defects go to **development** if reproducible and confirmed valid, otherwise to **testing** to gather more info. Move fast; no design discussions. Bring testers and the client (or a client proxy).
  - Why it works / failure mode: Per-defect cost of triaging stale defects is high — but necessary to regain confidence. Fails if you over-analyze early defects and short-shrift later ones as fatigue sets in.

- **The 5 C's — Anatomy of a Defect Entry**: Concise, Clear, Complete, Constructive, Closed.
  - When to use: Writing or supplementing any defect entry.
  - How: *Concise* summary (a mnemonic for the defect); *Clear* — replace "Tab order" with "Edit Customer tab order fails leaving Address Line 1"; *Complete* — steps to reproduce, data/files needed, observed wrong behavior, expected behavior, resolution summary; *Constructive* — classify (severity, module) for trend analysis; *Closed* — the goal is always resolution, not "off my plate."
  - Why it works / failure mode: Most rework is a communication problem, not a technical one. Failure mode: back-filling summaries en masse is low-value make-work (but back-filling *classifications* is valuable).

- **Collaborative Prioritization (defect vs. feature)**: Don't argue the bug/feature distinction with the client — make them rank all work.
  - When to use: When clients log feature requests as defects to force attention.
  - How: Put all work (defects + features) in one backlog; have the client rank each item; empower them to choose what's next. Prioritization is ongoing, not one-time.
  - Why it works / failure mode: Whether it's a bug or feature is moot — the work serves the business either way. Client learns they can't have everything; team gains an ally for scheduling. Arguing the distinction breeds "project doesn't serve the business" resentment and Hero Developers.

## Key Concepts
- **Languishing entries**: Old defects never resolved/closed in the system — a sign the *process*, not just the tool, is broken.
- **Incomplete entries**: Defects too vague to act on ("printing error"); pain accrues silently over time.
- **Spurious / ghost defects**: Not real defects — duplicates, wrong-version, or non-reproducible; the most time-consuming to disprove.
- **Feature requests in disguise**: Real missing functionality logged as a defect; politically charged, often becomes a languishing entry.
- **The "Deferred" Defect**: Legitimately postponed work — get it *out* of the open list (status flag you can filter, or even a `DeferredItems.xls`).
- **Client proxy**: Someone with domain knowledge empowered to act on the client's behalf when the client is unavailable.
- **Collective ownership**: All developers comfortable working anywhere in the codebase; disperses "hit by the bus" risk vs. siloed code fiefdoms.
- **Code churn**: Count of how often lines/areas of code change; an *indicator* of fragility warranting deeper investigation, not an auto-trigger for action.
- **Defect debt**: Open defects are a liability with risk, like financial debt; each resolution is risk reduction.
- **Trending data**: Watching rate-of-change of defects by module/version over time — supports decisions, shouldn't drive them.

## Mental Models
- Use **Zero Defect Count** when you want quality to be a cultural force rather than a managed activity — "if quality is naturally high, it's one less thing to manage."
- Use a **client proxy** when the real client can't attend triage but you still need business context to avoid closing defects erroneously.
- Use **swapping teams / tack-on defect tasks** when morale on a long backlog grind is flagging — both buy collective ownership at the cost of slower feature throughput.
- Use **face-to-face conversation** when clarifying a defect; the write-reply-reply email pattern is comfortable but slow and lossy.

## Anti-patterns
- **Treating defect tracking as a second-class citizen**: Installing a tool because "every project needs bug software," with no thought to team process — leads to abandoned/unused systems.
- **Imposing tool concepts the project lacks** (e.g., a "module" field): needless classification, sloppy entries, added friction for the defect creator.
- **"Get it off my plate"**: Finding one clarification point just to reassign a defect to QA; juggling without real work.
- **Numerically meaningless priorities**: Everyone marks their defect "High"/"Urgent" until priority is useless. (Fix: **Numerically Incrementing Priorities** — rank 1..N, no repeats, even when it forces hard calls.)
- **Big-bang "stabilization period"**: Letting defects pile up to fix "before release" — accumulates risk daily.
- **Back-filling release-note/version fields on historical defects**: tedious, error-prone, and historical release notes provide little value.

## Reference Tables

| Defect type | Typical disposition in triage |
|---|---|
| Spurious (duplicate / wrong-version / non-reproducible) | Close — document reasoning |
| Reproducible & client-confirmed | Assign to development |
| Unclear / unconfirmed | Assign to testing for more info |
| Feature-in-disguise | Add to backlog; client prioritizes |
| Deferred | Move out of open list (flag or separate file) |

**Three criteria for a spurious (false) defect** (any one qualifies): (1) the behavior described doesn't exist in the app; (2) the assertion about functionality is incorrect; (3) it duplicates another defect.

**Constructive classification dimensions**: severity, application area/module → feeds insight on problem areas, code fragility, churn, and rework rate.

## Worked Example
**Zero Defect Count In Action (Tales from the Trenches).** A pre-production project carried 700+ open defects — many over two years old, original authors gone, logged against drastically changed modules. The team spent two months in mass triage (efficiently working through reproduction, info-gathering, and resolution) so developers, testers, management, and the client could regain confidence in correctness.

Rather than propose the change bureaucratically, the team *declared* at the release wrap-up that they were moving to Zero Defect Count — a deliberately "dictatorial" move for a drastic culture shift. Management scoffed; developers were stunned; testers "aged instantly," but after the premise was explained the testers bought in. The keys to success: developer leads assigned defects to each developer *between* feature tasks (never asking one person to clear the whole backlog, for morale and equity); hand-offs to "whoever wrote that part" were denied to reinforce collective ownership over blame. After a few months, developers wouldn't pick up new feature work until they'd proven to the leads they'd resolved defects — Zero Defect Count stopped being a managed *policy* and became *culture*. Management stayed skeptical until many consecutive months of success proved it out.

## Key Takeaways
1. Tool vs. process: you can manage defects without a tool, never without a process — and the tool must fit your team's actual workflow.
2. Inherited defects come in four "defective" flavors — languishing, incomplete, spurious, and feature-in-disguise — and the backlog has a high per-defect cost; clear it sooner because it only gets staler.
3. Triage fast: close or assign, bring testers + client/proxy, document everything (even un-reproducible closures).
4. Don't fight the defect-vs-feature war — let the client prioritize all work in one ranked list; use unique numeric priorities so ranking stays meaningful.
5. A good defect entry is Concise, Clear, Complete, Constructive, Closed — most defect pain is a communication failure.
6. Zero Defect Count is the destination: defects are debt; making quality the team's foremost concern (not perfect first-try code) is what makes "zero" realistic.
7. Use trending (defects per module/version over time, rework rate) to *support* refactoring decisions, not to mechanically drive them.

## Connects To
- **Ch 2**: "Check In Often" — Zero Defect Count lets a developer finish to a safe check-in point before switching to a defect rather than stopping dead.
- **Ch 4**: Re-integrating existing tests — analyzing defects parallels reviewing inherited tests, but involves testers and business, not just developers.
- **Ch 5**: Code metrics — code churn and module trending extend static-analysis thinking into defect data.
- **Ch 1**: "Hero Developers" — the anti-pattern that arguing defect-vs-feature with clients can breed.
- **Ch 7**: This chapter **ends Part 1 "The Ecosystem."** Part 2 "The Code" begins next with object-oriented fundamentals — moving from process/ecosystem to the application's actual code.
