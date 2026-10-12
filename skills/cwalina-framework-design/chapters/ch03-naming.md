# Chapter 3: Naming Guidelines

## Core Idea
Consistent, understandable names are one of the biggest contributors to framework usability. These conventions apply **only to publicly exposed APIs** (public/protected types, members, and their parameters) — not private fields, locals, or test code.

## Frameworks Introduced
- **Two casing styles**: `PascalCasing` (everything except parameters) and `camelCasing` (parameters only). No underscores, ever.
- **The two-letter-acronym rule**: 2-letter acronyms are fully capitalized (`IOStream`, `DBRate`); 3+ letter acronyms capitalize only the first letter (`HtmlTag`, `XmlNode`). In a camel-cased parameter, all leading acronym letters are lowercase (`ioStream`, `htmlTag`).
- **The "grep test" (Brad Abrams)**: to decide if an acronym is "well known," search the web for it — if the top results match your intended meaning, it qualifies; otherwise be descriptive.

## Key Concepts
- **Scenario naming over hierarchy naming**: name commonly used types for the *scenario*, not the inheritance position — `Printer` beats `PrintQueue`; reserve `File` for the type users instantiate, not an abstract base.
- **Nouns vs. verbs vs. adjectives**: classes/structs = nouns; methods/events = verbs; capability interfaces = adjectives (`IComparable<T>`); root interfaces = nouns (`IList<T>`).
- **Hungarian notation**: prefixing names with type/scope encoding (`uiCount`, `s_`) — banned for public APIs.
- **Assembly ≠ namespace**: DLLs/assemblies are deployment/packaging boundaries; namespaces are logical groupings. Design them independently. The CLR enforces no relationship.
- **Type parameter (`T`)**: generics identifier; use `T` for single, `TDescriptive` for multiple/constrained.

## Reference Tables

Capitalization by identifier kind:

| Identifier | Casing | Example |
|---|---|---|
| Namespace, Type, Interface | Pascal | `System.Security`, `StreamReader`, `IEnumerable` |
| Method, Property, Event | Pascal | `ToString()`, `Length`, `Exited` |
| Public/protected static field | Pascal | `InfiniteTimeout`, `MinValue` |
| Enum value | Pascal | `FileMode.Append` |
| Generic type parameter | Pascal | `Task<TResult>`, `Parse<TEnum>` |
| Tuple element | Pascal | `(int Offset, int Length)` |
| **Parameter** | **Camel** | `ToInt32(string value)` |

Type-name suffix rules (apply to whole hierarchy):

| Base type | Rule |
|---|---|
| `System.Attribute` | DO add `Attribute` suffix |
| `System.Delegate` (event) | DO add `EventHandler`; other delegates → `Callback`; never `Delegate` |
| `System.EventArgs` | DO add `EventArgs` |
| `System.Exception` | DO add `Exception` |
| `System.Enum` | DO NOT add `Enum`/`Flag` suffix; don't derive — use `enum` keyword |
| `IDictionary<,>` | DO add `Dictionary` (takes precedence over Collection) |
| `IEnumerable/ICollection/IList` | DO add `Collection` (except `Queue`, `HashSet`, etc.) |
| `System.IO.Stream` | DO add `Stream` |

Common compound-word casing (treat closed-form compounds as single words):
`Callback` (not CallBack), `Endpoint`, `Filename`, `Metadata`, `Namespace`, `Placeholder`, `Timestamp`, `Username`, `Id` (not ID), `Ok` (not OK), `Email`, `Hashtable`, `WhiteSpace`, `Canceled` (one L).

## Mental Models
- **Test Boolean names in an `if` (Cwalina)**: `if(collection.Contains(item))` and `if(stream.CanSeek)` read naturally; prefer active voice (`CanSeek` over `IsSeekable`). Use `Is/Can/Has` prefixes only where they add value.
- **Naming new versions**: prefer a **suffix over a prefix** (`ReaderWriterLockSlim`), or a brand-new meaningful name; numeric suffix (`X509Certificate2`) is last resort; NEVER use `Ex`. Use `64` suffix only when retrofitting an existing 32-bit API (`PagedMemorySize64`).
- **Language-neutral names**: use CLR type names, not language aliases — `ToInt64`, not `ToLong`; `GetLength`, not `GetInt`.

## Anti-patterns
- **Overly general type names** (`Element`, `Node`, `Log`, `Message`): cause conflicts — qualify them (`FormElement`, `XmlNode`, `EventLog`, `SoapMessage`).
- **Type name == namespace name** in the same namespace (e.g., namespace `Debug` + class `Debug`).
- **Enum member prefixes** (`ImageModeBitmap`): unnecessary in .NET — members are scoped by the enum name; use `Bitmap`.
- **Property matching a `Get` method** (`TextWriter` property + `GetTextWriter`): the property should probably be a method.
- **`C` prefix on classes**; org-hierarchy-based namespaces (groups are short-lived); marketing-driven namespace names (burned into client code forever).

## Worked Example
The `Color.FromArgb` cautionary tale (Brad Abrams): the guideline was correctly followed (`Argb`, not `ARGB`), yet bug reports came in — *"all I see are methods to convert from argument b."* The real problem was **over-abbreviation**: `RGB` is well known, but `ARGB` (with alpha) is obscure. The lesson isn't "violate the casing rule" — it's that `FromAlphaRgb(int alpha, int red, int green, int blue)` would have been both clearer *and* more consistent. Over-abbreviation, not casing, was the defect.

## Key Takeaways
1. Favor readability over brevity: `CanScrollHorizontally` over `ScrollableX`, `HorizontalAlignment` over `AlignmentHorizontal`.
2. Classes = nouns, methods/events = verbs (with tense: `Closing`/`Closed`), capability interfaces = adjectives, all `I`-prefixed.
3. Reserve the best, most-intuitive names for the most-used types; name for scenario, not hierarchy.
4. Never rely on case alone to distinguish names (some CLR languages are case-insensitive).
5. No abbreviations/acronyms unless universally understood (`Id`, `Ok` are the rare sanctioned exceptions); ASCII only, no diacritics.
6. Class–interface standard-implementation pairs differ only by the `I` (`IComponent`/`Component`).
7. Name events with before/after tense; use `EventHandler<TEventArgs>` and the `(object sender, EventArgs e)` signature — don't roll your own delegate.

## Connects To
- **Ch 2**: the self-documenting principle — naming is its primary lever.
- **Ch 4**: choosing class vs. interface (section 4.3) informs noun-vs-adjective naming.
- **Ch 5**: member design — property-vs-method and event design details.
- **Ch 7**: exception naming (`Exception` suffix) + message design.
- **App. A**: C# coding-style casing conventions (internal/private).
- **App. B**: obsolete naming guidance (e.g., resource naming).
