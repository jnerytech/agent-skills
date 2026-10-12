# Chapter 5: Software Metrics and Code Analysis

## Core Idea
Software metrics don't fix brownfield pain points directly — they help you *locate* them. Use static and dynamic code analysis as "tracer bullets" to find the highest-coupling, most-complex, most-defective code so you know where to aim your refactoring effort in Part 2; track deltas over time, never worship the absolute numbers.

## Frameworks Introduced

- **The Three CC's (Coverage, Cyclomatic Complexity, Class Coupling)**: the baseline trio of metrics worth gathering before refactoring.
  - When to use: when first orienting yourself in an overwhelming, monolithic brownfield codebase and asking "where do I start?"
  - How: run a coverage tool against your test harness; run a static analyzer (VS Code Metrics or NDepend) for complexity and coupling; cross-reference with defect reports.
  - Why it works / failure mode: highlights actionable trouble spots. Failure mode: treating any single number as a verdict instead of reading it in context.

- **Metrics as Tracer Bullets**: gather metrics to get a *rough* fix on where problems live, then refine — not to score direct hits.
  - When to use: joining a large unfamiliar codebase; deciding where refactoring gives the most bang for the buck.
  - How: run NDepend (or similar), note clusters flagged as highly coupled / overly complex, combine with defect-tracking history, then re-measure each iteration and watch the *delta*.
  - Why it works / failure mode: directs effort toward quality/stability hotspots. Failure: chasing exact target values (e.g. "efferent coupling = 2") instead of trend direction.

- **Delta-driven monitoring (separate scheduled analysis, not per-check-in)**: run metric generation on a schedule (weekly/bi-weekly/monthly), not on every commit.
  - When to use: integrating metrics with CI without poisoning developer behavior.
  - How: keep metric NAnt/MSBuild targets alongside CI targets but trigger them on a schedule or manually; compare each run to the trend line.
  - Why it works / failure mode: avoids build overhead and "coding toward the number." Failure: wiring metrics into every-check-in builds, slowing the build and over-emphasizing stats.

## Key Concepts
- **Static code analysis**: metrics derived without executing the code (LOC, class coupling, cyclomatic complexity) — by parsing the source.
- **Dynamic code analysis**: metrics gathered while code runs (code coverage, memory leak detection).
- **Code coverage**: percentage of application code executed, most useful when the coverage tool monitors the *test harness* rather than the live app.
- **Cyclomatic complexity**: count of independent paths through code; each `if`, `for`, `switch`/`case`, and `and`/`or`/`not` adds one.
- **Class coupling**: how dependent classes are on one another; high coupling causes the "ripple effect" of cascading changes.
- **Afferent coupling (Ca)**: how many classes depend on me.
- **Efferent coupling (Ce)**: how many classes I depend upon.
- **Cohesion**: how closely a class's responsibilities relate; subjective, no single agreed formula.
- **Distance from main sequence (D)**: how far an assembly sits from the ideal balance where Abstractness + Instability = 1.
- **Depth of inheritance (DIT)**: how many base classes deep a class sits in its hierarchy.
- **Maintainability Index**: composite of Halstead Volume, cyclomatic complexity, and LOC; intuitive name but a "seductive," dated formula.

## Mental Models
- **Use metrics as tracer bullets when** orienting in unfamiliar code — refine your aim, don't expect direct hits.
- **Use the delta, not the absolute, when** the metric is subjective (distance from main sequence, cohesion, DIT) — care about movement over time, not the raw value.
- **Use coverage on the test harness when** you want an actionable map of untested code, not a live-app session.
- **Use static analysis to enforce architecture when** you have an inexperienced team (e.g. break the build if UI references the data layer) — but weigh the setup cost.

## Anti-patterns
- **Lines of Code as a quality metric**: a throwback to 1980s pay-by-the-line; more LOC ≠ worse (or better) code. Readability, maintainability, and correctness dominate. Useful at best for comparing similar projects.
- **Becoming a slave to statistics**: developers acting to protect a number regardless of project good (e.g. retrofitting pointless tests, or keeping dead code, just to hold 80% coverage).
- **Failing the build on a metric threshold**: don't make the build depend on coverage/coupling levels unless enforcing architecture — valid changes can legitimately drop a metric, and it keeps developers focused on numbers instead of code.
- **Trying to eliminate complexity/coupling/low-cohesion entirely**: many business rules are inherently complex; the goal is to *recognize* when a metric signals a problem, not drive it to zero.
- **Hard DIT rules**: "no class above DIT 5" is impractical — inheriting `System.Web.UI.UserControl` already gives you DIT 4.

## Code Examples

```csharp
// Listing 5.1 — cyclomatic complexity of 3 (one path per case + default)
void Process(Job job) {
    switch (job.status) {
        case JOB_STATUS.NEW:       ProcessNewJob(job); break;   // path 1
        case JOB_STATUS.CANCELLED: CancelJob(job);     break;   // path 2
        default:                   UpdateJob(job);     break;   // path 3
    }
}
```
- **What it demonstrates**: each `case` plus `default` is a distinct execution path; some tools report 4 (counting "fell through the switch entirely") — the exact number matters less than measuring consistently.

```xml
<!-- Sample NAnt target: NCover drives NUnit; two outputs (coverage + test results) -->
<target name="coverage" depends="compile test.compile">
  <exec program="${path.to.ncover.console.exe}">
    <arg value="//w &quot;${path.to.build.folder}&quot;" />
    <arg value="//x &quot;${path.to.output.file}&quot;" />
    <arg value="&quot;${path.to.nunit.console}&quot;" />
    <arg value="${name.of.test.assembly} /xml:${path.to.test.results.file}" />
  </exec>
</target>
```
- **What it demonstrates**: code coverage automation runs your tests *and* coverage in one task — NCover launches the NUnit console, so you get test results "for free."

```xml
<!-- NDepend metrics: detail lives in the project XML (metrics, output, CQL rules) -->
<target name="code-metrics" depends="compile">
  <exec program="${path.to.ndepend.console.exe}">
    <arg value="${path.to.ndepend.project.xml.file}" />
  </exec>
</target>
```
- **What it demonstrates**: automating any metric tool is "just executing an application"; NDepend's CQL query language can warn/fail when a metric (e.g. afferent coupling > 20) breaches a standard.

## Reference Tables

| Metric | Abbrev | Direction wanted | Notes / commitments authors make |
|---|---|---|---|
| Code coverage | — | Higher, but not 100% | 75% may be "adequate"; some chase 100% (impossible/inefficient in most cases). Example failing build set at 80%. |
| Cyclomatic complexity | CycCom | Lower / contextual | "7 isn't necessarily a problem" — but if peers hover at 3–4, that 7 warrants a look. |
| Afferent coupling | Ca | Higher = more stable | Many depend on you → you're less likely to change it. |
| Efferent coupling | Ce | Lower | Depending on many assemblies makes you unstable/fragile. |
| Instability | I = Ce / (Ce + Ca) | — | Range 0 (stable) → 1 (instable). |
| Abstractness | A | — | Range 0 (all concrete) → 1 (all abstract/interfaces). |
| Main sequence | A + I = 1 | balance | Ideal assembly. **Zone of Pain** = concrete + heavily depended-on; **Zone of Uselessness** = abstract + highly dependent. |
| Distance from main sequence | D | track delta | Watch movement toward Zone of Pain over time. |
| Depth of inheritance | DIT | Lower / flag only | DIT 7 → inspect; no hard cap (UserControl is already 4). |
| Maintainability Index | MI | — | = f(Halstead Volume, CycCom, LOC); data predates .NET by 5+ yrs — academic interest only. |
| Lines of code | LOC | — (anti-metric) | Not actionable; logical lines at best for comparing similar projects. |

Tools: **VS Code Metrics** (VS 2008, computes MI, CycCom, DIT, Class Coupling, LOC); **NDepend** (those plus dozens more, dependency matrix, CQL); **NCover** (de facto .NET coverage standard).

## Worked Example
The "Becoming a slave to statistics" scenario: the build fails below 80% coverage; the code sits at 81%. During a refactor you find a dead section that happens to be 100% covered. Deleting it drops overall coverage to 79% — failing the build. Three options: (1) roll back and keep dead code; (2) bolt on tests to claw back to 80%; (3) lower the coverage threshold. Options 1 and 2 are statistics-worship — the *intent* of the gate was to stop new untested code being checked in, and that hasn't happened. The correct move is option 3: lower the limit, ship the deletion (a genuine maintainability win), and preserve the metric's underlying purpose rather than its number.

## Key Takeaways
1. Metrics identify pain points; they don't fix them — they tell you *where* to point Part 2's refactoring techniques.
2. Numbers are meaningless without context; set consistent thresholds and read each metric relative to its peers.
3. Coverage is most valuable wired to the test harness, producing an actionable map of *un*tested code.
4. Prefer deltas over absolutes — especially for subjective metrics (distance from main sequence, cohesion, DIT).
5. Don't fail the build on a metric (except to enforce architecture); don't generate metrics on every check-in — schedule them so they don't slow the build or warp behavior.
6. LOC and Maintainability Index are low-value; treat LOC as an anti-pattern.
7. Eliminating complexity/coupling to zero is neither possible nor the goal — recognizing problem hotspots is.

## Connects To
- **Ch 3 (Continuous Integration)**: metric targets sit alongside CI compile/test targets but run on a schedule, not per check-in.
- **Ch 4 (Automated Testing)**: coverage only means something if tests give correct, positive confirmation; recommendation to test new/changed code only drives the coverage-threshold reasoning.
- **Ch 6 (Defects)**: combine metrics with defect-tracking history and trend analysis to focus effort.
- **Ch 9 (Dependency Injection)**: the concrete techniques — program to interfaces, inject dependencies — that reduce the class coupling this chapter measures.
