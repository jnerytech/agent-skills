# Chapter 5: Couplers & Other Smells (Code Smells)

## Core Idea
Coupler smells come from excessive coupling between classes — or from over-correcting coupling into excessive delegation. Good classes know as little about each other as possible.

## Smells & Their Cures
- **Feature Envy**: A method accesses another object's data more than its own. Often appears after fields move to a data class.
  - Cure: `Move Method` (whole method belongs elsewhere); `Extract Method` on just the envious part, then move it. If it envies several classes, place it with the class holding *most* of the data used. **Rule: things that change together belong together.**
- **Inappropriate Intimacy**: One class digs into another's internal fields/methods. Classes spending too much time together.
  - Cure: `Move Method` + `Move Field` to relocate the intimate parts; `Extract Class` + `Hide Delegate` to make the relationship official; mutual dependence → `Change Bidirectional Association to Unidirectional`; subclass↔superclass intimacy → `Replace Delegation with Inheritance`.
- **Message Chains**: Calls like `a->b()->c()->d()`. The client depends on the whole navigation path; any structural change breaks it.
  - Cure: `Hide Delegate`; or `Extract Method` the end functionality + `Move Method` it toward the chain's start.
- **Middle Man**: A class that does nothing but delegate. Often the result of over-eager Message-Chain removal.
  - Cure: `Remove Middle Man` — let clients call the real object directly.
- **Incomplete Library Class** *(Other Smells)*: A read-only library lacks methods you need and you can't modify it.
  - Cure: a few methods → `Introduce Foreign Method`; bigger changes → `Introduce Local Extension` (subclass or wrapper).

## Mental Models
- **"Things that change together belong together."** Data and the code that uses it should live in the same class — the antidote to Feature Envy.
- Message Chains vs Middle Man are a **balance**: hide delegation to kill chains, but over-hiding creates middle men. Tune, don't max out.
- **Server / Delegate** terminology: *server* = object the client accesses directly; *delegate* = end object with the real functionality. `Hide Delegate` and `Remove Middle Man` are exact inverses.

## Anti-patterns
- **Over-aggressive delegate hiding** → you can no longer see where work happens (Middle Man).
- **Reaching through objects** (`a.getB().getC().doThing()`) coupling the client to a navigation path.

## Worked Example (Feature Envy → Move Method)
A `Customer.discountedPrice()` that only reads `Order.getTotal()`, `Order.getItems()`, `Order.getTax()` envies `Order`. Move the method onto `Order` (or `Extract Method` the envious slice and move just that), so behavior sits next to its data.

## When to Ignore
- **Feature Envy**: behavior is sometimes *deliberately* separated to swap it dynamically (Strategy, Visitor).
- **Message Chains**: don't over-hide into Middle Man territory.
- **Middle Man**: keep intentional middle men — dependency isolation, or patterns like Proxy / Decorator.
- **Incomplete Library Class**: extending a library adds upkeep when the library changes.

## Key Takeaways
1. Feature Envy → move behavior to where its data lives.
2. Inappropriate Intimacy → relocate shared parts, formalize with Hide Delegate, or break bidirectional links.
3. Message Chains and Middle Man are opposite over-corrections — aim for balance.
4. Can't edit a library? Extend it via Foreign Method (one-off) or Local Extension (many methods).

## Connects To
- **Ch 7**: `Move Method`, `Move Field`, `Extract Class`, `Hide Delegate`, `Remove Middle Man`, `Introduce Foreign Method`, `Introduce Local Extension`.
- **Ch 8**: `Change Bidirectional Association to Unidirectional`.
- **Ch 11**: `Replace Delegation with Inheritance`.
