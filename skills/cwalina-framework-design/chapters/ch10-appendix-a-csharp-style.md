# Appendix A: C# Coding Style Conventions

## Core Idea
**Unlike the guidelines, these are suggestions, not rules** — coding style has no direct effect on framework *users*. This is the .NET BCL team's open-source style (17 rules, one screen). Governing principles: clarity over brevity (code is read more than written), prefer the form that minimizes noise in a future diff, and keep the rules few with few exceptions (hence Allman bracing).

## Frameworks Introduced
- **Allman bracing**: opening brace on its own next line, aligned with the block statement; closing brace on its own line.
- **Field prefix convention**: `_` for private/internal instance fields, `s_` for static, `t_` for thread-static — signals to a reviewer why a method isn't static and where shared/thread state lives.
- **The `var` rule**: use `var` *only* to save the result of `new`, an `as`-cast, or a "hard" cast — never for factory methods, `TryParse`, or "everyone knows the type" methods.

## Reference Tables

Spacing:

| Rule | Right | Wrong |
|---|---|---|
| After comma | `Foo(a, 0, 1)` | `Foo(a,0,1)` |
| Inside parens | `Foo(a, 0)` | `Foo( a, 0 )` |
| Member + `(` | `Foo()` | `Foo ()` |
| Square braces | `arr[index]` | `arr[ index ]` |
| Flow keyword + `(` | `while (x)` | `while(x)` |
| Binary operators | `if (x == y)` | `if (x==y)` |
| Unary operators | `if (!y)` | `if (! y)` |

Canonical modifier order:
`public/private/protected/internal` → `static` → `extern` → `new/virtual/abstract/sealed/override` → `readonly` → `unsafe` / `volatile` → `async`.
Use `protected internal` (not `internal protected`) and `private protected` (not `protected private`).

Indent: **4 spaces, never tabs**; chop long param/arg lists one-per-line indented one level; outdent `goto` labels.

## Key Concepts
- **Braces (mostly) required** even for single-statement blocks. Exceptions: `case` blocks (delimited by `case`/`break`) and the argument-validation *preamble* (`if (expr) throw ...;` with no braces, until a blank line or non-throw code appears).
- **Language keywords over BCL names**: `string`/`int`/`double`, not `String`/`Int32`/`Double`.
- **`nameof(...)` over string literals** for type/member/parameter names.
- **Trailing comma** after the last enum member and last multi-line initializer entry (keeps diffs clean).
- **Naming (internal/private additions to Ch 3)**: PascalCase for namespaces/types/members AND for `const` locals/fields; camelCase for locals, parameters, and private/internal fields (with the `_`/`s_`/`t_` prefixes); no `this.` unless invoking an extension method; no Hungarian notation.
- **Comments**: single-line `//` even across multiple lines (avoid `/* */`); only when they describe non-obvious intent; not at end-of-line unless very short.

## Mental Models
- **Braced `using`/`await using` only** — the braces mark exactly where the disposable is released; the braceless form invites scope creep and adds diff noise. (Exception: braceless `await using var ignored = x.ConfigureAwait(false);` to simulate stacked usings.)
- **`if … throw` over `?? throw` for validation** — assignment-expression-throw can leave some fields set and others not, causing subtle finalizer bugs; `if … throw` generalizes to types with/without finalizers.
- **Prefer object/collection initializers, expression-bodied members, auto-properties** — when the implementation is unlikely to change.
- **Careful with `readonly` on struct fields** — if the struct isn't `readonly`, method/property calls make defensive copies (perf hit).

## Code Examples
Braceless argument-validation preamble (the sanctioned exception):
```csharp
public void DoSomething(SomeCollection coll, int start, int count) {
    if (coll is null) throw new ArgumentNullException(nameof(coll));
    if ((uint)start >= (uint)coll.Count) throw new ArgumentOutOfRangeException(nameof(start));

    if (count == 0) { return; }   // blank line ended the preamble → braces required again
    ...
}
```
Field prefixes:
```csharp
[ThreadStatic] private static byte[] t_buffer;
private static int s_instanceCount;
private int _instanceId;
```

## Anti-patterns
- Braceless single-statement blocks (outside `case`/preamble); braceless `using`.
- BCL type names in code (`Int32 count`); `var` on factory/`TryParse`/well-known-return methods.
- `this.` field access when `_` prefix already disambiguates.
- Hungarian notation; `?? throw` for argument validation; `/* */` comments.

## Key Takeaways
1. These are suggestions — adopt them as a starting point for a new C# project, not a mandate.
2. Allman braces, braces required (except `case` and the validation preamble); braced `using` always.
3. 4-space indents, no tabs; canonical modifier order; explicit visibility always.
4. Language keywords over BCL names; `nameof` over strings; `if … throw` over `?? throw`.
5. `var` only for `new`/`as`/hard-cast; `_`/`s_`/`t_` field prefixes; PascalCase everywhere except private/internal fields, locals, and parameters.
6. Trailing commas, object/collection initializers, expression-bodied members, auto-properties where the implementation is stable.

## Connects To
- **Ch 3**: naming guidelines — this appendix adds the private/internal/local conventions the public guidelines deliberately omit.
- **Ch 5**: argument validation (§5.8.2) — the `if … throw` preamble.
- **Ch 7**: exception throwing.
- **Ch 9**: `using`/`await using`/`ConfigureAwait` (Dispose + async patterns).
- **App. D**: which of these style/API changes are binary/source breaking.
