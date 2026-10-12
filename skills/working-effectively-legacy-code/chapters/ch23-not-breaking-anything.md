# Chapter 23: How Do I Know That I'm Not Breaking Anything?

## Core Idea

Code only breaks when *someone edits it*. Left alone, it runs forever; the developer is the primary agent of fault injection, and breaking software is mechanically trivial — a stray keystroke can do it. This chapter is about *reducing edit risk*, especially the riskiest moment in legacy work: breaking dependencies to get the first tests in place. That's a chicken-and-egg trap — you often must refactor a little *without tests* just to make the code testable enough to refactor more. Those initial, untested moves (the dependency-breaking techniques in the Chapter 25 catalog) have to be **particularly conservative**. The chapter offers four disciplines — two mechanical, two psychological — to stay safe when the usual safety net (tests) isn't there yet.

Remember the operating definition: **legacy code is code without tests**. Until you have a characterization test pinning current behavior, every edit is a guess. These practices are how you make *good* guesses while you bootstrap toward a seam, an enabling point, and a test harness.

## Frameworks Introduced

**Hyperaware Editing.** Know exactly what each keystroke does. Every keystroke either changes behavior or it doesn't — text in a comment doesn't; a changed numeric literal in live code is a *functional change*, not refactoring. Hyperawareness isn't omniscience; it's any feedback that tells you, really tells you, how you're affecting the software as you type. TDD supplies it (run tests in under a second and *know* the effect of a change); pair programming supplies it (a second set of eyes). It's a flow state, not an exhausting one — what's actually exhausting is editing *without* feedback, holding all the unverified changes in your head and hoping you can later convince yourself you did what you intended.

**Single-Goal Editing.** "Programming is the art of doing one thing at a time." Don't start a feature, drift into a refactor, hop to a method, decide *it* needs changing, and leave three edits half-done. That's thrashing, and it's how integration fails. Instead: when a partner asks "What are you doing?" and your answer names more than one thing, pick one. Write the other down on paper and come back to it. Finish the current edit, run tests, *then* take the next item. It feels slower; it's faster, because you stay deliberate and always know what your code does.

**Preserve Signatures.** When breaking dependencies — invasive, large-scale editing where mistakes (misspellings, wrong types, swapped variables) abound and there are no tests to catch them — avoid changing signatures at all. By keeping parameter lists identical, you can cut/copy/paste *entire* method signatures verbatim from place to place, minimizing transcription errors. Resist the urge to "improve the design" mid-extraction; that good intention is exactly what plants late-found bugs. Beyond new method declarations, the same move builds instance fields for every argument in *Break Out Method Object*.

**Lean on the Compiler.** In statically typed languages, deliberately introduce a compile error (alter a declaration), then let the compiler's error list enumerate *every* site you must touch. The compiler does the legwork of finding changes — but you must still think, and you must know what the compiler *won't* catch.

## Key Concepts

- **Feedback closes the loop.** The faster and tighter the feedback (per-keystroke tests, a watching pair), the fewer bugs survive. The author predicts edit-triggered testing as inevitable.
- **Conservative first moves.** Dependency-breaking refactorings done *before* tests exist must be the most cautious edits you ever make — mechanical, signature-preserving, single-purpose.
- **Compiler ≠ full coverage.** Leaning on the compiler finds *type/structural* breakages, not behavioral ones, and inheritance can silently hide a breakage from it.
- **Judgment over recall.** Being able to hold an entire system in your head doesn't make you a better decision-maker. Doing one thing at a time does.

## Mental Models

- **Surgery, not solo heroics.** "Working in legacy code is surgery, and doctors never operate alone." Pair.
- **Code is fragile building material.** Unlike metal or wood it never fatigues — it only breaks when *edited*. So treat every edit as the hazard.
- **The racehorse vs. the deliberate pair.** One pair "kills the beast" then spends three-quarters of the session fixing what they broke and still fails integration; the disciplined pair does one verified thing at a time and integrates clean.
- **Two keystroke categories.** Behavior-changing vs. not. Always know which one you're typing.

## Anti-patterns

- **Improving design mid-dependency-break.** Extracting a method *and* inventing helper classes (`OrderBatch`, `CompensationTarget`) in one untested move — foolish mistakes, found far too late.
- **Multi-goal thrashing.** Chasing every "while I'm here" cleanup until several edits are pending at once and nothing is verifiable.
- **Blind compiler-leaning.** Trusting "no compile errors" as proof a method is unused — when a superclass version silently takes over.
- **Editing without feedback.** No tests, no pair, just willpower and memory.

## Code Examples

Preserve Signatures — the *wrong* eager extraction (changes the signature and adds helpers):

```java
public void process(List orders, int dailyTarget, double interestRate, int compensationPercent) {
    processOrders(new OrderBatch(orders), interestRate * 100, compensationPercent));
}
```

The *conservative* extraction — signature preserved verbatim on both the delegate and the new static method:

```java
public void process(List orders, int dailyTarget, double interestRate, int compensationPercent) {
    processOrders(orders, dailyTarget, interestRate, compensationPercent);
}
private static void processOrders(List orders, int dailyTarget, double interestRate, int compensationPercent) {
    ...
}
```

Lean on the Compiler — *Encapsulate Global References*: wrap the globals so the compiler flags every use site:

```cpp
class Exchange {
public:
    double domestic_exchange_rate;
    double foreign_exchange_rate;
};
Exchange exchange;

// compiler now errors at every old reference; fix each:
// total = domestic_exchange_rate * instrument_shares;
total = exchange.domestic_exchange_rate * instrument_shares;
```

The inheritance trap — commenting this out yields *no* error if a superclass defines `getX()`, silently switching to the superclass version:

```java
/* public int getX() { return x; } */
```

## Worked Example

**Preserve Signatures, step by step** (extracting `processOrders` from `process`). The whole trick is to never retype a parameter list:

1. Copy the *entire* argument list into the paste buffer:
   `List orders, int dailyTarget, double interestRate, int compensationPercent`
2. Type the new empty declaration: `private void processOrders() { }`
3. Paste the buffer between the parens:
   `private void processOrders(List orders, int dailyTarget, double interestRate, int compensationPercent) { }`
4. Type the call site: `processOrders();`
5. Paste the buffer into the call:
   `processOrders(List orders, int dailyTarget, double interestRate, int compensationPercent);`
6. At the call only, delete the *types*, leaving the names:
   `processOrders(orders, dailyTarget, interestRate, compensationPercent);`

Repeated enough, these moves go automatic, and you can spend your attention on the subtle hazards instead — e.g. is your new method accidentally hiding a same-signature method in a base class?

**Lean on the Compiler, step by step:**

1. **Alter a declaration to cause compile errors.** Want to encapsulate two file-scope globals so you can substitute them under test? Wrap them in a class and declare one instance (`Exchange exchange;`). Every existing reference to the bare globals now fails to compile.
2. **Navigate to those errors and make the changes.** Walk the compiler's error list; at each site rewrite `domestic_exchange_rate` → `exchange.domestic_exchange_rate`. When the list is empty, every use is converted.

Same technique for a *type* change: retype a variable's declaration from a concrete class to an interface, then let the compile errors tell you exactly which methods the interface must expose. Caveat: if builds are slow (see Chapter 7), searching may beat leaning — and never lean blindly past inheritance, where a hidden superclass member can swallow the error.

## Key Takeaways

- The developer is the fault source; reducing *edit risk* is the whole game when tests don't yet exist.
- **Hyperaware Editing:** know what every keystroke does — get feedback (TDD, pairing) rather than carry state in your head.
- **Single-Goal Editing:** one thing at a time; park the rest on paper; verify before moving on.
- **Preserve Signatures:** cut/copy/paste whole parameter lists verbatim; don't "improve" while breaking dependencies.
- **Lean on the Compiler:** break a declaration on purpose, then fix every error it reports — but know its blind spots (behavior, inheritance).
- Pair when doing untested dependency-breaking. Surgeons don't operate alone.

## Connects To

- **Ch. 25 (Dependency-Breaking Techniques):** *Expose Static Method*, *Encapsulate Global References*, *Break Out Method Object* are the catalog moves these disciplines protect — the conservative, signature-preserving edits you make *before* tests exist.
- **Ch. 22 / characterization tests:** once you've safely opened a seam and reached an enabling point, you pin behavior with a characterization test — turning untested legacy code into tested code.
- **The Legacy Code Change Algorithm** (identify change points → find test points → break dependencies → write tests → make changes): this chapter is the safety manual for the *break dependencies* step, which alone runs without a net.
- **Ch. 7 (It Takes Forever to Make a Change):** when slow builds make Lean on the Compiler impractical, prefer searching for change sites.
- **TDD (Ch. on test-driven development) and Pair Programming:** the two engines that supply hyperaware feedback.
