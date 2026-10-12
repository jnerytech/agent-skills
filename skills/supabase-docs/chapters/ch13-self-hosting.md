# Chapter 13: Self-Hosting (Docker)

## Core Idea
Self-hosted Supabase is the *same* open-source stack the platform runs — Postgres plus Kong (API gateway), Auth (GoTrue), PostgREST, Realtime, Storage, postgres-meta, Edge Runtime, Studio, Supavisor (pooler), and optional imgproxy/Logflare/Vector — packaged as one `docker-compose.yml` driven entirely by a `.env` file. Docker is the official, recommended path; everything is configured by editing env vars and restarting. It mimics a *single project*: no multi-org/multi-project, no branching, PITR, managed backups, ETL, or platform management API. **You own** provisioning, hardening, backups, HA, and uptime. Self-hosted Docker Compose collects **no telemetry**. (For deep operational detail, defer to the dedicated `supabase-self-hosting` skill — this chapter is the conceptual map.)

## Frameworks Introduced
- **Quick start (Linux) `setup.sh`**: one piped command installs Docker/git/openssl/jq, sparse-clones `docker/`, prompts for URLs, generates all secrets + asymmetric JWT keys + random `DASHBOARD_PASSWORD`, pulls images. Fastest production-ready bootstrap.
- **Manual install (clone + `.env.example`)**: clone repo (shallow or sparse), copy `docker/*` into a project dir, copy `.env.example` → `.env`, run `generate-keys.sh` + `add-new-auth-keys.sh`, set URLs, then `docker compose pull`. Any OS.
- **`run.sh` / `reset.sh` helpers**: `run.sh` wraps the stack (start/stop/restart/recreate/secrets/logs/`config add|remove`); `reset.sh` destroys all data and restores default `.env`.
- **Compose overrides via `COMPOSE_FILE`**: optional features layer extra files — `config add logs` (Logflare+Vector), Envoy gateway (`docker-compose.envoy.yml`) — toggled by `run.sh config add/remove <name>`.
- **Asymmetric key system (`generate-keys.sh` + `add-new-auth-keys.sh`)**: produces legacy HS256 keys *and* new ES256 keypair so both opaque `sb_` keys and legacy JWTs work simultaneously.

## Key Concepts
- **Kong gateway on `:8000`**: single front door for Studio + all APIs (`/rest/v1/`, `/auth/v1/`, `/storage/v1/`, `/realtime/v1/`, `/functions/v1/`). Envoy is an optional drop-in override on the same port that translates opaque `sb_` keys into internal credentials.
- **Dual auth keys**: legacy `ANON_KEY`/`SERVICE_ROLE_KEY` (HS256 JWTs from `JWT_SECRET`) coexist with new opaque `SUPABASE_PUBLISHABLE_KEY`/`SUPABASE_SECRET_KEY`. `JWT_KEYS` (signing, EC private + symmetric) used by Auth; `JWT_JWKS` (EC public + symmetric) used by PostgREST/Realtime/Storage to verify both token types. Self-hosted supports exactly **one** key per role; gateway matches `sb_` keys as opaque strings (no checksum validation).
- **Supavisor pooler**: Postgres reached through Supavisor — session mode `:5432`, transaction mode `:6543`; user is `postgres.[POOLER_TENANT_ID]` (default `your-tenant-id`).
- **Studio = HTTP basic auth**: gated by `DASHBOARD_USERNAME`/`DASHBOARD_PASSWORD`; password must contain at least one letter.
- **Edge Functions in `volumes/functions`**: a `hello` fn ships pre-wired; add `volumes/functions/<name>/index.ts`; `FUNCTIONS_VERIFY_JWT` controls JWT enforcement; limits (150 MB / 60 s) live in `main/index.ts`.
- **Critical secrets**: `SECRET_KEY_BASE` (≥64 chars), `VAULT_ENC_KEY` (exactly 32), `PG_META_CRYPTO_KEY` (≥32), `POSTGRES_PASSWORD`.

## Mental Models
- **`.env` is the control plane; `docker-compose.yml` references it.** Pattern: `PGRST_DB_MAX_ROWS: ${PGRST_DB_MAX_ROWS:-1000}`. Change config = edit `.env`, then `recreate` (not `restart`).
- **`recreate` ≠ `restart`.** Only force-recreate (`up -d --force-recreate`) picks up config changes; plain restart does not.
- **Gateway answers "what is connecting"; RLS answers "who".** Public keys are safe only because Postgres RLS guards rows — same as the platform.
- **Defaults are insecure by design.** `.env.example` placeholders MUST be regenerated before first start.

## Anti-patterns
- **Starting with `.env.example` defaults.** Always run key generation / set secrets first — danger-level warning in the docs.
- **`docker compose restart` after a config change.** Use `sh run.sh recreate [service]`.
- **Exposing Postgres directly without a firewall.** Bypasses pooling and the network boundary; restrict to trusted IPs.
- **Plain HTTP in production / with OAuth.** Put a reverse proxy (Caddy/Nginx) terminating TLS in front of Kong.
- **Special chars in `POSTGRES_PASSWORD`.** Use letters+numbers only to avoid URL-encoding breakage in connection strings.
- **Leaving all secrets in a flat `.env` in prod.** Move to a secrets manager (Vault, Doppler, Infisical, cloud KMS).
- **macOS local Storage bind mount.** Docker Desktop lacks xattr support — switch to a named volume.

## Code Examples
```sh
# Quick start (Linux): install, fetch config, generate ALL secrets + keys
curl -fsSL https://supabase.link/setup.sh | sh
cd supabase-project && sh run.sh start   # == docker compose up -d --wait
sh run.sh secrets                         # print POSTGRES_PASSWORD, sb_ keys, URL
```
- **What it demonstrates**: zero-to-running bootstrap; `run.sh` wraps compose and surfaces credentials.

```sh name=.env
## Never check your secrets into version control
SUPABASE_PUBLIC_URL=http://example.com:8000   # base URL (Dashboard/API/Storage)
API_EXTERNAL_URL=http://example.com:8000       # Auth callback base
SITE_URL=http://example.com:3000               # default Auth redirect
DASHBOARD_USERNAME=supabase
DASHBOARD_PASSWORD=this-needs-a-letter
SMTP_ADMIN_EMAIL=admin@example.com
SMTP_HOST=smtp.example.com
SMTP_PORT=465
SMTP_USER=your-smtp-user
SMTP_PASS=your-smtp-password
SMTP_SENDER_NAME=your-sender-name
```
- **What it demonstrates**: the three URL vars + Studio basic-auth + production SMTP (AWS SES recommended). Restart services to apply.

```yaml name=docker-compose.yml
# Expose Postgres directly: comment out the supavisor service, then:
db:
  ports:
    - ${POSTGRES_PORT}:${POSTGRES_PORT}
  container_name: supabase-db
```
- **What it demonstrates**: bypassing the pooler for direct DB access — only behind a firewall.

```sh
# Layer the Envoy gateway override instead of Kong
docker compose -f docker-compose.yml -f docker-compose.envoy.yml up -d
```
- **What it demonstrates**: optional features are compose overrides on the same `:8000` port.

## Reference Tables

Core services (all behind Kong, all talk to one Postgres):
| Service | Role |
|---|---|
| Kong / Envoy | API gateway, key translation, routing (`:8000`) |
| Auth (GoTrue) | JWT auth, sign-up/login/sessions |
| PostgREST | auto REST API from schema |
| Realtime | Postgres changes / broadcast / presence (Elixir) |
| Storage + imgproxy | S3-style files (perms in Postgres) + image transforms |
| postgres-meta | manage tables/roles/queries |
| Edge Runtime | Deno functions (`volumes/functions`) |
| Studio | dashboard (basic auth) |
| Supavisor | connection pooler (`5432` session / `6543` txn) |
| Logflare + Vector | logs/analytics (optional override) |

Key env vars:
| Var | Purpose |
|---|---|
| `POSTGRES_PASSWORD` | DB password / connection strings |
| `JWT_SECRET` | HS256 signing secret (legacy keys) |
| `ANON_KEY` / `SERVICE_ROLE_KEY` | legacy HS256 client/server JWTs |
| `SUPABASE_PUBLISHABLE_KEY` / `SUPABASE_SECRET_KEY` | new opaque `sb_` client/server keys |
| `JWT_KEYS` / `JWT_JWKS` | ES256 signing set / verification JWKS |
| `SUPABASE_PUBLIC_URL` / `API_EXTERNAL_URL` / `SITE_URL` | external URLs |
| `DASHBOARD_USERNAME` / `DASHBOARD_PASSWORD` | Studio basic auth |
| `POOLER_TENANT_ID` | Supavisor tenant (default `your-tenant-id`) |
| `FUNCTIONS_VERIFY_JWT` | edge fn JWT enforcement |
| `SECRET_KEY_BASE` / `VAULT_ENC_KEY` / `PG_META_CRYPTO_KEY` | service encryption keys |

## Worked Example
Minimal Linux production bring-up:
1. `curl -fsSL https://supabase.link/setup.sh | sh` — installs deps, fetches `docker/`, generates secrets + asymmetric keys + random `DASHBOARD_PASSWORD`, prompts for `SUPABASE_PUBLIC_URL`/`API_EXTERNAL_URL`/`SITE_URL`/`PROXY_DOMAIN`, pulls images.
2. `cd supabase-project && sh run.sh start` then `docker compose ps` — wait for all `Up (healthy)`. Debug with `sh tests/test-container-logs.sh` or `sh run.sh logs storage`.
3. `sh run.sh secrets` — grab `POSTGRES_PASSWORD`, `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SECRET_KEY`, URL.
4. Browse `http://<your-domain>:8000` → Studio basic-auth prompt (`DASHBOARD_USERNAME`/`PASSWORD`).
5. Test edge fn: `curl http://<your-domain>:8000/functions/v1/hello`.
6. Harden: set SMTP in `.env`, front with Caddy/Nginx for HTTPS (`https://<domain>`), move secrets to a manager, firewall the host. Apply config with `sh run.sh recreate`.

## Key Takeaways
- One `docker-compose.yml` + one `.env` = the entire platform stack, single-project scope.
- Regenerate secrets before first boot; never ship `.env.example` defaults.
- Edit `.env` then `recreate` (not `restart`) to apply changes.
- Kong/Envoy on `:8000` is the only public surface; access Postgres via Supavisor `5432`/`6543`.
- New `sb_` opaque keys and legacy HS256 JWTs run side-by-side for incremental migration.
- Production = HTTPS reverse proxy + secrets manager + firewall + your own backups/monitoring.
- For deep how-tos (auth keys, Envoy, S3, OAuth/SAML/MFA, Postgres 17 upgrade, HTTPS proxy, MCP, platform migration), use the dedicated **`supabase-self-hosting`** skill.

## Connects To
- **Ch 1 (Getting Started)**: same architecture (Postgres-as-core, Kong, RLS, key types) as the managed platform.
- **Auth/API-keys chapters**: `sb_publishable`/`sb_secret` vs legacy `anon`/`service_role`; RLS as the real guard.
- **Storage / Edge Functions / Realtime chapters**: self-host config knobs for each service.
- **`supabase-self-hosting` skill**: the deep operational companion to this overview.
