# Chapter 6: The Big Rewrite

## Core Idea
A from-scratch rewrite is the least-worst option only after refactoring, third-party replacement, and re-architecting have all failed; if you must do it, define a tight scope, treat the old code as a reference (not gospel), and keep the legacy system running in parallel so you can cut over incrementally and fail back when bugs appear.

## Frameworks Introduced

- **Exhaust-all-options-first decision rule**: A rewrite is justified only when every cheaper path is closed.
  - When to use: refactoring hit an impasse, AND a third-party product would need so much customization it's more work than building, AND re-architecting can't get you there.
  - How: enumerate the alternatives, prove each is exhausted, then accept that "there's no getting away from a rewrite." Go in eyes-open about the two costs below.
  - Go/no-go criteria (why your skin should crawl):
    1. It will take far longer than estimated — copying "what it does now" means excavating every corner case, rabbit hole, and undocumented behavior (laborious, dull investigation, not coding).
    2. It often delivers limited direct user value — months of work to reproduce existing behavior, while introducing new bugs and risking backlash from users who treat old bugs as features.

- **Three forms of rewrite (pick one up front)**: Classifies the project goal so stakeholders agree on what success means.
  - **Black-box rewrite**: keep functionality identical, reimplement internals (e.g. port off a mainframe, improve maintainability). Ideal: user notices nothing.
  - **Brush-up rewrite**: black-box plus the chance to document, update, and normalize the spec so the new software behaves differently/better.
  - **Quid pro quo rewrite**: bundle major new features into the rewrite to win business/management approval. Accepts that conflating "preserve old behavior" with "add new features" complicates planning, but it's often the only way to get the project green-lit.

- **Scope document (Single Source of Truth)**: Short, unambiguous, signed-off charter that anchors the project against feature creep.
  - When to use: before any code; every large project (rewrites included) needs one.
  - How — include: mission; developer goals; PM goals; end-user benefits; **New features** (each tagged must-have / nice-to-have); **Existing features** (which are kept/dropped, must-have / nice-to-have); **Timeliness vs feature-completeness** (date or completeness?); **Phased releases** (summary of each phase). Everyone reads, agrees, "speaks now or forever holds their peace."

- **"Learning from the past" balance rule**: How much the existing implementation acts as the spec.
  - When to use: every time a feature's behavior is ambiguous and you're tempted to either copy the old code verbatim or rewrite from first principles.
  - How: treat old code as a reference / tie-breaker, not the ultimate truth. For low-level detail, mine it. For high-level design/architecture, deliberately avoid emulating it. When a behavior is unclear, dig the VCS history: if there's evidence a condition was added for a reason, port it (with a documented why); if no record exists, discard it.

## Key Concepts
- **Black-box / brush-up / quid pro quo rewrite**: the three goal-types above; decide which you're doing first.
- **Big Bang release/cutover**: all-or-nothing switch at project end; high risk, no early feedback, no fallback.
- **Incremental (iterative) rewrite**: many small releases; needs old + new running side by side; less risky.
- **Parallel running**: old and new systems both live during migration, with two-way data sync, so traffic can be switched back on failure.
- **Cutover**: the moment traffic is redirected from legacy to new app; after it, write-replication reverses direction.
- **Translation layer**: code (or DB views) converting between new domain models and legacy DB models when sharing a DB.
- **Real-time vs batch synchronization**: near-instant write replication vs bulk copy (full or query-scoped) for recovery.
- **Sole-writer assumption**: an app assumes only it writes its DB; parallel running invalidates this, causing stale caches / overwrites.
- **Event Bus (Publish/Subscribe)**: pattern for emitting DB-write notifications to the other app, designed to be removed at legacy shutdown.
- **Traffic replication**: copy incoming requests to both apps (return only one's response) instead of forwarding writes between them.

## Mental Models
- **Use an iterative/phased rewrite when** you can run old and new side by side — the reduced risk and early feedback outweigh the extra sync effort. Use Big Bang only when parallel running is genuinely impossible (and accept the risk).
- **Use the existing code as a tie-breaker, not a blueprint, when** the spec is ambiguous — copy it too faithfully and you've just rebuilt what you had; ignore it and you lose years of bug fixes and corner-case handling.
- **Use a shared DB when** simplicity dominates and you can't change schema/tech anyway; **use a separate DB when** you need new datastore tech, to split a monolith, or to refactor the schema — and you can afford the sync tooling.
- **Use traffic replication instead of write-forwarding when** the apps have separate DBs and the new app is stable enough to receive most traffic.

## Anti-patterns
- **Rewriting from scratch before exhausting refactoring / replacement / re-architecting**: you take on the longest, dullest, lowest-value, highest-risk path unnecessarily.
- **Treating the legacy implementation as the ultimate source of truth**: you remake exactly what you had and inherit its design flaws; subconscious emulation of old architecture is the trap to actively fight.
- **Big Bang cutover with no fallback**: no early feedback, no way to revert; a production bug strands users on the new system.
- **Letting legacy DB models leak into the new codebase**: without a watertight translation layer, legacy hacks infect your clean domain models.
- **Corrupting the shared DB silently**: if new-app writes can't be read by the old app, you lose the parallel-running fallback and may not notice corruption for weeks.
- **Splitting live traffic to both apps simultaneously with two-way real-time sync**: order-of-magnitude more complexity and high data-corruption risk (e.g. one app updates a record the other deletes). Avoid unless you must.
- **Burying migration logic in DB triggers / stored procs / cron shell scripts**: invisible to source-reading developers; prefer application-layer code (unless performance forces DB-layer).

## Reference Tables

Rewrite vs the alternatives (decision gate):

| Option | Choose when | Cost/Risk |
|---|---|---|
| Refactor (Ch3/Ch4) | Codebase still tractable | Lowest |
| Third-party replacement | Off-the-shelf fits with little customization | Medium |
| Re-architect (Ch5) | Structure is the problem, code salvageable | Medium |
| Full rewrite (this ch.) | All above exhausted | Highest |

Database strategy:

| | Shared legacy DB | New separate DB |
|---|---|---|
| Simplicity | High (one DB, no sync) | Low (build sync tooling) |
| Touch other scripts/batches? | No | Maybe |
| Choose DB tech | No | Yes |
| Re-architect / split services | No | Yes |
| Refactor schema | No (must keep legacy compatible) | Yes |
| Main hazard | Corrupting shared data | Datastores drifting out of sync |

Synchronization query examples (single polling tool, vary the query):

| Sync type | PostgreSQL fragment |
|---|---|
| Near real time | `WHERE last_updated > current_timestamp - interval '1 second'` |
| Batch recovery (last 24h) | `WHERE last_updated > current_timestamp - interval '1 day'` |
| Full replication | `WHERE 1 = 1` |

Real-time sync approaches (Fig 6.5): DB-to-DB push (trigger copies write), DB-to-app push (trigger writes to queue, app consumes — queue avoids lost writes when app down), App-to-app push (legacy app writes to queue — undesirable: requires changing fragile legacy code), DB polling/pull (poller reads legacy DB — minimal legacy changes, slight lag).

## Worked Example
**World of RuneQuest** — a 10-year-old Java servlet game, stack frozen, UI dated, hard to maintain. Developers want a modern rewrite (Play/Scala); PMs want a real spec; upper management won't fund a "by devs, for devs" project. Resolution: a **quid pro quo rewrite** branded as a major new version, adding player-requested features competitors already have (in-game voice chat = must-have; advanced stats = nice-to-have). The scope doc names a deadline, marks all existing features must-have except Map Editor (nice-to-have) and Daily Email (won't implement), prefers on-time over feature-complete, and plans 3 releases at 3-month intervals with a user-data sync tool until the old system is switched off.

**The Player Matching dilemma**: Sarah picks up a card to reimplement player matching; the new spec says only "match a waiting player with another of similar ability." She and PM Phil read the legacy `runWaitingRoom()` loop — a thicket of conditions (`if (p1.isElf() && p2.isOrc()) continue;`, weapon/shield checks, etc.) wrapped in a `while(true) { ... Thread.sleep(1000L); }`. Rather than copy or guess, they walk the SVN log noting when/why each condition was added; Phil writes a fresh spec keeping only conditions with evidence (documenting why) and discarding unexplained logic. They also note the once-a-second polling design is worth replacing with events/event-handlers or the Actor model — proof of refusing to be constrained by legacy design.

**DB migration with two-way sync** (Fig 6.6/6.7): separate DBs, queue-based real-time replication, a batch replication tool, and a monitoring tool that alerts devs and auto-triggers re-replication of missed updates. Sync runs **both directions** so traffic can switch between apps. Before cutover: traffic → legacy, writes replicate to new. After cutover: traffic → new, writes replicate back to legacy. Find a bug: switch traffic back to legacy (which still has all the latest data) while you fix it — the essence of low-risk migration.

**Translation layer example**: legacy `player` table conflates human user + in-game persona (no `Character` model). New design wants many Characters per Player. Hack: keep each Player's first Character in `player`, put the rest in a new `character` table — invisible to the legacy app. The translation layer hides this ugliness so the new domain model just sees a Player with a list of 5 Characters. Alternative: do it with a writable DB **view** (`player_character`) the legacy app queries instead — but the author prefers application-layer logic (readable, testable, visible) unless performance demands DB-layer.

## Key Takeaways
1. Don't rewrite until refactoring, replacement, and re-architecting are genuinely exhausted — and even then expect it to run long and deliver little visible value.
2. Decide and document the rewrite type (black-box / brush-up / quid pro quo) and a signed-off scope document up front; it's your weapon against feature creep.
3. Make the rewrite iterative with phased releases; this requires running old and new in parallel but slashes risk.
4. Respect the old code as a reference for low-level behavior and a tie-breaker in debates, but never let it dictate the new architecture — use VCS history to keep conditions that earned their place and drop the rest.
5. Choose shared-DB (simple, constrained) vs new-DB (free, sync-heavy) deliberately; shared needs a watertight translation layer, separate needs serious real-time + batch + monitoring tooling.
6. Two-way data sync enables safe incremental cutover with fail-back; avoid Big Bang cutover and avoid simultaneous dual-write traffic splitting.
7. Parallel running breaks the sole-writer assumption — notify apps of external writes (Event Bus / Pub-Sub) and build the new side so the legacy-bridge can be removed cleanly at shutdown.

## Connects To
- **Ch3**: the refactor → re-architect → rewrite spectrum weighed by value/cost/risk; this chapter is the far, most-expensive end of it.
- **Ch4**: World of RuneQuest as the running case study; characterization/understanding of legacy behavior feeds the "learning from the past" rule.
- **Ch5**: re-architecting as the less drastic alternative to exhaust before committing to a full rewrite.
- **Strangler Fig (Martin Fowler)**: parallel-running + incremental cutover here is a strangler-style migration — grow the new system alongside the old, route traffic over time, retire the legacy app last.
- **Joel Spolsky, "Things You Should Never Do"**: the chapter's opening "exhaust all options, your skin should crawl" framing echoes Spolsky's classic warning that rewriting from scratch is the single worst strategic mistake — throwing away accumulated bug fixes and corner-case knowledge.
