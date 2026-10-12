# Cheatsheet

Decision rules — *When X, do Y, because Z.* Beside-you reference.

## Keys & access
| Situation | Do | Because |
|---|---|---|
| Code is public (browser/mobile/CLI) | use the **publishable** key | RLS (anon/authenticated) is the real guard |
| Code runs on a controlled backend | use the **secret** key | full BYPASSRLS; 401s in browsers |
| Sending keys from Postgres / non-JWT context | use the `apikey` header | publishable/secret keys aren't JWTs |
| Edge Function with new keys | `--no-verify-jwt`, check `apikey` yourself | EF JWT verify only supports legacy keys |
| New project / integration | use publishable/secret keys | anon/service_role are legacy |
| Verifying JWTs externally | use JWKS/asymmetric, not HS256 secret | a leaked shared secret allows impersonation |

## RLS & data security
- Table in `public` / exposed via Data API → **enable RLS + revoke blanket grants**, because PostgREST opens all rows to anon otherwise.
- Policy filters by user_id → **index it + wrap `auth.uid()` in `(select …)` + `to authenticated`** → ~95% speedup; Postgres caches per-statement.
- Storing authorization data → **`app_metadata`, not `user_metadata`** → users can edit user_metadata and escalate.
- MFA / hard gate → **`as restrictive`** → permissive policies elsewhere can't re-open access.
- Sensitive column → **REVOKE SELECT on the column (CLS)** → RLS gates rows, not columns.
- Internal security tables → **put in a non-exposed `private` schema** → never reachable via the API.
- `SECURITY DEFINER` → **`set search_path=''` + qualify names** → otherwise an injection vector.
- Suspected leaked key → **rotate + rebuild from lockfile** → service_role bypasses all RLS.

## Database & connections
- Serverless/edge client → **transaction mode `:6543`** → session features/prepared statements don't survive pooling.
- Long-lived backend / migrations → **session `:5432`**.
- Full-text search → **generated `tsvector` + GIN** → per-query `to_tsvector` won't scale.
- Notify external service on change → **AFTER trigger + pg_net `http_request`** (async).

## Vectors / AI
| Situation | Do | Because |
|---|---|---|
| Normalized vectors (OpenAI) | `<#>` inner product | fastest operator |
| Unsure if normalized | `<=>` cosine | magnitude-independent, safe default |
| New/changing table | **HNSW** | robust, build anytime (IVFFlat needs data) |
| Slow vector query | order by the distance **expression**, not the alias | alias makes planner ignore the index |
| Calling from supabase-js | **wrap in SQL function + `rpc()`** | PostgREST can't use distance operators |
| AI tool via MCP | read-only + project-scoped + non-prod | prompt injection can run arbitrary SQL |

## Realtime
- High-frequency data (cursors) → **Broadcast, not Presence** → Presence floods all subscribers on every change.
- Postgres Changes slow under load → **re-stream via Broadcast** → single ordering thread + per-subscriber RLS reads.
- Need old records on UPDATE/DELETE → **`replica identity full`** → only `new` is sent by default.
- Private channels → **short JWT expiry + `setAuth()`** → policy cache only refreshes on new tokens; match public/private flag both sides.

## Storage
- File > 6MB → **TUS resumable or S3 multipart** → standard upload is unreliable at size.
- Revoking access to a private asset → **delete the object** → cached edge responses outlive token expiry.
- Serving public assets → **public buckets over signed URLs** → per-user checks lower cache hit rate.
- No policy on a bucket → expect **zero access** → buckets deny-by-default.

## Edge Functions
- Heavy multi-round-trip DB work → **pin region (`x-region`)** → co-locating with the DB beats nearest-user latency.
- Many small actions → **one fat function** → each function cold-starts independently.
- Work outlasts the response → **`EdgeRuntime.waitUntil`** (not await) → isolate shuts down at response time.

## Migrations & deployment
- Schema change to prod → **committed migrations + CI** → direct remote edits break history and fail `db push`.
- Multiple devs → **one `db push` at a time** → migrations apply in timestamp order.
- Undo deployed change → **new forward/down migration, never reset** → prod migrations are forward-only.
- Evolving schema → **edit `schemas/*.sql` + `db diff -f`** → CLI computes a reviewable migration.
- migra can't track it (DML, RLS alter, matviews, comments, partitions) → **hand-write the migration**.

## Platform / queues / cron / self-host
- IPv6-resolving DB + network restrictions → **add BOTH IPv4+IPv6 CIDRs** → omitting v6 locks you out.
- Activating a custom domain → **update OAuth/SAML callback URLs first** → EntityID changes, login breaks.
- Enable PITR → **stop relying on daily backups** → PITR disables them, finer granularity.
- Different plans per project → **separate organizations** → one org = one plan.
- Queue processing can crash → **`read()`+`delete()`, not `pop()`** → pop is at-most-once.
- pgmq exposed to clients → **RLS on every `q_` table + grant `pgmq_public`** → raw tables have no RLS.
- Cron job name → **treat as immutable PK** → case-sensitive, reusing silently overwrites.
- Self-host `.env` change → **`sh run.sh recreate`** → plain restart won't apply.
- Self-host production → **HTTPS reverse proxy + secrets manager + firewall** → you own security/uptime.

## Telemetry
- Raw log timestamps → **wrap in `datetime()`** → stored as Unix microseconds.
- Query a `metadata` field → **`cross join unnest()` per level, select the leaf** → whole-object selects OOM/timeout.
- `WARNING`/`ERROR` missing from logs → **lower `log_min_messages` below `LOG`**.
- `trace_id` missing → verify active span + `@opentelemetry/api` + registered TracerProvider → SDK no-ops silently.
