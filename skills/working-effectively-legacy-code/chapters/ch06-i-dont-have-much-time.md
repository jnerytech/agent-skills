# Chapter 6: I Don't Have Much Time and I Have to Change It

## Core Idea

The honest tension every legacy-code change hits: you're under pressure, there
are no tests, and hacking the change inline will be done by 5:00. Feathers calls
this **pay-me-now-or-pay-me-later**. Writing tests and breaking dependencies up
front costs time today, but you almost always recoup it — partly because *changes
cluster in systems*: if you're touching this code today, you'll be back near it
soon. The chapter's pragmatic move: when you genuinely can't afford to get the
existing class under test right now, don't add code inline. Instead, write the
new behavior as **fresh code in a new, tested method or class**, and call it from
the untested code. You get tested new code with a clean **seam** between old and
new, even if the call site itself stays uncovered. Four techniques deliver this:
Sprout Method, Sprout Class, Wrap Method, Wrap Class. They are not an excuse to
skip testing forever — they are a way to make *safe* progress while leaving a
marker for the real cleanup later.

## Frameworks Introduced

- **Sprout Method** — *When to use*: the change is a distinct piece of new work
  that can be formulated as a single sequence of statements, and you can write
  tests for that new logic in isolation. *How*: (1) identify the change point;
  (2) write the call to a not-yet-existent method at the insertion point and
  comment it out; (3) pass needed locals as arguments; (4) if it must return a
  value, assign the call's result to a variable; (5) develop the new method
  test-first (TDD); (6) uncomment to enable the call. If creational dependencies
  block instantiation, make the sprout a `public static` method (a "staging
  area") or use Pass Null. *Advantages/Disadvantages*: cleanly separates new code
  from old with a tested interface; but you're "giving up" on the source method
  for now, leaving it in limbo with mixed responsibilities.

- **Sprout Class** — *When to use*: Sprout Method isn't enough because you can't
  even instantiate the source class in a test harness (heavy creational/hidden
  dependencies), or the new work is really a new responsibility off to the side.
  *How*: (1) identify the change point; (2) name a class to do the work, write
  code to create it and call it there, comment it out; (3) pass needed locals to
  the constructor; (4) if it must return a value, add a method to supply it and a
  receiving call; (5) develop the class test-first; (6) uncomment to enable.
  *Advantages/Disadvantages*: lets you move forward with confidence and (in C++)
  without touching the source header, reducing compile load; but adds conceptual
  complexity — abstractions get gutted into sprouts because your back is against
  the wall.

- **Wrap Method** — *When to use*: you need to add behavior that runs *before or
  after* an existing method's work (never intertwined), and you want to avoid
  temporal coupling — bolting unrelated code in just because it executes at the
  same time. *How* (form 1, same name): (1) identify the method; (2) rename it
  and create a new method with the **same name and signature** (Preserve
  Signatures); (3) have the new method call the renamed old one; (4) develop the
  new feature test-first and call it from the new method. *Form 2 (new name)*:
  develop the new behavior test-first, then create a method that calls both new
  and old code. *Advantages/Disadvantages*: introduces a **seam**, keeps new
  behavior independent, and does *not* grow existing methods; but it can force
  awkward names for the extracted old code (e.g. `dispatchPayment`).

- **Wrap Class** — *When to use*: the class-level companion to Wrap Method. Use
  when behavior is completely independent and you don't want to pollute the class,
  or the class is so large you refuse to make it worse — you "put a stake in the
  ground." *How*: (1) identify the change point; (2) create a class that takes the
  wrapped object as a constructor argument (use Extract Implementer / Extract
  Interface if you can't instantiate the wrapper in a harness); (3) test-first,
  add a method doing the new work plus one that calls both new and old; (4)
  instantiate the wrapper where the new behavior is needed. When there are many
  callers, lean toward a **decorator-style** wrapper (same interface, transparent
  to clients); for one-off use, a plain non-decorator wrapper is fine.
  *Advantages/Disadvantages*: adds behavior to a system without modifying any
  existing class; but stacked decorators are like peeling an onion — "necessary
  work, but it makes your eyes water."

## Key Concepts

- **Legacy code = code without tests.** The whole chapter is about making a change
  to such code without first getting it fully under test.
- **The Legacy Code Change Algorithm** (the default, not bypassed here): identify
  change points → find test points → break dependencies → write tests → make
  changes & refactor. These four techniques are what you reach for *when you've
  decided you can't afford the dependency-breaking step right now* — they let you
  satisfy "write tests / make changes" for the *new* code alone.
- **Seam + enabling point.** Wrap Method and Wrap Class manufacture a seam where
  none existed: the wrapping method/class is the place you can insert or alter
  behavior without editing the wrapped logic.
- **Sensing vs separation.** These techniques are about *separation* — pulling new
  responsibility apart from old — not about sensing values through a fake/mock.
  (Sensing/fakes come into play when you must test the call site itself.)
- **Characterization test.** Not the focus here (you're adding *new* behavior, so
  you write tests TDD-style for it), but the unwritten companion: someday you
  return to characterize the source class and fold the sprouts back in.
- **Temporal coupling.** Grouping operations only because they happen at the same
  time. Wrap Method exists to *avoid* creating it.
- **Decorator pattern.** The transparent form of Wrap Class: an abstract decorator
  subclasses/implements the target interface, holds an instance, delegates each
  method, and overrides the ones it augments. Decorators nest. Always need one
  concrete "basic" class at the bottom that actually does the work.

## Mental Models

- **Pay me now or pay me later.** Tests cost time today and save more later;
  cluster-of-change means "later" is usually soon, not years away.
- **Code is your house — you have to live in it.** The emergency-hack-and-fix-it-
  tomorrow plan rarely sees tomorrow.
- **Static methods as a staging area.** Park new logic in statics; when several
  share variables, that's the signal to extract a real class.
- **The carcass and the sprouts.** New tested classes/methods sprout around the
  carcasses of big untested classes; eventually you tire of sidestepping them and
  finally get them under test.
- **Get over the hump.** Teams that commit to "no change without a covering test"
  feel pain at first, then viscerally refuse to go back.

## Anti-patterns

- **Inline hacking under pressure** — adding code into all 10 call sites because
  "it'll be done by 5:00." Muddies methods, mingles responsibilities, spawns
  tempting temporaries that attract still more code.
- **Adding behavior straight into an existing method** just because it must run at
  the same time → temporal coupling; later you can't separate the concerns
  without a seam.
- **Using sprouts/wraps and forgetting them** — never returning to test the call
  site or fold the sprout back. The techniques are a beachhead, not a destination.
- **Over-decorating** — decorators wrapping decorators until navigation becomes
  onion-peeling. Use sparingly.
- **Wrapping for a name you'll regret** — renaming `pay()` to `dispatchPayment()`
  when that method also calculates pay; without a refactoring tool you're stuck
  with a misleading name.

## Code Examples

```java
// BEFORE — invasive inline change: duplicate-detection mingled with date posting
public void postEntries(List entries) {
    List entriesToAdd = new LinkedList();
    for (Iterator it = entries.iterator(); it.hasNext(); ) {
        Entry entry = (Entry)it.next();
        if (!transactionBundle.getListManager().hasEntry(entry)) {
            entry.postDate();
            entriesToAdd.add(entry);           // two concerns tangled
        }
    }
    transactionBundle.getListManager().add(entriesToAdd);
}

// AFTER — Sprout Method: duplicate removal is its own tested method
List uniqueEntries(List entries) {            // developed test-first (TDD)
    List result = new ArrayList();
    for (Iterator it = entries.iterator(); it.hasNext(); ) {
        Entry entry = (Entry)it.next();
        if (!transactionBundle.getListManager().hasEntry(entry)) {
            result.add(entry);
        }
    }
    return result;
}

public void postEntries(List entries) {
    List entriesToAdd = uniqueEntries(entries); // call the sprout
    for (Iterator it = entriesToAdd.iterator(); it.hasNext(); ) {
        Entry entry = (Entry)it.next();
        entry.postDate();
    }
    transactionBundle.getListManager().add(entriesToAdd);
}
```

- **What it demonstrates**: Sprout Method extracts genuinely new logic
  (`uniqueEntries`) into a small, TDD-tested method with a clean interface,
  leaving `postEntries` shorter and single-purpose even though `postEntries`
  itself never went under test. New code is tested; the seam is the method call.

## Worked Example

**Requirement:** every time `Employee.pay()` runs, write the employee's name to a
file for reporting software. There are no tests, and many clients call `pay()`.

**Tempting move (anti-pattern):** drop the file-write straight into `pay()`. It
"has to happen at the same time," so why not? Because it welds logging onto pay
via temporal coupling — later, when you need to pay without logging (or log
without paying), there's no seam to split them.

**Wrap Method (same-name form):**

```java
public class Employee {
    private void dispatchPayment() {          // old pay() body, renamed + private
        Money amount = new Money();
        for (Iterator it = timecards.iterator(); it.hasNext(); ) {
            Timecard card = (Timecard)it.next();
            if (payPeriod.contains(date)) {
                amount.add(card.getHours() * payRate);
            }
        }
        payDispatcher.pay(this, date, amount);
    }
    public void pay() {                        // same name + signature: clients unchanged
        logPayment();                          // new, TDD-tested behavior
        dispatchPayment();                     // delegate to old code
    }
    private void logPayment() { ... }          // developed test-first
}
```

Every existing caller of `pay()` keeps working, unaware of the change. `logPayment`
is new code written test-first. The seam is the new `pay()` method. Once you *do*
get tests around `Employee`, you'd clean up the forced name by extracting
`calculatePay()`, leaving a clear high-level algorithm:

```java
public void pay() {
    logPayment();
    Money amount = calculatePay();
    dispatchPayment(amount);
}
```

**When Wrap Method can't reach — escalate to Wrap Class:** suppose you can't even
instantiate `Employee` in a harness, or logging is genuinely a separate
responsibility. Use Extract Interface on `Employee`, then a decorator:

```java
class LoggingEmployee extends Employee {       // implements the extracted interface
    private Employee employee;
    public LoggingEmployee(Employee e) { employee = e; }
    public void pay() {
        logPayment();
        employee.pay();                         // delegate
    }
    private void logPayment() { ... }
}
```

Clients receive a `LoggingEmployee` and can't tell it's a wrapper — transparent,
nestable, and the new behavior lives entirely outside the existing class. If
logging is needed in just one place instead, skip the decorator and use a plain
`LoggingPayDispatcher` that holds an `Employee`, calls `pay()`, then logs.

**The judgment call:** Sprout Method when the existing method already reads as a
clear algorithm and you're adding a sub-step. Wrap Method when the new feature is
as important as the old work (you end up with a new top-level algorithm). Wrap
Class when the behavior is fully independent, or the class is too big to make
worse and you want to plant a stake in the ground for later.

## Key Takeaways

1. **Pay now or pay more later** — under time pressure the cheap-looking inline
   hack usually costs more; and because changes cluster, the payoff for testing
   comes sooner than you fear.
2. **Prefer fresh, tested code over inline edits.** When you can't get the class
   under test now, formulate the change as new code and call it from the old code.
3. **Sprout when adding to a class you can touch; Wrap when adding around it.**
   Sprout grows the method/adds a class; Wrap leaves existing methods the same
   size and manufactures a seam.
4. **Decide by intent.** Sprout Method = clear sub-step; Wrap Method = co-equal new
   feature; Sprout/Wrap Class = can't instantiate the class, or it's a distinct
   new responsibility, or the class is too big to worsen.
5. **These techniques cover the new code, not its callers.** Use caution — the
   call site stays untested until you come back and break its dependencies.
6. **Leave markers, not litter.** A sprout or wrapper is a beachhead; the win comes
   when you later return, characterize the carcass, and fold the pieces back in.

## Connects To

- **Ch 4 (Seams)**: Wrap Method and Wrap Class create seams + enabling points
  where the untested code had none.
- **Ch 5 (Tools)**: TDD drives every sprout/wrap; mock/fake frameworks and
  refactoring tools (Extract Method) make the cleanup safe.
- **Ch 7 (It Takes Forever to Make a Change)**: Sprout Class's C++ header-isolation
  advantage ties into build/dependency pain.
- **Ch 8 (How Do I Add a Feature?)**: deepens the feature-addition toolkit beyond
  these four "no-test-on-the-caller" techniques.
- **Ch 9 / Ch 10 (Can't get this class/method into a harness)**: the prerequisite
  problems that push you toward Sprout Class and Wrap Class in the first place.
- **Ch 20 (This Class Is Too Big)**: where the wrapped/sprouted-around carcasses
  finally get decomposed.
- **Ch 25 (Dependency-Breaking Techniques)**: Extract Interface, Extract
  Implementer, Pass Null, Preserve Signatures — the named moves used above.
