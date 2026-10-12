# Patterns & Techniques — Re-Engineering Legacy Software

## Measure Before You Touch (Continuous Inspection)
**When to use**: starting on any legacy codebase; deciding *where* to refactor.
**How**: stand up FindBugs → PMD → Checkstyle on a CI server (Jenkins via Maven goals `findbugs:findbugs pmd:pmd checkstyle:checkstyle`); publish trend graphs; trigger builds with a VCS webhook (not polling). Let data, not emotion, pick targets.
**Trade-offs**: setup cost up front; PMD/Checkstyle are noisy → must tune rulesets and set a low-warning baseline first.

## Churn-Based Target Selection
**When to use**: choosing the highest-value refactoring target.
**How**: `git log --since="90 days ago" --pretty=format:"" --name-only | grep "[^\s]" | sort | uniq -c | sort -nr | head -10`. The most-edited non-build file delivers the most value when improved.
**Trade-offs**: churn ≠ quality; combine with static-analysis hotspots and value/difficulty/risk triage.

## Exploratory Refactoring + Characterization Tests
**When to use**: fear of unfamiliar/"dangerous" code blocks you.
**How**: open in IDE, freely rename/move/comment to understand (VCS = undo, compiler/IDE = safety net); write characterization tests pinning *current* behavior before changing it.
**Trade-offs**: characterization tests lock in bugs-as-behavior; that's intended — change them deliberately later.

## Three-Axis Refactoring Triage (value / difficulty / risk)
**When to use**: prioritizing a backlog of candidate refactorings.
**How**: score each on value, difficulty (cost), risk (≈ number of dependents). Start with **low-hanging fruit** (low risk + low difficulty), then **pain points** (high value).
**Trade-offs**: estimates are rough; risk rises with dependents, so high-value changes are often high-risk.

## Separate Refactoring From Behavior Change
**When to use**: every time you refactor.
**How**: never mix a refactor with a bug fix/feature in one step or commit; put them in separate VCS commits. Beware "trivial" refactors (mark `final`, privatize a field) cascading across callers/subclasses.
**Trade-offs**: more commits, but reviewable and revertable.

## Break Dependencies via Introduce Indirection (Seam + DI)
**When to use**: untestable code coupled to static methods, God classes, or DB/email side effects.
**How**: (1) extract an interface for the dependency; (2) production impl delegates to the original; (3) add a *protected* constructor injecting the interface, keeping the public ctor signature unchanged; (4) mock in tests (Mockito `verify`). Commit + review the structural change *before* writing the test.
**Trade-offs**: adds an interface + impl class per dependency; the payoff is testability.

## Chain of Responsibility + Decorator (de-spaghetti business logic)
**When to use**: scattered-`if` business rules (e.g. authorization checks, ad selection) spread across the code.
**How**: make each rule a testable `Rule` subclass (`canApply`/`apply`) chained together; extract cross-cutting concerns (caching, logging) into Decorators wrapping a base implementation, wired by a factory.
**Trade-offs**: more classes; each rule and concern becomes independently testable.

## Test One Modularity Level Higher
**When to use**: refactorings that merge/split classes (which would destroy same-level unit tests).
**How**: System→system tests, Component→integration, Module→functional, Unit→unit. For legacy, start outside (Selenium/Capybara) and work inward.
**Trade-offs**: higher-level tests are slower and coarser, but survive structural change.

## Stale-Code Cleanup (warm-up refactoring)
**When to use**: building momentum / raising real coverage safely.
**How**: delete commented-out (VCS has history), dead (IDE/FindBugs detect), zombie (verify with data + DB constraint, then delete), and expired code (mark `// EXPIRES: yyyy-mm-dd`, fail CI when found).
**Trade-offs**: verify zombie/expired carefully before deleting.

## Modularize a Monolithic Codebase
**When to use**: fine-grained refactoring has plateaued but high-level structure is still a mess.
**How**: decide target modules up front (one per user-facing feature, validated by the one-sentence-purpose test); introduce interfaces; separate interface artifact from impl artifact (`*-iface.jar` vs `*-impl.jar`) so only the interface is on the compile classpath; wire with Guice DI; spin out easiest module first; quarantine un-untanglable utilities in a `Common` module.
**Trade-offs**: build/tooling complexity (Gradle, Ivy/Artifactory); enforces boundaries mechanically rather than by discipline.

## Incremental Strangler Migration (monolith → services)
**When to use**: any large monolith you're tempted to split; any rewrite you can run in parallel.
**How**: keep the monolith; extract 1–2 noncritical features as services first; build tooling/experience; re-evaluate (continue to SOA, stop, or settle on a few medium services). Each service owns its own datastore.
**Trade-offs**: every network hop adds failure modes (timeouts, partial data) + clients, retries, circuit breakers, discovery.

## Rewrite Decision Gate
**When to use**: tempted by a from-scratch rewrite.
**How**: a full rewrite is justified only when **both** hold — (1) refactoring tried and failed, AND (2) a paradigm/technology shift is required. Otherwise prefer, in order: replace (buy/OSS) → refactor → re-architect.
**Trade-offs**: rewrites run long, deliver little visible value, and silently reintroduce old bugs.

## Phased Rewrite With Parallel Running
**When to use**: a rewrite you can run alongside the legacy system.
**How**: pick rewrite type (black-box / brush-up / quid pro quo) + signed-off scope document up front; run old + new in parallel with two-way data sync; cut over incrementally and fail back on bugs. Use the old code as a low-level reference/tie-breaker, never as the architecture; mine VCS history to keep conditions that earned their place and drop the rest.
**Trade-offs**: sync tooling (real-time queue + batch + monitoring) and translation layers are significant work; avoid Big Bang cutover and simultaneous dual-write traffic splitting.

## Automate the Dev Environment (Vagrant + Ansible)
**When to use**: onboarding takes hours/days; "works on my machine."
**How**: README-as-onramp in repo root; `Vagrantfile` boots an isolated VM; Ansible playbook of **roles** provisions it declaratively (`state=present` for idempotency); pull shared resources (test DB) into the VM. `git clone` → `vagrant up` → working env.
**Trade-offs**: VM overhead; provisioning scripts *are* documentation and must be maintained.

## One Playbook Across All Environments
**When to use**: DEV/TEST/PROD have drifted; you want TEST to predict PROD.
**How**: replace hardcoded values with variables (`{{ app_user }}`); one inventory file per environment (`hosts-DEV/TEST/PROD.txt`); split roles across host groups; run `ansible-playbook -i <inventory> playbook.yml`. Hand the command to Jenkins (audit trail, parity); lock sudo/SSH to Jenkins. Share roles via an org-wide `ansible-scripts/common_roles/` repo.
**Trade-offs**: keep per-environment differences only in variables/inventory, never fork the playbook.

## Modernize Build + Automate Deploy
**When to use**: bespoke/old build tool; manual undocumented deploys; rare releases.
**How**: migrate to the org-standard build tool (Ant→Gradle) by adopting its directory conventions; minimum CI = test/build job + parameterized one-click TEST deploy; automate rolling PROD deploy with Fabric (detach from LB → stop → `git checkout <tag>` → start → poll healthcheck → reattach, one server at a time); wrap in a parameterized Jenkins job. Get developer buy-in before switching tools.
**Trade-offs**: releases are immutable (never re-release); deploy scripts are code and rot — run a weekly scheduled deploy to keep them alive.

## Prevent New Legacy (build quality in)
**When to use**: greenfield and ongoing — cheapest to prevent rot early.
**How**: disposable small/decoupled components; living specification (high-level tests CI enforces); Darwinian docs (in-repo, delete stale); communication rituals (code review, optional pairing, tech talks, hack days); periodic whole-codebase reviews; "fix one window" visibly.
**Trade-offs**: ongoing time investment; pays back by keeping the Big Rewrite off the table.
