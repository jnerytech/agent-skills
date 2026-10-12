# Chapter 4: Type Design Guidelines

## Core Idea
Choose the *kind* of type deliberately — class, struct, interface, enum, static class — each has distinct design rules. The dominant defaults: **favor classes over interfaces** (they evolve without breaking callers), and **most types should be classes**, with structs reserved for small immutable values.

## Frameworks Introduced
- **The logical type taxonomy**: classes (general reference types), interfaces (implementable by ref + value types, simulate multiple inheritance), structs (small primitive-like values), enums (small value sets), static classes (containers for static members), plus special cases (delegates, exceptions, attributes, arrays, collections).
- **One-sentence test (Brad Abrams)**: a good type is describable in one simple sentence; if you need "and" or a new sentence, split it. "If things get too complicated, make more types" (Jeffrey Richter).
- **Every member starts at net-negative value (Rico Mariani)**: it only earns its place by proven usefulness — what you omit matters as much as what you include.

## Reference Tables

**Class vs. Struct** — AVOID a struct *unless* it has ALL of:

| Criterion | Struct requirement |
|---|---|
| Semantics | Logically a single value (like `int`, `double`) |
| Size | Instance < 24 bytes (Richter: ~16) |
| Mutability | Immutable |
| Boxing | Won't be boxed frequently |

Otherwise → class. (Structs: cheaper alloc, inline in arrays, better locality; but boxing cost when cast to ref/interface, whole-value copies on assign/pass.)

**Class vs. Interface** — the big one:

| Situation | Choose |
|---|---|
| Default / exposing an abstraction | **Class** (favor) |
| Decouple contract from implementation | **Abstract class** (in a separate assembly) — NOT interface |
| Polymorphic hierarchy that must include value types | **Interface** (value types can't inherit but can implement) |
| Simulate multiple inheritance / "can-do" capability | **Interface** (`IDisposable`, `ICloneable`) |

Why favor classes: an interface's member set is **fixed forever** once shipped — adding a member breaks all implementers. A class can add non-abstract members with a default implementation and existing subclasses keep working (real example: `Stream.CanTimeout`/`ReadTimeout` added in .NET 2.0 without breaking `FileStream`).

## Key Concepts
- **"Interface-as-contract" is a dangerous myth (Cwalina)**: interfaces specify only *syntax*; a real contract is syntax + semantics, better locked with an abstract class (e.g., `Add` increments `Count`).
- **"is-a" vs. "can-do" (Richter)**: inheritance = is-a (`FileStream` *is a* `Stream`); interface = can-do (`FileStream` *can-do* dispose). Interfaces ending in `-able` signal capability.
- **Marker interface**: an empty interface used to tag a type — AVOID; prefer a custom attribute (unless you need a *compile-time* check, which attributes can't give).
- **Strongly typed string**: an immutable `readonly struct` wrapping a string, with static get-only properties for common values (`HashAlgorithmName.SHA256`) — the middle ground between an extensible-but-opaque `string`/`object` param and an inextensible-but-clear enum.
- **`ref struct`**: stack-only value type; DO NOT define except for perf-critical low-level scenarios (many restrictions, confusing to users).

## Mental Models
- **Value types must be immutable** — implicit copies on assign/return/pass make mutation invisible and confusing. Use get-only properties + a constructor; mark the type `readonly struct`.
- **Struct default state must be valid** — all-zero/false/null must be a legal instance (arrays skip constructors). If `value=0` is invalid, offset the logical value (store `value-1`).
- **Prefer a 2-value enum over a bool parameter (Abrams)**: `File.Open("f", CasingOptions.CaseSensitive, FileMode.Open)` reads far better than `File.Open("f", true, false)`; also future-proofs a possible 3rd value.

## Code Examples
Abstract class evolves gracefully where an interface can't:
```csharp
public abstract class Stream {
    public virtual bool CanTimeout { get { return false; } }        // added in v2.0,
    public virtual int ReadTimeout {                                 // no break
        get { throw new InvalidOperationException(); }
        set { throw new InvalidOperationException(); } }
}
```
Immutable struct done right:
```csharp
public readonly struct ZipCode {
    public ZipCode(int fiveDigitCode, int plusFourExtension) {...}
    public int FiveDigitCode { get; }       // get-only
    public int PlusFourExtension { get; }
}
```
- **What it demonstrates**: `readonly struct` lets the compiler skip defensive copies.

## Enum design (section 4.8)
- DO use enums to strongly type value sets; favor enum over static constants (better tooling/reflection).
- DO provide a zero value on simple enums (name it `None` or a sensible default); for flag enums, zero MUST mean "all cleared" and be named `None`.
- DO apply `[Flags]` to flag enums only; use powers of 2 (`1 << n`); name flag enums *plural*, simple enums *singular*.
- DO NOT: reserved/sentinel values (`LastValue`), enums with only one value, invalid flag combinations (split into multiple enums — cf. `BindingFlags` mistake), extend `System.Enum` directly.
- Default underlying type = `Int32`; changing enum size after ship is a binary breaking change.
- Adding values: generally safe for *input* enums and flag enums; risky for enums *returned* from APIs (clients may `switch` exhaustively).

## Anti-patterns
- **Types as dumping grounds** — no firm charter → magnet for random functionality.
- **Public/protected constructor on an abstract class** — misleading (use `protected` or `internal`).
- **Static class as a miscellaneous bucket** — needs a clear charter; use sparingly, only to support the OO core.
- **Public nested types as a grouping construct** — use namespaces; beginners get lost declaring dotted type names. Nested types are for implementation details (e.g., collection enumerators).
- **Adding members to a shipped interface** — breaks implementers; ship a new interface instead.

## Key Takeaways
1. Favor classes; nobody regrets shipping a class as a class, many regret shipping an interface (Cwalina).
2. Use abstract classes (separate assembly) to decouple contract from implementation — bake shared logic in, route to a protected abstract method (Template Method, §9.9).
3. Structs only for small, immutable, single-value, rarely-boxed types; implement `IEquatable<T>` to avoid boxing.
4. Provide ≥1 concrete implementation per abstract class/interface, and ≥1 consumer per interface — it validates the design before customers hit it late.
5. Value types immutable + valid zero state + `readonly` modifier; no default constructor on structs.
6. Enums: zero value, `[Flags]` + powers of 2 for flags, no sentinels/reserved values, `Int32` default.
7. Use a strongly typed string when a base type has a fixed input set but derived types could extend it.

## Connects To
- **Ch 3**: naming — nouns (classes) vs. adjectives (capability interfaces), suffix rules.
- **Ch 5**: member design — constructors, properties, the details inside these types.
- **Ch 6**: extensibility — base/abstract classes and sealing.
- **Ch 8**: `IEquatable<T>`/`IComparable<T>` implementation (§8.6), equality operators (§8.13).
- **Ch 9**: Template Method (§9.9); enums vs. strongly typed strings for open sets.
