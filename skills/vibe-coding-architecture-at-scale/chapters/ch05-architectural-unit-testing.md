# Chapter 5: Architectural Unit Testing

## Core Idea
Express architecture as tests and static-analysis gates that run inside the AI's own write → run → read-failure → fix loop, so boundary, structure, nullability and correctness violations fail fast with a pasteable message instead of waiting for a human reviewer. Written once by a human with intent, enforced forever by a machine, corrected by the AI itself.

## Frameworks Introduced
- **The Architectural Test Loop (Define → Violate → Trigger → Correct)**: an architecture fitness function (Ford/Parsons/Kua) expressed as an ordinary unit test.
  - When to use: any package-to-package rule ("order must never import billing") that no single annotation can capture.
  - How: (1) Define the boundary once in ArchUnit or Spring Modulith; (2) the AI takes a local shortcut and imports a forbidden package; (3) `mvn test` fails instantly with a clean violation trace; (4) paste the trace into the prompt ("You violated the architecture rule, fix it") and the AI reroutes through an interface or event.
- **Three cheap mechanisms in series (structure for the vibe)**: package-private by default + feature packages + ArchUnit/Modulith.
  - When to use: every Java codebase you vibe-code in.
  - How: organize top-level packages by feature/domain (not `controllers/services/repositories`); make classes package-private unless they genuinely must cross packages; put the rule in Tier 1 context; let tests catch what slips through. Visibility prevents most violations for free, feature packaging makes the rest legible, tests catch the remainder.
- **The Static Analysis Feedback Loop**: tool reports structured violation → paste into AI → AI fixes → repeat, with each tool placed as far left as possible.
  - When to use: to stop the accumulation problem (god classes, copy-paste, null holes, convention drift) that passes boundary and behavioral tests.
  - How: Error Prone + NullAway in `compile`; PMD (GodClass), CPD, Checkstyle, SpotBugs in `verify`; ArchUnit + behavioral tests in `test`; PIT nightly. One Tier 1 instruction makes the AI run `mvn clean verify` and fix everything before declaring done.
- **Suppression Discipline**: never suppress without a same-line justification; only statement-level suppressions.
  - When to use: as soon as any analyzer is enabled, because the AI's path of least resistance is `@SuppressWarnings("all")`.
  - How: codify in Tier 1 context; forbid class/method-level suppressions; enforce via a custom PMD rule or Checkstyle `SuppressWarningsHolder` that flags `@SuppressWarnings` without a trailing comment. "If you cannot articulate in one sentence why the warning is wrong, the warning is right."
- **The Ratchet Pattern**: baseline existing violations, fail only on new ones.
  - When to use: adopting any analyzer on a legacy codebase that reports thousands of violations on day one.
  - How: generate a baseline at adoption (SpotBugs `spotbugs-exclude.xml`, PMD exclude list, Checkstyle `SuppressionFilter` + `checkstyle-suppressions.xml`, Error Prone `-XepDisable` during ramp-up / Refaster mass-patches, NullAway `AnnotatedPackages` allowlist); freeze it; when anyone (human or AI) touches a baselined file, fix the surrounding violations and remove those entries.
- **Behavioral Tests First**: invert the generation order.
  - When to use: every feature where correctness matters, because AI code is "beautifully deceptive" and cannot be verified by reading.
  - How: Prompt 1 asks for the integration test only ("Do not implement the feature yet"), confirm red; Prompt 2 asks for the implementation "until that test passes. Do not modify the test." `@AITestDriven` (Ch 4) is the standing-policy version.

## Key Concepts
- **Architecture fitness function**: any mechanism giving an objective integrity assessment of an architectural characteristic; the only form of a rule the generator cannot talk its way around.
- **ArchUnit**: Java library (TNG, 2017) asserting dependency, naming and layering rules over compiled classes as plain unit tests; ~400 ms for 10,000 classes.
- **Spring Modulith**: treats top-level packages as logical modules; `modules.verify()` fails on illegal inter-module dependencies and on reaching into sub-packages (internal by default). The JPMS replacement you actually want.
- **Asymmetry of review**: AI generates 400 lines in seconds; a human needs 10 minutes to check boundaries; architectural tests make verification faster than generation.
- **Accumulation problem**: the AI piles new logic into the biggest, most-connected class until it no longer fits in context.
- **GodClass (PMD)**: Riel's god class measured by high WMC (summed cyclomatic complexity), high ATFD (access to foreign data), low TCC (tight class cohesion).
- **Confident incompleteness**: AI handles the happy path fluently and skips edge cases; SpotBugs patterns (NP_NULL_ON_SOME_PATH, OBL_UNSATISFIED_OBLIGATION) catch it.
- **JSpecify `@NullMarked` / `@Nullable`**: package-level non-null default plus explicit nullable marks; read by the AI as a prompt and enforced by NullAway at compile time ("serves two masters").
- **Survived mutant (PIT)**: a bytecode mutation that changed behavior while every test stayed green, proving a hole in the safety net.
- **Copy-paste reflex**: the AI's default of copying a similar method and modifying the copy; caught by CPD.

## Mental Models
- Think of static analysis as your codebase's institutional memory in executable form: every rule is a past outage or review fight the AI does not know about.
- Use the compile-time tools (Error Prone, NullAway) as the highest-leverage gate because their failures arrive inside the AI's normal compile step: no extra command, no extra latency.
- Think of package-private as converting "the AI shouldn't couple these" from a rule you enforce into something the AI cannot easily express.
- A survived mutant is a fact about the net, not a formality; coverage says the line ran, mutation says whether anything would notice it was wrong.

## Anti-patterns
- **JPMS / build-config enforcement**: enforces at compile time in module-info and build files, the friction point that kills the vibe; teams abandon it.
- **Layer-first packaging (`controllers/`, `services/`, `repositories/`)**: scatters each feature across every layer so "stay in your lane" has no spatial meaning.
- **Public by default**: a public class is reachable from anywhere, so the AI reaches for it.
- **Importing entities into controllers**: the classic AI shortcut because the entity already has the field the view wants.
- **`@SuppressWarnings("all")`**: green build, zero signal, plus false confidence; worse than not running the tool.
- **Turning on `failOnViolation` against a legacy codebase without a baseline**: 8,000 violations on day one gets the tool disabled.
- **Letting the AI fix a failing test**: unconstrained, it weakens the assertion instead of fixing the code.
- **PIT in the inner loop**: reruns the suite per mutant, an order of magnitude more expensive than anything else.

## Code Examples
```java
class ArchitectureTest {
  private final JavaClasses classes =
      new ClassFileImporter().importPackages("com.yourapp");

  @Test void orderMustNotDependOnBilling() {
    classes().that().resideInAPackage("..order..")
      .should().onlyDependOnClassesThat()
      .resideInPackages("..order..", "..common..", "java..")
      .check(classes);
  }

  @Test void layeredArchitectureIsRespected() {
    layeredArchitecture().consideringAllDependencies()
      .layer("Web").definedBy("..web..", "..controller..")
      .layer("Service").definedBy("..service..")
      .layer("Persistence").definedBy("..repository..", "..entity..")
      .whereLayer("Web").mayNotBeAccessedByAnyLayer()
      .whereLayer("Persistence").mayOnlyBeAccessedByLayers("Service")
      .check(classes);
  }

  @Test void entitiesMustNotLeakIntoControllers() {
    noClasses().that().resideInAPackage("..controller..")
      .should().dependOnClassesThat().resideInAPackage("..entity..")
      .check(classes);
  }
}
```
- **What it demonstrates**: the starter ArchUnit set (feature boundary, layering, entity leak) that covers most AI boundary entropy.

```java
// Spring Modulith: boundaries without the module path
class ModularityTests {
  static final ApplicationModules modules =
      ApplicationModules.of(ECommerceApplication.class);
  @Test void verifiesModularStructure() { modules.verify(); }
}
```
- **What it demonstrates**: JPMS-style hidden internals delivered through the test loop.

Tier 1 instruction that closes the loop:
> "After implementing a feature, run `mvn clean verify`. Error Prone and NullAway run as part of `compile`; PMD, CPD, Checkstyle, and SpotBugs run as part of `verify`; ArchUnit and behavioral tests run as part of `test`. If any tool reports a violation, fix it in the same session before declaring the task complete. Never suppress a warning without a same-line comment justifying why the warning is wrong for this specific case."

## Reference Tables
**Static analysis feedback loop**

| Tool | When it runs | Scope | What it catches |
|---|---|---|---|
| Error Prone | `mvn compile` | Statement/method | Equality bugs, missing overrides, mutable constants, test fakery |
| JSpecify + NullAway | `mvn compile` | Method/return/param | Null contract violations |
| PMD GodClass | `mvn pmd:check` | Class | Accumulated responsibilities |
| CPD | `mvn pmd:cpd-check` | Cross-file | Copy-paste duplication |
| Checkstyle | `mvn checkstyle:check` | File/statement | Convention drift, unbraced ifs, empty catches, import noise |
| SpotBugs | `mvn spotbugs:check` | Method/bytecode | Flow-inferred NPEs, resource leaks, concurrency bugs |
| ArchUnit | `mvn test` | Package/layer | Illegal cross-boundary dependencies |
| Behavioral tests | `mvn test` | Feature | Incorrect observable behavior |
| PIT | nightly / changed classes | The test suite | Assertions that would not notice a bug |

**High-yield Error Prone checks for AI code**: MissingOverride, ReferenceEquality (`==` on strings passes via interning, fails on JSON input), CollectionIncompatibleType, EqualsHashCode, MissingFail (most common AI test-fakery: `try/catch` with no `fail()`), MutableConstantField, StreamResourceLeak (`Files.lines` without try-with-resources), FutureReturnValueIgnored.

**High-yield Checkstyle rules**: NeedBraces (Apple `goto fail` 2014), EmptyCatchBlock, FallThrough, UnusedImports/RedundantImport/AvoidStarImport, MagicNumber, naming + CustomImportOrder/DeclarationOrder.

**PMD thresholds used**: GodClass; CyclomaticComplexity `methodReportLevel=10`; CognitiveComplexity; TooManyMethods `maxmethods=20`. CPD `minimumTokens` 50–100 (sweet spot 50–80).

## Worked Example
**GodClass split via pasted violation.** `OrderService` keeps absorbing features because it already has the dependencies. PMD fails the build: `The class 'OrderService' is a God class. WMC=47, ATFD=18, TCC=0.11`. Prompt: "PMD reports OrderService as a GodClass (WMC=47, ATFD=18, TCC=0.11). Extract the shipping logic into a `ShippingService` and the pricing logic into a `PricingCalculator`. Keep the behavioral tests green." The AI now has a measurable mandate: split until PMD stops complaining. The same shape works for every tool: NullAway `dereference of possibly-null value returned from findById(orderId)` → "Add a null check before `order.confirm()`"; CPD "14 line (52 tokens) duplication" between `processOrder` and `processRefund` → "Extract the shared logic into a private helper or a strategy. Tests must remain green."

## Why It Works / Failure Mode
- **Architectural test loop**: works because the enforcement lands inside the loop the AI already runs, with messages structured exactly as its tool loop expects; no human has to notice in review and no config-file archaeology is needed. Breaks when rules live only in prose (ADRs, wikis) the AI can confidently contradict, or when enforcement is moved to build configuration where friction gets it disabled.
- **Ratchet**: works by creating the asymmetry "can only get better, never worse" with no upfront cleanup project; the baseline drains as files are touched, and it gives the agent an unambiguous answer to "is this allowed here?". Breaks if the baseline is regenerated instead of frozen, or if suppressions are allowed without justification, which silently restores zero signal. Defect cost grows ~10x per stage survived (compile → tests → review → staging → production); Ariane 5 Flight 501 (16-bit overflow, $370M) is the canonical case a modern analyzer flags in milliseconds.

## Key Takeaways
1. Make the architecture a test: a fitness function in `mvn test` is the only form of a rule the AI reliably respects.
2. Package-private by default plus feature packages is the highest-return, lowest-effort guardrail; it makes most violations inexpressible.
3. Push gates left: Error Prone and NullAway fail inside `javac`, then PMD/CPD/Checkstyle/SpotBugs in `verify`, then ArchUnit and behavioral tests.
4. Every tool's output is pasteable verbatim into the next prompt; the human reserves review for judgment calls.
5. Adopt on legacy via the ratchet; never allow suppression without a same-line justification.
6. Write the behavioral test first and forbid the AI to modify it; behavior is pinned while implementation stays volatile.
7. Use PIT (nightly or incremental) to verify the tests themselves are load-bearing.

## Connects To
- **Ch 1**: why JPMS backfires and which AI shortcuts (entity leak into web layer) these rules neutralize.
- **Ch 2 / 2b**: AI code is beautifully deceptive; "The Canon Doesn't Compile" introduced fitness functions.
- **Ch 3**: Tier 1 context carries package-private, suppression and `mvn clean verify` instructions (Context Diet).
- **Ch 4**: `@AILocked`, `@AIContract`, `@AITestDriven` are per-element intent; custom Error Prone checks push `@AILocked` one layer deeper.
- **Ch 5b**: places these checks in the test topology (PIT is outside the 30-second inner loop).
- **Ch 6**: guardrails enforce structure but don't show it; architecture visualization closes that gap.
- **Ch 7**: unifies Part II under Spec-Driven Development.
- **Ch 20b**: mutation testing and auditing tests that pass for the wrong reason.
- **Fitness functions (Ford/Parsons/Kua, *Building Evolutionary Architectures*; Richards/Ford)**, **Riel's god class heuristic**, **McCabe cyclomatic complexity**.
