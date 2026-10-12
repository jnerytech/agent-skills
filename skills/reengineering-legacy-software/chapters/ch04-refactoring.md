# Chapter 4: Refactoring

## Core Idea
Refactoring is the developer's primary weapon against legacy, but only when done with discipline: small reversible steps, separated from feature work, and protected by tests at the right level of modularity. When done correctly, refactoring is perfectly safe — you can refactor all day without introducing a single bug.

## Frameworks Introduced

- **Separate refactoring from other work**: Never combine a behavior change (bug fix / feature) with a refactoring in the same step or commit.
  - When to use: Any time you open a file to do one thing and notice it's "ripe for refactoring."
  - How: Do the change, *then* refactor — or vice versa, but never both at once. Put refactoring and behavioral changes in **separate VCS commits** so reviewers and future-you can tell them apart. Beware: refactorings that look trivial (mark `final`, make fields private, add `hashCode`) can cascade across subclasses and callers.

- **Lean on the IDE (automated refactoring)**: Let the IDE perform mechanical refactorings (rename, extract, Replace Constructor with Builder, etc.).
  - When to use: Any refactoring the IDE supports — it's faster, safer, more thorough (updates comments, test class names), and more efficient than hand-editing.
  - How: Use the Refactor menu (e.g., IntelliJ). But don't trust it unconditionally: inspect the preview, confirm the project still compiles, run tests, and use `grep` for a second opinion (reflection foils its dependency analysis).

- **Lean on the VCS**: Treat version control as a giant Undo button.
  - When to use: During exploratory refactoring where you don't yet know if a solution will work.
  - How: Commit regularly. If a refactoring spirals, revert to the last commit. Use branches to keep several candidate solutions on the go simultaneously.

- **The Mikado Method**: Build a dependency graph of all sub-tasks needed for a large change, then execute them in an optimal, safe order.
  - When to use: Large changes/refactorings (e.g., porting a UI layer between frameworks).
  - How: Explore tasks, draw prerequisites as a graph, backtrack freely (revert via VCS), execute leaves first. See Ellnestam & Brolund, *The Mikado Method* (Manning, 2014).

- **Test-before-refactor via Introduce Indirection (break dependencies)**: Get untestable code into a test harness by wrapping a hard dependency behind an interface and injecting it.
  - When to use: Code coupled to static methods, God classes, DB/email side effects.
  - How: (1) Extract an interface for the dependency; (2) write a production impl that delegates to the original; (3) add a *protected* constructor that injects the interface, keeping the public constructor signature unchanged; (4) inject a mock in tests. Commit and code-review the structural change before writing the test.

- **Regression testing without unit tests**: When refactoring spans multiple units, rely on higher-level tests instead.
  - When to use: Refactorings that merge/split classes (so unit tests would be destroyed anyway), or untestable code where unit isolation is too costly.
  - How: Keep tests one level of modularity *higher* than the affected code. For legacy, start from the outside (system/UI tests via Selenium/Capybara) and work inward.

## Key Concepts
- **Macbeth Syndrome**: An undisciplined refactoring that cascades out of control until you're "in blood stepped in so far" that reverting is as painful as continuing.
- **Stale code**: Code still in the codebase that's no longer needed — deleting it is the easiest/safest refactoring and raises coverage.
- **Dead code**: Code that provably never executes (unreachable branch, unused variable).
- **Zombie code**: Code that *looks* alive but is effectively dead because real data never triggers it (e.g., DB-driven branches, unlinked pages).
- **Expired code**: Date-bounded logic (campaigns, A/B tests) that outlived its purpose.
- **Toxic tests**: Tests worse than no tests — they don't test anything (no assertions), are brittle, or fail randomly, giving false confidence.
- **Seam**: A place where you can alter behavior (inject a substitute) without editing in place — the hook for getting code under test.
- **God class / "Util"**: A huge grab-bag class of static methods referenced everywhere; a refactoring red flag.
- **View adapter (presentation model / ViewModel)**: A plain testable object between model and view that holds presentation logic out of the template.
- **Characterization test**: A test that pins down current behavior so you can refactor without changing it.

## Mental Models
- Use **"peel the orange"** when retroactively testing legacy: the chicken-and-egg of needing tests to refactor and refactoring to test breaks once you force in the first few tests; lower standards temporarily and use code review to cover the gap.
- Use **immutable-by-default** when designing/refactoring state; introduce mutability only when it aids reasoning or profiling proves a bottleneck.
- Use **tests one level higher** than the unit you're changing, because the refactoring itself can wipe out same-level unit tests.
- Use the **VCS as a safety net** to make refactoring exploratory and reversible rather than a high-stakes commitment.

## Anti-patterns
- **Mixing refactor + feature in one commit**: Overloads cognitive load, hides intent, and makes review/revert impossible.
- **Trusting the IDE blindly**: Reflection and overzealous matching cause missed or wrong edits — always verify.
- **Leaving commented-out code**: Pointless noise; that's what the VCS history is for. Just delete it.
- **Tests with no "then"**: Given-when with no assertion inflates coverage and gives false security.
- **Brittle tests via reflection on private fields**: Break on every refactoring; a hint the class holds too much state — split it.
- **Tolerating randomly failing tests**: Erodes the "zero failures = good" discipline; fix, disable, or delete them.
- **Chasing a coverage number**: You write the easy tests first and neglect the important, less-testable code.
- **Glut of nulls / needless mutability**: Implicit nullability and shared mutable state are top sources of bugs.

## Code Examples

Before — `Battle` hard-wired to a static God-class method with DB/email side effects:
```java
public void registerHit(Player attacker, Weapon weapon) {
    Player opponent = getOpponentOf(attacker);
    int damageCaused = calculateDamage(opponent, weapon);
    opponent.setHealth(opponent.getHealth() - damageCaused);
    Util.updatePlayer(opponent);   // writes to DB, may send email!
    updateBattleState();
}
```

After — dependency injected behind an interface, public constructor preserved:
```java
public class Battle {
    private final PlayerUpdater playerUpdater;

    public Battle(Player player1, Player player2) {            // unchanged public ctor
        this(player1, player2, new UtilPlayerUpdater());
    }
    protected Battle(Player player1, Player player2,           // test seam
                     PlayerUpdater playerUpdater) {
        this.player1 = player1; this.player2 = player2;
        this.playerUpdater = playerUpdater;
    }
    public void registerHit(Player attacker, Weapon weapon) {
        ...
        playerUpdater.updatePlayer(opponent);                 // no more static call
        updateBattleState();
    }
}
```
- **What it demonstrates**: Breaking a static dependency by introducing an interface + injected constructor (a seam), without altering existing callers — the classic "get it into a harness" move.

## Reference Tables

IDE-assisted refactoring — why automate:
| Benefit | Detail |
|---|---|
| Faster | Updates hundreds of classes in milliseconds |
| Safer | Far fewer mistakes than a human |
| More thorough | Updates comments, renames matching test classes |
| More efficient | Offloads boring drudge work |

Stale-code taxonomy:
| Type | Definition | Action |
|---|---|---|
| Commented-out | Disabled blocks left "for the record" | Delete; VCS has history |
| Dead | Provably never executes | Delete (IDE/FindBugs detect) |
| Zombie | Looks alive, never triggered by real data | Verify with data + DB constraint, then delete |
| Expired | Date-bounded logic past its window | Mark `// EXPIRES: yyyy-mm-dd`, fail CI build when found |

Levels of modularity → corresponding tests: System→System tests, Component→Integration tests, Module→Functional tests, Unit→Unit tests.

## Worked Example
Goal: get the untestable `Battle` class into a test harness. `Battle` depends on `Util.updatePlayer()`, a *static* method on a 3,000-line God class that writes to the DB and may email the user — fatal side effects in a test.

1. **Try the naive test** — `battleEndsIfOnePlayerAchievesThreeHits` calls `registerHit` three times and asserts `state.isFinished()`. It fails because the static call hits the DB/email.
2. **Cannot subclass/override** a static method, so introduce a layer of indirection. Extract an interface:
   ```java
   interface PlayerUpdater { void updatePlayer(Player player); }
   ```
3. **Production impl delegates** to the original static call:
   ```java
   public class UtilPlayerUpdater implements PlayerUpdater {
       public void updatePlayer(Player player) { Util.updatePlayer(player); }
   }
   ```
4. **Inject via a protected constructor**, leaving the public constructor's signature intact (default-wires the real impl). Put the test in the same package so it can call the protected ctor.
5. **Pause, commit, code-review** the structural change — behavior should be unchanged — *before* writing the test.
6. **Mock in the test** with Mockito, and verify interactions:
   ```java
   PlayerUpdater updater = mock(PlayerUpdater.class);
   Battle battle = new Battle(player1, player2, updater);
   battle.registerHit(player1, axe);  // x3
   assertThat(battle.getBattleState().isFinished(), is(true));
   verify(updater, times(3)).updatePlayer(player2);
   ```

Result: the skin is broken — the first test passes, the `Util` dependency is severed, and interactions are now verifiable. Further isolation and tests can follow.

(Companion example — *Byzantine business logic*: the scattered-`if` `BannerAdChooser.getAd()` is refactored by combining **Chain of Responsibility** (each business rule becomes a testable `Rule` subclass with `canApply`/`apply`, chained together) and **Decorator** (caching and logging extracted into `CachingBannerAdChooser`/`LoggingBannerAdChooser` wrapping a `BaseBannerAdChooser`, wired by a factory). Each rule and concern is now independently testable.)

## Key Takeaways
1. Discipline beats heroics: small, reversible steps committed separately keep you out of the Macbeth Syndrome.
2. Never mix a refactoring with a behavior change in one commit.
3. Automate the mechanical parts via the IDE, but verify (compile, tests, grep) — it isn't infallible.
4. Warm up by deleting stale code and toxic tests; it's safe, satisfying, and raises real coverage.
5. To test untestable code, introduce indirection (interface + injected constructor) to create a seam, then mock the dependency.
6. Unit tests aren't a silver bullet — keep tests one modularity level above the code you're changing, and automate *all* of them, not just unit tests.
7. Prefer immutability and explicit nullability (Optional, JSR-305 `@Nonnull`/`@Nullable`) to shrink whole classes of bugs.

## Connects To
- **Ch 1**: Fixes the untestable hardcoded-dependency problem (the ImageResizer) by the same injection technique applied here to `Battle`.
- **Ch 2**: Static-analysis tools (FindBugs) and JSR-305 annotations surface dead code and nullability issues to refactor.
- **Ch 3**: Refactoring is the execution arm of the prioritized improvement plan — this chapter is the code-level "how."
- **Working Effectively with Legacy Code (Feathers)**: Directly cited as the deep reference. The interface-extraction/injected-constructor move is breaking dependencies at a *seam* to get code into a test harness; the test-the-current-behavior tests are characterization tests. Birchall's "peel the orange" mirrors Feathers' bootstrap of getting the first tests in place.
