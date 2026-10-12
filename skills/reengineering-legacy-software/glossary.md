# Glossary — Re-Engineering Legacy Software

**Agentless** — Ansible needs no software pre-installed on targets; it runs remotely over SSH (Ch7).
**Ansible** — provisioning tool; installs/configures dependencies declared in YAML playbooks (Ch7, Ch8).
**Ansible Tower** — GUI dashboard for Ansible with access control and visibility (Ch8).
**Baseline (warnings)** — starting state with as few static-analysis warnings as possible (via exclusions) so new defects stand out (Ch2).
**Big Bang release/cutover** — all-or-nothing switch at project end; high risk, no early feedback, no fallback (Ch6).
**Black-box rewrite** — reimplement internals, keep functionality identical; ideal user notices nothing (Ch6).
**Bounded context** — each service owns its domain model; a translation layer converts between contexts (DDD, Ch5).
**Box (Vagrant)** — base image used as the foundation of a VM, e.g. `ubuntu/trusty64` (Ch7).
**Broken-window theory** — visible disrepair invites more; visible repair invites more (Ch10).
**Brush-up rewrite** — black-box rewrite plus the chance to document/normalize the spec and behave better (Ch6).
**Characterization test** — test that pins down how the system *actually* behaves today (Feathers' term) (Ch2, Ch4).
**Checkstyle** — Java static analysis enforcing coding standards/formatting; runs third (Ch2).
**Collective code ownership** — quality is everyone's responsibility, not one person's (Ch10).
**Configuration drift** — servers silently diverge over years of manual changes; you can't even tell how (Ch8).
**Connection draining** — after deregistering an instance from the LB, wait for in-flight requests to finish before stopping (Ch9).
**Continuous deployment** — auto-deploy to PROD on merge, no version numbers/release step (e.g. Guardian RiffRaff) (Ch9).
**Continuous inspection** — CI offshoot: build server runs static analysis on every commit to a shared dashboard (Ch2).
**Continuous integration (CI)** — server (Jenkins) that builds + tests on every push (Ch2, Ch9).
**Cutover** — the moment traffic is redirected from legacy to the new app; after it, write-replication reverses (Ch6).
**Cyclomatic complexity** — count of distinct paths through a method (ifs + loops + cases + catches + 1); higher = harder (Ch2).
**Darwinian documentation** — keep docs in-repo and concise; periodically delete any that went stale (Ch10).
**Dead code** — code that provably never executes (Ch4).
**Demarcating code** — team agreement on which areas are high-value and which high-risk, to aim effort (Ch3).
**Deployment** — installing a released artifact onto a machine and running it; distinct from release (Ch9).
**DevOps** — the team that builds the software also runs it in production (Ch8).
**Disposable software** — design so any component can be thrown away and rewritten in days, not months (Ch10).
**Environment parity** — TEST matches PROD (and machines match each other) so behavior is consistent (Ch8).
**Event Bus (Pub/Sub)** — emits DB-write notifications to the other app during parallel running; removable at shutdown (Ch6).
**Exclusion filter/file** — XML passed to FindBugs to suppress whole warning categories at package/project scope (Ch2).
**Expired code** — date-bounded logic (campaigns, A/B tests) that outlived its purpose (Ch4).
**Exploratory refactoring** — freely cleaning unfamiliar code (rename/move/comment) to build understanding, backed by VCS/IDE/compiler (Ch2).
**Fabric** — Python remote-execution-over-SSH tool used for rolling PROD deploys via a `fabfile` (Ch9).
**False positive / false negative** — flagging good code / missing a real bug; both occur with static analysis (Ch2).
**FindBugs** — Java static analysis on compiled bytecode; finds likely bugs (null derefs, threading); runs first (Ch2).
**Fix one window** — personal habit of repairing one hack every couple of weeks, visibly (Ch10).
**God class / "Util"** — huge grab-bag class of static methods referenced everywhere; refactoring red flag (Ch3, Ch4, Ch5).
**Greenfield doesn't stay green** — fresh rewrites re-accumulate complexity; "cruft" is often "complicated spec" (Ch3).
**Gradle** — modern Groovy-DSL build tool, strong multi-module support; migration target from Ant (Ch5, Ch9).
**Guice** — Google dependency-injection framework; callers depend on interface + DI module, impl at runtime (Ch5).
**Healthcheck endpoint** — trivial endpoint returning `OK`; "good to go" also verifies DB/caches/APIs (Ch9).
**Hotspot** — small cluster of frequently-changed code; prime refactoring target found by churn analysis (Ch2).
**Hotspot service** — service nearly everything depends on (e.g. auth); single point of failure/bottleneck (Ch5).
**Iconoclast** — developer who over-refactors others' code, risking regressions and resentment (Ch3).
**Idempotency** — a playbook/module runs any number of times with the same result (`state=present`) (Ch7, Ch8).
**Immutable infrastructure** — never provision a machine twice; to change config, replace the machine (Ch8).
**Incremental (iterative) rewrite** — many small releases; needs old + new running side by side; lower risk (Ch6).
**Inventory / host groups** — file listing target machines grouped by role (`[webserver]`, `[postgres]`) (Ch8).
**Leaning on the compiler** — recompile after each refactoring step (statically-typed langs) for fast feedback (Ch2).
**Legacification** — gradual rot of new code into legacy; prevented mainly by tests + small modules (Ch10).
**Legacy project** — any existing project difficult to maintain or extend (broad: code + infra + culture) (Ch1).
**Living specification** — suite of high-level tests that stays in sync with behavior because CI fails on drift (Ch10).
**Low-hanging fruit** — refactorings with low risk + low difficulty; the place to start (Ch3).
**Macbeth Syndrome** — undisciplined refactoring that cascades until reverting is as painful as continuing (Ch4).
**Microservice** — SOA with strong focus on decoupling, bounded contexts, and team autonomy (Ch5).
**Mikado Method** — build a dependency graph of sub-tasks for a large change, execute leaves-first, backtrack via VCS (Ch4).
**Modularization** — break one monolithic codebase into separate modules, each with an explicit interface/artifact (Ch5).
**Monolithic application** — runs entirely in one process on one machine (Ch5).
**Monolithic codebase** — all source in one folder, built as one binary (Ch5).
**One-sentence purpose test** — component-boundary heuristic: each component's purpose explainable to a user in one sentence (Ch5).
**Pain point** — high-value refactoring target; fixing it makes you a hero (Ch3).
**Parallel running** — old + new systems both live with two-way data sync, so traffic can fail back (Ch6).
**Periodic whole-codebase review** — scheduled group read of the whole code to catch architecture-level issues (Ch10).
**PMD** — Java static analysis on source; finds bad-practice/design issues; runs second; noisy by default (Ch2).
**Provisioning** — installing and configuring everything needed to run a piece of software (Ch7).
**Quid pro quo rewrite** — bundle major new features into a rewrite to win management approval (Ch6).
**Re-architecting** — refactoring "in the large," at the module/service level, preserving external behavior (Ch5).
**README-as-onramp** — concise in-repo Markdown giving a new dev exactly what's needed to start (Ch7).
**Regression** — a change unintentionally altering existing behavior; rewrite-specific risk of losing encoded rules (Ch3, Ch4).
**Release** — build + version-label + tag + publish an artifact; releases are immutable (Ch9).
**Role (Ansible)** — reusable unit grouping the tasks/templates for one dependency (Ch7, Ch8).
**Rolling deployment** — restart one server at a time behind a load balancer so users see no downtime (Ch9).
**Scariness ranking** — FindBugs rating (Of Concern → Scariest) of how bad a bug pattern would be (Ch2).
**Scope document** — short signed-off charter anchoring a project against feature creep (Ch6).
**Seam** — a place to alter behavior (inject a substitute) without editing in place (Feathers) (Ch4).
**Secret 20% Project** — do small (<1 dev-week) refactorings without approval, on <20% of your time, then share (Ch3).
**Service** — software isolated from the rest, communicating only via network messages (Ch5).
**SOA (service-oriented architecture)** — an application distributed across multiple services (Ch5).
**Sole-writer assumption** — an app assuming only it writes its DB; broken by parallel running (Ch6).
**SonarQube** — long-term code-quality dashboard, complements Jenkins per-commit feedback (Ch2).
**Stale code** — code still present but no longer needed; deleting it is the easiest/safest refactoring (Ch4).
**Static analysis** — inspecting code and flagging pieces matching predefined bug/style patterns (Ch2).
**Strangler pattern (Fowler)** — build the new system around the old, gradually assuming its responsibilities (Ch3, Ch5, Ch6).
**Technical debt** — accumulated quality shortcuts that levy "interest" (slower work) until repaid (Ward Cunningham) (Ch1, Ch3).
**Third Way (incremental rewrite)** — phase a rewrite so each phase delivers value and stopping early keeps the gains (Ch3).
**Toxic tests** — tests worse than none: no assertions, brittle, or randomly failing; give false confidence (Ch4).
**Traditionalist** — developer averse to all change; "if it ain't broke, don't fix it" (Ch3).
**Traffic replication** — copy incoming requests to both apps (return one response) instead of forwarding writes (Ch6).
**Translation layer** — code/DB views converting between new domain models and legacy DB models (Ch6).
**Trend graph** — visible downward-sloping warning count; a stronger motivator than absolute numbers (Ch2).
**Vagrant** — programmatically builds an isolated VM holding an app's full dependency stack (Ch7).
**View adapter (presentation model / ViewModel)** — testable object between model and view holding presentation logic (Ch4).
**Zombie code** — code that looks alive but never triggers because real data never reaches it (Ch4).
