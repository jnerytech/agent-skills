# Chapter 7: Exceptions

## Core Idea
Report **all** failures by throwing exceptions — never return error codes. Exceptions are out-of-band (work for constructors/properties/operators where the return value is fixed), impossible to silently ignore, carry rich diagnostics (call stack!), and enable unhandled-exception handlers and tooling. The costs (performance, choosing types) are managed with patterns, not by abandoning exceptions.

## Frameworks Introduced
- **Usage error vs. execution error** — the first decision when choosing an exception type:
  - **Usage error**: a bug in the *calling* code, fixable at compile-time (null passed, bad range) → throw an *existing* framework exception (`ArgumentNullException`, `InvalidOperationException`); never a custom type.
  - **Execution error** (can't be avoided by better code) splits into:
    - **Program error** — handleable programmatically (`FileNotFoundException` → create the file) → the *only* case where a custom exception type may be justified.
    - **System failure** — unhandleable (heap corruption) → call `Environment.FailFast`, don't throw.
- **Tester-Doer pattern**: split into a cheap tester (`IsReadOnly`) + a doer (`Add`) so callers avoid the throw in common cases. Caveat: race conditions in multithreaded use.
- **Try pattern**: fold the test into the member — `bool TryParse(string, out T)`; solves both the perf problem *and* the Tester-Doer race.

## Reference Tables

Standard exception usage (throw vs. reserved):

| Exception | Guidance |
|---|---|
| `Exception`, `SystemException` | DO NOT throw or catch (except top-level/rethrow) |
| `ApplicationException` | DO NOT throw or derive — meaningless |
| `InvalidOperationException` | Object in wrong *state* (write to read-only stream) |
| `ArgumentException`/`ArgumentNullException`/`ArgumentOutOfRangeException` | Bad *argument*; set `ParamName`; use most-derived |
| `NullReference`/`IndexOutOfRange`/`AccessViolation` | Reserved for the platform — DO NOT throw/allow from public APIs |
| `StackOverflow`/`OutOfMemory`/`ExecutionEngine`/`COM`/`SEH` | CLR-only; don't throw, don't catch `StackOverflow` |
| `OperationCanceledException` | Any caller-initiated cancel (prefer catching over `TaskCanceledException`) |
| `FormatException` | Malformed input string OR invalid format specifier |
| `PlatformNotSupportedException` | Op valid elsewhere but not this runtime/OS |

Argument state distinction (Cwalina): `ArgumentException` depends only on the argument; `InvalidOperationException` depends on the object's state. Malformed identifier → `ArgumentException`; nonexistent resource → `InvalidOperationException`.

## Key Concepts
- **Exceptions are for error conditions, NOT "exceptional conditions" (Cwalina)**: "one man's exceptional condition is another's chronic condition" — a library can't know its usage context, so `OutOfMemory` isn't inherently exceptional.
- **Handle vs. swallow**: you *handle* when you catch a specific type and understand the implications; you *swallow* when you catch a generic type and continue blindly. DO NOT swallow (catch `Exception`/`SystemException`) except to transfer across threads (and then never lose it).
- **Throw the most-derived exception that makes sense**; throwing/catching `System.Exception` is "always the wrong thing."
- **Empty `throw;` preserves the call stack**; `throw ex;` resets it. Across threads/contexts use `ExceptionDispatchInfo.Capture(e)` + `.Throw()`.
- **Wrapping exceptions**: wrap a lower-layer exception only when the original is meaningless at the higher layer (`TypeInitializationException` wraps static-ctor exceptions); always pass the inner exception; wrapping hurts debuggability, so do it rarely.

## Mental Models
- **"If a method doesn't do what its name says, throw" (Jason Clark)**: `ReadByte` at EOF → throw (can't read a byte); `ReadChar` at EOF → EOF is a valid char, don't throw.
- **Crash beats muddling on (Abrams/Richter)**: better to terminate than continue with corrupt state — swallowing exceptions is a security and correctness hazard. Handle only what you *understand and can recover from*.
- **try-finally >> try-catch**: catch blocks are needed far less than you'd think; use `using`/`lock`/`foreach` (all emit try-finally) for cleanup; error *recovery* → catch, cleanup → finally.
- **Don't over-catch (Gunnerson)**: exceptions are robust by default; every handler is a chance to *remove* robustness — be minimal.

## Code Examples
Tester-Doer:
```csharp
if (!numbers.IsReadOnly) { numbers.Add(1); }
```
Try pattern with proper `out` discipline (assign right before return; write `default` on false; don't leak on throw):
```csharp
public static bool TryDecode(byte[] data, out ParsedType value) {
    ParsedType parsed = new ParsedType();
    if (!LoadFields(parsed, data)) { value = null; return false; }
    value = parsed;               // only assigned on the success path
    return true;
}
```
Custom exception — the required constructor set:
```csharp
public class SomeException : Exception {
    public SomeException();
    public SomeException(string message);
    public SomeException(string message, Exception inner);
    protected SomeException(SerializationInfo info, StreamingContext context); // serialization
}
```

## Anti-patterns
- **Returning error codes** / returning an `Exception` as a value / `out` param.
- **`GetType(string, bool throwOnError)`** — a member that throws-or-not by option (indecision pushed onto the caller).
- **Throwing from exception filters or finally blocks** (filter exceptions silently become `false`; hard to debug).
- **Custom exception just to brand your feature** in the type/namespace name.
- **Deep exception hierarchies** — handlers rarely care about the hierarchy; if two errors are handled the same way, don't give them different types.
- **Exceptions for normal control flow** — use Tester-Doer/Try; throw rates >100/sec noticeably hurt performance.

## Key Takeaways
1. Throw exceptions for all execution failures; never return error codes.
2. Usage error → existing framework exception with a great *message*; program error → maybe a custom type; system failure → `FailFast`.
3. Custom exceptions: derive from `Exception`, `Exception` suffix, serializable, the 4 standard constructors, shallow hierarchy.
4. Write rich, grammatical, period-terminated messages for the developer; no security-sensitive info; consider localization.
5. Don't swallow generic exceptions; prefer try-finally/`using`; use empty `throw;` to preserve the stack.
6. Document contract exceptions and treat them as part of the API (don't change them across versions; adding a subtype is non-breaking).
7. For hot paths that fail often, use Tester-Doer (test cheaper than do) or Try (`bool Try...(out T)`); always provide a throwing twin.
8. Try methods: `Try` prefix + bool return, `out` value assigned only on success (`default` on false), pick one false-reason and throw for the rest.

## Connects To
- **Ch 2**: communicate usage mistakes via clear exception messages (self-documenting APIs).
- **Ch 3**: `Exception` suffix naming.
- **Ch 5**: exceptions from constructors/setters; the Try pattern uses `out` params (§5.8); argument validation (§5.8.2).
- **Ch 8**: `IDisposable`/`using` for cleanup in finally.
- **App. B**: obsolete exception guidance.
