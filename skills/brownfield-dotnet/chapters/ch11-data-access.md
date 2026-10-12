# Chapter 11: Re-factoring Data Access

## Core Idea
Data access is the most-written and most-painful layer in brownfield .NET apps; isolate it behind an anti-corruption interface, push business logic out of it (and out of stored procedures), then evaluate the three ways to build a DAL — hand-rolled, code-generated, or Object/Relational Mapper — against the fundamentals of a good data access layer.

## Frameworks Introduced

- **The three data-access techniques (hand-rolled / generated / ORM)**: The three main options for creating a DAL, each with different flavors, benefits, and pitfalls.
  - When to use: Choose based on project constraints, team skills/schedule, corporate policy, and the state of your current DAL — not on theoretical purity.
  - How: Hand-rolled = build everything from the .NET BCL (ADO.NET) by hand. Generated = a tool reads the database and emits an object model from developer-authored templates. ORM = define the object model independently, map it to tables, and let the tool generate parameterized SQL at runtime.
  - Why it works / failure mode: ORMs are usually feature-complete (lazy loading, Unit of Work) and minimize code to maintain — the authors openly favor them. Hand-rolled is application-specific and effort-heavy; generated code becomes a volatile maintenance burden (manual edits get overwritten; teams eventually abandon generation and hand-edit).

- **Object/Relational Mapper (ORM)**: A DAL implementation where you define objects independent of the DB, provide a mapping, and the ORM generates CRUD SQL inside itself.
  - When to use: Complex object graphs you constantly traverse to save/update; changing data store or domain model; when you want lazy loading/caching as config toggles.
  - How: Write a mapping (e.g. Fluent NHibernate `ClassMap<T>`) declaring table, id/generator, and property-to-column maps; reference the assembly.
  - Why it works / failure mode: Less code, parameterized SQL (immune to injection), most DAL features built in. Failure modes: configuration/mapping is fragile and not strongly tied to schema (rename a column, app still compiles — integration tests catch it), learning curve, and DBA resistance to "magic" SQL.

- **Repository pattern (anti-corruption layer over data access)**: A generic `IRepository<T>` interface contract that calling code works against, with specific sub-interfaces (e.g. `ICustomerRepository`) for class-specific queries.
  - When to use: Always — the first refactoring step before touching DAL internals.
  - How: Define generic CRUD interface; derive specialized interfaces for criteria-based finds; have DAL classes implement them; calling code depends on the interface.
  - Why it works / failure mode: Lets you mock the DAL (testability) and refactor internals freely as long as the contract holds. Generic interface can't express class-specific searches — that's the intended boundary, handled by derived interfaces.

- **Fundamentals of a good data access layer (Features of a DAL)**: Encapsulation, Unit of Work/transactions, Persistence Ignorance, Persistence by Reachability, Dirty Tracking, Lazy Loading, Caching.
  - When to use: As an evaluation checklist for any DAL — implement only what the current code needs (YAGNI).
  - How: See Key Concepts; apply incrementally, profile before optimizing.
  - Why it works / failure mode: Several (dirty tracking, lazy loading, caching) are performance optimizations — implementing them speculatively is premature optimization. ORMs supply most of them for free.

## Key Concepts
- **Encapsulation (DAL)**: A good DAL never requires callers to know about connections; passing connection strings/objects or checking `System.DBNull` upward is "misencapsulation."
- **Shotgun Effect**: Poor encapsulation forces one logical change to be made in many scattered places — prohibitively costly.
- **Unit of Work**: Bundle multiple DB calls, run them in one transaction (open before first, commit/rollback after last) so callers needn't pass connection/transaction objects around.
- **Persistence Ignorance**: Business entities (Customer, Order) carry no knowledge of how they're persisted — no mapping attributes; preserves Single Responsibility.
- **Persistence by Reachability**: The DAL traverses the full object graph from a single entry point and persists every publicly reachable entity (the DDD "aggregate root" idea).
- **Dirty Tracking**: The DAL identifies which objects were added/modified/deleted so it persists only those (vs. naïvely re-saving everything); naïve form is an `IsDirty` flag.
- **Lazy Loading**: Defer reads until the data is actually needed — variants: lazy initialization (explicit `.Load()`), virtual proxy, ghost, value holder.
- **Caching**: Keep frequently-read, slowly-changing data locally; the hard part is invalidation ("it depends"), web-farm/cross-session concerns.
- **Command/Query Separation**: Each method is either a command (acts/writes) or a query (reads), never both — enables pub/sub and scalable designs.
- **Anti-corruption layer**: A contract (interface) over the DAL isolating callers from internal changes (from Ch 8).

## Mental Models
- Use an **anti-corruption interface + integration tests** before mucking with any DAL — they're the net that lets you back out changes and catch regressions.
- Use an **ORM** when the domain model/data store change often or object graphs are deep; use hand-rolled only when the app-specific DAL is genuinely feature-complete and YAGNI-justified.
- **Profile before you optimize**: lazy loading, caching, and dirty tracking are optimizations — don't add them until users actually feel the pain. "Fast enough" and perceived performance win.
- Use **persistence ignorance** when you don't control the data store or it changes often; skip it if both schema and model are stable.

## Anti-patterns
- **Hard-coded SQL in ASPX code-behind**: A column rename ripples to every page; typos surface only by accidental runtime spot-checks.
- **Business logic in stored procedures**: Logic hidden where developers don't look; changes silently break things (especially conditional/branching SQL) with no compile-time or test safety net; often guarded by over-protective DBAs.
- **Dynamic SQL built by string concatenation in a proc**: e.g. `'UPDATE Users SET ' + @field + ' = ''' + @newValue` — SQL-injection prone and unmaintainable.
- **Datasets through every layer**: "Datasets are evil" — a leaky, data-centric abstraction that tightly couples the UI to table/column names.
- **Leaky connection management**: Service/business code opening, closing, or passing connection/transaction objects to the DAL.
- **Mapping attributes on entities**: `[TableMap]`/`[PropertyMap]` on the domain class violates SRP — two reasons to change (model vs. store).
- **Premature optimization / building for future use**: Adding transaction management, caching, or relationship support "because we'll need it" before the code in hand requires it.

## Code Examples
```csharp
public interface IRepository<T>
{
    IEnumerable<T> FetchAll();
    void Add( T itemToAdd );
    T FetchById( long itemId );
    void Update( T itemToUpdate );
    void Delete( T itemToDelete );
}

public interface ICustomerRepository : IRepository<Customer>
{
    IEnumerable<Customer> FetchByCityMatching( string cityToMatch );
}
```
- **What it demonstrates**: A generic repository contract (the anti-corruption layer) reused and extended for class-specific queries (Listing 11.4).

```csharp
public class CustomerMap : ClassMap<Customer>
{
    public CustomerMap()
    {
        WithTable("Customer");                          // table
        Id(x => x.Id, "CustomerId").GeneratedBy.Identity();
        Map(x => x.Name,  "CustomerName");              // property -> column
        Map(x => x.Email, "EmailAddress");
        Map(x => x.Phone, "PhoneNumber");
    }
}
```
- **What it demonstrates**: A Fluent NHibernate ORM mapping that keeps the `Customer` entity persistence-ignorant — column changes are isolated to this one class (Listing 11.7).

## Reference Tables

| Technique | What it is | Pros | Cons / Failure mode |
|---|---|---|---|
| Hand-rolled | Built from .NET BCL (ADO.NET) by hand | Application-specific (only needed features, YAGNI); full control | Huge effort; correctness of each feature is on you; app-specific knowledge per app; rarely implements UoW/lazy loading/caching well |
| Code generation | Tool reads DB, emits object model from templates | Less tedious than hand-rolling; pre-bundled pattern templates | Generated code is volatile (manual edits overwritten → partial classes/inheritance hacks); template learning curve; still a maintenance burden; often abandoned mid-project |
| ORM | Map objects to tables; tool generates SQL at runtime | Feature-complete (lazy loading/UoW as config); far less code; parameterized SQL (no injection) | Mapping config is fragile & non-intuitive; ramp-up time; can't "throw code" at problems; DBA resistance |

| Deployment of data access | Trade-off |
|---|---|
| Stored procedures | Deployable separately, but only safe if joint deploys are well-managed and integration-tested |
| Inline SQL | All artifacts in the assemblies — simpler deploy; hotfixes need app redeploy |
| ORM | Just ship the third-party assemblies; but DB changes force app redeploy (mappings) |

## Worked Example
Persistence by Reachability — collapsing graph-walking persistence. The brownfield code manually walks the object graph to save an invoice and everything it touches:

```csharp
public void Save(Invoice invoiceToSave) {
    _invoiceRepository.Save(invoiceToSave);
    _customerRepository.Save(invoiceToSave.Customer);
    foreach(var lineItem in invoiceToSave.Items)
        _invoiceRepository.SaveItem(lineItem);
}
```

For deep graphs this call stack grows several levels and breeds duplicate, brittle code. The goal is one entry point that hides the traversal:

```csharp
public void Save(Invoice invoiceToSave) {
    _invoiceRepository.Save(invoiceToSave);   // also persists Customer + Items implicitly
}
```

Whether you push the graph-walk inside `Save` (hand-rolled) or let an ORM do it, the result is Persistence by Reachability: the DAL persists every publicly reachable entity to the full depth of the graph, and the caller coordinates nothing. The authors note doing this reliably by hand is hard — most third-party ORMs implement it to some degree, so deep, frequently-traversed graphs are a strong signal to adopt an ORM.

## Key Takeaways
1. Isolate data access first (Ch 8 layering), incrementally and DRY — kill code that causes ripple effects before changing anything.
2. Put a Repository / anti-corruption interface over the DAL so you can mock it and refactor internals freely behind the contract.
3. Always have integration tests in place before touching CRUD or moving logic — they're your insurance against silent regressions.
4. Centralize business logic in the business layer; remove it from stored procedures (especially insert/update/delete) and from the DAL — but leave complex, vendor-specific SELECT procs alone.
5. Treat the DAL "features" (encapsulation, UoW, persistence ignorance, reachability, dirty tracking, lazy loading, caching) as a YAGNI checklist; most are optimizations — profile before implementing.
6. Of hand-rolled / generated / ORM, the authors strongly favor ORMs: less code, parameterized SQL, built-in features, big maintenance savings.
7. Don't forget deployment: automate DB versioning/migrations and per-environment connection strings into the build script.

## Connects To
- **Ch 8 (Layering)**: This chapter is the DAL counterpart to UI layering; reuses logical layers, the anti-corruption layer, and aspect-oriented dirty tracking.
- **Ch 4 (Automated Testing)**: Integration tests are the prerequisite net for refactoring CRUD and removing business logic; mockable repositories enable unit testing.
- **Ch 7 (Principles)**: DRY, SRP, Separation of Concerns, YAGNI, and premature optimization underpin nearly every recommendation here.
- **Ch 9 (IoC)**: Repository interfaces are the seams that dependency injection wires up.
- **Ch 3 (Continuous Integration)**: Database versioning and connection-string swapping belong in the automated build/release scripts.
- **Ch 10 (UI)**: Same SoC discipline — get data access (and datasets) out of the presentation layer.
