# Chapter 2: Version Control in Brownfield Applications

## Core Idea
A version control system (VCS) is the heart of the construction process; in a brownfield app you must audit how you use it, remove friction, and make the code retrievable, buildable, and runnable "out of the box" before tackling anything else.

## Frameworks Introduced
- **The Check-In Dance**: a formalized ritual you perform every time you commit code so the VCS is (almost) always in a compilable state.
  - When to use: every check-in, on any project (brownfield, greenfield, or legacy).
  - How (File Locking VCS): 1) Check out file(s) to modify, 2) Make changes, 3) Ensure the app compiles and runs, 4) **Get the latest version of the application**, 5) **Ensure again it compiles and runs**, 6) Check in.
  - How (Version Merging VCS): same six steps, but step 4 becomes "Get the latest version *and merge your changes into it*."
  - Why it works: the two added steps (4 and 5) ensure (a) the repo is always stable, and (b) the developer who *causes* a conflict is the one who *fixes* it — never offloaded onto the next person who pulls.
  - Failure mode: skipping steps 4–5 lets you check in an unstable state; the next person to pull cannot compile and is stuck fixing your problem before starting their own work. A non-compiling repo is "the ultimate failure in your process."

- **Self-Contained Solution (out-of-the-box build)**: a new developer should need only three steps to be productive.
  - When to use: organizing/re-organizing any brownfield project for the VCS.
  - How: 1) Retrieve latest code from VCS, 2) Open the .sln in Visual Studio, 3) Compile and run. No readme hunt, no manual installs.
  - Why it works: copy referenced third-party binaries into the solution tree (the `lib` folder) and reference them with *relative* paths; everything needed to build lives in one place and you control when/if libraries upgrade.

## Key Concepts
- **Pain point**: any aspect of the project that causes you or your client problems; in brownfield apps they set your initial agenda.
- **Friction**: any process that impedes a developer's forward motion and keeps her from working on code — should be rethought, reworked, replaced, or eliminated.
- **Changeset**: the list of files plus meta-information forming a single commit/check-in; some VCS store history as changesets, others as reverse diffs.
- **Atomic transaction**: a group of files updated all-or-nothing on check-in, so the repo is never left in an unstable partial state.
- **File Locking (lock-edit-commit)**: model where an edited file is locked, preventing anyone else from modifying it.
- **Version Merging (edit-merge-commit)**: model where anyone can edit any file anytime; conflicts are resolved by a merge step at check-in.
- **Branching**: forking the code down two or more paths from a common codebase; provides change isolation.
- **Trunk**: the main codebase off which branches are taken and development continues as if branches don't exist.
- **Spike**: a time-boxed, throw-away exploration (often in an isolated branch) to learn enough to estimate or understand a task — meant to learn, not to create.
- **Labeling/tagging**: stamping the current state of the application so you can retrieve exactly that version later.

## Mental Models
- Use the **out-of-the-box test** (retrieve → open → compile/run on a *fresh, different* workstation) as the only trustworthy verification that you've eliminated reference/dependency friction.
- Think of the **lib vs. tool question** as: "Will it be deployed with the application?" Yes → it's a `lib`. No (build-only) → it's a `tool`.
- Use **"if it hurts when you bend your arm, don't bend your arm"**: if merging many days of changes is painful, check in smaller, more often instead.
- Think of **branching as a tool for change isolation, not something to fear** — but remember branches usually arise from unforeseen circumstances, not plans, and every branch you intend to merge back implies a future (sometimes painful) merge.

## Anti-patterns
- **Source control via emailed `sourcecode.zip`**: technically meets the bare criteria but imposes massive manual friction and can't handle two people editing concurrently.
- **Workarounds for locked files** (e.g. "just put your DB code in the UI project until Martin gets back from vacation"): breeds technical debt and architectural rot.
- **Maintaining production code on one developer's machine**: forces the same bug fix in two places and risks losing the deployed version entirely.
- **Adding projects to the VCS directly from Visual Studio**: can commit a partial set that won't compile for others — do the initial structure manually so all artifacts go in as one package.
- **Committing `bin`/`obj` and user-specific files** (`*.suo`, `*.csproj.user`, `*.vbproj.user`): they regenerate on build, churn constantly, and in a locking VCS can even block compilation.
- **Direct project references to internal shared libraries**: forces you to integrate on the other team's schedule; reference them as binaries instead.

## Reference Tables

### File Management Models
| Model | Aliases | Advantage | Downside |
|-------|---------|-----------|----------|
| File Locking | lock-edit-commit | Intuitive; conflicts rare | Developers fight over file resources; idle time or hacky workarounds |
| Version Merging | edit-merge-commit | No blocking; momentum preserved | Occasional manual merge (usually trivial, often auto-merged) |

Authors' personal preference: **Version Merging** (reduces friction). Consider starting with File Locking only if the codebase is highly coupled with large classes that would cause frequent merges, then ease toward merging as you break dependencies.

### Suggested Folder Structure (Table 2.1)
| Folder | Contents |
|--------|----------|
| Build | Artifacts for the automated build process (Ch 3). |
| Docs | Documents *directly* related to the code; other docs go in a CMS outside the repo. |
| Lib | All third-party libraries required to *run* the application. |
| Src | `app` = application source; `test` = test projects (Ch 4). |
| Tools | Third-party tools/utilities needed for the *build* but not deployed (test frameworks, build tools, coverage/metrics). |

### Lib vs. Tools (deciding question: "deployed with the app?")
| Tools (not deployed) | Lib (deployed) |
|----------------------|----------------|
| Build tools (NAnt); unit test frameworks (NUnit, MbUnit, xUnit); mocking (Rhino Mocks, TypeMock, Moq); coverage/metrics (NCover, NDepend) | UI components (DevExpress, Infragistics, Telerik); IoC containers (Castle Windsor, StructureMap, Spring.NET); logging (log4net); ORMs (NHibernate, LLBLGenPro); internal org libraries |

## Worked Example
**Tales From the Trenches — Dispensing with Friction**: A team of three followed the corporate-standard locking VCS. Within a week the lock model blocked their work — adding any new artifact in Visual Studio exclusively checked out the project file, so others couldn't add their own classes. Four days in, one or two developers were idle at any given time. Rather than accept the friction, the team spent a couple dozen hours migrating to and training on an Edit-Merge-Commit VCS. The upfront training/teething cost was far cheaper than continuing to block developers.

**Companion tale — The Fear of Merging**: When another team moved to Edit-Merge-Commit, developers were terrified of merge effort. Remedy: a ~4-hour training session walking through common scenarios. Combined with strong adherence to the Single Responsibility Principle (Ch 7) and a culture of checking in multiple times per day, true "manual merge" situations arose only a couple of times per month — and every early detractor became an advocate.

## Key Takeaways
1. Treat the VCS as the single source of truth: at any moment the latest code must at least compile.
2. Make the solution self-contained — copy third-party binaries into `lib`, reference them relatively, so the build works out of the box and you control upgrade timing.
3. Prefer Version Merging over File Locking to keep developers from blocking each other; mitigate merges with SRP and frequent check-ins.
4. Build the VCS folder structure manually (don't auto-add from the IDE), mirror your physical structure, and add `branches`/`trunk` (and `tags` for SVN/CVS) when branching is supported.
5. Exclude `bin`, `obj`, and user-specific settings — but watch global ignore patterns, since some libs (e.g. log4net) ship a `bin` folder you must explicitly include.
6. Perform the Check-In Dance every time, and verify the out-of-the-box build on a *different* workstation.
7. Check in often (small useful chunks, not "feature complete"); branch a feature only when you truly can't, accepting a painful future merge. Decide a labeling strategy — at minimum, label every deployment.

## Connects To
- **Ch 1**: Builds on the defined notions of brownfield apps, pain points, and friction.
- **Ch 3**: Continuous Integration ties the VCS into an automated build; the Check-In Dance is updated again for CI, and labeling is revisited.
- **Ch 4**: Unit tests refine what it means for the app to "work" and strengthen the case for checking in often.
- **Ch 6**: Comparing file versions becomes invaluable when tracing how code deteriorated, while working on defects.
- **Ch 7**: The Single Responsibility Principle reduces coupling and makes merge conflicts rare.
