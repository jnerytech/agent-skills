# Chapter 1: Bloaters (Code Smells)

## Core Idea
Bloaters are code, methods, and classes grown to gargantuan size over time. They accumulate quietly — nobody removes anything. Attack them while small.

## Smells & Their Cures
- **Long Method**: A method with too many lines. Rule of thumb: **anything over ~10 lines should make you ask questions.** "It's just two more lines" is how spaghetti is born.
  - Cure: `Extract Method`. If local vars block extraction → `Replace Temp with Query`, `Introduce Parameter Object`, `Preserve Whole Object`. If still stuck → `Replace Method with Method Object`. Conditionals → `Decompose Conditional`; loops → `Extract Method`.
- **Large Class**: A class with too many fields/methods/lines — wearing too many hats.
  - Cure: `Extract Class` (spin off cohesive behavior), `Extract Subclass` (behavior used rarely / done differently), `Extract Interface` (list operations clients use), `Duplicate Observed Data` (move GUI data to a domain object).
- **Primitive Obsession**: Primitives used instead of small objects (currency, ranges, phone strings); constants coding info (`USER_ADMIN_ROLE = 1`); string constants as array field-name indices.
  - Cure: group fields → `Replace Data Value with Object`; params → `Introduce Parameter Object` / `Preserve Whole Object`; coded data → `Replace Type Code with Class/Subclasses/State-Strategy`; arrays → `Replace Array with Object`.
- **Long Parameter List**: More than 3–4 parameters.
  - Cure: args that are method results of another object → `Replace Parameter with Method Call`; a group from one object → `Preserve Whole Object`; unrelated data group → `Introduce Parameter Object`.
- **Data Clumps**: Same group of variables recurring (e.g. DB connection params). **Test: delete one value — if the rest stop making sense, it's a clump.**
  - Cure: fields → `Extract Class`; params → `Introduce Parameter Object`; passing them on → `Preserve Whole Object`.

## Mental Models
- Use **the ~10-line trigger** as a tripwire for Long Method — length, not correctness, is the signal.
- Think of Primitive Obsession as **a class waiting to be born**: the primitive already has behavior + associated data scattered around it.
- Use **the delete-one-value test** to confirm a Data Clump before extracting.
- "**If you feel the need to comment inside a method, extract that code into a named method instead.**"

## Anti-patterns
- **Padding an existing method** because making a new one "feels harder" mentally — the real cost is the unreadable beast you create.
- **Over-splitting for performance fears**: the cost of extra method calls is almost always negligible; clean code reveals *real* optimization opportunities.

## Worked Example (Long Method → Extract Method)
```java
void printOwing() {
    printBanner();
    // Print details.
    System.out.println("name: " + name);
    System.out.println("amount: " + getOutstanding());
}
```
→ extract the commented block into a named method:
```java
void printOwing() {
    printBanner();
    printDetails(getOutstanding());
}
void printDetails(double outstanding) {
    System.out.println("name: " + name);
    System.out.println("amount: " + outstanding);
}
```
The comment became the method name; the body reads itself.

## When to Ignore
- **Long Parameter List**: keep params if removing them creates unwanted dependency between classes (e.g. would force passing a whole object and coupling the two).
- **Data Clumps**: passing a whole object instead of primitives can create an undesirable dependency.

## Key Takeaways
1. Length is a smell by itself — extract aggressively; call overhead rarely matters.
2. Primitive Obsession and Data Clumps both resolve into *new small classes* that hold data + behavior together.
3. Long Parameter Lists shrink by passing objects (`Preserve Whole Object`, `Introduce Parameter Object`), not more primitives.
4. Bloaters are cumulative — refactor early or pay compound interest.

## Connects To
- **Ch 6**: `Extract Method`, `Replace Method with Method Object` cure Long Method.
- **Ch 7**: `Extract Class` cures Large Class / Data Clumps.
- **Ch 8**: `Replace Type Code with *`, `Replace Data Value with Object` cure Primitive Obsession.
- **Ch 10**: `Introduce Parameter Object`, `Preserve Whole Object`, `Replace Parameter with Method Call` cure Long Parameter List.
