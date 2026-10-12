# Chapter 12: Deployment & Environments

## Core Idea
Supabase deployment centers on **version-controlled database migrations** flowing through environments (`local → staging → prod`) via Git and CI/CD. The recommended path: develop locally with the CLI, push to GitHub, auto-deploy from `main`. Branching (Pro Plan) adds isolated, data-less **preview environments** per pull request so migrations and config are validated before they touch production. The governing principle: once you use migrations, **never mutate the remote database directly** — all schema change goes through committed migration files.

## Frameworks Introduced
- **Local → Staging → Prod pipeline**: Three Git branches (`feature`/local, `develop`/staging, `main`/prod) each mapped to a separate Supabase project, with GitHub Actions promoting changes between them.
- **Maturity Model**: Practices evolve by team stage — Prototyping (Dashboard OK, capture with `db diff`) → Collaborating (everything in version control, stop using Dashboard for schema) → Production (no Dashboard changes, CI-only deploys, network restrictions, PITR) → Enterprise (separate Production org, restricted access).
- **Branching deployment DAG**: A 7-step Directed Acyclic Graph run on merge/commit — Clone → Pull → Health → Configure → Migrate → Seed → Deploy. Failed parent step skips all dependent children.
- **Configuration-as-code (`config.toml` + `[remotes]`)**: One file configures all branches; `[remotes.<name>]` blocks bind persistent branches (by `project_id`) to environment-specific settings, kept in version control.
- **Production Checklist**: Pre-launch gate across three axes — Security, Performance, Availability.

## Key Concepts
- **Preview branch**: Ephemeral isolated Supabase instance per PR; own API credentials; auto-paused on inactivity, deleted on PR merge/close; starts data-less.
- **Persistent branch**: Long-lived (staging/QA/develop); not auto-paused or deleted; configured via `[remotes]`.
- **Data-less branching**: New branches carry schema only, no production data — protects sensitive data; seed via `seed.sql`.
- **Migration history table**: `supabase_migrations.schema_migrations` tracks what's *applied per database*; Git tracks the *files*. Two separate systems that must stay in sync.
- **`migration repair`**: Updates the tracking table only (`--status applied|reverted`) — applies/reverts no SQL.
- **What gets deployed**: migrations in `supabase/`, plus Edge Functions and Storage buckets declared in `config.toml`. API/Auth/seed config ignored by default.
- **Required check**: GitHub branch-protection rule blocking PR merge until the "Supabase Preview" check passes — stops invalid migrations reaching prod.
- **Shared Responsibility Model**: Some operational concerns are Supabase's, some yours (you decide your own workflow).

## Mental Models
- **Git = files, Supabase = applied state.** Sync errors mean these two ledgers diverged; reconcile with `migration list` → `db pull` / `repair`.
- **The remote DB is read-only to humans.** All writes arrive as migrations through CI. The `postgres` password is never shared.
- **Branches are throwaway prod clones (minus data).** Test migrations end-to-end, then discard.

## Anti-patterns
- Editing the remote DB via SQL Editor / Table Editor — bypasses migration history; `db push` then fails with sync errors.
- Running `supabase db push` from a developer laptop in production — use CI with approval workflows instead.
- Concurrent `db push` from multiple machines — migrations apply in timestamp order; coordinate so only one person pushes.
- Reusing an already-modified project as a new staging project — CLI reapplies changes and conflicts; use a *new* project.
- Sharing production passwords (especially `postgres`) with the team.
- Using the Dashboard for schema changes once collaborating or in production.

## Code Examples
```yaml .github/workflows/staging.yml
name: Deploy Migrations to Staging

on:
  push:
    branches:
      - develop
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest

    env:
      SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
      SUPABASE_DB_PASSWORD: ${{ secrets.STAGING_DB_PASSWORD }}
      SUPABASE_PROJECT_ID: ${{ secrets.STAGING_PROJECT_ID }}

    steps:
      - uses: actions/checkout@v4

      - uses: supabase/setup-cli@v1
        with:
          version: latest

      - run: supabase link --project-ref $SUPABASE_PROJECT_ID
      - run: supabase db push
```
- **What it demonstrates**: Non-interactive CI deploy — three secrets (`SUPABASE_ACCESS_TOKEN`, `*_DB_PASSWORD`, `*_PROJECT_ID`) drive `link` then `db push`. The `production.yml` is identical except it triggers on `main` and uses `PRODUCTION_*` secrets.

```yaml .github/workflows/ci.yml (PR check)
on:
  pull_request:
  workflow_dispatch:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: supabase/setup-cli@v1
        with:
          version: latest
      - name: Start Supabase local development setup
        run: supabase db start
      - name: Verify generated types are checked in
        run: |
          supabase gen types typescript --local > types.gen.ts
          if ! git diff --ignore-space-at-eol --exit-code --quiet types.gen.ts; then
            echo "Detected uncommitted changes after build. See status below:"
            git diff
            exit 1
          fi
```
- **What it demonstrates**: PR-time validation — spins up local stack, fails if generated TS types drift from committed ones.

```toml config.toml — remote-specific environment binding
[remotes.staging]
project_id = "staging-project-ref"

[remotes.staging.api]
max_rows = 1000

[remotes.staging.db.seed]
enabled = true
sql_paths = ["./seeds/staging.sql"]

[remotes.production]
project_id = "prod-project-ref"
[remotes.production.db]
pool_size = 25
```
- **What it demonstrates**: Configuration-as-code — per-environment settings in one version-controlled file, each bound to a real `project_id`.

## Reference Tables

### Environments
| Env | Where | Branch | Deploy trigger |
|-----|-------|--------|----------------|
| Development | Local CLI stack | `feature/*` | `supabase db reset` (local) |
| Staging | Separate Supabase project | `develop` | push → `db push` via CI |
| Production | Separate Supabase project | `main` | push/merge → `db push` via CI or GitHub integration |

### Branch types
| Type | Lifespan | Auto-paused/deleted | Use for | Config |
|------|----------|---------------------|---------|--------|
| Preview | Ephemeral (per PR) | Yes | PR testing | `config.toml` synced |
| Persistent | Long-lived | No | staging/QA/develop | `[remotes.<name>]` |

### Deployment DAG steps (on merge)
| # | Step | Action |
|---|------|--------|
| 1 | Clone | Checkout repo at git branch |
| 2 | Pull | Fetch migrations from main project / init history table |
| 3 | Health | Wait ≤2 min for all services healthy |
| 4 | Configure | Apply `config.toml` (GitHub branching only) |
| 5 | Migrate | Apply pending migrations + vault secrets |
| 6 | Seed | Run seed files (persistent branches need it enabled) |
| 7 | Deploy | Deploy changed Edge Functions + secrets |

### CLI cheat
| Command | Purpose |
|---------|---------|
| `supabase init` / `link --project-ref $ID` | scaffold / connect |
| `supabase migration new <name>` | create migration file |
| `supabase db diff -f <name>` | generate migration from local changes |
| `supabase db reset` | recreate local DB, apply all migrations + seed |
| `supabase db push` (`--include-seed`) | apply migrations to remote |
| `supabase migration list` | compare local vs remote applied state |
| `supabase db pull` | capture remote schema into a migration |
| `supabase migration repair --status applied\|reverted <ts>` | fix history table only |

## Worked Example
Branch → preview → merge → prod flow:
```bash
# 1. Branch off staging, create migration locally
git checkout -b feat/employee develop
supabase migration new add_employee_table       # edit the .sql
supabase db reset                                # apply + test locally
git add supabase/migrations && git commit -m "Add employee table"
git push --set-upstream origin feat/employee
# 2. Open PR feat/employee -> develop
#    CI (ci.yml) runs; with branching enabled a preview branch spins up,
#    runs the DAG (Migrate/Seed), and posts deployment status on the PR.
#    A 'required check' blocks merge if migrations fail.
# 3. Merge to develop -> staging.yml runs `supabase db push` to STAGING.
# 4. After verifying staging, PR develop -> main; merge ->
#    production.yml runs `supabase db push` to PRODUCTION.
```

## Key Takeaways
- Develop locally, deploy via Git + CI; never push to prod from a laptop.
- Migrations are the single source of schema truth — keep Git files and the applied history table in sync.
- Branching gives data-less preview environments per PR; enable a required check to gate merges.
- Promote through `local → staging → prod`, each a distinct project, gated by approval workflows.
- Run the Production Checklist (RLS on all tables, SSL enforcement, network restrictions, MFA, PITR) before launch.

## Connects To
- **Local Development / CLI** (chapter): `supabase init`, `start`, `db reset`, type generation.
- **Branching configuration & secrets**: `config.toml`, `[remotes]`, dotenvx-encrypted env files.
- **Platform / Backups**: PITR, Read Replicas, Network Restrictions referenced in the checklist & maturity model.
- **Auth & Security**: RLS, SSL enforcement, rate limits, custom SMTP in the production checklist.
- **Terraform provider**: alternative IaC deployment path to the GitHub integration.
