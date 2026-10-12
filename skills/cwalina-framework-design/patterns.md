# Patterns & Techniques — Framework Design Guidelines

## Scenario-Driven Design
**When**: starting any public API feature.
**How**: write client code for the top 5–10 scenarios (in ≥2 dissimilar languages) FIRST; derive the object model from those samples. Scenarios ≈ end-user use cases ("read a file", not "open/read-line/close").
**Trade-offs**: more up-front discipline; but standard OO methodologies optimize implementation maintainability, not API usability.

## Pit of Success
**When**: every default/overload/API-shape decision.
**How**: make the most natural usage correct + secure + fast; make misuse hard.
**Trade-offs**: harder to design; occasionally sacrifices flexibility.

## Layered Architecture
**When**: a framework must serve both power users and productivity users.
**How**: low-level types (expressive) + high-level types wrapping them (convenient), usually in separate related namespaces (`Utf8JsonReader` vs. `JsonDocument`).
**Trade-offs**: more types; but yields power + simplicity in one framework.

## Aggregate Component + Create-Set-Call
**When**: a common feature area needs a simple entry point.
**How**: a façade over factored types; simple constructor, get/set properties with defaults, methods without option params, events (not delegates/virtuals); one `new` per simple scenario. Communicate invalid states via `InvalidOperationException` at operation time, not construction.
**Trade-offs**: can have modes/invalid states — acceptable for usability-first components.

## Template Method
**When**: you need controlled extensibility (vs. public virtuals).
**How**: public non-virtual member does arg/state validation, then calls a `protected virtual XxxCore`; only Core is overridable. Derived types add only their own extra validation.
**Trade-offs**: one indirection; but keeps overload semantics consistent and enforces call order.

## Optional Feature Pattern
**When**: some implementations of an abstraction support a feature, others don't.
**How**: a `bool CanXxx` property + a virtual `Xxx()` that throws `NotSupportedException` by default (`Stream.CanSeek`/`Seek`).
**Trade-offs**: no compile-time safety; but avoids interface explosion and dynamic casts.

## Tester-Doer
**When**: a member throws often in common scenarios and the test is cheap.
**How**: split into a tester (`IsReadOnly`) + doer (`Add`); callers test before doing.
**Trade-offs**: race conditions in multithreaded use (test/do must share a lock).

## Try Pattern
**When**: hot paths that fail often; also fixes Tester-Doer races.
**How**: `bool TryXxx(..., out T value)`; `Try` prefix + bool return; assign `out` only on success (`default` on false); pick one false-reason, throw for the rest; always provide a throwing twin.
**Trade-offs**: `out` param is expert-only ergonomics.

## Dispose Pattern (Basic)
**When**: a type holds unmanaged resources or owns disposable objects.
**How**: `Dispose()` → `Dispose(true)` + `GC.SuppressFinalize(this)`; all cleanup in `protected virtual void Dispose(bool disposing)` (managed resources only when `disposing`); idempotent; throw `ObjectDisposedException` from members after dispose; never throw when `disposing == false`.
**Trade-offs**: keep public types non-finalizable — wrap unmanaged resources in `SafeHandle`.

## Scoped Operation (disposable return)
**When**: a begin/end operation must be paired reliably (locks, indentation).
**How**: return an `IDisposable`/disposable struct so callers use `using` (Dispose in a finally block): `using (writer.OpenScope(4)) { ... }`.
**Trade-offs**: allocation unless a value type is used carefully.

## Factory (method / abstract factory)
**When**: need a derived/cached return, a self-explanatory name, or conversions.
**How**: static `Create<Type>` / `<Type>Factory`; `Parse`/`Decode` for conversions; return via return value, not `out` (except Try).
**Trade-offs**: loses IntelliSense discoverability vs. constructors — prefer constructors by default.

## Task-Based Async Pattern (TAP)
**When**: all new async APIs (I/O, long-running).
**How**: `Async` suffix; return `Task`/`Task<T>` (or `ValueTask<T>` if usually synchronous); trailing `CancellationToken cancellationToken = default`; `ConfigureAwait(false)` off UI; throw `OperationCanceledException` on cancel; usage errors thrown synchronously (validate then defer to `...Core`).
**Trade-offs**: `ValueTask` trades usability for fewer allocations — await/return once only.

## Simulated Covariance Pattern
**When**: you need a common root type for all `Foo<T>` instantiations.
**How**: define `IFoo<out T>` (contravariant members removed), implement explicitly on `Foo<T> : IFoo<object>`, add back strongly typed members.
**Trade-offs**: extra types + complexity; use only when truly needed.

## Strongly Typed String
**When**: a base type has a fixed input set but derived types could extend it.
**How**: `readonly struct` wrapping a string, static get-only value properties (`HashAlgorithmName.SHA256`), `IEquatable<T>`, override `ToString`/`==`, allow null in constructor.
**Trade-offs**: middle ground between opaque `string`/`object` and inextensible enum.

## Buffer Operations with Span
**When**: encoding/crypto/serialization/parsing over byte/char buffers.
**How**: accept `ReadOnlySpan<T>` (read) / `Span<T>` (write) — callers slice, so no offset/count overloads; `Memory<T>`/`ReadOnlyMemory<T>` for storage and async; don't return a `Span` over your own field (copy to a destination `Span` or return a `Range` instead).
**Trade-offs**: `ref struct` restrictions; can't be fields or cross awaits.
