# Chapter 3f: The Rule That Never Fired: Evals for the Instruction Layer

## Core Idea
The instruction layer (CLAUDE.md, .cursor/rules, AGENTS.md) is the one artifact in a guardrailed repo that cannot go red, so it decays unmeasured. Treat every standing instruction as a probabilistic bias, measure its adherence rate with an eval harness (task bank + headless agent runs + deterministic detectors), then rewrite, promote, or delete each rule based on evidence.

## Frameworks Introduced
- **Instruction Evals (adherence as a quantity)**: a fixed task bank run against the agent N times per cell, scored by deterministic detectors; the eval is a fitness function whose system under test is your prose, not your code.
  - When to use: any repo where principles live as prose in instruction files, especially after a model/harness upgrade or when "how did this merge without X?" keeps recurring.
  - How: (1) pick the rules that matter; (2) build small, ticket-sized tasks pinned to a fixture git tag; (3) write one boring yes/no detector per rule (ArchUnit, field-type scan, AST visitor, file-pairing check); (4) run each task 10 times in a disposable worktree under three rule variants; (5) assert rate >= floor in a parameterized JUnit test; (6) read the adherence matrix and act.
- **The three adherence measurements**: for each rule compare its rate across variants.
  - When to use: diagnosing *why* a rule underperforms, not just *that* it does.
  - How:
    - **Binding power** = adherence with rule minus adherence with rule deleted (BASELINE). 96 vs 94 = 2 points (lucky charm); 30 vs 90 = 60 points (load-bearing).
    - **Persistence** = short-task rate vs long-session rate. A rule that holds for 3 turns but drops after 40 is buried by Lost-in-the-Middle; fix by moving it closer to the code (Tier 2 directory rule or Tier 3 annotation).
    - **Interference** = RULE_ALONE rate vs FULL_FILE rate. 90 alone, 65 in company means neighbors dilute or contradict it.
- **The Promotion Path (Rewrite → Promote → Delete)**: three moves for a failing row, taken in order of increasing cost.
  - When to use: after every matrix run, per row.
  - How: **Rewrite** first on two axes: *formulation* (name trigger, required artifact, location so the model can self-check: "Every new @RestController class requires a *IT class using Testcontainers in the same package") and *placement* (smallest scope covering everything the rule governs: Tier 1 global, Tier 2 directory, Tier 3 annotation). Rerun. **Promote** if still under floor after honest rewriting: the sentence wants to be code, so make it a PreToolUse hook (Ch 3d), an ArchUnit test (Ch 5), or a merge gate (Ch 21). **Delete** when binding power is near zero: refunds tokens and attention to every remaining rule.
- **Four decay forces (Dilution, Drift, Contradiction, Redundancy)**: why a sentence that once worked stops working without anyone editing it.
  - When to use: interpreting a rate that moved.
  - How: dilution = file grew, attention per rule fell; drift = model/harness changed, same sentence, different reader; contradiction = two rules collide and the winner varies per run (shows as a rate stuck ~60% no rewording fixes); redundancy = the model does it anyway (only revealed by deleting the rule and re-measuring).

## Key Concepts
- **A hook executes, an instruction persuades**: a hook is a branch (same input, same block); an instruction only shifts odds by an unprinted amount.
- **Adherence rate**: fraction of N trials in which the agent's output satisfied the rule's detector.
- **Binding power**: with-rule adherence minus baseline (rule deleted) adherence; the number nobody has.
- **Task bank**: frozen, ticket-sized units of work: fixture repo ref + prompt + rule variant + detector + floor.
- **Detector**: plain deterministic code returning yes/no over the produced tree; "boring on purpose."
- **Adherence matrix**: one row per rule, columns for baseline / full file / binding power / verdict.
- **Rule variants**: FULL_FILE, RULE_ALONE, BASELINE (rule deleted).
- **LLM-as-judge**: a second model scores output against a rubric (Zheng et al., NeurIPS 2023); known biases: position, verbosity, self-preference.
- **Judge-only rule smell**: a rule only a model can check is usually a rule written for a human; sharpen it until a detector can check it.

## Mental Models
- Think of the instruction file as **odds, not law**; its decay is then a rate that moved, which only an eval can see.
- Use the eval to divide labor: **hook or gate what must always hold, eval what should usually hold**, and stop asking prose to do a hook's job.
- Think of a rule at 40% as **worse than no rule**: it costs tokens and attention and buys false safety that prevents anyone wiring the real gate.
- Prose you do not measure is **vibes with a commit history**.

## Anti-patterns
- **Repeating, bolding, or re-stating a weak rule**: adds dilution, the disease it tries to cure. Sharpen and re-tier instead.
- **Crediting a rule because you watched the agent comply**: redundancy is invisible from inside a session; only the baseline column reveals it.
- **Two-decimal dashboards on 10 trials**: N=10 separates 90% from 50%, not 95% from 90%. Gating on 0.9 vs 0.85 buys noise and argued-about reverts.
- **Running the full matrix on every commit**: 10 tasks x 3 variants x 10 trials = 300 headless runs, minutes and tens of thousands of tokens each.
- **Running evals on a cheaper model**: measures a different system; Ch 23b routing does not apply. "An eval on the wrong model is not a discount. It is a different experiment."
- **Letting judged scores gate merges**: judge scoring drifts on judge-model upgrades; judged rows report only.
- **A rule written for a reviewer, not a generator** ("Endpoints should be well tested"): humans fill gaps with judgment, generators fill them with defaults.

## Code Examples
```java
public record EvalTask(
    String id,          // "add-refund-endpoint"
    String fixtureRef,  // git tag of the fixture repo state
    String prompt,      // "Add a POST /refunds endpoint that..."
    RuleSet rules,      // FULL_FILE, RULE_ALONE, or BASELINE (rule deleted)
    Detector detector,  // deterministic pass/fail over the produced tree
    double floor        // minimum adherence rate to stay green
) {}

AdherenceReport run(EvalTask task, int trials) throws Exception {
  int passed = 0;
  for (int i = 0; i < trials; i++) {
    Path wt = worktrees.checkout(task.fixtureRef());   // git worktree add
    rules.install(wt, task.rules());                   // write the CLAUDE.md variant
    exec(wt, "claude", "-p", task.prompt(),
         "--permission-mode", "acceptEdits", "--output-format", "json");
    if (task.detector().holds(wt)) passed++;
    worktrees.discard(wt);
  }
  return new AdherenceReport(task, passed, trials);
}
```
- **What it demonstrates**: the whole harness is a task record plus a loop of isolated headless runs (Ch 21b worktree hygiene) scored by a deterministic detector.

```java
Detector constructorInjection = wt -> {
  JavaClasses generated = new ClassFileImporter().importPath(wt.resolve("target/classes"));
  return noFields().should().beAnnotatedWith(
      "org.springframework.beans.factory.annotation.Autowired")
    .evaluate(generated).getFailureReport().isEmpty();
};

@ParameterizedTest @MethodSource("bank")
void ruleBinds(EvalTask task) throws Exception {
  AdherenceReport r = harness.run(task, 10);
  assertThat(r.rate())
    .as("%s under %s: %d/%d trials adhered", task.id(), task.rules(), r.passed(), r.trials())
    .isGreaterThanOrEqualTo(task.floor());
}
```
- **What it demonstrates**: detectors reuse the ArchUnit library already guarding the architecture; the assertion (rate >= floor over a fixed sample) is deterministic, so it does not violate Ch 5b's zero-flakiness law.

```yaml
on:
  pull_request:
    paths: ["CLAUDE.md", ".claude/**", ".cursor/rules/**"]
jobs:
  instruction-evals:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: mvn -pl evals test -Devals.scope=diff -Devals.trials=10
```
- **What it demonstrates**: the missing merge gate: an edit to steering prose can finally go red before it steers anything, scoped to rules whose text changed.

## Reference Tables
**Payments team's first adherence matrix (10 trials/cell)**

| Rule | Baseline | Full file | Binding power | Verdict |
|---|---|---|---|---|
| Constructor injection | 0.9 | 1.0 | +0.1 | Redundant: model does it anyway |
| Money uses BigDecimal | 0.4 | 0.9 | +0.5 | Load-bearing: keep, protect |
| Endpoint ships a Testcontainers IT | 0.1 | 0.4 | +0.3 | Failing: promote |
| Never swallow InterruptedException | 0.6 | 0.7 | +0.1 | Weak: rewrite or promote |

**Detector per rule type**

| Rule | Detector |
|---|---|
| Constructor injection | ArchUnit: no @Autowired fields |
| Money uses BigDecimal | Field-type scan over touched entities |
| Endpoint ships IT | Pairing check: each new @RestController has a compiling *IT class |
| Never swallow InterruptedException | AST visitor flagging empty catch |

**Eval triggers (when to pay)**

| Trigger | Scope |
|---|---|
| PR touching CLAUDE.md, .claude/**, .cursor/rules/** | Slice for rules whose text changed |
| Model or harness version bump | Full matrix (drift arrives here, never in a diff) |
| Weekly schedule | Full run; builds the trend line for slow decay |

**Tool summary**: Java harness ~200 lines (JUnit 5 parameterized + git worktree + `claude -p` + ArchUnit/AST detectors). Off-the-shelf: promptfoo, DeepEval, Braintrust, LangSmith (Node/Python; can shell out to Java detectors). Judged rules via the Ch 22 Inquisitor, report-only.

## Worked Example
A payments team's CLAUDE.md says "Every new REST endpoint ships with a Testcontainers integration test." It is cited in reviews and everyone believes it works. Someone counts: 8 of the last 20 agent-authored endpoints have the test (40%). The eval confirms it: baseline 0.1, full file 0.4. Meanwhile the most-cited rule, constructor injection, turns out redundant (0.9 without it), and the unglamorous BigDecimal rule is the quiet hero (+0.5). Actions: rewrite the IT rule with an exact trigger/artifact/location and move it to the payments module's Tier 2 file; if it still sits under the 0.8 floor, promote it to an ArchUnit pairing test or PreToolUse hook that fails when a controller arrives without its IT; delete the constructor-injection sentence to refund tokens and attention. The year of "how did this endpoint merge without a test" stops being blamed on individual sessions.

For judge-only rules: "explain the trade-off considered" resists detection; rewrite as "the PR description contains a section titled Trade-offs with at least one rejected alternative," which a detector can check.

## Why It Works / Failure Mode
- **Why**: converting folk belief into a measured rate per rule localizes the problem (dilution vs placement vs redundancy) before anyone reads a word, and hands you the division of labor between prose and hooks. Deleting redundant rules raises adherence of the rest because attention is zero-sum.
- **Failure mode (the honest limit)**: the bank measures the bank. Goodhart's law (Strathern's phrasing) and Beizer's pesticide paradox mean tasks and rules tuned to each other drift from real work; refresh the bank from real tickets and incidents on a schedule (as Ch 20b does for test suites). Statistics stay coarse; interference across all rule pairs is quadratic, so sample pairs. Cost grows with ambition.

## Key Takeaways
1. If a principle cannot fail a build, the agent will eventually violate it; that law applies to the instruction file itself.
2. Measure every rule as a rate; binding power (with minus without) tells you which sentences actually work.
3. Fix failing rules in order: rewrite (formulation, then tier placement), promote to hook/test/gate, or delete.
4. Use coarse floors (0.8) and 10 trials; never trust decimals on small samples.
5. Gate PRs that touch the instruction layer; run the full matrix on model bumps and weekly; always on the production model.
6. LLM-as-judge rows report, never gate; treat a judge-only rule as a formulation smell first.

## Connects To
- **Ch 2b**: the governing law ("if a principle cannot fail a build...") applied to the instruction layer.
- **Ch 3 / 3c**: context diet, attention tax, Lost in the Middle, Tier 1/2/3 placement, token cost of every rule.
- **Ch 3d**: hooks are the promotion target; advise vs enforce distinction.
- **Ch 3e**: same promotion-by-demonstrated-behavior path used for memory.
- **Ch 4 / 4b**: Tier 3 annotations as placement fix; 4b is the same "enforces nothing" audit one layer down.
- **Ch 5 / 5b**: ArchUnit detectors; deterministic rate assertion is not flakiness.
- **Ch 21 / 21b / 22 / 23b**: merge gates, worktree isolation, Inquisitor as judge, why model routing does not apply to evals.
- **Fitness functions (Ford/Parsons/Kua)**: an eval is a fitness function over prose.
- **LLM-as-judge (Zheng et al. 2023)**, **Goodhart's law**, **Beizer's pesticide paradox**.
