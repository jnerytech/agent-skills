# Glossary — Dive Into Refactoring

**Alternative Classes with Different Interfaces** — smell: two classes do the same job with different method names (Ch 2).
**Anti-refactoring** — the inverse operation of a given refactoring (e.g. Extract Method ⇄ Inline Method).
**Bloaters** — smell family: code/methods/classes grown too large (Ch 1).
**Change Preventers** — smell family: one change forces edits in many places (Ch 3).
**Code Smell** — a surface sign of a deeper problem; the trigger for refactoring (Ch 1–5).
**Command-Query Separation (CQRS)** — a method should either return data (query) or change state (modifier), not both (Ch 10).
**Compose over Inherit** — prefer component objects (Strategy) to subclassing when variation has multiple axes (Ch 11).
**Comments** — smell: a method needing explanatory comments hides unclear code (Ch 4).
**Couplers** — smell family: excessive coupling between classes (Ch 5).
**Control Flag** — a boolean steering flow; replace with break/continue/return (Ch 9).
**Data Class** — smell: only fields + getters/setters, no behavior (Ch 4).
**Data Clumps** — smell: the same group of variables recurring together (Ch 1).
**Dead Code** — smell: an element no longer used (Ch 4).
**Delegate** — the end object holding the functionality the client needs (Ch 5, 7).
**Dispensables** — smell family: pointless code better removed (Ch 4).
**Divergent Change** — smell: many unrelated methods change in one class (Ch 3).
**Dominant class** — in a bidirectional association, the side owning association updates (Ch 8).
**Duplicate Code** — smell: near-identical fragments (Ch 4).
**Feature Envy** — smell: a method uses another object's data more than its own (Ch 5).
**Guard Clause** — an early-return check for an edge case, flattening nested conditionals (Ch 9).
**Inappropriate Intimacy** — smell: a class uses another's internals (Ch 5).
**Incomplete Library Class** — smell: an unmodifiable library lacks needed methods (Ch 5).
**Lazy Class** — smell: a class not doing enough to justify itself (Ch 4).
**Liskov Substitution Principle (LSP)** — a subclass must be usable wherever its superclass is; guides delegation-vs-inheritance choices (Ch 11).
**Long Method** — smell: too many lines (~10+ is suspect) (Ch 1).
**Long Parameter List** — smell: more than 3–4 parameters (Ch 1).
**Magic Number** — a literal number with hidden meaning (Ch 8).
**Message Chains** — smell: `a.b().c().d()` navigation coupling (Ch 5).
**Method Object** — a class created from a method so its locals become fields (Ch 6).
**Middle Man** — smell: a class that only delegates (Ch 5).
**Null Object** — a subclass with default behavior returned instead of null (Ch 9).
**Object-Orientation Abusers** — smell family: misapplied OO (Ch 2).
**Observer** — pattern used by Duplicate Observed Data to sync domain↔GUI (Ch 8).
**Open/Closed Principle** — open for extension, closed for modification; served by polymorphism refactorings (Ch 8, 9, 11).
**Parallel Inheritance Hierarchies** — smell: subclassing A forces subclassing B (Ch 3).
**Primitive Obsession** — smell: primitives/constants used instead of small classes (Ch 1).
**Query** — code that returns data without changing visible state (Ch 6, 10).
**Refactoring** — controlled improvement of code structure without changing behavior (Ch 6).
**Refused Bequest** — smell: a subclass uses only some inherited members (Ch 2).
**Reference object** — one program object per real-world entity (user/order) (Ch 8).
**Server** — the object the client accesses directly (Ch 5, 7).
**Shotgun Surgery** — smell: one change forces many small edits across classes (Ch 3).
**Single Responsibility Principle (SRP)** — a class should have one reason to change (Ch 4, 7, 8).
**Speculative Generality** — smell: unused "just in case" abstraction (Ch 4).
**State** — pattern for type code governing the whole object condition (Ch 8).
**Strategy** — pattern for interchangeable algorithms; result of delegation refactorings (Ch 8, 11).
**Switch Statements** — smell: complex switch/if-chains; think polymorphism (Ch 2).
**Tell-Don't-Ask** — tell an object what to do rather than query its state and branch (Ch 9).
**Template Method** — pattern: algorithm skeleton in parent, steps in children (Ch 11).
**Temporary Field** — smell: fields set only in certain circumstances (Ch 2).
**Type Code** — a set of numbers/strings acting as a pseudo-type (Ch 8).
**Value object** — an (ideally immutable) object; many represent one real-world thing (date/money) (Ch 8).
