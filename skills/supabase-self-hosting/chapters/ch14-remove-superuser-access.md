# Chapter 14: Remove Superuser Access from Studio

## Core Idea
Align self-hosted with the platform's late-2022 security change: stop Studio from operating as the `supabase_admin` superuser and move object ownership to the `postgres` role. This migration was never auto-applied to self-hosted, so objects created via Studio may still be `supabase_admin`-owned.

## Frameworks Introduced
- **Ownership reassignment + role switch** (3 steps):
  - When to use: hardening self-hosted to match platform behavior, or fixing migrations that fail when run as `postgres`.
  - How: (1) `sh utils/reassign-owner.sh` reassigns `public`-schema object ownership `supabase_admin`→`postgres`; (2) set Studio/meta env vars to `postgres`; (3) `down && up -d`; verify `select current_user;` returns `postgres`.

## Key Concepts
- **`supabase_admin` vs `postgres`**: superuser vs the intended non-super role for dashboard operations.
- **Scope of `reassign-owner.sh`**: only the `public` schema — Supabase-managed and custom schemas untouched.
- **`POSTGRES_USER_READ_WRITE` (studio)** and **`PG_META_DB_USER` (meta)**: the two env vars to flip to `postgres`.

## Mental Models
- Think of it as catching self-hosted up to a change the platform made years ago: less privilege for Studio, consistent ownership for new objects.

## Anti-patterns
- **Assuming self-hosted already did this**: it didn't — the migration was platform-only.
- **Expecting custom schemas to be reassigned**: the script only covers `public`.
- **Skipping the restart**: env changes need `down && up -d`.

## Code Examples
```sh
sh utils/reassign-owner.sh        # public-schema objects -> postgres
```
```yml name=docker-compose.yml
studio:
  environment:
    POSTGRES_USER_READ_WRITE: postgres
meta:
  environment:
    PG_META_DB_USER: postgres      # was supabase_admin
```
```sh
docker compose down && docker compose up -d
```
```sql
select current_user;   -- expected: postgres
```
- **What it demonstrates**: the full reassign → reconfigure → restart → verify flow.

## Reference Tables
| Step | Action |
|---|---|
| 1 | `sh utils/reassign-owner.sh` (public schema only) |
| 2 | `studio.POSTGRES_USER_READ_WRITE: postgres` |
| 2 | `meta.PG_META_DB_USER: postgres` |
| 3 | `docker compose down && up -d` |
| Verify | `select current_user;` → `postgres` |

## Key Takeaways
1. Self-hosted never auto-applied the 2022 superuser-removal change.
2. `reassign-owner.sh` moves `public` object ownership to `postgres`.
3. Flip `POSTGRES_USER_READ_WRITE` (studio) and `PG_META_DB_USER` (meta) to `postgres`.
4. Restart with `down && up -d`; confirm `current_user` is `postgres`.
5. Custom/managed schemas are out of scope.

## Connects To
- **Ch 15**: "Legacy Studio configuration" troubleshooting references the same `POSTGRES_USER_READ_WRITE` setting.
- **Ch 1**: editing `docker-compose.yml` service env + restart workflow.
