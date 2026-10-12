# Chapter 6: Simplify data access with object-relational mappers

## Core Idea
An **object-relational mapper (ORM)** automates the boilerplate of converting between C# objects and relational database rows (and between C# types like `string`/`int` and DB types like `VARCHAR`/`Blob`). The chapter contrasts two kinds — a **micro-ORM** (**Dapper**) that only maps results and parameters but leaves SQL to you, and a **full ORM** (**Entity Framework Core**) that also writes the SQL and models object relationships. Along the way it evolves a factory into **dependency injection** using the `Microsoft.Extensions` libraries.

## Frameworks Introduced
- **Dapper (micro-ORM)**: A set of extension methods on `DbConnection` (`Query<T>`, `Execute`). Maps SQL result columns to `T` properties **by name** via reflection; maps object/anonymous-type properties to `@named` SQL parameters. **You still write the SQL.** Powers Stack Overflow/Stack Exchange.
- **Entity Framework Core (full ORM)**: Microsoft's full ORM for .NET Core (a rewrite, not a port, of EF). You define a `DbContext` with `DbSet<T>` collections; EF **generates SQL** for CRUD, understands object relationships (foreign keys) by convention, and translates **LINQ** queries to SQL. Schema is applied via **EF migrations** (`dotnet ef` CLI tool).
- **Dependency Injection in .NET Core**: `Microsoft.Extensions.DependencyInjection`. The **host** builds an `IServiceCollection`, registers implementations against interfaces, then calls `BuildServiceProvider()` to get an `IServiceProvider`. Consumers ask for `IScmContext` and never reference the concrete DB implementation.
  - **When to use**: whenever you want to swap implementations (e.g., SQLite for tests, PostgreSQL for prod) without tight coupling or a factory that must know every implementation.
  - **How**: `AddSingleton` / `AddTransient` / `AddScoped` register; `GetService(typeof(T))` or the `GetRequiredService<T>()` extension (from `...DependencyInjection.Abstractions`) resolve.

## Key Concepts
- **Micro-ORM drawback**: your SQL lives in application code, and SQL is **not standardized** — SQLite `last_insert_rowid()` vs SQL Server `SCOPE_IDENTITY()` vs PostgreSQL `INSERT INTO … RETURNING id`. Portability and SQL-injection risk remain your problem.
- **Factory → DI evolution**: `DataAccessFactory` (factory pattern) must reference *every* implementation (tight coupling; consumers download Oracle libs they don't use). Removing the `new` operator — first passing a `Type`, then having the host supply the *object* into a `Dictionary<Type,object>` — turns the factory into inversion of control (DI). The host now owns creation, so it can pass the connection string.
- **Anonymous type**: `new { To = ..., Subject = ... }` — a read-only class whose name you don't care about; used to hold Dapper parameters inline. Property names are **case-sensitive** matches to `@params`.
- **EF conventions**: an `Id` or `<ClassName>Id` property = the identity/primary key; a `PartType Part` navigation property = a one-to-one relationship with a foreign key. No manual `PartTypeId` wiring needed (unlike Dapper).
- **`DbSet<T>` is not an in-memory list**: LINQ over it is translated to SQL and executed in the DB; only retrieved objects are tracked. `SaveChanges()` flushes inserts/updates/deletes.
- **Configuration**: `ConfigurationBuilder` chains sources (`AddInMemoryCollection`, `AddJsonFile("config.json", optional:true)`) then `.Build()` → `IConfigurationRoot`. **Last source added wins / is searched first**; put defaults in the in-memory collection added first.

## Mental Models
- **Dapper = ADO.NET with the tedious parts removed.** `Query<T>` ≈ `ExecuteReader` + manual row mapping; `Execute` ≈ `ExecuteNonQuery` (returns rows affected). One line replaces ~8 statements.
- **DI = the host injects dependencies instead of the object fetching them.** Object A no longer creates B; the creator of A supplies B. This is inversion of control.
- **EF = you model objects, EF speaks SQL.** You write LINQ; EF picks the provider's dialect. Same C# code runs against any supported database.

## Anti-patterns
- **Factory that references every implementation**: forces consumers to depend on DB drivers they'll never use and requires a new package release to add a DB. Use DI instead.
- **Hard-coding the connection string** (`Data Source=:memory:`): breaks per-environment deployment. Use the configuration library.
- **Singleton context in parallel unit tests**: xUnit runs tests in random order and in parallel; a shared singleton `IScmContext` lets one test's writes corrupt another's expectations. Use `AddTransient` for isolation.
- **Depending on `...DependencyInjection.Abstractions` in a published library**: forces a DI implementation on consumers. Use the built-in `IServiceProvider.GetService(typeof(T))` instead of the `GetRequiredService<T>()` extension.
- **Returning `IEnumerable` when you must fully materialize** (e.g. deleting rows while iterating): return an **array** so all rows are read before side effects; `IEnumerable` streams lazily.

## Code Examples
```csharp
// --- Dapper: query, insert-with-returned-id, and a transaction ---
using Dapper;

// SELECT — maps columns to PartType properties by name (no column list needed)
Parts = connection.Query<PartType>("SELECT * FROM PartType");   // IEnumerable<PartType>

public void CreateOrder(Order order)
{
    var transaction = connection.BeginTransaction();
    try
    {
        // Query<int> returns IEnumerable<int>; First() grabs the new id.
        order.Id = connection.Query<int>(
            @"INSERT INTO [Order] (SupplierId, PartTypeId, PartCount, PlacedDate)
              VALUES (@SupplierId, @PartTypeId, @PartCount, @PlacedDate);
              SELECT last_insert_rowid();",
            order, transaction).First();          // whole object maps to @params

        // Execute == ExecuteNonQuery; anonymous type supplies the parameters
        connection.Execute(
            @"INSERT INTO SendEmailCommand ([To], Subject, Body)
              VALUES (@To, @Subject, @Body)",
            new { To = order.Supplier.Email,
                  Subject = $"Order #{order.Id} for {order.Part.Name}",
                  Body = $"Please send {order.PartCount} items" },
            transaction);                          // same transaction on both

        transaction.Commit();
    }
    catch { transaction.Rollback(); throw; }
}

// --- Registering services in IServiceCollection with a lifetime (host owns creation) ---
var serviceCollection = new ServiceCollection();

// Singleton: one shared instance for every resolve
IScmContext ctx = new SqliteScmContext(conn);
serviceCollection.AddSingleton<IScmContext>(ctx);

// Transient: factory delegate runs on every resolve -> fresh instance/DB per test
serviceCollection.AddTransient<IScmContext>(provider =>
{
    var conn = new SqliteConnection("Data Source=:memory:");
    conn.Open();
    return new SqliteScmContext(conn);
});

IServiceProvider services = serviceCollection.BuildServiceProvider();
var context = services.GetRequiredService<IScmContext>();       // resolve

// --- EF Core: DbContext + DbSet + LINQ ---
using Microsoft.EntityFrameworkCore;

public class EfScmContext : DbContext
{
    public DbSet<PartType> Parts { get; set; }
    public DbSet<InventoryItem> Inventory { get; set; }
    public DbSet<Supplier> Suppliers { get; set; }

    protected override void OnConfiguring(DbContextOptionsBuilder options)
        => options.UseSqlite("Filename=efscm.db");
}

using (var ctxt = new EfScmContext())
{
    var part = new PartType { Name = "Widget" };
    ctxt.Parts.Add(part);
    ctxt.SaveChanges();                              // EF emits INSERT

    var got = ctxt.Parts.Single(p => p.Name == "Widget");  // LINQ -> SQL
    ctxt.Parts.Remove(got);
    ctxt.SaveChanges();                              // EF emits DELETE
}
```
- **What it demonstrates**: Dapper collapses ADO.NET boilerplate to one line per statement while keeping explicit SQL and transactions; DI moves object creation to the host with an explicit lifetime; EF Core removes SQL entirely, mapping objects and LINQ to generated SQL.

## Reference Tables

**Micro-ORM vs full ORM vs hand-rolled ADO.NET**

| Dimension | Hand-rolled ADO.NET (ch 5) | Dapper (micro-ORM) | EF Core (full ORM) |
|---|---|---|---|
| Who writes SQL | You | You | EF generates it |
| Object↔row mapping | Manual (`reader.GetInt32`) | Auto by name (reflection) | Auto by convention |
| Relationships/FKs | Manual | Manual (`item.Part = …`) | Understood (navigation props) |
| Boilerplate | Highest | Low | Lowest |
| Control / performance | Highest | Near-native | Good, less control |
| Portability across DBs | None (raw SQL) | None (raw SQL) | High (providers) |
| Schema management | Manual | Manual | **EF migrations** |
| Pick when | Complex mapping or max perf | Productivity + keep SQL/perf | Max productivity, LINQ, multi-DB |

**DI lifetimes (`IServiceCollection`)**

| Lifetime | Instances created | Registration | Use for |
|---|---|---|---|
| **Transient** | New every resolve (needs a factory delegate) | `AddTransient<I>(provider => …)` | Isolation — fresh state per resolve; parallel/atomic tests |
| **Scoped** | One per scope (e.g. per web request) | `AddScoped<I,Impl>()` | Per-request services (e.g. a request-bound `DbContext`) |
| **Singleton** | One shared for app lifetime | `AddSingleton<I>(instance)` | Shared/expensive state (e.g. one in-memory SQLite DB shared across tests) |

## Worked Example
Starting from ch 5's hand-rolled `ScmContext` (manual `DbCommand`/`DbDataReader`):

1. **Swap to Dapper**: add the `Dapper` package; replace the whole `ReadParts` loop with `conn.Query<PartType>("SELECT * FROM PartType")`. Replace the 8-statement `CreateOrder` insert with a single `Query<int>(…).First()` to get the id, wrapped in a `BeginTransaction()`/`Commit()`/`Rollback()` block that also runs the `SendEmailCommand` insert via `Execute`. Because Dapper can't resolve relationships, still set `item.Part = Parts.Single(p => p.Id == item.PartTypeId)` manually.
2. **Split by DB behind an interface**: define `IScmContext`; implement `SqliteScmContext : IScmContext` in its own `SqliteDal` package.
3. **Inject via DI**: in the xUnit fixture (the host), build a `ServiceCollection`, create an in-memory SQLite connection + schema, register `AddTransient<IScmContext>(…)` (so each test gets its own DB), and expose `BuildServiceProvider()`. The test resolves via `fixture.Services.GetRequiredService<IScmContext>()` — it never references SQLite.
4. **Configure the connection string**: replace hard-coded `:memory:` with a `ConfigurationBuilder().AddInMemoryCollection(defaults).AddJsonFile("config.json", true).Build()`, reading `configRoot["ConnectionString"]`.
5. **EF Core alternative**: drop the per-DB packages. Give `InventoryItem`/`Supplier` a `PartType Part` navigation property (EF infers the FK). Define `EfScmContext : DbContext` with `DbSet<>`s and `UseSqlite`. Generate schema with the CLI (run against the test project, which stands in as the required console app):
   ```bash
   dotnet ef --startup-project ../EfScmDalTest migrations add EfScmMigration
   dotnet ef --startup-project ../EfScmDalTest database update
   ```
   Tests now use `ctxt.Parts.Add(...)`, `SaveChanges()`, and LINQ (`Single`, `FirstOrDefault`) — no SQL and no DI needed.

## Key Takeaways
- ORMs eliminate most object↔table boilerplate; choose the *type* by how much control vs productivity you need.
- **Dapper**: keep your SQL, lose the mapping boilerplate, keep near-native performance — but you own portability and injection risk.
- **EF Core**: model classes + `DbContext`/`DbSet` + LINQ; EF writes the SQL and manages schema via **migrations** (`dotnet ef`). Migrations need a console app (use the test project) and, on SQLite, only *create* — they don't *update* existing DBs.
- **DI** decouples business code from a concrete DB: register once in `IServiceCollection`, resolve an interface, pick **Transient/Scoped/Singleton** deliberately.
- The `Microsoft.Extensions` family (DependencyInjection, Configuration) is built on .NET Standard and reused throughout the book; prefer `IServiceProvider`/`IConfiguration` abstractions to avoid forcing dependencies on consumers.

## Connects To
- **Ch 5**: replaces the hand-rolled `DbCommand`/`DbDataReader` data-access layer — the manual column reads, per-parameter `AddParameter` calls, and `ExecuteScalar` id retrieval — with Dapper one-liners or EF's generated SQL.
- **Ch 7**: the same `IServiceCollection`/DI and configuration mechanics wired here get reused when composing ASP.NET Core services and fetching data over the network from other services.
