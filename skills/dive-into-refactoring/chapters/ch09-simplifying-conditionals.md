# Chapter 9: Simplifying Conditional Expressions (Refactoring Techniques)

## Core Idea
Conditional logic grows tangled over time. These techniques flatten it, name it, deduplicate it, and — best of all — replace it with polymorphism.

## Refactorings
- **Decompose Conditional**: A complex `if/else`/`switch` → extract the condition, the `then`, and the `else` into named methods (`isSummer(date)`, `summerCharge(quantity)`).
- **Consolidate Conditional Expression**: Multiple conditionals with the **same result** → combine into one expression (nested → `and`, consecutive → `or`), then `Extract Method` to name it. Precondition: no side effects.
- **Consolidate Duplicate Conditional Fragments**: Identical code in **all branches** → move it out (before if at start, after if at end).
- **Remove Control Flag**: A boolean flag steering loop/flow → replace with `break`, `continue`, or `return`. Control flags are an obsolete single-exit relic.
- **Replace Nested Conditional with Guard Clauses**: Deeply nested conditionals (the rightward "arrow of doom") → isolate special/edge cases as **guard clauses** that return early, producing a flat list. Rid side effects first (`Separate Query from Modifier`).
- **Replace Conditional with Polymorphism**: A conditional branching on **type or property** → a subclass per branch overriding a shared method; the conditional vanishes. Follows **Tell-Don't-Ask** and **Open/Closed**. Needs a class hierarchy first (build via `Replace Type Code with Subclasses` / `State-Strategy`).
- **Introduce Null Object**: Many `null` checks → return a **null object** with default behavior and an `isNull()` method; polymorphism replaces the checks. *Drawback:* another class. Implements the Null Object pattern.
- **Introduce Assertion**: Code assumes a condition holds → make it explicit with an assertion (live documentation). Assertions must not change behavior; don't over-assert — only conditions required for correctness; prefer an exception when user/system can trigger and handle it.

## Mental Models
- **Guard clauses flatten the arrow of doom** — handle edge cases up front and return; keep the happy path un-nested.
- **Tell-Don't-Ask**: instead of interrogating an object's type/state and branching, tell it what to do and let polymorphism decide (Replace Conditional with Polymorphism).
- **Consolidate before you extract**: merge same-destination conditionals, then name the combined check.

## Anti-patterns
- **Control flags** with single-entry/single-exit dogma — modern flow operators (`break`/`return`) read better.
- **Nested `if` pyramids** where the normal path is invisible.
- **Exceptions used as flow control** (see Ch 10 `Replace Exception with Test`).

## Worked Examples
**Guard Clauses:**
```java
public double getPayAmount() {
    if (isDead)      return deadAmount();
    if (isSeparated) return separatedAmount();
    if (isRetired)   return retiredAmount();
    return normalPayAmount();
}
```
**Replace Conditional with Polymorphism:**
```java
abstract class Bird { abstract double getSpeed(); }
class European extends Bird { double getSpeed(){ return getBaseSpeed(); } }
class African extends Bird  { double getSpeed(){ return getBaseSpeed() - getLoadFactor()*numberOfCoconuts; } }
class NorwegianBlue extends Bird { double getSpeed(){ return isNailed ? 0 : getBaseSpeed(voltage); } }
// client: speed = bird.getSpeed();
```
**Introduce Null Object:**
```java
class NullCustomer extends Customer {
    boolean isNull() { return true; }
    Plan getPlan() { return new NullPlan(); }
}
customer = (order.customer != null) ? order.customer : new NullCustomer();
plan = customer.getPlan();  // no null check needed
```

## Key Takeaways
1. Flatten nesting with guard clauses; name conditions with Decompose/Consolidate.
2. Replace type/property switches with polymorphism (Tell-Don't-Ask, Open/Closed).
3. Null Object erases scattered null checks via a default-behavior subclass.
4. Assertions document assumptions without altering behavior.

## Connects To
- **Ch 2**: cures Switch Statements; Null Object also cures Temporary Field.
- **Ch 6**: built on `Extract Method`; `Separate Query from Modifier` clears side effects first.
- **Ch 8**: polymorphism cure needs a hierarchy from `Replace Type Code with Subclasses / State-Strategy`.
