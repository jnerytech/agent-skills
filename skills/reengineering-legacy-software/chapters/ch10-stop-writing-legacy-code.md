# Chapter 10: Stop Writing Legacy Code!

## Core Idea
The same disciplines used to rescue legacy code prevent new code from becoming legacy — but it's far cheaper to build them in from day one. The closing chapter recaps five cross-cutting themes (source isn't the whole story, information leaks away, the work is never done, automate everything, small is beautiful) and argues the highest-leverage move is writing **disposable** code.

## Frameworks Introduced

- **Darwinian documentation**: Survival-of-the-fittest doc maintenance.
  - When to use: any project accumulating stale docs.
  - How: keep docs concise and inside the same Git repo as the code (so they're committed/reviewed alongside changes); periodically review and *delete* any doc that's out of date rather than trying to salvage it — if it wasn't maintained, it wasn't useful.

- **Foster communication** (knowledge-sharing practices to break silos):
  - **Code reviews**: every change reviewed by ≥1 other developer — catches mistakes *and* spreads knowledge of what others are doing.
  - **Pair programming**: try it for a few weeks (past initial weirdness), then let people opt in; the goal is people pairing unprompted.
  - **Tech talks**: regular (e.g. Friday afternoon) presentations to show off and learn.
  - **Present projects to other teams**: semi-regular cross-team technical overviews surface duplication and sharing opportunities.
  - **Hack days**: cross-team, new-tech, off-site building to mix people and ideas.

- **Periodic whole-codebase review**: Catch architecture-level issues that per-change reviews miss.
  - When to use: in addition to (not instead of) day-to-day change reviews.
  - How: (1) everyone spends ~1hr reading the code and taking notes beforehand; (2) one knowledgeable person leads, intros the code, then solicits comments; (3) cap each session ~1hr, run multiple sessions over weeks if needed; (4) write up conclusions split into concrete actions vs. ideas-to-investigate, share, and check progress weeks later.

- **Fix one window**: Personal entropy-fighting habit (from the broken-window theory).
  - When to use: continuously, as collective-ownership ritual.
  - How: make it a personal objective to fix one "broken window" (hack/pain point) every couple of weeks, and make the fix *visible* (code review is a good amplifier) so others are inspired to repair too.

- **Disposable software / "small is beautiful"**: Design so any component can be thrown away and rewritten in days/weeks, not months.
  - When to use: as the top design priority for new software.
  - How: build large systems from many small, decoupled, replaceable components (modular monolith *or* microservices). Keep each piece small enough that a successor who dislikes it can discard and rewrite with negligible risk.

## Key Concepts
- **Legacification**: the gradual rot of new code into legacy; prevented mainly by tests and small modules.
- **Living specification**: a suite of high-level (functional/integration/acceptance) tests that stays in sync with behavior because CI fails when they drift — unlike a written spec doc.
- **Broken-window theory**: visible disrepair invites more disrepair; visible repair invites more repair.
- **Collective code ownership**: quality is everyone's responsibility, not one person's.
- **Knowledge silo**: a developer who holds critical undocumented information; their departure loses it.
- **Theseus' paradox / Ford Model T analogy**: a system whose parts are all individually replaceable can outlive every one of its original components.
- **Source code is not the whole story**: toolchain, infra, docs, automation, and team culture determine project success as much as code quality.

## Mental Models
- Use **higher-level tests as documentation** when you want a successor to understand behavior; use **unit tests** when writing new code for fast feedback — and it's OK to delete unit tests later if they obstruct refactoring (provided higher-level tests guard regressions).
- Use **disposability over preservation**: keeping geriatric code on life support because it's "too big to die" is worse than designing it small enough to die cheaply.
- Use the **"stitch in time"** rule: fix technical debt the moment it appears — the cost only compounds.
- Prefer **building quality in early** over retrofitting it; greenfield is the cheapest time to add tests, docs-in-repo, automation, and review culture.

## Anti-patterns
- **Treating source code as the whole project**: ignoring docs/toolchain/culture/automation; building the *wrong* thing makes code quality irrelevant.
- **Hoarding knowledge / relying on memory**: undocumented, un-shared expertise walks out the door when the developer leaves.
- **Salvaging dead documentation**: rehabbing a neglected doc just lets it rot again — delete it.
- **Writing specs once and never updating them**: static spec docs drift; tests don't (CI enforces them).
- **Building one large monolithic blob**: large codebases resist refactoring and rewriting, raising the psychological and actual risk of an eventual Big Rewrite.
- **Manual repeatable tasks**: every un-automated button-click or memorized command is documentation debt and a mistake waiting to happen.

## Worked Example
**The Guardian Content API — disposability in practice.** The back end is built from small microservices: one service polls a legacy DB for changes, another consumes CMS/other systems via queues, both push content through a queue to a *writer* service whose only job is to read the queue and write to the datastore, and a *front-end* service serves client requests. The whole is complex, but each component is small, simple, and disposable. The author's team once wrote a new component in Clojure just because a developer wanted to try the language; months later a feature request made it easier to rewrite the whole thing in Scala (the team's stronger language). The rewrite was estimated at a day or two — so they did it with essentially zero risk. That ability to throw away and restart a part without endangering the system is the real payoff of disposable software.

## Key Takeaways
1. Don't focus only on source code — documentation, toolchain, infrastructure, automation, and team culture all determine whether a project stays healthy.
2. Information about software leaks away by default; you must actively guard against silos via docs *and* communication rituals (reviews, pairing, tech talks, hack days).
3. Keep docs concise and in the repo, review them like code, and delete the stale ones (Darwinian approach).
4. High-level automated tests double as a living spec and give the confidence to refactor; unit tests are for writing new code and are disposable once higher-level coverage exists.
5. Quality work is never done — schedule whole-codebase reviews and "fix one window" regularly, making repairs visible to spread collective ownership.
6. Automate everything you can: it saves your time, reduces mistakes, and transfers knowledge to your successor without loss.
7. Small is beautiful — build large systems from tiny, decoupled, replaceable components so the whole can live on (Ford Model T / ship of Theseus) even as parts die.

## Connects To
- **Ch1**: directly counters the legacy culture described there — knowledge silos, fear of change, and undocumented tribal knowledge; here the antidotes are review culture, in-repo docs, and tests that grant refactoring confidence.
- **Ch4–Ch9**: the practices reinforce earlier work — automated tests (test harnesses), CI/continuous inspection (Jenkins), automated provisioning (Ansible/Vagrant), the rewrite risk analysis (Ch6), and refactoring all reappear as preventive measures rather than rescue measures.
- **The Pragmatic Programmer (Hunt & Thomas)**: source of the broken-window theory applied to software entropy.
- **Chad Fowler / microservices movement**: disposable-software philosophy; the Ford Model T analogy from his Scala Days 2014 keynote.
- **Theseus' paradox (Plutarch)**: philosophical framing for a system that survives total component replacement.
