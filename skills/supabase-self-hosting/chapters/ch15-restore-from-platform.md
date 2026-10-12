# Chapter 15: Restore a Platform Project to Self-Hosted

## Core Idea
Restore a managed-project database to self-hosted by dumping three SQL files with `supabase db dump` (roles, schema, data) and restoring with `psql` in one transaction with triggers disabled. The CLI's Supabase-specific filtering is what makes the dump restorable — raw `pg_dump` will not work.

## Frameworks Introduced
- **Three-file dump + single-transaction restore**:
  - When to use: migrating a platform DB to self-hosted (storage objects & functions handled separately).
  - How: dump `roles.sql --role-only`, `schema.sql`, `data.sql --use-copy --data-only`; restore via one `psql` with `--single-transaction`, `ON_ERROR_STOP=1`, and `SET session_replication_role = replica` before the data file.
- **`supabase db dump` over raw `pg_dump`**: excludes internal schemas, strips reserved roles, adds idempotent `IF NOT EXISTS`. Raw `pg_dump` includes internals → permission errors.
- **`session_replication_role = replica`**: disables triggers during data import → prevents issues like double-encryption of columns.

## Key Concepts
- **What's included**: schema, data, roles, RLS policies, functions, triggers, `auth.users`.
- **What's NOT** (manual): JWT secrets/API keys, OAuth provider settings, edge functions, storage objects, SMTP, custom domains/DNS.
- **Self-hosted connection string**: `postgres://postgres.your-tenant-id:[POSTGRES_PASSWORD]@<your-domain>:5432/postgres` (Supavisor session mode).
- **Version-mismatch hazards**: platform PG17 dump on self-hosted PG15 → PG17-only settings / newer tables/columns absent.

## Mental Models
- Think "data moves, config doesn't": the dump carries the database; auth secrets, providers, storage, SMTP all need reconfiguring on the new instance.
- Existing platform-issued JWTs die — different `JWT_SECRET` → users re-authenticate.

## Anti-patterns
- **Raw `pg_dump`**: includes Supabase internals → restore permission errors. Use `supabase db dump`.
- **Restoring without disabling triggers**: risks double-encryption and trigger side effects.
- **Pre-creating extensions skipped**: non-default extensions must be enabled on self-hosted first.
- **Expecting users' old tokens to work**: JWT secrets differ; they must re-auth.

## Code Examples
```sh
# Dump (three files)
supabase db dump --db-url "[CONN]" -f roles.sql --role-only
supabase db dump --db-url "[CONN]" -f schema.sql
supabase db dump --db-url "[CONN]" -f data.sql --use-copy --data-only
# Restore (one transaction, triggers off during data)
psql --single-transaction --variable ON_ERROR_STOP=1 \
  --file roles.sql --file schema.sql \
  --command 'SET session_replication_role = replica' \
  --file data.sql \
  --dbname "postgres://postgres.your-tenant-id:[POSTGRES_PASSWORD]@<your-domain>:5432/postgres"
```
- **What it demonstrates**: the canonical dump + restore commands.

## Reference Tables
Requires manual setup post-restore:
| Item | How |
|---|---|
| JWT secrets / API keys | generate new, update `.env` |
| OAuth/Auth providers | `GOTRUE_EXTERNAL_*` in `.env` |
| Edge functions | copy manually |
| Storage objects | transfer separately (Ch 12) |
| SMTP/email | `SMTP_*` in `.env` |
| Custom domains/DNS | point DNS to self-hosted |

Verify: `\dt public.*`, `SELECT count(*) FROM auth.users;`, `SELECT * FROM pg_extension;`.

## Worked Example — handling PG17→PG15 version mismatches
The data dump can contain PG17-only or newer-Auth artifacts that fail on PG15:
- `SET transaction_timeout = 0` (PG17-only) → `sed -i 's/^SET transaction_timeout/-- &/' data.sql`
- `COPY` for tables absent on self-hosted (`auth.oauth_clients`, `storage.buckets_vectors`, `storage.vector_indexes`) → comment out the `COPY ... FROM stdin;` line AND its `\.` terminator.
- `COPY` with newer columns (`auth.flow_state.oauth_client_state_id`, `linking_target_id`) → same.

Strategy: run the restore **without** `--single-transaction` first to surface all failures, fix them, then re-run **with** `--single-transaction`. Best: match versions — if platform is PG17, deploy self-hosted PG17 too (Ch 7). Custom roles with `LOGIN` lose passwords in the dump → `ALTER ROLE your_role WITH PASSWORD '...';`.

## Key Takeaways
1. Use `supabase db dump` (three files), never raw `pg_dump`.
2. Restore in one transaction with `ON_ERROR_STOP=1` and triggers disabled.
3. Dump carries schema/data/roles/RLS/functions/`auth.users`; secrets/providers/storage/SMTP are manual.
4. Old platform JWTs become invalid — users re-authenticate.
5. Enable non-default extensions on self-hosted before restoring.
6. Mind PG17→PG15 mismatches; dry-run without `--single-transaction` to find them; match versions when possible.

## Connects To
- **Ch 7**: match Postgres versions / consider PG17 self-hosted.
- **Ch 12**: storage objects copied separately via rclone.
- **Ch 1**/**Ch 2**: regenerate JWT secrets and API keys on the new instance.
- **Ch 14**: legacy `supabase_admin` Studio ownership note.
