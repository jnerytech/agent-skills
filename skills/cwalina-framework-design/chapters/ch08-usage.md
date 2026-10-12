# Chapter 8: Usage Guidelines

## Core Idea
How to use common built-in types in public APIs: prefer collections over arrays, use collection *abstractions* (not `List<T>`/`Dictionary`) on the public surface, avoid `ICloneable`, use `DateTimeOffset` by default, and implement `Equals`/`GetHashCode`/`ToString`/equality operators correctly and consistently.

## Frameworks Introduced
- **"Require the weakest thing you need, return the strongest thing you have" (Anthony Moore)**: parameters → `IEnumerable<T>`; return values → richer types — but balance against not returning `List<T>`/`T[]`.
- **Snapshot vs. live collections**: snapshot = state at a point in time (DB query rows); live = always-current (`ComboBox.Items`). Properties must return *live* collections (getters are cheap); use a method or `IEnumerable<T>` for snapshots.
- **The Equals/GetHashCode contract**: if `Equals` is overridden, `GetHashCode` must be too; equal objects → equal hash codes; hash code must never change over the object's lifetime.

## Reference Tables

Public-API collection type choices:

| Need | Use | NOT |
|---|---|---|
| Read/write collection property/return | `Collection<T>` (or subclass) | `List<T>`, `ArrayList` |
| Read-only collection | `ReadOnlyCollection<T>` (or `IEnumerable<T>`) | — |
| Dictionary-like | `IDictionary<K,V>` / custom | `Dictionary<K,V>`, `Hashtable` |
| Keyed by unique key | `KeyedCollection<TKey,TItem>` | — |
| Parameter (input) | `IEnumerable<T>` (weakest) | `List<T>`, weakly typed `IList` |

`DateTime` vs. `DateTimeOffset`:

| Use | For |
|---|---|
| **`DateTimeOffset`** (default) | Exact point in time: "now", transactions, file/log times (UTC if zone unknown) |
| `DateTime` | Point-in-time doesn't apply (store opening hours across zones); zone unknown/legacy; whole dates (00:00:00, e.g. DOB) |
| `TimeSpan` | Time of day without a date |
| avoid `DateTimeKind`, `DBNull` | prefer `DateTimeOffset`, `Nullable<T>` |

## Key Concepts
- **Arrays are mutable — even arrays of immutable types**: `readonly char[]` only stops replacing the whole array, not `arr[0] = 'x'`. Never expose `public static readonly` array fields (`Path.InvalidPathChars` bug); return a clone, a `ReadOnlyCollection<T>`, or `ReadOnlySpan<T>`.
- **AVOID array properties**: getters must be ~field-fast, but array properties usually return a copy (shallow/deep) → O(n). Use collection properties, `ReadOnlyMemory<T>`, or a `GetRawBuffer`-style method.
- **Attributes**: `Attribute` suffix, `[AttributeUsage]`, required args = get-only properties + constructor params, optional args = settable properties (never both), one constructor, sealed.
- **Don't return null from collection members** — return empty; treat null and empty the same.
- **A type is a collection OR an enumerator, never both** — don't implement `IEnumerable<T>` and `IEnumerator<T>` on the same type; only return `IEnumerator<T>` from `GetEnumerator`.

## Mental Models
- **`ICloneable` is broken by design** — its contract never specified deep vs. shallow copy, so it's useless. DO NOT implement or use it; define your own strongly typed `Clone()` with documented copy semantics.
- **`IEquatable<T>` on value types avoids boxing** — `Object.Equals` boxes and uses reflection (slow); always pair with an `Object.Equals` override + matching `==`/`!=`; implement `IEquatable<T>` whenever you implement `IComparable<T>`.
- **`ToString` is a diagnostic tool** (Sells/Pepin): the debugger uses it; keep it short, side-effect-free, culture-aware; make output "geeky" so no one mistakes it for a UI string; use a separate method for user presentation.
- **`System.Uri` over `string` for URLs** (Alcazar): string URL manipulation causes security/correctness bugs; store `Uri`, offer selective string convenience overloads that delegate to the `Uri` version.
- **`System.Xml`**: expose `IXPathNavigable`/`XmlReader`/`XmlWriter`/`XNode`, never `XmlNode`/`XmlDocument` (not designed for public APIs); don't subclass `XmlDocument` (`XmlDataDocument` is the anti-example).

## Code Examples
Safe read-only exposure of an array:
```csharp
public static ReadOnlyCollection<char> GetInvalidPathChars()
    => Array.AsReadOnly(badChars);
public static char[] GetInvalidPathChars()
    => (char[])badChars.Clone();
```
`GetHashCode` via the built-in `HashCode` helper:
```csharp
public override readonly int GetHashCode() => HashCode.Combine(Width, Height);
```
- **What it demonstrates**: uniform distribution without hand-rolled bit math.

## Anti-patterns
- **Weakly typed collections in public APIs** (`IList Components` returning `object`/`IComponent`) — use `Collection<Component>`.
- **`List<T>`/`Dictionary<K,V>`/`Hashtable` on the public surface** — implementation types; you lose modification notifications and leak irrelevant members (`BinarySearch`).
- **Settable collection properties** — clear + add instead; offer `AddRange` if replacing is common.
- **Overloading only one of `==`/`!=`** (or `Object.Equals` inconsistent with `==`); throwing from `Equals`/`GetHashCode`/`ToString`/equality operators.
- **Value equality on mutable reference types** — they get "lost" in hashtables when the value/hash changes.
- **`operator==` across different types** — forces 6 methods + 2 interfaces; use a conversion operator or a property instead (`DateTimeOffset.UtcDateTime`).
- **Multidimensional arrays** — prefer jagged arrays (less waste, CLR-optimized indexing).
- **Serialization attributes on general-purpose public types** — only exception-like cross-AppDomain types keep `[Serializable]`; leave serializer choice to the app developer.

## Key Takeaways
1. Prefer collections over arrays; use `Collection<T>`/`ReadOnlyCollection<T>`/interfaces on public APIs, never `List<T>`/`Dictionary`.
2. Weakest parameter type (`IEnumerable<T>`), strongest sensible return type; properties return live collections, never null, never snapshots.
3. Arrays are always mutable — never expose readonly array fields or array properties that copy.
4. `DateTimeOffset` is the default for exact points in time; `DateTime`/`TimeSpan` for the specific cases above.
5. Don't implement `ICloneable`; roll a documented `Clone()`.
6. `IEquatable<T>` on value types (no boxing); override `Object.Equals`+`GetHashCode` together, keep hash stable and well-distributed, honor the reflexive/symmetric/transitive contract.
7. Override `ToString` for a short, side-effect-free, culture-aware diagnostic string; implement `IFormattable`/`ToString(format)` when culture-sensitive.
8. `Uri` not `string` for URLs; `XmlReader`/`IXPathNavigable`/`XNode` not `XmlDocument`; equality operators only on value types / immutable reference types.

## Connects To
- **Ch 4**: `IEquatable<T>` on value types; enum vs. type choices.
- **Ch 5**: array-returning properties → methods (§5.1.3); operator overloading (§5.7); parameter design.
- **Ch 6**: `Collection<T>` as a base class for custom collections.
- **Ch 7**: `IDisposable`/`using` cleanup; exceptions from equality methods.
- **Ch 9**: Dispose pattern (§9.4), factories, `IAsyncEnumerable`, `Span<T>`/buffers (§9.12).
- **App. B**: full serialization guidance (moved there).
