# Chapter 6: Composing Methods (Refactoring Techniques)

## Core Idea
Long methods are the root of most evil — their tangled internals hide logic. These techniques streamline methods, kill duplication, and pave the way for later refactorings.

## Refactorings
- **Extract Method**: Group a code fragment into a named method; replace with a call. Name for *purpose* (`printDetails`), not how. Foundation of most other refactorings. *Anti:* Inline Method.
- **Inline Method**: When the body is more obvious than the method, replace calls with the body and delete the method. Guard: don't inline if redefined in subclasses. *Anti:* Extract Method.
- **Extract Variable**: Put a complex expression (or parts) into self-explanatory `final` variables. First step toward Extract Method. *Drawback:* extracted sub-conditions defeat short-circuit evaluation — both operands now always run (watch perf on heavy calls). *Anti:* Inline Temp.
- **Inline Temp**: A temp assigned a simple expression → replace refs with the expression. Almost never done alone; enables Replace Temp with Query / Extract Method. *Drawback:* keep the temp if it caches an expensive call. *Anti:* Extract Variable.
- **Replace Temp with Query**: Move an expression into a method; query it instead of storing. Precondition: assigned exactly once (else `Split Temporary Variable` first); the query must not change object state (else `Separate Query from Modifier`).
- **Split Temporary Variable**: One variable reused for different values → one variable per responsibility, each `final` with a meaningful name (except loop counters).
- **Remove Assignments to Parameters**: Value assigned to a param inside the body → use a local variable instead. By-reference params can leak changes back to the caller; multiple assignments obscure the param's meaning.
- **Replace Method with Method Object**: Long method whose intertwined locals block Extract Method → turn the method into its own class where locals become fields; then split freely. *Drawback:* adds a class.
- **Substitute Algorithm**: Replace a method body wholesale with a cleaner algorithm. Simplify first (Extract Method), swap, compare test results.

## Mental Models
- **Extract Method is the gateway drug** — most refactorings begin with it.
- Use **one variable, one responsibility** (Split Temporary Variable; Remove Assignments to Parameters).
- Prefer **queries over temps** (Replace Temp with Query) so expressions are reusable and Extract Method becomes possible.
- Reach for **Method Object** only when locals are too tangled to Extract Method.

## Anti-patterns
- **Reusing one temp for unrelated values** — forces you to recheck every use before any change.
- **Assigning to parameters** — silent by-reference side effects.

## Worked Examples
**Replace Temp with Query:**
```java
double calculateTotal() {
    double basePrice = quantity * itemPrice;
    if (basePrice > 1000) return basePrice * 0.95;
    else return basePrice * 0.98;
}
```
→
```java
double calculateTotal() {
    if (basePrice() > 1000) return basePrice() * 0.95;
    else return basePrice() * 0.98;
}
double basePrice() { return quantity * itemPrice; }
```
**Replace Method with Method Object:**
```java
class Order {
    public double price() { return new PriceCalculator(this).compute(); }
}
class PriceCalculator {
    private double primaryBasePrice, secondaryBasePrice, tertiaryBasePrice;
    public PriceCalculator(Order order) { /* copy data */ }
    public double compute() { /* long computation, now splittable */ }
}
```

## Key Takeaways
1. Extract Method underlies nearly everything — extract early and name well.
2. Tame temps: split by responsibility, inline the trivial, promote to queries.
3. Never assign to parameters; use a local.
4. Method Object rescues methods too tangled to extract; Substitute Algorithm replaces the whole thing.

## Connects To
- **Ch 1**: cures Long Method, Duplicate Code, Comments.
- **Ch 9**: `Separate Query from Modifier` guards Replace Temp with Query; `Decompose Conditional` builds on Extract Method.
- **Ch 10 / Ch 11**: Extract Method feeds `Introduce Parameter Object`, `Parameterize Method`, `Form Template Method`.
