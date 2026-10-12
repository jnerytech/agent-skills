# Chapter 2: Introduction to Patterns

## Core Idea
A design pattern is a typical, reusable solution to a commonly occurring design problem — a general concept you customize to your code, not a copy-paste snippet.

## Frameworks Introduced
- **Standard pattern description format**: the sections used to document a pattern formally so others can reproduce it.
  - When to use: when reading, comparing, or writing up any pattern.
  - How: capture Intent (problem + solution briefly), Motivation (deeper explanation), Structure (classes and relations), and a Code example; optionally applicability, implementation steps, and relations to other patterns.
- **Classification by intent**: three groups this book covers.
  - When to use: to choose where to look for a solution given the kind of problem you face.
  - How: Creational (object creation), Structural (assembling objects/classes into larger structures), Behavioral (communication and responsibilities between objects).
- **Classification by scale**: idioms → design patterns → architectural patterns.
  - When to use: to gauge how broad and language-dependent a solution is.
  - How: idioms are low-level and language-specific; design patterns are mid-level cross-language class arrangements; architectural patterns design whole applications in virtually any language.

## Key Concepts
- **Design pattern**: a customizable blueprint for solving a recurring design problem.
- **Pattern vs algorithm**: an algorithm is a fixed recipe of steps; a pattern is a high-level blueprint whose code can differ per program.
- **Idiom**: the most basic, low-level pattern, usually tied to one language.
- **Architectural pattern**: the most universal, high-level pattern, used to design an entire application's architecture.
- **Creational patterns**: provide object-creation mechanisms that increase flexibility and reuse.
- **Structural patterns**: assemble objects and classes into larger, still-flexible structures.
- **Behavioral patterns**: handle effective communication and assignment of responsibilities between objects.
- **GoF book**: *Design Patterns* (1995) by Gamma, Helm, Johnson, Vlissides — 23 OO patterns; the "Gang of Four."

## Mental Models
- Think of a **pattern as a blueprint and an algorithm as a cooking recipe**: the recipe fixes the steps; the blueprint fixes the result, leaving implementation order to you.
- Think of pattern scale **like road construction**: a small fix (traffic lights = idiom) vs a multi-level interchange (architectural pattern).

## Anti-patterns
- **Treating a pattern as copy-paste code**: a pattern is a concept, not an off-the-shelf function or library; implementations legitimately differ between programs.
- **Applying patterns dogmatically**: knowing names helps, but forcing patterns where unneeded adds complexity.

## Reference Tables
| Group | Purpose |
|---|---|
| Creational | Object creation mechanisms for flexibility and reuse |
| Structural | Assemble objects/classes into larger flexible structures |
| Behavioral | Effective communication and responsibility assignment between objects |

## Worked Example
Christopher Alexander introduced "patterns" in *A Pattern Language* (urban/building design: window heights, building levels, green areas). Four authors (Gamma, Vlissides, Johnson, Helm) applied the idea to programming in the 1995 GoF book, cataloging 23 patterns; the approach then spread far beyond OO design.

## Key Takeaways
1. Learn patterns as a toolkit of tried-and-tested solutions and a way to train OO design thinking.
2. Patterns give teams a shared vocabulary ("just use a Singleton") that speeds communication.
3. Locate solutions by intent: creational, structural, or behavioral.
4. Match the pattern's scale (idiom vs architectural) to the scope of your problem.
5. You can be a working programmer for years and still implement patterns unknowingly — naming them makes them reusable.

## Connects To
- **Ch 1**: pattern structures are expressed using OOP relations (association, composition, inheritance).
- **Ch 3**: most patterns in this book are built on the design principles and SOLID.
