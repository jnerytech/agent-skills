# Glossary — Framework Design Guidelines

**Abstraction** — a type describing a contract without a full implementation (abstract class or interface); e.g., `Stream`, `IEnumerable<T>` (Ch 6).
**Aggregate component** — a façade over factored types supporting Create-Set-Call for common scenarios; e.g., `HttpClient`, `EventLog` (Ch 9).
**Attached dependency property** — a DP defined on one type but settable on another (`Grid.Column` on a `Button`) via static Get/Set (Ch 9).
**Base class** — a class designed for subclasses to reuse a default implementation (`Collection<T>`), mid-hierarchy (Ch 6).
**Breaking change** — a change classified as runtime, compilation, recompile, or reflection break (App. D).
**camelCasing** — first letter of each word capitalized except the first; used only for parameters/locals (Ch 3).
**Classic Async Pattern (APM)** — legacy Begin/End + `IAsyncResult` async model (Ch 9).
**CLS (Common Language Specification)** — the interoperability subset usable by all .NET languages; mark assemblies `[CLSCompliant(true)]` (Ch 4).
**Convenience overload** — a short-parameter-list overload with good defaults that lowers the entry barrier (Ch 2).
**Contravariance (`in`)** — generic type parameter used only as input; allows a wider type to substitute (Ch 9).
**Covariance (`out`)** — generic type parameter used only as output; allows a narrower type to substitute (Ch 9).
**Create-Set-Call** — usage pattern: instantiate, set properties, call methods (Ch 9).
**Dependency property (DP)** — a property storing its value in a property store, enabling WPF styling/binding/animation (Ch 9).
**Deep vs. shallow immutability** — deep = whole object graph transitively immutable; shallow = only the top level (Ch 5).
**Dispose Pattern** — standardized `IDisposable`/finalizer implementation via `Dispose(bool disposing)` (Ch 9).
**Doer** — the member performing a potentially throwing operation in Tester-Doer (Ch 7).
**Event-Based Async Pattern (EAP)** — legacy event-callback async model (Ch 9).
**Execution error** — a failure not avoidable by better code; splits into program error and system failure (Ch 7).
**Explicit interface implementation** — a member callable only via the interface cast (Ch 5).
**Factored type** — a richer, mode-free type behind an aggregate component (`SerialPort.BaseStream`) (Ch 9).
**Factory** — an operation/type abstracting object creation (factory method or abstract factory) (Ch 9).
**Finalizable type** — a type overriding `Finalize` to release unmanaged resources (Ch 9).
**Flag enum** — an enum for bitwise combination; `[Flags]`, powers of 2, plural name, zero = `None` (Ch 4).
**Framework** — a set of reusable APIs providing most of an app's pieces to be customized and connected (Ch 1).
**Hungarian notation** — encoding type/scope in a name (`uiCount`, `s_`); banned in public APIs (Ch 3).
**It-Just-Works** — hiding a component's internal complexity so it works without user awareness (Ch 9).
**Layered architecture** — low-level (power) + high-level (productivity) API layers (Ch 2).
**Live collection** — a collection always reflecting current state (`ComboBox.Items`); properties should return these (Ch 8).
**Marker interface** — an empty interface used to tag a type; avoid (prefer an attribute) (Ch 4).
**Optional Feature Pattern** — `CanXxx` bool + virtual `Xxx()` throwing `NotSupportedException` (Ch 9).
**PascalCasing** — first letter of every word capitalized; used for all identifiers except parameters (Ch 3).
**Pit of Success** — designing so the natural way to use the API is correct, secure, and fast (Ch 2).
**Progressive framework** — a single framework with a gradual learning curve across skill levels (Ch 2).
**Program error** — an execution error handleable programmatically; may justify a custom exception (Ch 7).
**Property store** — where a dependency property keeps its value instead of a field (Ch 9).
**`ref struct`** — a stack-only value type; can't be boxed, a field of a non-ref-struct, or cross an await (Ch 4).
**Reserved value / sentinel** — enum values for future use / range markers; both banned (Ch 4).
**Scenario-driven design** — write client code for top scenarios first, then design the object model (Ch 2).
**Scoped operation** — a begin/end operation exposed as a disposable used with `using` (Ch 9).
**Sealing** — preventing inheritance (class) or override (member) (Ch 6).
**Simulated Covariance Pattern** — an `IFoo<out T>` root implemented explicitly so all `Foo<T>` share a root (Ch 9).
**Snapshot collection** — a collection capturing state at a point in time (DB rows); don't return from properties (Ch 8).
**`Span<T>` / `ReadOnlySpan<T>`** — ref-struct over contiguous memory with O(1) slicing; `Memory<T>` for storage/async (Ch 9).
**Static class** — a class of only static members; sealed + abstract; use sparingly (Ch 4).
**Strongly typed string** — a `readonly struct` wrapping a string with static value properties (`HashAlgorithmName`) (Ch 4).
**System failure** — an unhandleable execution error (heap corruption); call `Environment.FailFast` (Ch 7).
**Task-Based Async Pattern (TAP)** — the recommended async model: `Async` suffix, `Task`/`ValueTask<T>`, `CancellationToken` (Ch 9).
**Template Method** — public non-virtual member validating + calling a `protected virtual XxxCore` (Ch 6, 9).
**Tester-Doer** — split a throwing member into a cheap tester + a doer to avoid exceptions in common cases (Ch 7).
**Try pattern** — fold the test into the member: `bool TryXxx(..., out T)` (Ch 7).
**Type parameter** — a generics identifier (`T`, `TResult`) (Ch 3).
**Usage error** — a bug in calling code, fixable at compile-time; throw an existing framework exception (Ch 7).
**`ValueTask<T>`** — value-type async result for methods that commonly complete synchronously; await/return once only (Ch 9).
**Weakly typed collection** — a collection exposing `object`/base types instead of the item type; avoid in public APIs (Ch 8).
