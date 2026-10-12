# Chapter 4: Dispensables (Code Smells)

## Core Idea
A dispensable is something pointless whose absence makes code cleaner, more efficient, and easier to understand. Delete or absorb it.

## Smells & Their Cures
- **Comments**: A method filled with explanatory comments. **Comments are often deodorant masking fishy code. The best comment is a good method/class name.**
  - Cure: complex expression → `Extract Variable`; a commented block → `Extract Method` (name it from the comment); already-extracted but still needs explaining → `Rename Method`; a rule/state assumption → `Introduce Assertion`.
- **Duplicate Code**: Two fragments look almost identical.
  - Cure (by location): same class → `Extract Method`; sibling subclasses → `Extract Method` + `Pull Up Field`, or `Pull Up Constructor Body`, or `Form Template Method` (similar-not-identical), or `Substitute Algorithm` (same goal, different algo); unrelated classes → `Extract Superclass` or `Extract Class`; duplicated conditionals → `Consolidate Conditional Expression`; identical code in all branches → `Consolidate Duplicate Conditional Fragments`.
- **Lazy Class**: A class that doesn't do enough to justify its maintenance cost.
  - Cure: near-useless → `Inline Class`; thin subclass → `Collapse Hierarchy`.
- **Data Class**: Only fields + crude getters/setters; a dumb container that can't operate on its own data.
  - Cure: `Encapsulate Field` (public fields), `Encapsulate Collection` (collections); migrate client behavior in via `Move Method` + `Extract Method`; then tighten access with `Remove Setting Method` + `Hide Method`.
- **Dead Code**: A variable/param/field/method/class no longer used.
  - Cure: delete it; unneeded class → `Inline Class` / `Collapse Hierarchy`; unused param → `Remove Parameter`. **A good IDE finds it fastest.**
- **Speculative Generality**: Unused class/method/field/param created "just in case" for a future that never came.
  - Cure: abstract classes → `Collapse Hierarchy`; needless delegation → `Inline Class`; unused methods → `Inline Method`; unused params → `Remove Parameter`; unused fields → delete.

## Mental Models
- Treat a **comment as a rename/extract opportunity**: name the thing the comment describes.
- A **Data Class is anemic** — "the true power of objects is behavior on their own data." Pull behavior toward the data.
- YAGNI: **Speculative Generality** is premature abstraction; remove it until a real need appears.

## Anti-patterns
- **Writing comments to explain bad structure** instead of fixing the structure.
- **Building framework-style extensibility** in application code before it's needed.

## Worked Example (Comment → Extract Method + Extract Variable)
```java
// If the platform is Mac and browser is IE and initialized and resized...
if ((platform.toUpperCase().indexOf("MAC") > -1) &&
    (browser.toUpperCase().indexOf("IE") > -1) &&
    wasInitialized() && resize > 0) { ... }
```
→ `Extract Variable` the sub-conditions into `isMacOs`, `isIE`, `wasResized`; the comment disappears because the code now reads like prose.

## When to Ignore
- **Comments**: keep them to explain *why* (not what), or genuinely complex algorithms after all simplification fails.
- **Duplicate Code**: rare cases where merging makes code *less* obvious.
- **Speculative Generality**: framework code legitimately needs unused-by-you features; don't delete elements only used by unit tests.

## Key Takeaways
1. Comments that explain *what* are a smell; convert them to names via Extract/Rename.
2. Duplicate Code's cure depends entirely on *where* the duplicates live (same class / siblings / unrelated).
3. Data Classes should grow behavior; Lazy/Dead/Speculative code should be deleted or inlined.
4. Delete unused elements — but check tests and framework contracts first.

## Connects To
- **Ch 6**: `Extract Method`, `Extract Variable`, `Inline Method`, `Substitute Algorithm`.
- **Ch 7**: `Inline Class`, `Move Method` for Data/Lazy classes.
- **Ch 9**: `Consolidate Conditional Expression` / `...Duplicate Conditional Fragments` for conditional duplication; `Introduce Assertion` for comment-encoded rules.
- **Ch 11**: `Collapse Hierarchy`, `Form Template Method`, `Pull Up *`.
