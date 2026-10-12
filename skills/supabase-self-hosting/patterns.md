# Patterns & Techniques

## Two-Layer Env Config (`.env` + passthrough)
**When to use**: configuring any service variable (OAuth, SMS, SAML, S3, functions).
**How**: put the value in `.env`; add a matching `SERVICE.environment.GOTRUE_X: ${X}` (or equivalent) passthrough in `docker-compose.yml`. Recreate the service.
**Trade-offs**: a `.env` value without a passthrough is invisible inside the container — the single most common "it's not working" cause. Verify with `docker compose exec <svc> env | grep <PREFIX>`.

## Recreate vs Restart
**When to use**: after editing configuration vs only restarting a running service.
**How**: `docker compose up -d --force-recreate --no-deps <svc>` (or `sh run.sh recreate <svc>`) for config/env changes; `docker compose restart <svc> --no-deps` only re-runs without reloading config (fine for picking up new function *files*).
**Trade-offs**: `restart` silently keeps old config — use `recreate` whenever env/compose changed.

## Override-File Layering
**When to use**: enabling optional features (logs, Envoy, Caddy/Nginx, S3/RustFS, PG17).
**How**: `docker compose -f docker-compose.yml -f docker-compose.<name>.yml up -d`, or `sh run.sh config add <name>` to manage via `COMPOSE_FILE`.
**Trade-offs**: extra services raise resource use; order matters (base first).

## Secret Generation & Rotation
**When to use**: initial setup and key compromise/periodic rotation.
**How**: `generate-keys.sh` + `add-new-auth-keys.sh` at setup. Rotate API keys (`rotate-new-api-keys.sh`) without touching the EC keypair → sessions survive. Regenerate keypair (`add-new-auth-keys.sh`) → ES256 sessions invalidated.
**Trade-offs**: regeneration needs a maintenance window; rotation does not.

## Gateway Opaque-Key Translation
**When to use**: understanding/debugging API-key auth (Kong or Envoy).
**How**: gateway swaps opaque `sb_` keys for pre-signed internal ES256 JWTs before upstream; real user-session JWTs (not `Bearer sb_`) pass through unchanged; upstream verifies via `JWT_JWKS`/`JWT_SECRET`.
**Trade-offs**: translation needs all new-key vars set; functions/storage routes bypass it (self-auth).

## Reverse-Proxy TLS Termination
**When to use**: production HTTPS.
**How**: Caddy (auto-TLS) or Nginx+Certbot in front of gateway `:8000`; update the URL trio to HTTPS; proxy must support WebSocket + add `X-Forwarded` headers.
**Trade-offs**: self-signed only for dev (browser warnings, OAuth rejects).

## Two-Phase pg_upgrade
**When to use**: PG15→PG17 in place.
**How**: `sudo bash utils/upgrade-pg17.sh` — Phase 1 (PG15) disables incompatible extensions + `pg_upgrade`; Phase 2 (PG17) patches extensions, re-enables, vacuums. Back up data dir + pgsodium key + optional logical dump first.
**Trade-offs**: needs 2× DB size + 5 GB; rollback only while `data.bak.pg15` exists; never `down -v`.

## Three-File Dump + Single-Transaction Restore
**When to use**: platform DB → self-hosted.
**How**: `supabase db dump` → roles/schema/data; `psql --single-transaction --variable ON_ERROR_STOP=1` with `SET session_replication_role = replica` before data.
**Trade-offs**: raw `pg_dump` breaks; secrets/providers/storage/SMTP are manual; PG17→15 mismatches need editing `data.sql`.

## rclone S3-to-S3 Storage Migration
**When to use**: copying storage objects platform → self-hosted.
**How**: two rclone remotes (both `/storage/v1/s3` endpoints), pre-create destination buckets, `rclone copy`, verify with `rclone size`.
**Trade-offs**: direct file copy fails (wrong internal structure); buckets must pre-exist.

## URL-Fetched Email Templates
**When to use**: custom auth/notification emails.
**How**: serve HTML via a portless `templates-server` (caddy file-server) on the Docker network; point `GOTRUE_MAILER_TEMPLATES_*` at `http://templates-server/<file>.html`; notifications also need `_ENABLED='true'`.
**Trade-offs**: Auth never reads mounted files; invalid/unreachable template → silent fallback to default.

## Network-Restricted MCP Access
**When to use**: enabling the (auth-less) MCP server safely.
**How**: allow-list the Docker bridge gateway IP (Kong `ip-restriction` / Envoy RBAC ALLOW), restart gateway, reach via SSH tunnel (`ssh -L localhost:8080:localhost:8000`), point client at `http://localhost:8080/mcp`.
**Trade-offs**: never Internet-expose; YAML indentation breaks the gateway config if disturbed.

## Studio Superuser Removal
**When to use**: aligning self-hosted ownership with the platform model.
**How**: `reassign-owner.sh` (public schema) + set `studio.POSTGRES_USER_READ_WRITE: postgres` and `meta.PG_META_DB_USER: postgres`; `down && up -d`; verify `select current_user;` → `postgres`.
**Trade-offs**: only the `public` schema is reassigned.
