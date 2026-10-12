# Chapter 11: Local Development & CLI

## Core Idea

Supabase ships a single CLI that runs the *entire* stack (Postgres, Auth/GoTrue, Storage, PostgREST, Realtime, Edge Functions, Studio, an SMTP catcher) locally inside Docker. The workflow is: develop locally against disposable containers, capture every database change as a versioned SQL migration committed to git, then push those migrations to a linked remote project. Two commands bootstrap everything: `supabase init` (creates the `supabase/` folder + `config.toml`) and `supabase start` (boots the Docker stack). Local dev is faster (instant feedback), offline-capable, free (no quota), private (data stays local), and reproducible (reset to a known state anytime).

## Frameworks Introduced

- **Imperative migrations**: hand-written, ordered SQL DDL files in `supabase/migrations/`; you author each forward change. The source of truth for what gets deployed.
- **Declarative schemas**: define the *desired end state* in `supabase/schemas/*.sql`; the CLI generates migrations for you via `db diff`. Edit entities (views, functions) in place instead of recreating them.
- **pgTAP testing**: transaction-wrapped, in-database unit tests (`supabase test db`) for structure, functions, and especially RLS policies.
- **Seeding**: idempotent data population (`supabase/seed.sql`) run on first `start` and every `db reset`, after migrations.
- **Linking + push**: connect local project to a remote (`supabase link`), then `db push` migrations or `db pull` remote schema.

## Key Concepts

- **The `supabase/` folder** is committed to version control; it holds `config.toml`, `migrations/`, `schemas/`, `seed.sql`, `functions/`, and `tests/`.
- **Migrations are forward-only in production.** To "undo" deployed changes, write a new down-migration; never reset a deployed version.
- **`db diff` powers declarative schemas** using the `migra` tool — it compares declared schema vs. current migrations and emits the incremental DDL.
- **Seeding is deterministic**: glob-matched seed files run in lexicographic order, deduplicated; only put `INSERT`s in seeds, never DDL.
- **`config.toml` supports `env(VAR)`** to pull secrets from a root `.env` (gitignored) — used for OAuth provider keys and other secrets.
- **Mailpit** (localhost:54324) captures all auth emails locally; the default email sender is dev-only and rate-limited.

## Mental Models

- **Database-as-code**: every schema change lives in a file, reviewable in PRs, reproducible on any machine. The DB is rebuildable from `migrations/` + `seed.sql`.
- **Declarative = desired state, migration = the diff to get there.** You edit the schema; the CLI computes the steps. (Analogous to Terraform plan/apply.)
- **Reset is your undo button** during development: `db reset` drops, re-applies all migrations, then re-seeds — back to a known, clean state.
- **Local-first, deploy-later**: prove changes against the local stack, commit migrations, push to remote. Remote is just another database that consumes the same migration files.

## Anti-patterns

- Putting schema/DDL statements in `seed.sql` (seeds are for data only).
- Resetting or rewriting a migration version already deployed to production (breaks forward-only invariant; risks data loss).
- Committing `.env` to git (use `env()` references + `.gitignore`).
- Exposing the local dev stack on an untrusted network (bind to 127.0.0.1 via a dedicated Docker network).
- Relying on `db diff` for things `migra` can't track: DML, RLS `alter policy`, materialized views, comments, partitions, `create domain`, publication changes — use hand-written migrations for these.
- Application-level tests assuming a clean DB (use unique IDs per suite instead of resetting).

## Code Examples

```bash
# Bootstrap and run the stack
supabase init                 # creates supabase/ + config.toml (commit it)
supabase start                # boots Docker stack (Studio :54323, DB :54322, API :54321)

# Imperative migration workflow
supabase migration new create_employees_table   # writes empty timestamped SQL file
# ...author DDL in supabase/migrations/<ts>_create_employees_table.sql...
supabase db reset             # drop, re-apply ALL migrations, then run seeds

# Declarative schema workflow
# 1. edit supabase/schemas/employees.sql (desired state)
supabase db diff -f add_age   # generate incremental migration from the diff
supabase migration up         # apply pending migrations to local DB

# Deploy to remote
supabase login
supabase link
supabase db push              # apply local migrations to linked remote

# Pull an existing remote schema into declarative files
supabase db dump > supabase/schemas/prod.sql

# Roll back locally during dev (NOT for deployed versions)
supabase db reset --version 20241005112233

# Safely stop, preserving schema + data first
supabase db diff -f my_schema
supabase db dump --local --data-only > supabase/seed.sql
supabase stop --no-backup
```

- **What it demonstrates**: the two coexisting change paths (imperative `migration new` vs. declarative `schemas/` + `db diff`), how `migration up`/`db reset` apply them locally, and how `link` + `db push` promote the same files to a remote. `db diff -f` is the bridge that turns desired-state edits into reviewable forward migrations.

## Reference Tables

| Command | Purpose |
|---|---|
| `supabase init` | Create `supabase/` folder + `config.toml` |
| `supabase start` / `supabase stop` | Boot / halt the local Docker stack (`stop --no-backup` discards data) |
| `supabase migration new <name>` | Create empty timestamped migration file |
| `supabase migration up` | Apply pending migrations to local DB |
| `supabase migration list` | Show local vs. remote migration state |
| `supabase db diff -f <name>` | Generate migration from declared-schema diff (`migra`) |
| `supabase db reset [--version <ts>]` | Re-apply all (or up to a version) migrations + re-seed |
| `supabase db push` / `db pull [--schema X]` | Apply local migrations to remote / pull remote schema down |
| `supabase db dump [--local] [--data-only]` | Export schema or data SQL |
| `supabase db lint [--level error] [--linked]` | Postgres static analysis (`plpgsql_check`) |
| `supabase test new <name>` / `supabase test db` | Scaffold / run pgTAP tests |
| `supabase seed buckets` | Seed storage buckets |
| `supabase login` / `supabase link` | Authenticate / connect to a remote project |
| `supabase telemetry disable` | Opt out of usage telemetry |

| `config.toml` block | Effect |
|---|---|
| `[db.migrations] schema_paths = [...]` | Order/glob of declarative schema files (lexicographic) |
| `[db.seed] enabled = true; sql_paths = [...]` | Seed file globs (base dir is `supabase/`) |
| `[auth.external.<provider>]` | OAuth provider config; values via `env(VAR)` |

## Worked Example

```bash
# 1. New project
mkdir myapp && cd myapp
supabase init
supabase start                       # Studio at http://localhost:54323

# 2. Declarative schema: declare desired state
cat > supabase/schemas/employees.sql <<'SQL'
create table "employees" (
  "id" integer not null,
  "name" text
);
SQL

# 3. Generate + apply the migration
supabase db diff -f create_employees_table   # -> supabase/migrations/<ts>_create_employees_table.sql
supabase migration up

# 4. Evolve: append a column (append, don't reorder)
#    edit schemas/employees.sql -> add "age" smallint not null
supabase db diff -f add_age          # -> alter table ... add column "age" smallint not null;
supabase migration up

# 5. Seed + verify clean rebuild
echo "insert into employees (id, name, age) values (1, 'Ada', 30);" > supabase/seed.sql
supabase db reset                    # re-applies both migrations + seed -> known state
```

Result: `supabase/` now holds two ordered migrations, one declarative schema file, and a seed — the full DB is reproducible on any machine and PR-reviewable.

## Key Takeaways

- `init` + `start` give you the whole stack locally in Docker; commit the `supabase/` folder.
- Choose imperative migrations for full control (and unsupported entities), declarative schemas for ergonomic in-place edits with auto-generated diffs.
- `db diff -f` converts desired-state changes into versioned migrations; `migration up` and `db reset` apply them locally.
- Seeds are data-only, run after migrations on first start and every reset.
- Production migrations are forward-only; never reset a deployed version.
- Test RLS with pgTAP (`supabase test db`, transaction-wrapped) and use `env()` in `config.toml` to keep secrets out of git.

## Connects To

- **Database migrations & deployment** (linking, `db push`, CI/CD via `supabase/setup-cli`).
- **Self-hosting** (same stack, run via docker-compose instead of the CLI).
- **Auth** (OAuth provider config in `config.toml`, local email via Mailpit).
- **RLS / database security** (pgTAP policy testing).
- **Edge Functions** (Deno-based local testing through the same CLI).
