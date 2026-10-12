# Chapter 13: I Need to Make a Change, but I Don't Know What Tests to Write

## Core Idea

In legacy code (code without tests), you usually can't verify that a change preserves behavior — there's nothing pinning down what the code currently does. Don't start by writing tests for what the code *should* do; that's just bug-finding, and if you make finding and fixing every bug your goal in legacy code, you'll never finish. Instead write **Characterization Tests**: tests that document the *actual current behavior* of the code, with no "it should do this" or "I think it does that." Their job isn't to assert a moral standard — they have **no moral authority**. They are a safety net that detects *differences* from current behavior later, when you change something you didn't intend to. Automated tests in general specify a goal or **preserve behavior that is already there**; in the natural flow of development, tests that specify become tests that preserve.

## Frameworks Introduced

### Characterization Test (the algorithm — the chapter's payload)

A characterization test captures what the code *really does* by letting the failure message reveal the truth, then encoding that truth as the expectation.

1. **Use a piece of code in a test harness.** Get the class/method instantiable and callable under xUnit.
2. **Write an assertion that you know will fail.** Assert an absurd expected value (the classic: `assertEquals("fred", ...)`).
3. **Let the failure tell you what the behavior is.** The comparison-failure message reports the actual produced value.
4. **Change the test so that it expects the behavior that the code produces.** Paste the real value into the assertion; the test now passes and documents the fact.
5. **Repeat** — feed new inputs, characterize more behavior, until you understand the area you'll change.

This is *not* black-box testing: you are allowed to read the code you're characterizing. Get into a **state of curiosity** about the code's behavior and write tests until you're satisfied you understand it.

### Characterizing Classes (heuristics)

Figure out what the class does at a high level, test the simplest thing you can imagine it doing, then let curiosity guide you. Heuristics:

1. **Look for tangled pieces of logic.** If you don't understand an area, introduce a **sensing variable** to characterize it and to make sure you actually execute particular areas of the code.
2. **List what can go wrong** as you discover responsibilities; formulate tests that trigger those failures.
3. **Probe inputs** — what happens at extreme values?
4. **Hunt for invariants** — conditions that should hold at all times during the object's lifetime; write tests to verify them. You may have to refactor to discover them, and that refactoring often yields new insight.

### A Heuristic for Writing Characterization Tests

1. Write tests for the **area where you will make your changes** — as many cases as you need to understand the behavior.
2. Then look at the **specific things you are going to change** and write tests targeting those.
3. If extracting or moving functionality, **verify the existence and connection** of behaviors case-by-case: exercise the code you're going to move, confirm it's connected properly, and **exercise conversions**.

## Key Concepts

- **The Method Use Rule** — Before you use a method in a legacy system, check whether tests exist for it. If not, write them. Tests then become a medium of communication; making a class testable in itself tends to raise code quality.
- **Targeted Testing** — After characterizing an area, look at exactly what will change and confirm your tests cover *that*. For a branch you'll alter, make sure a test actually executes that branch. Ask: *is there any other way this test could pass besides executing this branch?* If unsure, use a **sensing variable** or the debugger to confirm the path is hit.
- **When you find a bug** — You will find bugs while characterizing; all legacy code has them. If the system has never been deployed, just fix it. If it *has* shipped, examine whether someone depends on that behavior before "fixing" it. Don't drop the test — mark it as **suspicious**, include it in the suite, and escalate to find out fast whether it's truly a bug and how to fix it without ripple effects.
- **Refactoring + conversions** — When refactoring you must check two things: does the behavior still exist, and is it **connected correctly**? Watch silent type conversions (e.g., Java's double→int truncation) — a "sunny day" test can still pass while a truncation bug slips through if inputs don't force the error to show.

## Mental Models

- **No moral authority.** The expected values come *from* the software, so the tests can't judge the software — they just sit there documenting what each piece really does. Combine that knowledge of *what is* with your knowledge of *what should be* to make changes deterministically.
- **Tests as the only durable record of behavior.** Short of tests, the only way to know what a system does is "playing computer" in your head — reading code and reasoning through values. That's tedious and wasteful to redo every time.
- **Specify → preserve.** A test written to pin behavior today becomes the alarm that catches an unintended change tomorrow. You find bugs in *later* runs, not the first.
- **The change guides curiosity.** The modification you set out to make naturally steers which behaviors are worth characterizing.

## Anti-patterns

- **Relying on manual testing** for changes — you have to redo it on every change, people don't, and the team falls behind with low confidence.
- **Writing tests from requirements docs / "what it should do"** in legacy code — collapses back into bug-finding; in a legacy system what it *does* matters more than what it's *supposed* to do.
- **Trying to fix every bug you find** — infinite work; you'll never finish.
- **Reflexively "fixing" surprising behavior** in deployed code without checking who depends on it.
- **Sunny-day tests over conversion-heavy code** — passing tests that never exercise the truncation/conversion that an extraction can break.
- **Assuming a test hit your branch** — without a sensing variable or debugger, the test may pass for an unrelated reason.

## Code Examples

```java
// 2. Assert something you KNOW is wrong
void testGenerator() {
    PageGenerator generator = new PageGenerator();
    assertEquals("fred", generator.generate());
}
// 3. Failure reveals truth: expected:<fred> but was:<>
// 4. Encode the real behavior — now it documents a fact
void testGenerator() {
    PageGenerator generator = new PageGenerator();
    assertEquals("", generator.generate());   // fresh generator -> empty string
}
```

```java
// Targeted Testing: force the else-branch that the refactoring will move
public void testValueForGallonsMoreThanCorpMin() {
    StandardLease lease = new StandardLease(Lease.MONTHLY);
    FuelShare share = new FuelShare(lease);
    share.addReading(FuelShare.CORP_MIN + 1, new Date()); // > CORP_MIN -> hits else
    assertEquals(12, share.getCost());
}
```

## Worked Example

You must characterize a `PageGenerator` before changing it, but you have no idea what `generate()` returns.

1. **Harness it.** `PageGenerator generator = new PageGenerator();`
2. **Guess wrong on purpose:** `assertEquals("fred", generator.generate());` — you're confident it won't produce `"fred"`.
3. **Run it.** JUnit reports `ComparisonFailure: expected:<fred> but was:<>`. The failure just told you: a freshly created generator returns the empty string.
4. **Encode the fact:** change the expectation to `assertEquals("", generator.generate());`. Green. You've now documented a real behavior — no requirements doc consulted.
5. **Repeat with more input:** add `generator.assoc(RowMappings.getRow(Page.BASE_ROW));` then assert `"fred"` again. The failure reveals the real output: `<node><carry>1.1 vectrai</carry></node>`. Paste that in as the expected value. Green again.

You never decided what the code *should* do — you interrogated it and recorded the answers. Then, before extracting `FuelShare`'s top-level `if` into `ZonedHawthorneLease.computeValue`, you add a **targeted** test that drives `gallons > CORP_MIN` so the `else` you're about to move is actually exercised, and you pick inputs (and watch for `double`→`long` truncation) so a silent conversion can't pass unnoticed.

## Key Takeaways

- A characterization test documents **actual current behavior**, not intended behavior — that's its whole point and its safety value.
- Memorize the five-step loop: harness → assert-known-fail → read the failure → expect the real value → repeat.
- You're not black-boxing — read the code, get curious, and stop when you understand the area *and* can sense the changes you're about to make.
- Apply **Targeted Testing**: confirm your tests truly cover the lines that will change, including branch coverage and type conversions; verify with a sensing variable or debugger.
- Follow the **Method Use Rule** — no tests for a method you're about to use? Write them first.
- On surprising behavior in deployed code: mark **suspicious**, keep the test, escalate — don't "fix" until you know who depends on it.

## Connects To

- **Ch 4 (The Seam Model)** — to get code into a harness (step 1) you exploit **seams** and their **enabling points** to substitute dependencies.
- **Ch 8/9/10 ("How do I add a feature / get this class / method into a test harness")** — the mechanics that make step 1 possible.
- **Ch 11 (I Need to Make a Change. What Methods Should I Test?)** — effect sketches and the reasoning behind Targeted Testing.
- **Ch 6 (The Legacy Code Change Algorithm)** — characterization tests fill the "cover" step (identify change points → find test points → break dependencies → write tests → make changes and refactor).
- **Ch 5 (Tools)** — fake/mock objects support **sensing** (verifying calls) vs. **separation** (breaking dependencies); sensing variables likewise probe internal execution.
- **Ch 13's own "legacy code = code without tests"** definition — the premise that makes characterization the default move.
