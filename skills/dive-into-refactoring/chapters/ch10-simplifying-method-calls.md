# Chapter 10: Simplifying Method Calls (Refactoring Techniques)

## Core Idea
Make method calls simpler and clearer — better names, right parameters, separated concerns, proper errors. This simplifies the interfaces *between* classes.

## Refactorings (safe-rename mechanic)
Most of the signature-changing ones share a mechanic: **create the new method by copying the old, point the old at the new, redirect all callers, then delete the old — but if it's public API, mark it deprecated instead of deleting.**

- **Rename Method**: Name doesn't describe behavior → rename (`createOrder`, `renderCustomerInfo`). *Cures:* Alternative Classes with Different Interfaces, Comments.
- **Add Parameter**: Method lacks needed data → add a parameter. Prefer a param over a field for occasional/changing data. *Drawback:* feeds Long Parameter List. *Anti:* Remove Parameter.
- **Remove Parameter**: Unused parameter → remove it. Don't remove if used by a sub/superclass override. *Cures:* Speculative Generality. *Anti:* Add Parameter.
- **Separate Query from Modifier**: A method both returns a value **and** mutates → split into a pure query + a modifier. Implements **CQRS** (Command-Query Separation). Side effects only matter for *visible* state changes.
- **Parameterize Method**: Several near-identical methods differing only in a value → one method taking that value as a parameter. *Cures:* Duplicate Code. *Anti:* Replace Parameter with Explicit Methods.
- **Replace Parameter with Explicit Methods**: A method branches on a parameter's value → one explicit method per branch (`setHeight`/`setWidth` vs `setValue(name,val)`). Use when variants are few and rarely added. *Anti:* Parameterize Method.
- **Preserve Whole Object**: You extract several values from an object then pass them as params → pass the whole object. *Cures:* Long Parameter List, Data Clumps. *Drawback:* couples method to that object's interface.
- **Replace Parameter with Method Call**: A param is computed then passed, but the callee could compute it itself → drop the param, call the query inside. Precondition: the value doesn't depend on the caller's other params.
- **Introduce Parameter Object**: A recurring group of params → one **immutable** parameter object; consider moving related behavior onto it (else it smells of Data Class). *Cures:* Long Parameter List, Data Clumps, Primitive Obsession.
- **Remove Setting Method**: A field should be set only at creation → delete its setter; set only in the constructor. Enables immutability.
- **Hide Method**: A method unused outside its class/hierarchy → make it private/protected. Underscores the public interface.
- **Replace Constructor with Factory Method**: A constructor doing more than field-setting → a static factory (better name, can return subclasses or cached objects). Pairs with `Replace Type Code with Subclasses`, `Change Value to Reference`. Implements Factory Method.
- **Replace Error Code with Exception**: A method returns a special error value → throw an exception. Frees callers from error-code conditionals; error codes can't be returned from constructors. *Drawback:* don't use exceptions for normal flow.
- **Replace Exception with Test**: You throw where a simple pre-check would do → test the condition first. Exceptions are for real errors, not avoidable conditions ("read the warning sign instead of triggering the mine").

## Mental Models
- **Command-Query Separation**: a method either *answers a question* (query, no side effects, callable freely) or *changes state* (command) — never both.
- **Pass objects, not piles of primitives** (Preserve Whole Object, Introduce Parameter Object) to fight Long Parameter Lists.
- **Exceptions signal errors, not control flow** — precede with a test when the condition is checkable.
- **Factory methods > constructors** when creation needs a name, subclass selection, or object reuse.

## Anti-patterns
- **Query methods with hidden side effects** — callers can't trust repeated calls.
- **Boolean/flag parameters** that fork behavior (`setValue("engineEnabled", true)`) vs explicit `startEngine()`.
- **Try/catch as an `if`** — abusing exceptions for expected conditions.

## Worked Examples
**Preserve Whole Object:**
```java
// before
int low = daysTempRange.getLow();
int high = daysTempRange.getHigh();
boolean withinPlan = plan.withinRange(low, high);
// after
boolean withinPlan = plan.withinRange(daysTempRange);
```
**Replace Error Code with Exception:**
```java
void withdraw(int amount) throws BalanceException {
    if (amount > _balance) throw new BalanceException();
    balance -= amount;
}
```
**Replace Exception with Test:**
```java
double getValueForPeriod(int periodNumber) {
    if (periodNumber >= values.length) return 0;
    return values[periodNumber];
}
```

## Key Takeaways
1. Use the copy-redirect-deprecate mechanic for safe signature changes; never break public API abruptly.
2. Separate queries from modifiers (CQRS) so reads are side-effect-free.
3. Bundle params into whole objects / parameter objects; drop computable and unused params.
4. Exceptions for errors, tests for avoidable conditions; factory methods for rich creation.

## Connects To
- **Ch 1**: cures Long Parameter List (Preserve Whole Object, Introduce Parameter Object, Replace Parameter with Method Call).
- **Ch 8**: `Replace Constructor with Factory Method` supports Change Value to Reference & type-code cures.
- **Ch 9**: `Separate Query from Modifier` prepares Guard Clauses / Replace Temp with Query.
