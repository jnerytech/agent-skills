# Cheatsheet — Re-Engineering Legacy Software

## Master decision rule: how to revitalize legacy
Always prefer the lowest-risk option that achieves the goal:
- **Replace (buy/OSS)** — when an off-the-shelf product fits with little customization. "Best code is no code."
- **Refactor (Ch4)** — *default*. Codebase still tractable; small behavior-preserving steps under tests.
- **Re-architect (Ch5)** — structure is the problem but code is salvageable; module/service split.
- **Full rewrite (Ch6)** — ONLY when **refactoring tried-and-failed AND a paradigm shift is required** (both).

## Refactoring triage (value / difficulty / risk)
- **Start here**: low risk + low difficulty = *low-hanging fruit*.
- **Big win**: high value = *pain point* → fixing it makes you a hero.
- Risk ≈ number of dependents → high-value changes are often high-risk; gate with review + tests.

## Java static analysis — apply in order
| Order | Tool | Analyzes | Fix | Suppress |
|---|---|---|---|---|
| 1 | FindBugs | bytecode | bugs (null, threading) | `@SuppressFBWarnings(justification=...)` or XML exclusion filter |
| 2 | PMD | source | design / bad practice | `@SuppressWarnings("PMD...")` or `//NOPMD` |
| 3 | Checkstyle | source | formatting / standards | XML config |
Rule: no point beautifying formatting over spaghetti design, or refactoring broken code. Tune rulesets — PMD is noisy by default (260 violations on a 1-warning project). Compile first (FindBugs reads bytecode).

## Pick a refactoring target (data, not emotion)
```bash
git log --since="90 days ago" --pretty=format:"" --name-only \
  | grep "[^\s]" | sort | uniq -c | sort -nr | head -10
```
Most-edited non-build file = strongest candidate. Scariest/least-understood code is usually highest value.

## Refactoring discipline (tells you're doing it wrong)
- Refactor + feature in one commit → STOP, split them.
- Reverting feels as painful as continuing → *Macbeth Syndrome*; revert to last commit anyway.
- IDE refactor touched reflection-accessed code → it missed edits; `grep` to verify, run tests, recompile.
- Test has no assertion / fails randomly → *toxic test*; fix, disable, or delete.

## Get untestable code into a harness (seam + DI)
1. Naive test fails (static call hits DB/email). 2. Extract interface. 3. Prod impl delegates to original. 4. Inject via *protected* ctor (public ctor signature unchanged; test in same package). 5. Commit + review structural change. 6. Mock + `verify()` in test.

## Test level matches change scope
| Changing… | Test at level | Tool |
|---|---|---|
| Unit | unit | JUnit/Mockito |
| Module | functional | |
| Component | integration | |
| System | system | Selenium/Capybara |
Rule: test one level *higher* than the code you're changing (the refactor can wipe same-level tests). Legacy: start outside, work in.

## Architecture choice — trade-offs
| | Pick when | Main cost |
|---|---|---|
| Monolith | latency + simple dev matter; not ready for ops burden | whole-app scaling only; large-codebase complexity |
| FE + BE | want presentation/logic split, reuse BE | network-call complexity; team blocking |
| SOA | isolation between features is the pain | ops, latency, discovery, tracing, data fragmentation |
| Microservices | max autonomy via bounded contexts | implies DevOps + platform team; implicit coupling |
Decouple the codebase question (modules) from the deployment question (process vs services). Modularize first. Every network hop = new failure class. Each service owns its own DB.

## Rewrite type — decide & document up front
- **Black-box**: identical behavior, new internals.
- **Brush-up**: black-box + normalize/improve the spec.
- **Quid pro quo**: bundle new features to win management sign-off.
Write a **scope document** (mission, features must-have/nice-to-have, on-time-vs-complete, phases). Phase it so each phase ships value and stopping early keeps the gains.

## Rewrite migration safety
- Old + new in **parallel running** with **two-way sync**; cut over incrementally; **fail back** to legacy on any bug.
- Avoid: Big Bang cutover; simultaneous dual-write traffic split; burying migration logic in DB triggers/cron.
- DB strategy: shared = simple but needs watertight translation layer; separate = free schema/tech but needs real-time + batch + monitoring sync.
- Old code = low-level reference & tie-breaker, NOT the new architecture. Mine VCS history: keep conditions with a documented reason, drop the unexplained.

## Provisioning & environments
- DEV: 1 Vagrant VM, all host groups = `default`, `vagrant up`.
- TEST/PROD: separate machines per role, `ansible-playbook -i hosts-<ENV>.txt playbook.yml`, run by **Jenkins** (audit trail; lock sudo to Jenkins).
- Per-env differences live ONLY in variables (`{{ app_user }}`) + inventory files — never fork the playbook.
- Write declaratively (`state=present`) for idempotency; `register`+`when` for conditionals.
- Roll out least-critical-first (DEV→TEST→PROD); separate inventory files prevent run-against-everything disasters.

## Release vs Deployment
| | Release | Deployment |
|---|---|---|
| What | build + version + tag + publish | install + run a built artifact |
| Immutable? | YES — never re-release | n/a |
| Needs the other? | no | no (continuous deployment) |

## Rolling PROD deploy (per server, one at a time)
detach from LB → stop server → `git checkout <tag>` (tag, not branch) → start → poll healthcheck (give up after 10) → reattach → next server. Wrap `fab deploy_to_prod:tag=$tag` in a parameterized Jenkins job. Deploy scripts rot → schedule a weekly dummy deploy.

## Prevent new legacy (smells & habits)
- Trusting a doc over a committed script → devs distrust docs; ship a readable `deploy.sh`.
- One large monolithic blob → build from small *disposable* components (rewritable in days).
- Static spec doc → use a **living specification** (high-level tests CI enforces).
- Stale doc → delete it (Darwinian), don't salvage.
- Entropy creeping → "fix one window" every couple weeks, visibly. Knowledge silo → review + pairing + tech talks + hack days.
