# Chapter 8: How Do I Add a Feature?

## Core Idea

Once a class is under test, you have a solid foundation for adding features in a way that makes the code *better* rather than worse. This is the contrast with Chapter 6's sprout/wrap escape hatches: those add behavior alongside untested code without improving it, leaving duplication, fear, and resignation in their wake. Feathers' advice is blunt: "it's better to confront the beast than hide from it." Get tests in place, then use two feature-addition techniques — **Test-Driven Development** and **Programming by Difference** — to grow the system. The key insight for legacy work is that the tests we write *while* adding a feature are what give us a free hand later: they let us add code quickly (even by brute copy/paste) and then fold it back in cleanly, knowing nothing broke. Remember the working definition: *legacy code is code without tests*. Adding a feature well starts by ending that condition for the class you're touching.

## Frameworks Introduced

### Test-Driven Development (TDD)

TDD is the most powerful feature-addition technique in the book. You imagine a method that solves part of the problem and write a failing test for it before the method exists. Writing the test solidifies your understanding of what the code must do. The cycle:

1. **Write a failing test case.**
2. **Get it to compile.**
3. **Make it pass.**
4. **Remove duplication.**
5. **Repeat.**

In step 2 you stub the method so it compiles but still fails (e.g., return `Double.NaN` so it can't accidentally equal the expected value). In step 3 you write the real implementation — usually in tiny increments, though a large step is acceptable when you are certain of the algorithm. Step 4 is non-negotiable: brutal copy/paste is fine to make a test pass, but if you don't remove the duplication afterward you've just manufactured a maintenance burden. The tests are what make removing duplication safe.

**The legacy extension** of the algorithm adds a step 0:

0. **Get the class you want to change under test.**
1. Write a failing test case.
2. Get it to compile.
3. Make it pass. *(Try not to change existing code as you do this.)*
4. Remove duplication.
5. Repeat.

The deep value of TDD in legacy code is *separation of concerns in time*: you are either writing code or refactoring, never both at once. You write new code independently, then refactor to remove duplication between the new and the old.

### Programming by Difference

TDD isn't tied to OO. In object-oriented code we have another lever: use inheritance to introduce a feature *without modifying the existing class*. Subclass, override the one method that needs to differ, and point your test at the subclass. This makes the test pass fast. It is an old 1980s technique that fell out of favor when the community noticed inheritance is problematic when overused — but the point is you don't have to *keep* the inheritance. With tests pinning the new behavior, you can migrate to a cleaner structure (configuration object, delegation, a renamed collaborator) and the move is rapid.

### Liskov Substitution Principle (LSP)

The main "gotcha" of Programming by Difference. Objects of a subclass should be substitutable for objects of their superclass everywhere in the code; if they aren't, you get silent errors. Rules of thumb:

1. Whenever possible, avoid overriding concrete methods.
2. If you do, try to call the overridden method from within the override.

## Key Concepts

- **Remove duplication is a first-class step**, not cleanup you do "later if there's time." Tests are the enabling point that makes it safe.
- **Procedural code in a class** — the `InstrumentCalculator` example is really procedural code wrapped in a class; TDD applies regardless of paradigm.
- **Generalize later.** When you spot a general pattern (the n-th moment), resist building the general method mid-stride. Finish the current red-green cycle; generalize only if you still want to.
- **Normalized hierarchy** — a hierarchy in which no class has more than one implementation of a method; no class overrides a *concrete* method it inherited. When you ask "how does this class do X?" the answer is either right there or abstract-and-implemented-in-a-subclass. You never have to worry about an inherited concrete method being silently replaced.
- **Single Responsibility Principle** tension — folding both features into `MessageForwarder` can violate SRP; whether it matters depends on how large and tangled the responsibility becomes.
- **Rename Class** is, in Feathers' words, the most powerful refactoring: renaming `MailingConfiguration` to `MailingList` changes how people *see* the code and reveals possibilities.

## Mental Models

- **Confront the beast, don't hide from it.** Sprout/wrap leave fear and resignation behind as little reminders; getting code under test removes them.
- **Side-by-side before folded-in.** Copying awful code into a new method and modifying it there lets you see your change next to the original — easier to understand, and easy to discard and retry because the old code is still visible.
- **Tests as a safety harness for design moves.** A passing test written against the quick-and-dirty version is a license to refactor toward the real design.
- **Inheritance is a temporary scaffold,** not a commitment. Use it to pass the test, then dismantle it if it degrades the design.

## Anti-patterns

- **Reaching for sprout/wrap by default** because tests are hard to write — it never improves existing code and breeds duplication you may not notice until you're deep in.
- **Skipping "Remove duplication."** Copy/paste features that are never folded back create a maintenance burden.
- **Subclass-per-feature explosion.** Put each feature in its own subclass and you can only have *one feature at a time* — you can't combine "anonymous" + "off-list recipients" without a combinatorial mess of subclasses.
- **Overriding concrete methods freely.** A reader who sees a `MessageForwarder` reference will assume `MessageForwarder.getFromAddress` runs; they may have no idea it's really an `AnonymousMessageForwarder`. Frequent concrete overrides make code confusing and risk LSP violations (the `Square extends Rectangle` trap, where `setWidth(3); setHeight(4)` surprisingly yields area 16, not 12).
- **Generalizing mid-cycle.** Designing the fully general API while you're only trying to "get it to compile" — getting lost in thought instead of closing the loop.

## Code Examples

Stub that compiles but fails on purpose (step 2):

```java
double firstMomentAbout(double point) {
    return Double.NaN;          // not -0.5, so the test fails
}
```

Brute-force duplication to make a second test pass (acceptable *if* removed next):

```java
public double secondMomentAbout(double point) throws InvalidBasisException {
    ...
    numerator += Math.pow(element - point, 2.0);   // copy of firstMomentAbout, exponent changed
    ...
}
```

Duplication removed by extracting a parameterized private method (step 4):

```java
public double firstMomentAbout(double point)  throws InvalidBasisException { return nthMomentAbout(point, 1.0); }
public double secondMomentAbout(double point) throws InvalidBasisException { return nthMomentAbout(point, 2.0); }

private double nthMomentAbout(double point, double n) throws InvalidBasisException {
    if (elements.size() == 0) throw new InvalidBasisException("no elements");
    double numerator = 0.0;
    for (Iterator it = elements.iterator(); it.hasNext(); ) {
        double element = ((Double)(it.next())).doubleValue();
        numerator += Math.pow(element - point, n);
    }
    return numerator / elements.size();
}
```

## Worked Example

**Programming by Difference, then refactoring the inheritance away — `MessageForwarder`.**

A tested `MailForwarder`/`MessageForwarder` strips the "from" address off an incoming message and reuses it when forwarding to list recipients. New requirement: *anonymous* mailing lists, where the "from" address must become `anon-members@<domain>`.

**1 — Failing test (red).** Point the test at a not-yet-existing subclass:

```java
public void testAnonymous() throws Exception {
    MessageForwarder forwarder = new AnonymousMessageForwarder();
    forwarder.forwardMessage(makeFakeMessage());   // fake message — sensing via a stand-in collaborator
    assertEquals("anon-members@" + forwarder.getDomain(),
                 expectedMessage.getFrom()[0].toString());
}
```

**2 — Make it pass by subclassing.** Change `getFromAddress` from private to **protected** in `MessageForwarder`, then override it:

```java
public class AnonymousMessageForwarder extends MessageForwarder {
    protected InternetAddress getFromAddress(Message message) throws MessagingException {
        String anonymousAddress = "anon-" + listAddress;
        return new InternetAddress(anonymousAddress);
    }
}
```

Green, fast. But this added a whole class for trivial behavior — and exposed the trap: a *second* feature, off-list (bcc) recipients, would want its own subclass. We can't get a forwarder that is both anonymous **and** sends off-list — one-feature-per-subclass.

**3 — Refactor the inheritance away (tests protect us).** Make anonymity a configuration option instead. Constructor takes a `Properties`; `getFromAddress` on `MessageForwarder` itself handles both cases:

```java
private InternetAddress getFromAddress(Message message) throws MessagingException {
    String fromAddress = getDefaultFrom();
    if (configuration.getProperty("anonymous").equals("true")) {
        fromAddress = "anon-members@" + domain;
    } else {
        Address[] from = message.getFrom();
        if (from != null && from.length > 0) fromAddress = from[0].toString();
    }
    return new InternetAddress(fromAddress);
}
```

Comment out the subclass override; the test still passes — proof the behavior is preserved. Delete `AnonymousMessageForwarder`, replace its constructor calls with the properties-based constructor.

**4 — Evolve toward a real abstraction.** As properties multiply and conditionals litter the class, push them into a `MailingConfiguration` object, then move `getFromAddress` and `buildRecipientList` onto it. The object now does real work, so the passive name no longer fits — **Rename Class** to `MailingList`. `MessageForwarder` now asks a mailing list to compute from-addresses and build recipient lists: a clean responsibility split.

**LSP coda.** Had we kept the inheritance, the right shape is a **normalized hierarchy**: make `MessageForwarder` abstract with an abstract `getFromAddress`, and let each subclass supply the one concrete body — no class overriding an inherited concrete method, no silent substitution surprises.

## Key Takeaways

- Get the target class under test first (step 0); then TDD: red, green, refactor — **write failing test → compile → pass → remove duplication → repeat.**
- You are either writing code or refactoring, never both at once — this time-separation is what makes TDD safe in legacy code.
- "Remove duplication" is mandatory, and tests are what make it cheap; copy/paste to go green is fine only because you'll fold it back.
- **Programming by Difference** introduces variations fast via inheritance, but treat the inheritance as scaffolding — migrate to configuration/delegation once tests pin the behavior.
- Watch for the **LSP** trap (don't override concrete methods casually) and aim for **normalized hierarchies** when you choose to keep inheritance.

## Connects To

- **Chapter 6 (I Don't Have Much Time)** — sprout/wrap are the fallback this chapter argues against when you can instead get code under test.
- **Chapter 13 (I Don't Know What Tests to Write)** — how to get the characterization tests in place that step 0 requires.
- **Chapters 9 & 10 (Can't Get This Class / Method into a Test Harness)** — breaking dependencies via seams and their enabling points (the fake/mock used as `makeFakeMessage()`), sensing vs. separation, so step 0 is achievable.
- **Single Responsibility Principle** — the design pressure that drives moving behavior out of `MessageForwarder` into `MailingList`.
- **Kent Beck, *Test-Driven Development by Example*** and **Dave Astels, *Test-Driven Development: A Practical Guide*** — recommended deeper reading on the cycle.
