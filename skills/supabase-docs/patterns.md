# Patterns

Reusable techniques across Supabase. Each: **When** / **How** / **Trade-offs**.

## Own-row CRUD with RLS
**When**: user-scoped data exposed via the Data API (Ch3).
**How**: `enable row level security`, then per-op policies `using ((select auth.uid()) = user_id)` + matching `with check`; add a SELECT policy; `to authenticated`.
**Trade-offs**: one rule protects every client path, but forgotten RLS = full anon read.

## Cached auth.uid() in hot policies
**When**: policies on large tables filtered by user/team (Ch2, Ch3).
**How**: wrap as `(select auth.uid())` and index the policy column; for teams use `team_id in (select team_id from team_user where user_id=(select auth.uid()))`.
**Trade-offs**: ~95% scan speedup; avoid joins inside policies.

## MFA / restrictive gate
**When**: force a second factor or hard security boundary (Ch3).
**How**: add `as restrictive` policy on `(auth.jwt()->>'aal') = 'aal2'`.
**Trade-offs**: ANDs with all policies so permissive rules elsewhere can't re-open access.

## SECURITY DEFINER escalation
**When**: a low-priv caller needs a privileged read (Ch2).
**How**: `security definer set search_path = ''`, fully-qualify every object, grant EXECUTE narrowly.
**Trade-offs**: unlocked search_path is an injection vector.

## Grants + RLS in one migration
**When**: exposing any table via REST/GraphQL (Ch7).
**How**: grant minimum privileges, enable RLS, add policies — before granting writes.
**Trade-offs**: a granted table without RLS is fully readable by anon.

## Read hint, branch on code
**When**: handling supabase-js errors (Ch7).
**How**: log the whole error; apply `error.hint` (often the exact GRANT); branch on stable `error.code`, not `message`.

## db_pre_request hook
**When**: rate-limits, app API keys, quotas on the Data API (Ch7).
**How**: a Postgres function on `authenticator`; store state in an unexposed `private` schema.

## Function-wrapped vector similarity
**When**: always — PostgREST can't call distance operators (Ch8).
**How**: wrap the query in a SQL function, `order by` the raw distance expression, call via `rpc()`; put metadata/RLS filters inside the function.
**Trade-offs**: ordering by the `similarity` alias makes the planner skip the index.

## HNSW-first vector indexing
**When**: adding any vector index (Ch8).
**How**: `using hnsw (col vector_cosine_ops)`; use `<#>` for normalized vectors, `<=>` when unsure. IVFFlat only for huge/low-memory sets after data exists.

## Hybrid search via RRF
**When**: mixing keyword + semantic search (Ch8).
**How**: run full-text and vector as CTEs, full-outer-join on id, order by weighted `1/(rrf_k+rank)`.

## Generated tsvector + GIN
**When**: scalable full-text search (Ch2).
**How**: STORED generated `tsvector` column + GIN index; query against the column.
**Trade-offs**: per-query `to_tsvector` won't scale.

## Subscribe-then-act (Realtime)
**When**: any Realtime feature (Ch6).
**How**: create channel by topic, register `.on(type, opts, cb)`, then `.subscribe()` guarded by status.

## DB-driven broadcast
**When**: UI must react to row changes at scale (Ch6).
**How**: AFTER trigger calls `realtime.broadcast_changes()` to `topic:<id>`; client listens with `setAuth()`. Match public/private flag on both sides.
**Trade-offs**: re-streaming via Broadcast beats raw Postgres Changes (single ordering thread, per-subscriber RLS reads).

## Per-user folder scope (Storage)
**When**: uploads/reads limited to the owner (Ch4).
**How**: policy `with check (storage.foldername(name))[1] = auth.jwt()->>'sub'`; reuse one signed URL for cache hits.
**Trade-offs**: revoke access by deleting the object — cached edge responses outlive token expiry.

## Secure Edge endpoint / signed webhook
**When**: client-invoked function vs external provider callback (Ch5).
**How**: client → `withSupabase({auth:'user'})`, keep `verify_jwt=true`, use `ctx.supabase`. Webhook → `auth:'none'` + `verify_jwt=false`, verify the provider signature in-handler. Outlast the response with `EdgeRuntime.waitUntil`.

## Reliable queue consume
**When**: processing must not be lost (Ch9).
**How**: `read()` then explicit `delete`/`archive`; on error skip ack so VT redelivers. Enqueue inside the business transaction (outbox).
**Trade-offs**: `pop()` is at-most-once and loses the message on crash.

## Scheduled invocation (cron)
**When**: periodic jobs / queue draining (Ch5, Ch9, Ch10).
**How**: `cron.schedule` + dollar-quoted `net.http_post` to the function URL with the `apikey` header (enable pg_net first). Pause with `alter_job(active := false)`.

## Declarative-to-migration loop
**When**: evolving schema ergonomically (Ch11).
**How**: edit `schemas/*.sql`, `supabase db diff -f name`, `migration up`. Append new columns at the end. Hand-write when migra can't track (DML, RLS alter, matviews).

## CI deploy on branch push
**When**: promoting schema to staging/prod (Ch12).
**How**: GitHub Actions `link` + `db push` keyed by per-env secrets; gate merges with a required "Supabase Preview" check; only one `db push` at a time.
**Trade-offs**: direct remote edits break migration history.

## Harden a project before prod
**When**: exposing a managed project publicly (Ch14, Ch15).
**How**: custom domain → SSL enforcement (verify-full) → IPv4+IPv6 network restrictions; move sensitive tables to a non-exposed schema; store secrets in Vault.

## PITR restore
**When**: recover from a bad migration / data loss (Ch14).
**How**: POST restore-pitr with a Unix timestamp before the incident.
**Trade-offs**: downtime scales with DB size; PITR must be pre-enabled.

## Postgres dump/restore migration
**When**: source is already Postgres (RDS/Heroku/Render) (Ch18).
**How**: `pg_dump`/`pg_restore`, no rewrite. NoSQL (Firestore): collection→table, nested→jsonb, subcollections→child tables + FK.

## OAuth + PKCE (Management API)
**When**: delegated, revocable access to a user's orgs/projects (Ch17).
**How**: PKCE `code_challenge=SHA256(verifier)` (S256), echo `state` for CSRF; health-gate (`/health` until ACTIVE_HEALTHY) before configuring new projects.
**Trade-offs**: changing scopes forces re-consent; 401 on refresh = revoked.

## Self-host: edit-env-then-recreate
**When**: any self-hosted config change (Ch13).
**How**: edit `.env`, `sh run.sh recreate [service]` (plain restart won't apply). Front Kong with an HTTPS reverse proxy for production/OAuth.

## Telemetry: error log query + Prometheus scrape
**When**: triage failures / export metrics (Ch16).
**How**: unnest `metadata` per level, `regexp_contains(error_severity,'ERROR|FATAL|PANIC')`, wrap timestamps in `datetime()`. Metrics: 60s scrape job per project hitting the metrics endpoint with the secret key; import the Grafana dashboard.
