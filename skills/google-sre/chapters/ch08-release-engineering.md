# Chapter 8: Release Engineering
*Authors: Dinah McNutt (ed. Betsy Beyer and Tim Harvey)*

## Core Idea
Reliable services require reliable release processes: binaries and configurations must be built in a reproducible, automated way so releases are repeatable and never "unique snowflakes," and changes to the release process are intentional, not accidental.

## Frameworks Introduced
- **The Four Release Engineering Principles (Philosophy)**:
  1. **Self-Service Model** — teams must be self-sufficient to work at scale; release engineering provides tools and best practices so product teams control and run their own release processes, deciding how often/when to release. Releases are "truly automatic" and need engineers only when problems arise.
  2. **High Velocity** — frequent releases mean fewer changes between versions → easier testing and troubleshooting. Options: hourly builds then select which to deploy (based on test results and features), or **"Push on Green"** (deploy every build that passes all tests).
  3. **Hermetic Builds** — same revision on different machines → identical results; builds insensitive to libraries installed on the build machine; depend on known versions of tools (compilers) and dependencies; no reliance on services external to the build environment. Build tools are themselves versioned with the project revision, so a cherry pick of last month's build uses last month's compiler.
  4. **Enforcement of Policies and Procedures** — layered security/access control gating: approving source changes (config files across the codebase), specifying release actions, creating a release, approving the initial **integration proposal** and subsequent cherry picks, deploying, changing build configuration. Almost all changes code-reviewed; automated report of all changes in a release, archived with build artifacts.
  - Why it works: hermeticity + gating make every release reconstructable and auditable, which shortens troubleshooting. Failure mode: non-hermetic builds make rebuilding an old release for a hotfix pull in incompatible tooling.

- **Branch and cherry-pick release model**:
  - When to use: major projects that shouldn't release directly from mainline.
  - How: (1) all code checked into mainline; (2) branch from mainline at a specific revision; (3) **never merge branch back** to mainline; (4) submit bug fixes to mainline, then cherry pick into the release branch; (5) individual cherry picks approved/rejected in Rapid. Result: exact known contents of each release, no accidental unrelated changes.

- **Testing alignment rules**:
  - Continuous test system runs unit tests on mainline at each submitted change.
  - Continuous build test targets should equal the targets that gate the release.
  - Cut releases at the revision of the **last continuous test build that passed all tests**.
  - Re-run unit tests on the release branch and keep an audit trail (cherry picks may create code that exists nowhere on mainline).
  - Plus an independent environment for system-level tests on packaged artifacts.

- **Typical Rapid release process**:
  1. Use the requested integration revision (often from the continuous test system) to create a release branch.
  2. Blaze compiles binaries and runs unit tests, often in parallel, in dedicated environments (not in the Rapid Borg job).
  3. Artifacts become available for system testing and canary deployments (a few jobs started in production after system tests).
  4. Log results of each step; create a report of all changes since the last release.

- **Configuration distribution models** (all stored in the primary repo with strict code review):
  1. **Use the mainline for configuration** — edit at head, review, apply. Decouples binary and config; simple, but causes **skew** between checked-in and running config (jobs must be updated to pick up changes).
  2. **Include config files and binaries in the same MPM package** — for few files or files changing every release; less flexible, simpler (install one package).
  3. **Package config into MPM "configuration packages"** — hermetic principle for config; snapshot and release alongside binaries; reconstruct by build ID; change config independently (cherry pick + rebuild config package, no new binary build); tie binary+config with a shared label.
  4. **Read config from an external store** — for frequently or dynamically changing config (Chubby, Bigtable, source-based filesystem).
  - How to choose: project owners decide case by case.

- **Fit the deployment to the risk profile**: dev/pre-prod → hourly builds, auto-push when tests pass; large user-facing services → start in one cluster, **expand exponentially** until all updated; sensitive infrastructure → roll out over several days, interleaved across geographic regions.

## Key Concepts
- **Release engineering**: building and delivering software; spans source control, compilers, build config languages, build tools, package managers, installers.
- **Release velocity**: time for a code change to be deployed to production; tracked by release-engineering tools.
- **Cherry picking**: rebuilding at the original revision plus specific later changes.
- **Integration proposal**: request to perform a build at a specific source revision.
- **Blaze** (open-sourced as **Bazel**): build tool for C++, Java, Python, Go, JavaScript; targets with dependencies built automatically; every binary has a flag showing build date, revision, build ID.
- **Midas Package Manager (MPM)**: packages named (e.g., `search/shakespeare/frontend`), versioned by unique hash, signed; supports **labels** (build ID; dev/canary/production) — reapplying a label moves it to the new package.
- **Rapid**: Google's automated release system; configured by **blueprints**; role-based ACLs; workflows (serial/parallel, can launch other workflows); runs as a Borg job, handles thousands of concurrent releases.
- **Sisyphus**: SRE's general-purpose rollout automation framework; extensible Python classes; dashboard; a **rollout** is a logical unit of one or more tasks; driven by Rapid using the MPM build label.
- **Canary deployment**: starting a few production jobs after system tests.

## Mental Models
- Think of **every release as a reproducible artifact** of (revision + hermetic toolchain + build ID): you can always reconstruct it.
- Use **small, frequent releases** when you want easier troubleshooting — fewer changes between versions.
- Think of **configuration as a release artifact**, not a side channel: version, review, label, and deploy it like binaries.
- Use **labels as moving pointers** (canary, production, `much_ado`) to deploy matched sets of packages.

## Anti-patterns
- **"Unique snowflake" releases**: unreproducible builds break debugging and hotfixes.
- **Builds depending on build-machine state or external services**: non-hermetic, non-repeatable.
- **Merging release branches back into mainline / releasing directly from mainline**: pulls in unrelated changes; unknown release contents.
- **Testing only on mainline**: cherry-picked release branches may contain code that exists nowhere else.
- **Mainline-only config without awareness of skew**: running config diverges from checked-in config.
- **Throwing results over the fence**: developers shouldn't build and hand off to release engineers; collaborate on intent.
- **Release engineering as an afterthought**: retrofitting is more expensive than budgeting it at project start.
- **Reinventing release tooling per team (poorly)**: use shared tools with correct defaults and docs.

## Code Examples
Config-package flag example (labels/flag values from the text):
```
binary package   : search/shakespeare/frontend   (label: much_ado)
config package   : flag = first_folio  ->  cherry pick change  ->  flag = bad_quarto
                   rebuild + deploy config package only (no new binary build)
```
What it demonstrates: separating binary and configuration MPM packages lets you fix a misconfigured feature flag with a config-only release, while a shared label (`much_ado`) fetches the matched set; the label moves to the newest packages on each build.

## Reference Tables
| Gated operation (access-controlled) |
|---|
| Approving source code changes |
| Specifying release-process actions |
| Creating a new release |
| Approving integration proposal and cherry picks |
| Deploying a new release |
| Changing a project's build configuration |

| Config model | Coupling | Best for | Drawback |
|---|---|---|---|
| Mainline config | Decoupled | Simple setups | Checked-in vs running skew |
| Same MPM package as binary | Tight | Few files / change every release | Limited flexibility |
| Separate config MPM package | Versioned, independent | Flags tied to binary versions | More packages to label |
| External store (Chubby/Bigtable/source FS) | Dynamic | Frequently/dynamically changing config | Outside hermetic release |

## Worked Example
**A Rapid + Sisyphus release.** The continuous test system reports the last revision that passed all tests; Rapid takes it as the integration revision and cuts a release branch. Blaze compiles binaries and runs unit tests in parallel in dedicated environments; tests re-run on the branch create an audit trail. MPM packages artifacts, versioned by hash, signed, and labeled with the build ID. System tests run in an independent environment, then a canary starts a few production jobs. Rapid logs every step and generates the change report. For deployment, Rapid creates a rollout in a long-running Sisyphus job, passing the build label so Sisyphus deploys exactly those MPM versions — e.g., for a large user-facing service, one cluster first, then exponential expansion. If a bug surfaces, the fix goes to mainline and is cherry picked (with approval) into the branch, rebuilt with the same versioned toolchain.

## Key Takeaways
1. Make builds hermetic and toolchains versioned with the source so any release can be rebuilt exactly.
2. Branch from a known-green revision, never merge back, and get fixes in only via approved cherry picks.
3. Re-run tests on the release branch; align continuous-test targets with release-gating targets.
4. Release frequently (or Push on Green) to keep change sets small.
5. Treat configuration as a reviewed, versioned release artifact; pick the distribution model per project.
6. Match rollout speed to risk: canary → exponential cluster expansion → multi-day regional interleaving for sensitive infra.
7. Budget for release engineering at the start of a project; define release policies even if you can't automate them yet.

## Connects To
- **Ch 7**: Rapid/Sisyphus as rollout automation; idempotent, gated changes.
- **Ch 9**: release simplicity — small batches, one change understood in isolation.
- **Ch 17**: testing for reliability; canaries and release gating.
- **Ch 2**: Borg, Chubby, Bigtable, monorepo.
- **Ch 3**: release velocity vs risk managed by error budgets.
- **Ch 27**: launch processes and gradual rollouts.
- **Bazel**: open-source Blaze.
- **Continuous delivery / trunk-based development**: Push on Green, mainline + release branches.
