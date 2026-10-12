# Chapter 24: TEMPLATE METHOD

## Core Idea
Template Method is a behavioral pattern that defines the skeleton of an algorithm in a superclass but lets subclasses override specific steps without changing the algorithm's overall structure.

## Frameworks Introduced
- **Template Method**: Break an algorithm into steps (methods), call them in fixed order inside one "template method" in the base class; subclasses override individual steps but not the template method itself.
  - When to use: when clients should extend only particular steps of an algorithm, not its structure; when several classes contain almost identical algorithms differing only in minor steps (to eliminate duplication).
  - How: (1) break the algorithm into steps; (2) create the abstract base class with the template method (consider making it `final`) plus abstract step methods; (3) give some steps default implementations; (4) add hooks between crucial steps; (5) create a concrete subclass per variation, implementing abstract steps and overriding optional ones.

## Key Concepts
- **Abstract Class**: declares the step methods and the template method that calls them in order.
- **Template method**: the fixed-order sequence of step calls; subclasses must not override it.
- **Abstract step**: a step every subclass must implement.
- **Optional step**: has a default implementation but can be overridden.
- **Hook**: an optional step with an empty body; placed before/after crucial steps as an extension point; the algorithm works even if it isn't overridden.
- **Concrete Class**: overrides steps but keeps the template method intact.

## Mental Models
- **Real-World Analogy**: Mass housing construction — a standard architectural plan with extension points (foundation, framing, walls, plumbing, wiring) that owners can slightly adjust to make each house a little different.
- Think of the template method as a recipe with fixed steps where you may customize a few ingredients.

## Anti-patterns
- **Overriding the template method itself**: breaks the guaranteed structure — only override steps.
- **Suppressing a default step in a subclass**: may violate the Liskov Substitution Principle.
- **Too many steps**: template methods get harder to maintain as step count grows.

## Code Examples
```
class GameAI is
    // The template method defines the skeleton — not overridden.
    method turn() is
        collectResources()
        buildStructures()
        buildUnits()
        attack()

    method collectResources() is        // default step
        foreach (s in this.builtStructures) do s.collect()

    abstract method buildStructures()   // abstract steps
    abstract method buildUnits()

class OrcsAI extends GameAI is
    method buildStructures() is /* build farms, barracks, stronghold */
    method buildUnits() is /* build peons/grunts */

class MonstersAI extends GameAI is
    method collectResources() is // override default: do nothing
    method buildStructures() is  // do nothing
```
- **What it demonstrates**: `turn()` fixes the AI algorithm; each race subclass overrides only the steps it needs (Monsters even neutralize default steps).

## Reference Tables
| Pros | Cons |
|------|------|
| Clients override only certain parts of a large algorithm | Clients may be limited by the provided skeleton |
| Pull duplicate code up into a superclass | Suppressing a default step may break LSP |
| | Many steps make template methods hard to maintain |

## Worked Example
A data-mining app extracts data uniformly from DOC, then CSV, then PDF files. The three parser classes share nearly identical data-processing/analysis code but differ in file open/close and extract/parse logic; client code is full of conditionals choosing a parser. Template Method defines a base class whose template method calls steps in order: open file, extract data, parse data, analyze data, send report, close file. The format-specific steps stay abstract (per subclass); the identical analyze/report steps move up to the base class. A common base also lets client code use polymorphism instead of conditionals.

## Key Takeaways
1. The base class owns the algorithm structure; subclasses fill in steps.
2. Steps come in three flavors: abstract (mandatory), optional (default, overridable), and hooks (empty extension points).
3. Make the template method `final` so subclasses can't break the structure.
4. The pattern eliminates duplication by pulling shared steps up.
5. It works at the class/compile-time level via inheritance — behavior is static.

## Connects To
- **Factory Method**: a specialization of Template Method; a Factory Method can also serve as a step within a larger Template Method.
- **Strategy**: inheritance/static (Template Method) vs. composition/runtime (Strategy) for varying parts of behavior.
