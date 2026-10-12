# Appendix D: Breaking Changes

## Core Idea
Every change to a reusable library can break something — even a perf improvement can reveal a caller's race condition. This appendix classifies changes by *break type* and says whether the .NET BCL team would generally accept them (informative, not prescriptive — a small-audience library can tolerate more).

## Frameworks Introduced
- **The four break types**:
  - **Runtime break** — existing (unrecompiled) programs observably change/fail against the new library.
  - **Compilation break** — existing source fails to *recompile* against the new library.
  - **Recompile break** — behavior changes merely by recompiling (same source, new result).
  - **Reflection break** — observable only via reflection/metadata (e.g., `AssemblyQualifiedName`, `Type.IsSealed`).
  - (API reviews group compilation + recompile as **source-breaking**.)

## Reference Tables

Common changes and BCL-team acceptability (✅ generally allowed / ❌ generally not / ⚠️ contextual):

| Change | Verdict | Why |
|---|---|---|
| Rename assembly / namespace / type; change casing | ❌ | Name is type identity → equivalent to delete + recreate |
| Move type WITHOUT `[TypeForwardedTo]` | ❌ | = delete + recreate (assembly is part of identity) |
| Move type WITH `[TypeForwardedTo]` | ✅ | When technically required |
| Remove a type | ❌ | `TypeLoadException` at runtime |
| Seal an unsealed type | ❌ | Breaks existing subclasses |
| Unseal a sealed type | ✅ | Only metadata/reflection impact |
| Add `readonly` to a struct | ✅ | Callers benefit after recompile |
| Remove `readonly` from a struct | ❌ | Mutations leak to un-recompiled callers → subtle bugs |
| class ↔ struct (either direction) | ❌ | `TypeLoadException`, null-vs-default divergence |
| struct → `ref struct` | ❌ | Boxing/generic-arg/field uses break |
| `ref struct` → struct | ✅ | But can't be safely undone |
| Add member to an interface | ❌ | Implementers fail to initialize (`TypeLoadException`) |
| Add base interface to an interface | ❌ | Unless all implementers "duck-type" conform |
| Add `abstract` member | ❌ | Derived non-abstract types break |
| Add member to unsealed/sealed (concrete) type | ✅ | Only a hiding *warning* (unless warnings-as-errors) |
| Add `override` to unsealed type | ✅ | But un-recompiled derived base-calls skip it |
| Add first reference-type field to a struct | ❌ | Breaks `fixed`/`unmanaged`-constrained uses |
| Move member to a base **class** | ✅ | CLR handles gracefully (can't be undone) |
| Move member to a base **interface** / derived type | ❌ | Explicit-impl / not-found failures |
| Remove any (non-override) member | ❌ | `MissingMethod`/`MissingField`Exception |
| Remove override of a virtual member | ✅ | No observable runtime diff (caution advised) |
| Remove override of an abstract member | ❌ | Derived types lose the only implementation |
| Remove finalizer from unsealed type | ❌ | Derived types relying on `Dispose(false)` stop finalizing |
| Remove finalizer from sealed type | ✅ | Faster GC sweeps; assess `Dispose(false)` side effects |

## Key Concepts
- **"Close enough" resolution**: the CLR loads types/members lazily, so a runtime break may not surface until execution reaches (roughly) the start of a method that uses the changed type — JIT inlining/preload can move it earlier.
- **Namespace and assembly are part of type identity** — the CLR has no rename mechanism; any name/casing/namespace/assembly change ≈ delete + recreate.
- **Default parameters aren't real overloads** — changing a shipped default value is a recompile break (old callers keep the old value until they rebuild); use a sentinel if the default must evolve (cf. Ch 5).
- **Adding a value to an enum** is generally safe for input enums, risky for returned enums (callers may `switch` exhaustively — cf. Ch 4 §4.8.2).
- **Reflection is always fragile** — private/internal members accessed via reflection can break at any time; metadata changes are immediately visible.

## Mental Models
- **The lower the layer, the stricter the bar** — the BCL sits at the bottom of the ecosystem, so it rejects almost all runtime/source breaks; your library's tolerance scales with how many (and how uncontrolled) your consumers are.
- **Adding is safer than changing is safer than removing** — prefer adding new overloads/types/interfaces over modifying or deleting existing ones.
- **Some acceptable changes are one-way** — `ref struct`→struct and moving members to a base class are allowed but *cannot be safely undone*.
- **Recompile the whole graph after risky changes** — override skipping, default-value drift, and base-call encoding all differ between recompiled and non-recompiled callers.

## Key Takeaways
1. Classify any proposed change as runtime / compilation / recompile / reflection break before shipping it.
2. Names (assembly, namespace, type, casing) and identity (class↔struct, ref struct) are effectively immutable once public.
3. You can add members to concrete types and interfaces only safely for *concrete* types — adding to interfaces or as `abstract` breaks implementers.
4. Removing anything public (type, member, override of abstract, base-class finalizer) is a break; removing a virtual override or sealed-type finalizer is acceptable.
5. Widen, don't narrow: add overloads/sub-interfaces; never change a shipped default value or enum-return contract lightly.
6. Judge acceptability against your audience — the BCL's "unacceptable" may be fine for a small internal library.

## Connects To
- **Ch 3**: naming new versions of APIs (suffix over numeric over rename).
- **Ch 4**: class vs. interface evolution (§4.3); adding enum values (§4.8.2); struct `readonly`.
- **Ch 5**: default parameters and why changing them breaks callers (§5.1.1).
- **Ch 6**: sealing/unsealing, adding virtual/abstract members, base classes.
- **Ch 9**: `[TypeForwardedTo]`, Dispose/finalizer changes, variance changes.
- **App. B**: obsolete guidance (how to deprecate rather than break).
