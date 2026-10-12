# Chapter 1: Introduction

## Core Idea
Framework guidelines exist to create a shared language between framework authors and the developers who consume them, so that APIs communicate *how they are meant to be used* through their shape alone (e.g., exposing something as a property vs. a method conveys intent). Consistency is the through-line of the whole book.

## Frameworks Introduced
- **The 7 Qualities of a Well-Designed Framework**: the authors' checklist for what "good" means.
  - When to use: as design north-star and review rubric for any reusable API surface.
  - How: a well-designed framework is Simple, Expensive (to design), Full of Trade-offs, Borrows from the Past, Designed to Evolve, Integrated, and Consistent.

## Key Concepts
- **Framework**: a set of reusable APIs (types + members) that provide most of an application's pieces, to be customized and connected — not written from scratch.
- **Guideline vs. rule**: guidelines guide trade-off decisions; they are not absolute laws, because design is about trade-offs.
- **Consistency**: the single most important productivity factor — lets knowledge transfer between parts of a framework.
- **"You can always add; you cannot ever remove"**: the asymmetry that makes simplicity a must-have.
- **Addition through subtraction**: removing/never-adding features can make developers *more* productive (fewer concepts).

## Mental Models
- **Think of API design as language design** — every naming and shape choice teaches the caller how to use it.
- **When schedule pressure hits, cut features, not simplicity** — ship less, get the design right next release.
- **Client-first programming (Chris Sells' test)**: describe what the library does, ask several devs to write the client code they *expect*; if the majority converge on something unlike yours, they're right — redesign. The authors design by writing the client code they wish they could write, then implement to match.

## Anti-patterns
- **Framework = whatever's left public after implementation**: API surface must be an explicit, distinct, planned activity — not a side effect of coding.
- **Mixing implementer and framework-designer responsibilities**: leaks implementation details into the public surface.
- **Innovating in API shape**: make the API "as boring as possible" — the functionality is what should be interesting, not the API.

## Key Takeaways
1. Consistency is the main theme of the book — chapters 3–5 carry the core consistency guidelines.
2. Simplicity is a feature; when in doubt, cut and defer. Addition is cheap, removal is impossible.
3. Good framework design is *expensive* and must be planned, staffed, and budgeted — including redesign after prototyping.
4. Every design is trade-offs; if you think you have none, you're missing something big.
5. Borrow proven designs; reserve novelty for cross-cutting areas and use with utmost caution.
6. Design to evolve — always ask how a decision affects future backward-compatible growth.

## Connects To
- **Ch 2**: turns these qualities into concrete design principles (Pit of Success, scenario-driven design).
- **Ch 3–5**: the core consistency guidelines (naming, type, member design).
- **Ch 9**: proven common design patterns ("borrow from the past").
