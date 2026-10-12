# Chapter 7: Moving Features Between Objects (Refactoring Techniques)

## Core Idea
Even with badly distributed responsibilities, there's hope: safely move functionality between classes, create new classes, and hide implementation details.

## Refactorings
- **Move Method**: A method used more in another class → recreate it there, turn the original into a delegating reference or remove it. Increases cohesion / cuts dependency. Watch for super/subclass declarations. *Cures:* Shotgun Surgery, Feature Envy, Switch Statements, Message Chains, Inappropriate Intimacy.
- **Move Field**: A field used more elsewhere → create it (with accessors) in the target, redirect all users. **Rule of thumb: put a field where the methods that use it live.** Make it private first (`Encapsulate Field`) to ease the move.
- **Extract Class**: One class doing the work of two → create a new class, move the relevant fields/methods (`Move Field` + `Move Method`, private methods first, test after each). Serves the **Single Responsibility Principle**. Prefer a unidirectional relationship. *Anti:* Inline Class.
- **Inline Class**: A class that does almost nothing → fold its features into another and delete it. *Anti:* Extract Class.
- **Hide Delegate**: Client calls `server.getDelegate().method()` → add a delegating method on the server so the client no longer knows the delegate. Reduces coupling. *Drawback:* too many delegating methods → Middle Man. *Anti:* Remove Middle Man.
- **Remove Middle Man**: A class over-delegates → expose a getter for the delegate and let clients call it directly. *Anti:* Hide Delegate.
- **Introduce Foreign Method**: A utility class you can't modify lacks a method → add it to the *client* class, passing the utility object as an argument. Tag it "Foreign method" in comments.
- **Introduce Local Extension**: You need several methods on an unmodifiable class → create a subclass or wrapper holding the new methods, plus a converting constructor.

## Mental Models
- **Cohesion compass**: put behavior (methods) and state (fields) where they're most used.
- Extract Class ⇄ Inline Class and Hide Delegate ⇄ Remove Middle Man are **paired opposites** — you'll oscillate to find the right balance.
- **Foreign Method** = one-off; **Local Extension** = when several such methods pile up (wrap or subclass instead).

## Anti-patterns
- **Overdoing Extract Class** until classes are anemic → reach back with Inline Class.
- **Scattering utility helpers** across clients when a Local Extension would consolidate them.

## Worked Example (Introduce Foreign Method)
```java
class Report {
    void sendReport() {
        Date nextDay = new Date(previousEnd.getYear(),
            previousEnd.getMonth(), previousEnd.getDate() + 1);
        // ...
    }
}
```
Can't add `nextDay` to `Date` → add a foreign method to the client:
```java
class Report {
    void sendReport() {
        Date newStart = nextDay(previousEnd);
        // ...
    }
    private static Date nextDay(Date arg) {
        return new Date(arg.getYear(), arg.getMonth(), arg.getDate() + 1);
    }
}
```

## Key Takeaways
1. Move methods/fields toward the data they use most — cohesion up, coupling down.
2. Extract/Inline Class and Hide-Delegate/Remove-Middle-Man are inverses; use them to tune structure.
3. Move fields with `Encapsulate Field` first, private methods first, test after each move.
4. Unmodifiable library? Foreign Method for one, Local Extension for many.

## Connects To
- **Ch 1**: `Extract Class` cures Large Class, Data Clumps, Primitive Obsession.
- **Ch 3 / Ch 5**: primary cures for Shotgun Surgery, Feature Envy, Message Chains, Inappropriate Intimacy, Middle Man, Incomplete Library Class.
- **Ch 8**: `Encapsulate Field` supports Move Field; `Duplicate Observed Data` splits GUI/domain.
