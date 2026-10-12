# Chapter 5: Working with relational databases

## Core Idea
Access relational data in .NET Core using the low-level, database-agnostic **ADO.NET** types in the `System.Data.Common` namespace. Code against the abstract base types (`DbConnection`, `DbCommand`, `DbDataReader`, `DbTransaction`) so you can prototype and unit test against an in-memory **SQLite** database, yet run the same data-access library against a full database (SQL Server) in production. Build a hand-rolled data-access library (a "context" that hydrates objects from rows), always use **parameterized** commands, and wrap multi-step writes in **transactions** for all-or-nothing consistency.

## Frameworks Introduced
- **ADO.NET data-access pattern (`System.Data.Common`)**: Open a `Connection`, issue `Command`s, read rows with a `DataReader`, group writes in a `Transaction`.
  - When to use: low-level control, no ORM, or when learning what an ORM (ch 6) hides.
  - How: `new SqliteConnection("Data Source=:memory:")` → `Open()` → create command → `ExecuteScalar` / `ExecuteNonQuery` / `ExecuteReader`.
- **In-memory SQLite for prototyping & test**: NuGet `Microsoft.Data.Sqlite`, connection string `Data Source=:memory:`. No install; runs in-process (fine for dev/test, not production — app and DB compete for resources).
  - How: a **xUnit class fixture** (`IClassFixture<T>`) creates the schema + seed data on startup, exposes the open `Connection`, and disposes it.
- **Context class (hand-rolled mini-ORM)**: `ScmContext` takes a `DbConnection`, reads tables into `IEnumerable<T>` object collections ("hydration"), and exposes CRUD methods.
- **CQRS + eventual consistency**: inventory reads hit `InventoryItem`; writes are appended as `PartCommand` rows and applied later by a single-threaded processor. Trades consistency for availability (CAP theorem).

## Key Concepts
- **Connection string** keys a provider's connection pool; SQLite runs in-process (rare exception).
- **Three execute methods**: `ExecuteScalar` (single value, returns `object` → cast), `ExecuteNonQuery` (INSERT/UPDATE/DELETE/DDL, returns rows-affected `int`), `ExecuteReader` (returns `DbDataReader` for multi-row queries).
- **DataReader cursor** starts *before* the first row; `Read()` advances and returns `false` when exhausted. `GetInt32(0)`/`GetString(1)` read by zero-based column ordinal; they **cast, not convert** (wrong type → `InvalidCastException`). Indexer alternatives: `(int)reader[0]` or `(int)reader["Id"]`.
- **Program to abstractions**: `SqliteConnection : DbConnection`. Library targets low `netstandard` + `System.Data.Common` so any provider works.
- **Parameters**: `@name` placeholders bound via `DbParameter` (created by `cmd.CreateParameter()`, given `DbType`, `Direction`, `ParameterName`, `Value`).
- **Identity columns** (`INTEGER PRIMARY KEY` in SQLite = auto-populated) → retrieve inserted id with `SELECT last_insert_rowid();`. Don't use identity for row counts or ordering.
- **Nullable value types**: `DateTime?` (`.HasValue`, `default(DateTime?)`) model NULL columns; read with `reader.IsDBNull(i) ? default(DateTime?) : reader.GetDateTime(i)`.
- **Transaction** = atomic group; `DbTransaction` from `connection.BeginTransaction()`, assigned to `command.Transaction`, ended by `Commit()` or `Rollback()`.
- **ACID**: Atomic, Consistent, Isolated, Durable. (SQLite in-memory is transactional but not durable.)

## Mental Models
- **Hydration**: reading a row and setting all members of a matching object.
- **Rollback restores the database, not your objects**: after `transaction.Rollback()` you must manually restore in-memory state (e.g. `item.Count = oldCount`).
- **Single-writer, multiple-reader** is easier to keep consistent than multiple-writer — the reason writes funnel through the command queue.
- **Order may not matter**: prefer making the processor robust to out-of-order commands over depending on id/timestamp ordering.

## Anti-patterns
- **String-concatenated / interpolated SQL** → SQL injection and breakage on values containing `'` (e.g. `"John's bearing"`). *Always parameterize.* (xkcd 327.)
- **`SELECT *`** → column order/count not guaranteed; breaks silently on schema change. *List columns explicitly.*
- **Exposing internal `List<T>`** as-is → callers mutate it. *Expose `IEnumerable<T>`* to signal read-only.
- **Wrong Get accessor** (`GetString` on an int column) → `InvalidCastException`.
- **Updating a shared table from many writers directly** → race conditions; use the command-queue instead.
- **App-generated timestamps for ordering** across machines → clock skew; let the DB generate them.
- **Caching all data** (done here for simplicity) → not safe when data changes in a real app.

## Code Examples
```csharp
// Parameterized INSERT + retrieve auto-generated id (ExecuteScalar)
public void CreatePartCommand(PartCommand partCommand)
{
    var command = connection.CreateCommand();
    command.CommandText = @"INSERT INTO PartCommand (PartTypeId, Count, Command)
        VALUES (@partTypeId, @partCount, @command);
        SELECT last_insert_rowid();";                 // SQLite: id of inserted row
    AddParameter(command, "@partTypeId", partCommand.PartTypeId);
    AddParameter(command, "@partCount",  partCommand.PartCount);
    AddParameter(command, "@command",    partCommand.Command.ToString()); // enum -> 'Add'/'Remove'
    long partCommandId = (long)command.ExecuteScalar();
    partCommand.Id = (int)partCommandId;
}

// Helper: build a typed input DbParameter
private void AddParameter(DbCommand cmd, string name, object value)
{
    var p = cmd.CreateParameter();
    if (value == null) throw new ArgumentNullException("value");
    Type t = value.GetType();
    if      (t == typeof(int))      p.DbType = DbType.Int32;
    else if (t == typeof(string))   p.DbType = DbType.String;
    else if (t == typeof(DateTime)) p.DbType = DbType.DateTime;
    else throw new ArgumentException($"Unrecognized type: {t}", "value");
    p.Direction = ParameterDirection.Input;
    p.ParameterName = name;
    p.Value = value;
    cmd.Parameters.Add(p);
}

// Multi-step write wrapped in a transaction (all-or-nothing)
var transaction = context.BeginTransaction();        // connection.BeginTransaction()
try
{
    context.UpdateInventoryItem(item.PartTypeId, item.Count, transaction);
    context.DeletePartCommand(cmd.Id, transaction);  // same transaction on each command
    transaction.Commit();
}
catch
{
    transaction.Rollback();
    item.Count = oldCount;   // DB rolled back; restore the object manually
    throw;
}
```
- **What it demonstrates**: parameterized commands (no injection), enum↔string mapping, `ExecuteScalar` + `last_insert_rowid()`, `DbParameter` construction, and a `DbTransaction` guaranteeing that the inventory update and the queue-row deletion either both happen or neither does.

## Reference Tables

ADO.NET core types (all abstract in `System.Data.Common`; SQLite provides `Sqlite*` implementations):

| Abstract type | SQLite type | Role | Key members |
|---|---|---|---|
| `DbConnection` | `SqliteConnection` | Session to the database; disposable | `Open()`, `CreateCommand()`, `BeginTransaction()`, `Dispose()` |
| `DbCommand` | `SqliteCommand` | Carries SQL text + parameters, executes it | `CommandText`, `Parameters`, `Transaction`, `ExecuteScalar()`, `ExecuteNonQuery()`, `ExecuteReader()`, `CreateParameter()` |
| `DbDataReader` | (from `ExecuteReader`) | Forward-only cursor over result rows | `Read()`, `GetInt32(i)`, `GetString(i)`, `GetDateTime(i)`, `IsDBNull(i)`, `this[i]`/`this["col"]` |
| `DbTransaction` | `SqliteTransaction` | Groups commands atomically | `Commit()`, `Rollback()` |
| `DbParameter` | `SqliteParameter` | Safe, typed value binding | `ParameterName`, `DbType`, `Direction`, `Value` |

Execute-method selector:

| Method | Use for | Returns |
|---|---|---|
| `ExecuteScalar` | query yielding one value | `object` (cast it) |
| `ExecuteNonQuery` | INSERT/UPDATE/DELETE/DDL | `int` rows affected |
| `ExecuteReader` | multi-row query | `DbDataReader` |

## Worked Example — Widget Corp. supply-chain (SCM)
Goal: track parts, inventory counts, and auto-order low parts.

1. **Schema** (created by the test fixture, in-memory):
   ```sql
   CREATE TABLE PartType(Id INTEGER PRIMARY KEY, Name VARCHAR(255) NOT NULL);
   CREATE TABLE InventoryItem(
       PartTypeId INTEGER PRIMARY KEY, Count INTEGER NOT NULL, OrderThreshold INTEGER,
       FOREIGN KEY(PartTypeId) REFERENCES PartType(Id));
   -- plus PartCommand (queue), Order, SendEmailCommand, Supplier
   ```
   `PRIMARY KEY = NOT NULL + UNIQUE`; `FOREIGN KEY` enforces the one-to-one `InventoryItem→PartType` link.

2. **Data-access method with parameterized command + reader** (explicit columns, ordinal reads, hydrate + wire relationship via LINQ):
   ```csharp
   private void ReadInventory()
   {
       using (var command = connection.CreateCommand())
       {
           command.CommandText = @"SELECT PartTypeId, Count, OrderThreshold FROM InventoryItem";
           using (var reader = command.ExecuteReader())
           {
               var items = new List<InventoryItem>();
               Inventory = items;                         // exposed as IEnumerable
               while (reader.Read())
                   items.Add(new InventoryItem {
                       PartTypeId     = reader.GetInt32(0),
                       Count          = reader.GetInt32(1),
                       OrderThreshold = reader.GetInt32(2)
                   });
           }
       }
       // relationship in code: item.Part = Parts.Single(p => p.Id == item.PartTypeId);
   }
   ```

3. **Multi-step inventory update in a transaction** — the single-threaded processor drains the `PartCommand` queue, and per command atomically updates the count and deletes the queue row (see Code Examples). If the delete failed without a transaction, restart would double-apply the command and corrupt the count.

4. **Auto-ordering**: after applying commands, for each `InventoryItem` where `Count < OrderThreshold` and no outstanding order (`FulfilledDate == null`), call `OrderPart`, which builds a fully-hydrated `Order` and calls `CreateOrder`. `CreateOrder` inserts an `Order` row **and** a `SendEmailCommand` row inside one transaction — both or neither. A test (`TestCreateOrderTransaction`) omits `Order.Supplier`, forcing a `NullReferenceException` on the second insert, and asserts (via `SELECT Count(*)`) the first insert was rolled back.

## Key Takeaways
- Target `System.Data.Common` abstractions → same library runs on SQLite (dev/test) and SQL Server (prod).
- In-memory SQLite via a xUnit class fixture makes data-access tests fast and deterministic.
- Always parameterize; never concatenate values into SQL.
- List columns explicitly; read by ordinal in that order.
- `ExecuteScalar` + `last_insert_rowid()` retrieves auto-generated ids.
- Wrap any multi-statement write in a transaction; remember rollback restores only the DB — reset in-memory objects yourself.
- Use nullable value types (`DateTime?`) for nullable columns; guard with `IsDBNull`.
- Even a small model = a lot of hand-written boilerplate — motivating an ORM.

## Connects To
- **Ch 6 (ORMs / EF Core)**: removes nearly all of this boilerplate — no manual readers, hydration, parameter helpers, or `last_insert_rowid()`; the ORM maps objects↔tables and manages transactions for you.
- **Ch 4 (unit testing)**: the `IClassFixture<SampleScmDataFixture>` pattern and in-memory SQLite are how you unit-test data access — `Assert.Throws<NullReferenceException>` verifies transactional rollback.
- **`System.Transactions` (aside)**: `TransactionScope` + `using` gives ambient, per-thread transactions (simpler than passing `DbTransaction`), but .NET Core supports local transactions only (no DTC/distributed); provider must opt in, and SQLite didn't support it at the time of writing.
