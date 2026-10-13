# Chapter 6c: The Docs Are Load-Bearing Now

## Core Idea
Documentation stopped being output and became input: the agent reads it *before* the code, so a stale doc is a wrong instruction to the thing writing your code today. Structure the Markdown surface as one-file-one-job, one owner per topic, current vs. point-in-time separated, and maximize the fraction of every document a build can check.

## Frameworks Introduced
- **Two Inversions**: (1) writing cost collapsed — the agent holding the diff updates the doc in seconds; (2) more important, docs moved *upstream of the diff* — orientation file → routed docs → code → change.
  - When to use: explaining why "we'll document after the release" no longer holds; justifying doc investment.
  - How: treat every doc as an input to code generation, and inputs get verified. Payoff moved from diffuse and deferred to immediate and yours — every wrong doc is a defect with your name on the commit.
- **The Markdown Surface / One File, One Job**: a repo's docs are a set with different readers, lifetimes and update triggers; most damage comes from files doing two jobs.
  - When to use: laying out or auditing `docs/`.
  - How: README = outward face (90-second human evaluation, quick start that runs in a clean shell, link to INDEX). CLAUDE.md/AGENTS.md = Tier 1 orientation (10–20 lines: project in two lines, module layout, loop-closing commands, where guardrails live phrased as "run them", 5–10 house conventions, pointer to INDEX). `docs/INDEX.md` = router, one line per doc with category. `docs/architecture/` = one topic per file, present tense, rule first, history after. `docs/decisions/` = dated, immutable, superseded not edited. `analysis/` = point-in-time, dated. CHANGELOG = the only time-ordered doc, observable change only.
- **One Source of Truth Per Topic**: one document owns each topic; every other mention is a link. "Two documents describing the same rule are one document and one time bomb."
  - When to use: any rule/number stated in more than one place.
  - How: replace restatements with links (a link cannot drift from its target). Duplication is acceptable only where something checks it — a test asserting both statements agree.
- **The Auto-Loaded Set Has a Budget (three load tiers)**: Always loaded (root + module CLAUDE.md, harness injections; paid every session) → Routed (named by path in orientation file; paid when the task touches them) → Retrieved (via INDEX or search; paid only when looked for).
  - When to use: deciding whether content goes in CLAUDE.md.
  - How: importance argues for being findable; only universality argues for being resident. Apply Ch 3f's binding-power test: if you can't name a session where a line changed what the agent did, cut it. Link, don't inline. When edits to the orientation file stop having observable effect, cut and route — never restate louder.
- **Claims a Build Can Check**: prose has no red state; maximize checkable fraction by sorting claims into three levels.
  - When to use: designing doc CI; any doc an agent navigates by.
  - How: **Structural** (paths, filenames, module lists, links) — trivially checkable, costliest when stale since the agent navigates by them and invents when they're wrong. **Executable** (commands, snippets) — run them; README quick start in a clean container in CI; generate examples from compiled test classes pulled in between markers. **Numeric/behavioral** (attempt counts, timeouts, thresholds) — assert the doc against the artifact holding the value.
- **Generated Regions Need a Fence**: machine-written content sits between BEGIN/END GENERATED markers.
  - When to use: guardrail files (Ch 4), diagrams (Ch 6), API refs, generated changelogs, the second orientation filename.
  - How, four rules: generated file is committed; CI regenerates and fails on drift; header names the exact command; hand-written prose lives above BEGIN or below END, never inside.
- **The Update Trigger**: three events oblige a doc change — (1) behavior/structure changed → doc ships in the same commit; (2) a release → changelog entry in the PR that caused it; (3) **an agent got it wrong** → a documentation defect with a free reproduction; fix the wording in the same commit as the code.
  - How: end each session with "what did you have to work out that the documentation should have told you?" Filter answers into an existing doc (INDEX names it) or a deliberate new topic — never `notes-on-payments.md` at root. CI warns (not gates) when a behavior-changing PR touches no Markdown.

## Key Concepts
- **Payoff matrix of rot**: docs rotted because skipping was the rational local move (cost now, benefit to someone else later, no test fails) — not laziness.
- **Self-accelerating rot**: the only stale-doc detector is a reader; once unreliable, nobody reads it, so it decays silently.
- **Sprawl**: the new failure mode — near-free to write isn't near-free to read; six agent-written summaries of one subsystem are worse than none.
- **Upstream of the diff**: docs are read before code in an agent session, sharing the input role with source.
- **Point-in-time document**: an analysis correct about a moment and silent about now; needs a date in filename and header plus a pointer to current reference.
- **Partial agreement hides drift**: documents that agree on almost everything make one differing number read as detail, not contradiction.
- **Living documentation**: a document is living only while something keeps verifying it against current source (Martraire).
- **Fence**: BEGIN/END GENERATED markers separating machine-owned from hand-owned content.

## Mental Models
- Think of the Markdown surface as **the third telemetry channel and the only one written by hand** — which is why it alone can be wrong for a year unnoticed.
- Think of an undated analysis as **an un-stamped memory everyone on the team can read** (Lehman's first law: every observation is a photograph with a date).
- Use a stale README usage example as a warning sign: it is **a hallucinated API with a citation**.
- Prefer putting rationale in `docs/decisions/` because nothing can assert the "why" — keep it dated and immutable so it's never read as current policy.

## Anti-patterns
- **Exhortation ("document more")**: doesn't change the arithmetic; forty years without results.
- **Single 900-line architecture.md**: nobody can tell which section is stale; agent reads 900 lines for 40.
- **History before the rule**: buries the load-bearing sentence mid-context where attention is weakest (Ch 3).
- **Two hand-maintained orientation files (CLAUDE.md + AGENTS.md)**: pick one source, generate or symlink the other.
- **Analysis filed as reference**: confident present-tense conclusions with numbers outrank the code.
- **Promoting docs to always-loaded because they're "important"**: permanent tax on every session.
- **Follow-up ticket for docs**: "where documentation goes to die"; author never again has this context.
- **Hand-editing generated files / disabling the generator**: creates a fork with a plausible origin story (Ch 4b regeneration gap), or kills the guardrail.

## Code Examples
```java
@Test void everyDocumentAppearsInTheIndex() throws IOException {
  String index = Files.readString(DOCS.resolve("INDEX.md"));
  try (Stream<Path> found = Files.walk(DOCS)) {
    List<String> missing = found
        .filter(p -> p.toString().endsWith(".md"))
        .filter(p -> !p.endsWith("INDEX.md"))
        .map(p -> DOCS.relativize(p).toString().replace('\\', '/'))
        .filter(name -> !index.contains(name))
        .toList();
    assertThat(missing).as("documents not routed from docs/INDEX.md").isEmpty();
  }
}

@Test void documentedRetryPolicyMatchesConfiguration() throws IOException {
  RetryConfig configured = retryRegistry.retry("paymentGateway").getRetryConfig();
  String doc = Files.readString(Path.of("docs/architecture/resilience.md"));
  assertThat(doc).as("resilience.md must state the configured attempt count")
      .contains("maxAttempts: " + configured.getMaxAttempts());
}
```
- **What it demonstrates**: two of the four `DocsAreTrueTest` checks (index coverage = cheapest drift detector; numeric claim vs. live config). The others: every relative link resolves; CLAUDE.md lists every Maven module from `pom.xml`.

```markdown
# Payment Latency Investigation
> Point-in-time analysis. Written 2026-03-11 against commit `a3f19c2`.
> Describes behavior observed on that date. This is not current reference.
> Current retry and timeout policy: `docs/architecture/resilience.md`.
```
- **What it demonstrates**: the mandatory header for anything in `analysis/`.

```markdown
<!-- BEGIN GENERATED: mvn -q vibetags:generate; do not edit between markers -->
...machine-written content...
<!-- END GENERATED -->
```
- **What it demonstrates**: the fence, naming the regenerating command.

## Reference Tables
| Document | Primary reader | Question it answers | Rewritten when |
|---|---|---|---|
| README.md | Human evaluating the project | Should I use this, how do I run it? | Pitch or quick start changes |
| CLAUDE.md / AGENTS.md | Every agent session | Where am I, what may I not do, which commands close the loop? | Module layout, commands, or house rules change |
| docs/INDEX.md | Anyone looking | Which document answers my question? | A doc is added, renamed, retired |
| docs/architecture/*.md | Agent first, human second | How does this one topic work now? | That topic's behavior changes |
| docs/decisions/*.md | Anyone asking why | Why this choice, what was rejected? | Never — superseded by a new file |
| analysis/*.md | Whoever asked | What was true on this date? | Never — point in time |
| CHANGELOG.md | Consumers; you while bisecting | What changed, does it break me? | Every release |
| Generated blocks | Tools and agents | Whatever the generator knows | Every build, by the generator only |

## Worked Example
**Retry-policy drift across three docs.** Day 0: README ("retry 3 times, exponential"), root CLAUDE.md ("3 attempts, 200ms base") and `resilience.md` all agree. April: someone tunes base to 500ms, edits only `resilience.md` (the file they had open). June: an agent drops the payment gateway to 2 attempts and edits only CLAUDE.md (auto-loaded; resilience.md wasn't in context). Result: README = 3/exponential, CLAUDE.md = 2/200ms, resilience.md = 3/500ms — one code path, three confident committed policies, no authority marker (git timestamps mislead: a typo fix looks fresh). Final act: asked to "make retry policy consistent," the agent reads all three and picks one — drift becomes an instruction written into code. Fix: README and CLAUDE.md link to `resilience.md`; `documentedRetryPolicyMatchesConfiguration` would have failed on the April commit.

Second case — **stale analysis**: a March investigation proves `PaymentGatewayClient` opens a new connection per call; April adds a pool; September an agent greps "latency," finds the undated finding, and adds a second pooling layer. The present-tense doc with numbers outranked the code.

## Why It Works / Failure Mode
- **One source of truth** works because a link doesn't restate its target, so it can't diverge — same instinct as Ch 4 (rule next to the code) and Ch 3b (traversal over restatement). It fails when copies are tolerated "for convenience" without a test asserting agreement; partial agreement guarantees nobody notices.
- **Claims a build can check** works because tests don't rot — a stale test fails loudly on the commit that staled it; turning doc claims into fitness functions gives prose a red state. Limit: nothing checks rationale/"why" (Naur's design theory) — keep it in dated, immutable decisions.

## Key Takeaways
1. Documentation is no longer a gift to a future reader; it is an input to the next change you make — and the writer benefits most.
2. One file, one job; one topic, one owning document; everything else links.
3. Keep the auto-loaded orientation file on one screen; route and retrieve the rest.
4. Separate current reference (present tense) from point-in-time analysis (dated, headed, never linked as reference) and decisions (immutable).
5. Make structural, executable and numeric claims fail the build; state a number in prose only if it's asserted against its source.
6. Fence generated regions; commit, regenerate in CI, fail on drift.
7. An agent guessing wrong is a doc bug with a free repro — fix the doc in the same commit.

## Connects To
- **Ch 3 / 3c / 3f**: Tier 1 orientation budget, attention tax, context locality, binding-power test.
- **Ch 3b / 3e**: graveyard of notes files; age-stamping memory.
- **Ch 4 / 4b**: VibeTags generated guardrails, regeneration gap, partly-wrong files.
- **Ch 2b**: "if a principle cannot fail a build, it will eventually be violated."
- **Ch 5 / 5b**: arch tests run in the same loop; inner-loop budget (why `-Pit` split exists).
- **Ch 6 / 6b**: the two generated telemetry channels; "ship the missing log line" → ship the doc fix.
- **Ch 7**: the doc surface is the prose half of one spec; INDEX.md its table of contents.
- **Ch 18 / 20b**: changelog feeds contract discipline; green for the wrong reason.
- **Fitness functions (Ford/Parsons/Kua)**, **Living Documentation (Martraire)**, **Lehman's laws**, **Parnas & Clements "fake it"**, **Naur "Programming as Theory Building"**, **Humble & Farley** (bring the pain forward).
