# Chapter 18: My Test Code Is in the Way

## Core Idea

When you start writing tests, the volume of new code can swamp the project — you browse around and lose track of whether you're looking at production code or test code. The fix is not fewer tests; it's **conventions**. Establish naming and placement rules so tests stay close enough to find instantly but never get confused with production classes. The governing value is *ergonomics*: how cheaply you can navigate back and forth between a class and its tests. Anything that taxes that navigation eventually stops people from writing tests at all.

## Frameworks Introduced

No new code-mechanics framework here. This chapter is conventions and project structure, supporting the testing harness you build with the **Legacy Code Change Algorithm** (identify change points, find test points, break dependencies, write tests, change). It leans on **Subclass and Override Method** for one of its naming categories.

## Key Concepts

- **Class naming conventions.** Keep one unit test class per production class, named as a variation of it. Two common forms: `Test` as a **prefix** (`TestDBEngine`) or as a **suffix** (`DBEngineTest`). It doesn't really matter which — Feathers prefers the **suffix** because in an IDE that lists classes alphabetically, each class lines up directly next to its test class, easing navigation.
- **Fake classes.** Fakes (and mocks) for collaborators get the prefix `Fake` (e.g. `FakeTransaction`, `FakeAccountOwner`). The prefix groups them alphabetically, set somewhat apart from the main classes — convenient because fakes are often subclasses of classes from other directories.
- **Testing subclasses.** A *testing subclass* is a class written purely to test another class while separating out a dependency — the subclass you create when applying Subclass and Override Method. Convention: prefix the production class name with `Testing` (e.g. `TestingCheckingAccount`). This groups all testing subclasses together alphabetically.
- **Test location.** Easiest structure: put test and production code **in the same directory**. The real decision driver is **deployment size constraints**. Server software you control has few constraints, so shipping production binaries plus their test binaries is fine. A commercial product running on someone else's machine may need the tests stripped out.
- **Same package, two directories.** In Java a package can span two directories — e.g. `source/com/orderprocessing/dailyorders` and `test/com/orderprocessing/dailyorders` — so production and test classes still belong to the same package, and some IDEs show both in one view. In many other languages/environments, physical location matters more.
- **Strip at build time.** An alternative to physical separation: keep production and test code together but use **build scripts or settings to exclude test code from the deployment**. With good naming conventions this works cleanly.

## Mental Models

- **Navigation is a tax.** Every directory you climb to get from a class to its test is a cost paid on every edit. Raise that tax high enough and people quietly stop writing tests, and the work slows down.
- **Alphabetical grouping as design.** Prefixes (`Fake`, `Testing`) and suffixes (`Test`) are deliberate levers: they cluster related classes in an alphabetical browser so structure emerges for free.
- **It feels normal eventually.** The discomfort of tests sitting beside production source is acclimation, not a real problem. After a while, tests next to production code just feels right.

## Anti-patterns

- **Separating tests for aesthetics.** Teams often split test and production code simply because they "can't stand" mixing them. The payoff is painful navigation forever after. Only separate for a concrete reason (deployment size, packaging) — never taste.
- **No conventions at all.** Letting test classes, fakes, and testing subclasses accumulate with ad-hoc names until you can't tell test from production.
- **Dogmatism.** Feathers is explicit that he's *not* dogmatic about this layout — there are many valid variations. Forcing one rigid scheme over ergonomics misses the point.

## Key Takeaways

- One test class per class; pick `Test` prefix or suffix and apply it consistently. Suffix aligns each class beside its test alphabetically.
- Prefix fakes/mocks with `Fake` and testing subclasses with `Testing` to group them in the browser.
- Default to tests in the same directory as production code; separate only for a real, deployment-driven reason.
- If you must keep test code out of the shipped product, prefer build-time exclusion over physical separation — naming conventions make this easy.
- Optimize for ergonomics above all: minimize the cost of moving between a class and its tests.

## Connects To

- **Chapter 13 (I Need to Make a Change but Don't Know What Tests to Write):** these conventions house the **characterization tests** you write to pin down existing behavior.
- **Subclass and Override Method (and Chapters 23–25):** the source of the `Testing`-prefixed testing subclasses, used to break dependencies.
- **The book's premise — "legacy code is code without tests":** as you add the tests that retire legacy code, this chapter keeps the growing test suite organized instead of overwhelming.
- **Build/deployment practice:** ties test-location decisions to packaging and deployment-size concerns.
