# Chapter 2: Finding Your Starting Point

## Core Idea
Before refactoring legacy software, put a measurement infrastructure in place so data — not fear, frustration, or random urges — decides where you start and proves you're making progress. Use static analysis (FindBugs, PMD, Checkstyle) plus VCS history and a CI server (Jenkins) to continuously inspect quality.

## Frameworks Introduced
- **Exploratory refactoring**: Diving into unfamiliar code and freely renaming methods, moving methods, introducing interfaces, and adding comments — anything that makes code cleaner.
  - When to use: When fear of the unknown is blocking you from touching "dangerous" code you don't understand.
  - How: Open the project in your IDE; make cosmetic/structural cleanups; lean on VCS (revert anytime), the IDE refactor tools, and the compiler as safety nets. Do it with another developer or the whole team on a big screen to share knowledge. Goal is understanding (primary) and readability (secondary), NOT architectural change.

- **Characterization tests (Michael Feathers' term)**: Tests that document how the system *actually* behaves today, which may differ from the spec.
  - When to use: As a complement to exploratory refactoring, when you must preserve existing behavior of poorly-understood code (e.g. distinguishing `convertDate`, `convertDate2`, `convertDate_new`).
  - How: Write tests pinning current behavior so future changes are protected against unintended regressions.

- **The big three Java static analysis tools, applied in order**: FindBugs → PMD → Checkstyle.
  - When to use: As the starting point when preparing to refactor a legacy Java codebase.
  - How: (1) Fix critical bugs (e.g. NullPointerExceptions) with FindBugs; (2) fix design issues by refactoring with PMD; (3) fix formatting/readability with Checkstyle. No point in beautiful formatting over spaghetti design, or refactoring code that doesn't work.

- **Continuous inspection**: Offshoot of continuous integration (CI) where a build server runs static analysis on every commit and publishes results to a shared dashboard.
  - When to use: To overcome the two drawbacks of IDE-only inspection — results only visible to one developer, and reliance on developers remembering to run tools.
  - How: On each VCS check-in, trigger a build; build, run inspections/tests; notify the committing developer on failure; expose status + trend graphs on a dashboard for the whole team.

- **Gather data for two reasons**: (1) show software quality and how it changes over time (motivation, trend graphs); (2) decide the next refactoring target — either code quantitatively worse than the rest, or code whose refactoring gives the team the most value (frequently touched).

## Key Concepts
- **Static analysis**: Inspecting human- or machine-readable code and flagging pieces matching predefined bug/style patterns or rules.
- **False positive / false negative**: Flagging good code as a bug / failing to detect a real bug — both occur with these tools.
- **Cyclomatic complexity**: Count of distinct paths through a method — sum of `if`s, loops, `case`s, and `catch`es, plus 1 for the method itself; higher = harder to read/maintain.
- **Scariness ranking**: FindBugs rating (Of Concern → Scariest) of how bad a bug pattern would be if present; separate from its per-instance confidence rating.
- **Hotspot**: A small cluster of frequently-changed functionality where development concentrates while the rest of the app goes static — a prime refactoring target.
- **Leaning on the compiler**: Running the compiler after each refactoring step in a statically-typed language to get fast feedback on what your change affected.
- **Exclusion filter / file**: An XML file passed to FindBugs to suppress whole categories of warnings at package/project scope.
- **Baseline**: A starting state with as few warnings as possible (achieved via exclusions) so newly-introduced bugs stand out.
- **CI server / build server**: A server (Jenkins here) that auto-builds and inspects on commit; the terms are used interchangeably.

## Mental Models
- Think of fear of legacy code as **fear of the unknown** — the "dangerous" classes you avoid are exactly the ones that most deserve attention and refactoring.
- Use **trend graphs over absolute numbers**: a downward-sloping warning count, visible to the whole team, is a stronger motivator than a vague "must improve quality."
- Treat **frequently-edited files as refactoring targets**: improving a class on the critical path of many changes delivers far more value than fixing the class that merely irritated you.
- Think of **Jenkins as a communications hub and team member**, not just an automation tool — it codifies how to test/deploy and bridges developer/non-developer gaps.

## Anti-patterns
- **Edit-and-pray fixes / programming defensively around scary code**: Avoiding the worst code leaves the highest-value refactoring targets untouched.
- **Desperate "maverick" refactoring raids**: Randomly stabbing at your least-favorite class for catharsis gives an endorphin rush but no measurable, prioritized impact.
- **Marking software as doomed and giving up**: Loss of motivation helps nobody; pick metrics and watch them improve instead.
- **Running FindBugs on stale bytecode**: It analyzes compiled bytecode — if source and bytecode are out of sync results are confusing; always compile first.
- **Enabling all PMD/Checkstyle rules by default**: PMD is noisy out of the box (e.g. demanding `final` on every arg → thousands of warnings); tune the ruleset and avoid PMD/Checkstyle overlap (e.g. CyclomaticComplexity exists in both).
- **Reinventing the wheel with shell scripts**: For log/performance analysis, prefer existing open-source tools (Kibana/Elasticsearch/Fluentd, Sentry) over hacked-together scripts.
- **Jenkins polling the VCS**: Polling every 5 min wastes up to ~5 min before a commit is even noticed; use a VCS webhook to push changes instead.

## Code Examples
```bash
# Top 10 most frequently edited files in the last 90 days (Git) — find hotspots
git log --since="90 days ago" --pretty=format:"" --name-only | \
    grep "[^\s]" | \
    sort | uniq -c | \
    sort -nr | head -10
```
- **What it demonstrates**: Mining VCS history to pick a refactoring target by churn — the most-edited non-build file is the strongest candidate.

```xml
<!-- FindBugs exclusion filter (Listing 2.5): suppress mutable-exposure warnings for one package -->
<FindBugsFilter>
  <Match>
    <Bug pattern="EI_EXPOSE_REP,EI_EXPOSE_REP2" />
    <Package name="com.mycorp.timetrack.ui.beans" />
  </Match>
</FindBugsFilter>
```
- **What it demonstrates**: Killing whole categories of unavoidable false positives at package scope to set a clean baseline; check this file into VCS.

```java
// Suppress a single FindBugs false positive in place (Listing 2.3)
@SuppressFBWarnings(
        value = "UUF_UNUSED_FIELD",
        justification = "This field is accessed using reflection")
private String name;
```
- **What it demonstrates**: Annotation-level suppression with a `justification` so teammates know why. (Requires `com.google.code.findbugs:annotations` dependency. PMD instead reuses the standard `@SuppressWarnings("PMD")` / `@SuppressWarnings("PMD.RuleName")` or a `//NOPMD` line comment — no dependency needed.)

```
# Jenkins Maven goals to run all three tools (job step 3)
clean compile findbugs:findbugs pmd:pmd checkstyle:checkstyle
```
- **What it demonstrates**: Each tool has a Maven plugin, so Jenkins (which knows Maven) runs all three by adding three plugin blocks to pom.xml — no IDE needed.

## Reference Tables

| Tool | Analyzes | Primary purpose | Suppression |
|------|----------|-----------------|-------------|
| **FindBugs** | Compiled bytecode | Find potential/likely bugs (null derefs, thread-safety, correctness) missed in review | `@SuppressFBWarnings` annotation (needs JAR dep) or XML exclusion filter |
| **PMD** | Source code | Find technically-correct but bad-practice code needing refactoring (high coupling, high cyclomatic complexity, dup imports) | `@SuppressWarnings("PMD"...)` or `//NOPMD` comment |
| **Checkstyle** | Source code | Enforce coding standards/formatting; also some design & complexity metrics | XML file and/or annotations |

Apply order and effect (figure 2.5): FindBugs (fix Many→Few bugs) → PMD (Poor→Good design) → Checkstyle (Low→High readability).

| Metric category | What it tells you |
|---|---|
| Bugs & coding-standard violations | Overall state; pinpoints poor-quality hotspots |
| Performance | Whether refactoring improved speed (write perf tests; monitor prod via Kibana/Elasticsearch/Fluentd) |
| Error counts | Quality from end-user view (e.g. count HTTP 500s/day; use Sentry for stack traces) |
| Time to set up dev env | Onboarding friction (automate in ch7) |
| Time to release/deploy | Too many manual steps (automate in ch9) |
| Average time to fix a bug | Quality of team communication |
| Commonly used files (churn) | Best next refactoring target |

## Worked Example
**TimeTrack** — a legacy in-house Java time-tracking app whose sole author left no tests/docs. Components: Core (business logic + utilities), UI (Struts-based web front end), Batch (nightly inserts into Payroll DB), Audit (processes batch logs for tax-audit compliance reports). The maintainer knows UI but fears touching Core because the payroll batches depend on it.

Process the author models: (1) Use **exploratory refactoring** on Core to build understanding, backed by VCS/IDE/compiler safety nets; (2) write **characterization tests** to disambiguate the near-duplicate `convertDate*` utility methods; (3) run **churn analysis** — since managers keep requesting new report features while the hours-entry UI is static, the report-generation module is the data-justified hotspot to refactor first; (4) for the Audit pipeline (Parse logs → Calculate report → Render report), write a coarse perf test (start system → feed 1M dummy log lines → time processing → tear down), then refactor the coupled stages into three classes so each can be perf-tested in isolation.

Separately, on `cb372/externalized` (tag 0.3.0), the FindBugs IntelliJ plugin found exactly one bug — a `switch` missing a `default` case (Listing 2.1 adds it) — yet missed two identical cases in the same file, demonstrating that automated tools don't replace code review. On the larger Apache Camel `camel-core`, FindBugs found many bugs, grouped by category and scariness (Of Concern → Scariest). PMD on the tiny project that gave FindBugs one warning produced 260 violations — illustrating PMD's default noisiness and the need to tune rulesets.

## Key Takeaways
1. Don't refactor on emotion — stand up a measurement infrastructure first and let data choose targets and prove progress.
2. The scariest, least-understood code is usually the highest-value refactoring target; conquer it with exploratory refactoring + characterization tests.
3. For Java, run FindBugs → PMD → Checkstyle in that order: fix bugs, then design, then formatting.
4. Tune rulesets and set a low-warning baseline (annotations + exclusion files) so new defects stand out; suppress only with documented justification.
5. Pick refactoring targets by churn (`git log --name-only | sort | uniq -c | sort -nr`) — frequently edited files deliver the most value.
6. Automate inspection on every commit with a CI server (Jenkins via Maven goals), publish trend graphs, and trigger builds with VCS webhooks not polling.
7. Graduate to SonarQube for long-term quality dashboards while keeping Jenkins for fast per-commit feedback.

## Connects To
- **Ch 1**: Builds on the definition of legacy software and *why* to improve it; this chapter is the *where to start*.
- **Ch 4**: Refactoring techniques referenced for decoupling stages (e.g. splitting the Audit pipeline) before tests can be written.
- **Ch 7**: Automating dev-environment setup to cut onboarding time.
- **Ch 9**: Automating release/deployment to reduce manual steps and human error.
- **Working Effectively with Legacy Code (Feathers)**: Source of characterization tests; complements this chapter's "preserve existing behavior" stance.
- **Continuous Integration / Extreme Programming**: Continuous inspection is an offshoot of CI, a late-1990s XP practice.
