# Patterns — Refactoring Techniques Catalog

Grouped by chapter category. Each: **When** / **How** / **Trade-off**.

## Composing Methods (Ch 6)
## Extract Method
**When:** a fragment can be grouped/named. **How:** copy to a named method, replace with a call, pass in needed locals. **Trade-off:** foundation of most refactorings; overhead negligible.
## Inline Method
**When:** body is clearer than the call. **How:** replace calls with body, delete method. **Trade-off:** don't inline if overridden.
## Extract Variable / Inline Temp
**When:** complex expression (extract) / trivial temp (inline). **How:** name sub-expressions in `final` vars, or replace temp with its expression. **Trade-off:** extracting sub-conditions defeats short-circuit eval.
## Replace Temp with Query
**When:** a temp holds an expression reused/reusable. **How:** move expression to a method, query it. **Trade-off:** minor perf cost; keep temp if caching an expensive call. Requires single assignment + no side effects.
## Split Temporary Variable / Remove Assignments to Parameters
**When:** one variable/param reused for multiple values. **How:** one variable per responsibility (`final`); use a local instead of the param. **Trade-off:** clarity over terseness.
## Replace Method with Method Object
**When:** tangled locals block Extract Method. **How:** promote method to a class, locals → fields, split freely. **Trade-off:** adds a class.
## Substitute Algorithm
**When:** a cleaner algorithm exists. **How:** simplify, swap body, compare test results. **Trade-off:** all-or-nothing rewrite.

## Moving Features Between Objects (Ch 7)
## Move Method / Move Field
**When:** used more in another class. **How:** recreate in target, redirect users; `Encapsulate Field` first for fields. **Trade-off:** raises cohesion, cuts coupling.
## Extract Class / Inline Class
**When:** one class does two jobs / a class does almost nothing. **How:** split via Move Field+Method (test each) / fold features in and delete. **Trade-off:** inverses — tune to balance.
## Hide Delegate / Remove Middle Man
**When:** client walks `server.getDelegate().m()` / a class over-delegates. **How:** add delegating method / expose delegate getter. **Trade-off:** inverses; too much hiding → Middle Man.
## Introduce Foreign Method / Local Extension
**When:** unmodifiable class lacks 1 method / many. **How:** add method to client passing the object / subclass or wrap it. **Trade-off:** foreign method sits in a suboptimal place; extension adds a class.

## Organizing Data (Ch 8)
## Self Encapsulate Field / Encapsulate Field / Encapsulate Collection
**When:** direct field access / public field / raw collection field. **How:** route through accessors; return read-only collections + add/remove methods. **Trade-off:** flexibility over slight verbosity; skip for perf-critical hot fields.
## Replace Data Value with Object / Replace Array with Object
**When:** a primitive/array grew data+behavior. **How:** move it into a named class with fields/accessors. **Trade-off:** cures Primitive Obsession.
## Change Value ⇄ Reference
**When:** many identical instances → one shared (value→ref) / costly reference → immutable (ref→value). **How:** factory + registry / remove setters + add equality. **Trade-off:** references harder; values must stay immutable.
## Replace Type Code with Class / Subclasses / State-Strategy
**When:** type code with no behavior / behavior + immutable / behavior + runtime-changing or hierarchy-blocked. **How:** type class / subclass-per-value + polymorphism / pluggable state object. **Trade-off:** progressively more classes.
## Replace Magic Number with Symbolic Constant
**When:** literal with hidden meaning. **How:** named `static final`. **Trade-off:** not for self-evident numbers.
## Replace Subclass with Fields
**When:** subclasses differ only by constant methods. **How:** fields in parent via factory + protected ctor. **Trade-off:** simpler hierarchy.
## Duplicate Observed Data
**When:** domain data trapped in GUI. **How:** split domain/GUI, sync via Observer. **Trade-off:** not for per-request web apps.
## Change Uni ⇄ Bidirectional Association
**When:** both sides need each other / one side stopped using the other. **How:** add reverse field (pick dominant) / drop unused link. **Trade-off:** bidirectional harder to maintain.

## Simplifying Conditional Expressions (Ch 9)
## Decompose / Consolidate Conditional / Consolidate Duplicate Fragments
**When:** complex / same-result / all-branch-duplicate conditionals. **How:** extract named methods / merge with and-or / hoist common code out. **Trade-off:** must be side-effect-free.
## Remove Control Flag / Replace Nested Conditional with Guard Clauses
**When:** boolean flag / nested arrow-of-doom. **How:** break/continue/return / early-return guards. **Trade-off:** flatter, clearer flow.
## Replace Conditional with Polymorphism
**When:** branch on type/property. **How:** subclass per branch overriding a method. **Trade-off:** needs a hierarchy; Tell-Don't-Ask, Open/Closed.
## Introduce Null Object / Introduce Assertion
**When:** many null checks / assumed condition. **How:** default-behavior subclass + isNull() / explicit assertion. **Trade-off:** extra class; don't over-assert.

## Simplifying Method Calls (Ch 10)
## Rename / Add Parameter / Remove Parameter
**How (shared):** copy old→new, redirect callers, delete (or deprecate if public API). **Trade-off:** Add feeds Long Parameter List.
## Separate Query from Modifier
**When:** a method returns *and* mutates. **How:** split query + modifier (CQRS). **Trade-off:** two calls where one was convenient.
## Parameterize Method ⇄ Replace Parameter with Explicit Methods
**When:** near-identical methods differ by a value / method branches on a param. **How:** unify with a param / split into explicit methods. **Trade-off:** inverses; balance count vs complexity.
## Preserve Whole Object / Introduce Parameter Object / Replace Parameter with Method Call
**When:** many values from one object / recurring param group / computable param. **How:** pass the object / an immutable param object / call the query inside. **Trade-off:** couples to interface; param object may smell of Data Class.
## Remove Setting Method / Hide Method
**When:** field set only at creation / method unused outside. **How:** delete setter / reduce visibility. **Trade-off:** enables immutability, tighter interface.
## Replace Constructor with Factory Method
**When:** constructor does more than set fields. **How:** static factory returning the (sub)object. **Trade-off:** better naming, subclass/cache returns; implements Factory Method.
## Replace Error Code with Exception ⇄ Replace Exception with Test
**When:** returns error code / throws where a test suffices. **How:** throw exception / pre-check condition. **Trade-off:** exceptions for real errors only, not flow control.

## Dealing with Generalization (Ch 11)
## Pull Up Field / Method / Constructor Body
**When:** duplication in sibling subclasses. **How:** move up (super(...) for constructors). **Trade-off:** ctor code must be at start.
## Push Down Method / Field
**When:** superclass member used by few subclasses. **How:** move down. **Trade-off:** cures Refused Bequest.
## Extract Subclass / Superclass / Interface
**When:** rare-case features / shared members / shared interface slice. **How:** new subclass / superclass (pull up) / interface. **Trade-off:** single-inheritance limits — compose for multiple axes; interface shares signatures not code.
## Collapse Hierarchy
**When:** subclass ≈ superclass. **How:** merge. **Trade-off:** watch Liskov with remaining subclasses.
## Form Template Method
**When:** subclasses share step order. **How:** skeleton + common steps up, differing steps abstract. **Trade-off:** Open/Closed; implements Template Method.
## Replace Inheritance ⇄ Delegation
**When:** subclass uses part of superclass (→delegation) / class delegates to all methods (→inheritance). **How:** field + delegate & drop inheritance / subclass & drop delegating methods. **Trade-off:** delegation = flexibility + boilerplate; inheritance only when *all* methods delegated (else Liskov break).
