# Chapter 5b: The Test Topology: Designing for Machine-Speed Feedback

## Core Idea
In an AI-assisted loop the test suite runs 100–300 times a day, so it is no longer a checkpoint but the agent's inner loop and runtime environment. Design the suite for the machine that runs it, not for the human who occasionally watches it: hard time budgets, isolation then parallelism, zero flakiness, and coverage as a compass.

## Frameworks Introduced
- **The Feedback Budget (two tiers, two budgets)**: treat test time as an engineering constraint like a memory limit or latency SLA.
  - When to use: before writing tests; whenever the suite slows down.
  - How: **Inner loop < 30 seconds, unconditionally** — unit tests, fast component tests with in-memory infrastructure, ArchUnit rules; run on every AI cycle. **Full suite < 5 minutes** — integration, DB, contract, external-infrastructure tests; run in CI on every push and before the AI declares a feature done. Beyond 5 minutes people and agents skip the full run. Violating both ceilings is a design problem, not a discipline problem.
- **Two-speed test execution via a tag contract**: make the inner/full split explicit and mechanical.
  - When to use: as soon as you have both unit and integration tests.
  - How: tag with JUnit 5 `@Tag("fast")` / `@Tag("integration")`; run with `mvn test -Dgroups=fast` or `-Dgroups=integration`; add an ArchUnit rule that fails the build if any `@SpringBootTest` lacks `@Tag("integration")`. Informal "the unit tests are the fast ones" drifts.
- **Isolate first, then parallelize**: you cannot parallelize what you cannot isolate.
  - When to use: before turning on JUnit parallel execution.
  - How: remove the three parallelism killers — shared DB state (each test owns data, transaction rollback, or schema-per-test; never test ordering), shared static state (reset in teardown; treat static mutation as a design smell in production code), shared port bindings (random dynamic ports for embedded servers, TestContainers, WireMock). Then enable parallelism with three properties.
- **Advanced DB isolation: Pattern A (Namespacing) vs Pattern B (Dynamic Schema-per-Test)**.
  - When to use: when rollback isolation breaks on global queries (`findAll().size()`) or unique constraints under concurrency.
  - How: A — each test class generates a short UUID token, suffixes emails/SKUs/keys with it, and queries only by namespaced fields (never `findAll`). B — when global lookups or native SQL make namespacing impractical, a JUnit 5 extension creates `test_schema_<uuid>` in `beforeAll`, sets `search_path` and Hibernate/Flyway schema properties, and `DROP SCHEMA ... CASCADE` in `afterAll`. B is the "gold standard" for DB-heavy parallel suites.
- **Coverage as a Compass, Not a Contract**: calibrate, don't enforce.
  - When to use: setting coverage policy, directing the AI to add tests.
  - How: (1) baseline current coverage; (2) pick lowest-coverage modules by domain risk, not line count; (3) task the AI with a target of 65% meaningful coverage and an explicit ban on number-moving tests; (4) review new tests for assertions and behavioral specificity; (5) re-check: 65–70% means the AI did the job, >75% means examine for vacuous tests. Add **patch coverage** per PR as an informational comment.

## Key Concepts
- **Compounding math**: a 3-minute suite at 25 manual runs = 75 min/day; at 100 AI iterations = 300 min (5 hours) of blocked feedback per engineer per day.
- **Inner loop**: the fast, deterministic, "complete" subset the AI runs every cycle — complete meaning it catches the mistakes the AI makes in a single iteration.
- **Test slices**: `@WebMvcTest` (~2 s), `@DataJpaTest` (~3 s), `@JsonTest` (<1 s) instead of `@SpringBootTest` (≥30 s full context).
- **TestContainers reuse**: one container per JVM (`.withReuse(true)`) shared by all subclasses of a base test class.
- **Schema caching**: run Flyway migrations once per JVM against the reused container; cuts CI suite time 15–30%.
- **Flaky test (AI era)**: a random signal the AI misdiagnoses, "fixing" production code to eliminate a phantom failure and learning the wrong lesson.
- **Re-run analysis**: CI reruns failing tests (`surefire.rerunFailingTestsCount=3`); fail-then-pass = flagged flaky even if the suite is green.
- **Meaningful coverage**: covered lines whose tests have assertions, fail when the code is deleted (mutation), and encode a business behavior.
- **Patch coverage**: percentage of lines changed in this PR that tests exercise; catches the generator where project averages can't.
- **Test suite as infrastructure**: the AI's runtime environment, owned operationally with metrics and alerts.

## Mental Models
- Think of every second over the inner-loop budget as multiplied by the iteration count; a suite that busts the budget eventually gets skipped, which costs more than it ever saved.
- Think of the database as the bottleneck by default: profiled suites typically spend two-thirds of runtime waiting on pools, serial commits and from-scratch migrations.
- Use project coverage as the dashboard number and patch coverage as the number that catches the AI: 200 untested lines move project coverage 65.0% → 64.6% while patch coverage is 0%.
- Think of people who fix test infrastructure (isolation, profiling, tag-enforcing ArchUnit rules) as doing architecture work.

## Anti-patterns
- **Fixing flaky tests by ordering**: buys a few months until a new test breaks it; isolation is the only fix.
- **Enabling parallelism on an unisolated suite**: produces mysterious intermittent failures (off-by-one counts "only on Tuesdays with two threads").
- **Fixed ports in tests**: five workers bind 8080, four crash.
- **Container-per-test-class**: hundreds of Postgres starts dominate runtime.
- **`@SpringBootTest` everywhere**: full context where a slice would do; often five minutes of waste.
- **Tolerating "known flaky" tests**: the AI doesn't know which are known; it introduces real bugs to fix phantom ones.
- **40% coverage floor**: codifies mediocrity and rewards happy-path, no-consequence tests.
- **80–100% coverage as a merge gate**: AI produces syntactically valid, structurally covering, behaviorally vacuous tests; confidence rises, detection stays flat.
- **Project-wide coverage gates**: reward test theater and move too slowly to catch untested generated code.

## Code Examples
```properties
# junit-platform.properties
junit.jupiter.execution.parallel.enabled=true
junit.jupiter.execution.parallel.mode.default=concurrent
junit.jupiter.execution.parallel.config.strategy=dynamic
```
```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20      # accommodate N parallel test workers
      minimum-idle: 5
      connection-timeout: 5000   # fail fast rather than queue and timeout
```
```java
@Test void springContextTestsMustBeTaggedIntegration() {
  methods().that().areAnnotatedWith(SpringBootTest.class)
    .should().beAnnotatedWith(Tag.class)
    .andShould().beAnnotatedWithValueMatching(Tag.class, "value", "integration")
    .check(classes);
}
```
- **What it demonstrates**: parallelism is three properties plus pool sizing once tests are isolated; the inner/full contract is enforced by an ArchUnit rule rather than discipline.

```yaml
# codecov.yml: calibration, not a wall
coverage:
  status:
    project:
      default:
        target: auto       # never regress the existing baseline
        threshold: 1%      # tolerate noise; don't block on rounding
    patch:
      default:
        target: 65%        # new code should arrive with meaningful tests
        informational: true  # comment and warn, do not hard-block
```
- **What it demonstrates**: patch coverage as a per-PR compass comment, not a merge gate.

## Reference Tables
**Test Topology Checklist**

| Area | Check |
|---|---|
| Budgets | Inner loop < 30 s via `@Tag("fast")` (unit, ArchUnit, fast slices; no Spring context) |
| Budgets | Full run < 5 min, strict PR merge gate |
| Budgets | ArchUnit enforces Spring-context tests tagged `integration` |
| Isolation | Zero shared DB state (rollback / UUID namespacing / schema-per-test) |
| Isolation | Zero shared static state (`@AfterEach` reset) |
| Isolation | Zero hardcoded ports |
| Containers/DB | TestContainers `.withReuse(true)` |
| Containers/DB | Migrations once per JVM |
| Containers/DB | Hikari pool sized for N workers |
| Operations | Zero flakiness tolerance: quarantine (`@Disabled` + tracking issue), fix or delete within the sprint |
| Operations | Re-run analysis (`rerunFailingTestsCount=3`) |
| Operations | ~65% meaningful coverage on critical risk paths |
| Operations | Patch coverage posted per PR (informational) |
| Operations | Runtime and flaky counts tracked weekly as health metrics |

**Operational metrics**: suite runtime tracked with alert at +10% without matching test-count growth; flaky count reviewed weekly; inner-loop compliance as a CI check; coverage heat map reviewed quarterly alongside module ownership.

**Coverage calibration zones**: < 65% substantial untested surface; 65–80% coverage correlates with meaningful investment; > 80% testing for testing's sake (private methods, getters, framework code).

## Worked Example
**Namespacing a concurrent repository test (Pattern A).**
```java
@DataJpaTest
class OrderRepositoryTest {
  private final String ns = UUID.randomUUID().toString().substring(0, 8);
  private final String uniqueEmail = "user_" + ns + "@company.com";
  private final String uniqueSku = "SKU-" + ns;

  @Test void shouldFindOrderByName() {
    Customer customer = new Customer(uniqueEmail, "Alice");
    orderRepository.save(new Order(customer, uniqueSku, 100));
    // AVOID: orderRepository.findAll()
    List<Order> found = orderRepository.findBySku(uniqueSku);
    assertThat(found).hasSize(1);
    assertThat(found.get(0).getCustomer().getEmail()).isEqualTo(uniqueEmail);
  }
}
```
Before: tests seeded `test@example.com` and asserted `findAll().size() == 2`, colliding on unique constraints and counting other workers' rows. After: every entity is namespaced and every query is targeted, so concurrent workers share tables without seeing each other. When native SQL/global lookups make this impractical, switch to `@ExtendWith(DynamicSchemaExtension.class)` for a per-class Postgres schema.

**Coverage prompt**: "Add tests to OrderPaymentService that cover the failure paths. Current coverage is 42%; target is 65% meaningful coverage. Do not write tests that exist only to move the number; write tests that would catch a regression in payment processing logic."

## Why It Works / Failure Mode
- **Feedback budget**: the AI's velocity compounds with iteration rate; a 30-second inner loop keeps correction inside the same context before it drifts. Fails when integration tests leak into the fast tier (no tag enforcement) or when the full suite exceeds 5 minutes and gets skipped, leaving only the inner loop.
- **Zero flakiness**: a flaky test turns the loop into write → pass → pass → fail → misdiagnose → modify unneeded code → pass; the AI "learns" its fix worked. Quarantine plus re-run detection removes the random signal. Fails if flaky tests are merely rerun and ignored.

## Key Takeaways
1. Measure test runs per day; at 100–300 AI iterations, a 3-minute suite is a production incident.
2. Hard budgets: inner loop < 30 s, full suite < 5 min, enforced by tags plus an ArchUnit rule.
3. Isolate on three axes (DB, static, ports) before enabling JUnit parallel execution.
4. Attack the database first: container reuse, migrations once per JVM, transaction rollback, namespacing or schema-per-test, slices instead of `@SpringBootTest`.
5. Flaky tests are existential: quarantine immediately, fix or delete within the sprint.
6. Coverage is a compass: aim for ~65% meaningful coverage by risk; report patch coverage per PR informationally.
7. Own the test suite as infrastructure with tracked runtime and flakiness metrics.

## Connects To
- **Ch 5**: ArchUnit rules live in the inner loop; PIT runs outside it (nightly/incremental).
- **Ch 8b**: CodeKarta renders coverage as a heat map over the architecture.
- **Ch 20b**: mutation testing defines "meaningful" coverage and audits tests that pass for the wrong reason.
- **Test pyramid**: two-speed execution is its implied practice, now a hard requirement.
- **Goodhart's Law**: coverage gates turn a measure into a target and breed test theater.
