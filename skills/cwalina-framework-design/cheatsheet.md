# Cheatsheet — Framework Design Guidelines

## The 4 verbs (how to read every guideline)
- **DO** — always follow (unless a rare, well-understood reason not to).
- **DO NOT** — never do this.
- **CONSIDER** — the default; deviate only with a good reason.
- **AVOID** — generally a bad idea; not absolute.

## Type-kind decision
- Single small immutable value < 24 bytes, rarely boxed → **struct**; else → **class**.
- Exposing an abstraction / need to evolve → **class** (default); nobody regrets shipping a class.
- Decouple contract from impl → **abstract class in a separate assembly**, NOT interface.
- Need value types in a polymorphic hierarchy, or "can-do" capability → **interface**.
- Closed value set → **enum**; open extensible set → **strongly typed string**.
- Container of static members only → **static class** (sealed+abstract), used sparingly.

## Class vs. interface — the tiebreaker
Ship a class. An interface's members are frozen forever (adding breaks implementers); a class can add non-abstract members without breaking subclasses.

## Property vs. method — use a METHOD when
Slower than field access · does I/O/network/DB · returns different result each call · significant side effect · returns a copy of internal state · **returns an array**. Otherwise use a property (keep getters trivial so the JIT inlines them).

## Naming quick rules
- PascalCase everything except parameters (camelCase). No underscores. ASCII only.
- Classes/structs = nouns · methods/events = verbs (tense: `Closing`/`Closed`) · capability interfaces = adjectives, `I`-prefixed.
- Readability > brevity: `CanScrollHorizontally` not `ScrollableX`.
- 2-letter acronym → both caps (`IOStream`); 3+ → first only (`XmlNode`).
- New version: **suffix > numeric > rename**; NEVER `Ex`; `64` only when retrofitting a 32-bit API.
- Boolean test: `if (stream.CanSeek)` should read naturally; prefer active voice.

## Parameters
- Take the **weakest type you need** (`IEnumerable<T>`), return the **strongest you have**.
- ≥2 bool params → use an enum; even 1 bool → enum if a 3rd value is plausible.
- `out` params last; avoid `out`/`ref` except the Try pattern; keep pointers out of public APIs.
- Validate all public/protected/explicit args high on the stack; validate enum range against **real values**, never `Enum.IsDefined`.

## Exceptions
- Throw for all failures; **never return error codes**. Throw the most-derived type that fits.
- Usage error (caller bug) → existing framework exception + great message. Program error → maybe custom. System failure → `Environment.FailFast`.
- "If the method doesn't do what its name says → throw."
- Don't swallow `Exception`/`SystemException` (except to transfer across threads); prefer try-finally/`using`; empty `throw;` preserves the stack.
- Custom exception: derive `Exception`, `Exception` suffix, serializable, 4 standard ctors, shallow hierarchy.
- Hot path failing often → Tester-Doer (test cheaper than do) or Try (`bool Try...(out T)`); throw rate >100/sec hurts.

## Async (TAP) — always
`Async` suffix · `Task`/`Task<T>` (or `ValueTask<T>` if usually sync) · trailing `CancellationToken cancellationToken = default` · `ConfigureAwait(false)` off the UI thread · throw `OperationCanceledException` on cancel · never `.Wait()`/`.Result` in async · throw usage errors synchronously (validate → `...Core`) · never return null/`Created`-state Task · `ValueTask`: await/return once only.

## Dispose
`Dispose()` → `Dispose(true)` + `GC.SuppressFinalize(this)`; cleanup in `protected virtual Dispose(bool disposing)` (managed only when `disposing`); idempotent; `ObjectDisposedException` after dispose; **never throw when `disposing==false`**; public types non-finalizable (use `SafeHandle`).

## Extensibility ladder (cheapest → most powerful)
unsealed class → protected members → events/callbacks → virtual members → abstractions.
- Add extensibility later, never remove it. Unseal deliberately.
- Treat protected as public for security/docs.
- Prefer events > callbacks > virtuals for broad audiences; don't invoke callbacks under a lock.
- Public members non-virtual → route to `protected virtual XxxCore` (Template Method).
- Don't seal without reason (static class / many inherited virtuals / perf-critical attribute are good ones).

## Enums
Provide a zero value (`None`); `[Flags]` + powers of 2, plural name, zero = `None`; no sentinels/reserved/one-value enums; don't extend `System.Enum`; `Int32` default (changing size = binary break).

## Collections in public APIs
Return `Collection<T>`/`ReadOnlyCollection<T>`/interfaces — never `List<T>`/`Dictionary`/`Hashtable`. Properties return **live**, never null (empty instead), never settable. Prefer collections over arrays (arrays are always mutable).

## Breaking-change fast filter (BCL bar)
- **Never** (❌): rename type/namespace/assembly, remove a type/member, add interface/abstract member, class↔struct, seal, remove `readonly` from struct, change a shipped default value.
- **OK** (✅): add member to a concrete type, unseal, add `readonly` to struct, move member to a base class, `[TypeForwardedTo]`, remove sealed-type finalizer.
- Rule of thumb: **adding < changing < removing**; widen, don't narrow.

## Style (suggestions, not rules)
Allman braces, braces required (except `case` + validation preamble) · 4 spaces no tabs · language keywords not BCL names · `nameof(...)` · `_`/`s_`/`t_` field prefixes · `var` only for `new`/`as`/hard-cast · `if … throw` not `?? throw` · braced `using`.
