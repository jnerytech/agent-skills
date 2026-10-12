# Chapter 5: Member Design

## Core Idea
Members (methods, properties, events, constructors, fields) are how framework functionality reaches users. The recurring themes: **properties over methods for data**, **overload from short → long (only the longest is virtual)**, **fields always private**, **validate arguments high on the stack**, and **prefer enums/descriptive types over bools/tuples** for readability.

## Frameworks Introduced
- **Overload chaining**: shorter overloads call through to the longest; make only the **longest** overload virtual (do arg-checking in the non-virtual public method, defer to a protected abstract/virtual "Core" method — this is Template Method, §9.9).
- **Property vs. method rule of thumb**: methods = actions, properties = data. Properties are "smart fields" — must look and cost like a field access.
- **The `On<EventName>` pattern**: raise every event via a `protected virtual void OnXxx(EventArgs e)` so derived classes can override.
- **Try pattern**: the sanctioned use of `out` parameters (`bool TryParse(string, out T)`).

## Reference Tables

**Property vs. Method** — use a **method** (not a property) when:

| Signal | Why |
|---|---|
| Orders of magnitude slower than field access | Property implies cheap; network/file/DB access → method |
| It's a conversion (`ToString`) | Not attribute-like |
| Returns a different result each call | `Guid.NewGuid`, `DateTime.Now` (Richter: should've been a method) |
| Significant observable side effect | (populating a cache is OK) |
| Returns a copy of internal state, or an **array** | array copy in a loop = O(n) allocations |

**Parameter passing** — four kinds, and the guidance:

| Kind | Guidance |
|---|---|
| by-value | Default; almost always right |
| `ref` | AVOID except swap-like; DO NOT pass reference types by `ref` |
| `in` (`ref readonly`) | DO NOT use on public/protected members (silent defensive-copy cost) |
| `out` | AVOID except Try pattern; place ALL `out` params last |

## Key Concepts
- **Explicit interface implementation**: member callable only via the interface cast. AVOID without strong reason (confusing, boxes value types). Legit uses: hide infra members (`ICollection<T>.IsReadOnly`), simulate variance, rename (`TryTake`→`TryDequeue`), or resolve same-name/different-return-type. Provide a `protected virtual ...Core` if it must be specializable — and never use as a security boundary.
- **Default parameters**: not CLS-compliant; DO NOT use on virtual/interface methods (except `CancellationToken`); DO NOT change a shipped default; always provide a simple no-default overload for methods with ≥2 defaults.
- **Encapsulation**: all instance fields **private** — a field can't become a property without breaking binary compatibility. Exceptions: `const` and `static readonly`.
- **Deep vs. shallow immutability (Joe Duffy)**: `readonly` on a reference-type field only prevents replacing the instance, not mutating it — don't expose mutable types via `readonly` fields.
- **Descriptive type vs. tuple**: prefer descriptive types (validation, methods, evolvable, named in all languages); then named tuples over unnamed; never >3 fields; never as parameters or extension-method receivers.

## Mental Models
- **Enum over bool parameter**: `File.Open("f", true, false)` is unreadable; `File.Open("f", CasingOptions.CaseSensitive, FileMode.Open)` self-documents. DO use an enum if a member would have ≥2 bool params; DO NOT use a bool unless certain there'll never be a 3rd value.
- **"Properties cause more performance crimes than any other feature" (Mariani)**: keep getters trivial (no I/O, no locks, no loops-worth of work) so the JIT inlines them.
- **Least-derived parameter type**: take `IEnumerable<T>`, not `List<T>`, unless you need the richer type's members/perf.
- **Constructors do minimal work** — capture params, defer the rest. Constructor params = required dependencies (DI-friendly); mirror them as get-only properties by default.
- **Operator overloads only on primitive-feeling types**: overload symmetrically (`==`↔`!=`, `<`↔`>`), always provide a named-method twin (`Subtract` for `operator-`) since not all languages/IntelliSense expose operators. Never "be cute" (no `|` for query union).

## Code Examples
Overload chaining with a single virtual:
```csharp
public class Encoding {
    public bool IsAlwaysNormalized() => IsAlwaysNormalized(NormalizationForm.FormC);
    public virtual bool IsAlwaysNormalized(NormalizationForm form) { /* real work */ }
}
```
Raise events via protected virtual + null-conditional:
```csharp
protected virtual void OnAlarmRaised(AlarmRaisedEventArgs e) => AlarmRaised?.Invoke(this, e);
```
- **What it demonstrates**: derived classes override to react faster than subscribing; pass `EventArgs.Empty`, never `null`.

## Anti-patterns
- **`Enum.IsDefined` for range checks**: loads reflection (expensive) AND has a versioning hole — a value added later (`Ultraviolet = -1`) silently passes the check. Range-check against real values instead.
- **Set-only properties / setter broader than getter**: use a `SetXxx` method instead.
- **Throwing from property getters** (indexers excepted) — redesign as a method.
- **Calling virtual members inside a constructor**: the derived override runs before the derived constructor finishes → operates on uninitialized state.
- **Throwing from static constructors**: makes the type unusable in the AppDomain forever; also avoid locking there (deadlock risk).
- **Adding a parameterized constructor without re-declaring the default** — silently removes the compiler-generated default constructor (a breaking change). Always declare the public default explicitly (classes only; not structs).
- **Frivolous extension methods**, especially on `System.Object` (VB can't call them) or on tuples; DO throw `ArgumentNullException` when the `this` param is null.

## Worked Example
The array-property trap (Brad Abrams, "school of hard knocks"): `microsoft.Employees` typed as an array must return a *copy* to protect internal state, so this loop makes 2n+1 array copies:
```csharp
for (int i = 0; i < microsoft.Employees.Length; i++)
    if (microsoft.Employees[i].Alias == "kcwalina") { ... }
```
.NET 1.0 profiling found thousands of arrays created and trashed this way. Two fixes: (1) turn it into a **method** `GetEmployees()` — signals to callers "this allocates, cache it"; or (2) return a `ReadOnlyCollection<Employee>` wrapping the private array. The guideline "properties returning arrays are misleading" was born from this.

## Key Takeaways
1. Overload short→long, keep params consistently named/ordered, make only the longest virtual, allow `null` for optional reference-type args.
2. Property = cheap data access; method = action / expensive / non-idempotent / side-effecting / returns array-or-copy.
3. All instance fields private; use `const` / `static readonly` for constants; don't put mutable instances in `readonly` fields.
4. Events: use `EventHandler<T>`, `(object sender, EventArgs e)`, subclass `EventArgs` even if empty, raise via `protected virtual OnXxx`, say "raise" not "fire".
5. Validate all public/protected/explicit member args high on the stack (`ArgumentException`/`ArgumentNullException`); validate enum range against real values; don't over-validate hot low-level code.
6. Prefer enums over bools; descriptive types over tuples (>3 fields → descriptive type; never tuple params).
7. Constructors: minimal work, mirror params as get-only properties, prefer static factory methods when construction semantics don't fit; never call virtuals inside.
8. `out`/`ref`/`in` are for experts — avoid except the Try pattern; wrap multiple returns in a type; keep pointers out of the public surface (offer array/`Span<T>` alternatives).

## Connects To
- **Ch 2**: low barrier to entry (simple overloads, good defaults).
- **Ch 3**: member naming (verbs for methods, `On`/`Try` prefixes, `EventHandler`/`EventArgs` suffixes).
- **Ch 4**: constructor rules for abstract classes/structs; enum vs. bool.
- **Ch 6**: virtual members and extensibility (this chapter's overload-virtual guidance).
- **Ch 7**: exceptions from constructors/setters; the Try pattern (§7.5.2).
- **Ch 8**: `Object.Equals`/`GetHashCode`, equality/inequality operators (§8.9, §8.13), `ReadOnlyCollection<T>`/`Collection<T>` (§8.3).
- **Ch 9**: factory methods (§9.5), Template Method (§9.9).
