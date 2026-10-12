# Chapter 1: Self-Hosting with Docker

## Core Idea
Docker Compose is the canonical way to self-host the full Supabase stack. The whole game is: get the `docker/` config onto your machine, replace every default secret before first start, set your URLs, then manage the stack with the `run.sh`/`reset.sh` wrappers.

## Frameworks Introduced
- **Two install paths**: Quick start vs Manual.
  - When to use: Quick start (`curl -fsSL https://supabase.link/setup.sh | sh`) on Debian/Ubuntu or RHEL/CentOS/Fedora — installs prereqs+Docker, sparse-clones `docker/`, generates ALL secrets + JWT keypair, prompts for URLs. Manual (git clone) on any OS, then configure secrets yourself.
  - How: Quick start does `generate-keys.sh` + `add-new-auth-keys.sh` automatically and a random `DASHBOARD_PASSWORD`. Manual: copy `docker/*` into `supabase-project`, copy `.env.example`→`.env`, `docker compose pull`.
- **`run.sh` wrapper**: manages the Compose stack (start/stop/restart/recreate/secrets/config/logs/printenv). Replaces raw `docker compose` for common ops.
- **`reset.sh` wrapper**: full teardown — `docker compose down -v`, deletes `volumes/db/data` + `volumes/storage`, backs up `.env`→`.env.old`, restores `.env.example`. **Destroys all data.**
- **Optional override files (`config add/remove`)**: layer extra Compose files via the `COMPOSE_FILE` env var. E.g. `sh run.sh config add logs` appends `docker-compose.logs.yml`.

## Key Concepts
- **API gateway (Kong)**: default front door on port `8000`. All service APIs route through it.
- **Supavisor**: the Postgres connection pooler. Session mode = port `5432`, transaction mode = `6543`.
- **`<your-domain>`**: stands for domain / server IP / `localhost`. Default URL `http://<your-domain>:8000`; behind reverse proxy `https://<your-domain>`.
- **`recreate` vs `restart`**: `restart` does NOT pick up config changes; `recreate` force-recreates the container (`--force-recreate --no-deps`) and does.
- **Override file**: a `docker-compose.<name>.yml` layered on the base to add/replace services (logs, envoy, caddy, nginx, s3, rustfs, pg17).

## Mental Models
- Think of `.env` as the single source of truth for secrets and URLs; `docker-compose.yml` only *references* `${VARS}`. A var in `.env` does nothing until a matching passthrough exists in the service's `environment:` block.
- Use `recreate` (not `restart`) whenever you changed configuration — restart silently keeps old config.
- Treat secrets as production-critical: never start with `.env.example` defaults.

## Anti-patterns
- **Starting with example secrets**: `.env.example` placeholders must never run in production — review every secret first.
- **`docker compose down -v`**: destroys named volumes (incl. pgsodium key) — avoid unless you mean to wipe.
- **CRLF line endings on Windows**: Kong fails with an entrypoint error. Re-clone or normalize `docker/` to LF.
- **Dashboard password with only numbers/special chars**: must include at least one letter.

## Code Examples
```sh
# Manual install (any OS)
git clone --depth 1 https://github.com/supabase/supabase
mkdir supabase-project
cp -rf supabase/docker/* supabase-project
cp supabase/docker/.env.example supabase-project/.env
cd supabase-project && docker compose pull

# Generate secrets BEFORE first start
sh utils/generate-keys.sh
sh utils/add-new-auth-keys.sh

# Start / check / logs / stop
sh run.sh start            # = docker compose up -d --wait
docker compose ps          # want "Up (healthy)"
sh run.sh logs storage
sh run.sh stop
```
- **What it demonstrates**: the minimum end-to-end manual bring-up.

## Reference Tables
System requirements:
| Resource | Minimum | Recommended |
|---|---|---|
| RAM | 4 GB | 8 GB+ |
| CPU | 2 cores | 4 cores+ |
| Disk | 40 GB SSD | 80 GB+ SSD |

`run.sh` commands:
| Command | Description |
|---|---|
| `start` / `stop` | Start or stop the stack |
| `restart [service]` | Restart (does NOT pick up config) |
| `recreate [service]` | Force-recreate, picks up config |
| `secrets` | Print key credentials from `.env` |
| `config add/remove <name>` | Enable/disable an override file |
| `printenv <service>` | Show env vars inside the container |
| `logs [service]` | Follow logs |

Secrets set by `generate-keys.sh`:
| Secret | Constraint / generator |
|---|---|
| `SECRET_KEY_BASE` | ≥64 chars; `openssl rand -base64 48` (Realtime/Supavisor) |
| `VAULT_ENC_KEY` | exactly 32 chars; `openssl rand -hex 16` (Supavisor) |
| `PG_META_CRYPTO_KEY` | ≥32 chars; `openssl rand -base64 24` |
| `LOGFLARE_PUBLIC/PRIVATE_ACCESS_TOKEN` | ≥32 chars; `openssl rand -base64 24` |
| `S3_PROTOCOL_ACCESS_KEY_ID` | `openssl rand -hex 16` |
| `S3_PROTOCOL_ACCESS_KEY_SECRET` | `openssl rand -hex 32` |
| `MINIO_ROOT_PASSWORD` | ≥8 chars; `openssl rand -hex 16` |

## Worked Example — bringing up the stack and connecting
1. `cp .env.example .env`, run `sh utils/generate-keys.sh`, then `sh utils/add-new-auth-keys.sh`.
2. Edit `.env` URLs: `SUPABASE_PUBLIC_URL=http://example.com:8000`, `API_EXTERNAL_URL=http://example.com:8000`, `SITE_URL=http://example.com:3000`.
3. Set `DASHBOARD_PASSWORD` (must contain a letter).
4. `sh run.sh start`; wait for all services `Up (healthy)` via `docker compose ps`.
5. Access Studio at `http://<your-domain>:8000` (HTTP basic auth: `DASHBOARD_USERNAME`/`DASHBOARD_PASSWORD`).
6. Connect Postgres via Supavisor session mode:
   `psql 'postgres://postgres.your-tenant-id:[POSTGRES_PASSWORD]@<your-domain>:5432/postgres'`
   (note the `-U` / username is `postgres.[POOLER_TENANT_ID]`, not bare `postgres`).
7. Invoke the demo function: `curl http://<your-domain>:8000/functions/v1/hello`.

## Key Takeaways
1. Replace every secret before first start — example values are unsafe.
2. `.env` holds values; `docker-compose.yml` references them — both layers are required.
3. Use `recreate` after config changes; `restart` won't reload config.
4. API gateway is `:8000`; APIs live under `/rest/v1/`, `/auth/v1/`, `/storage/v1/`, `/realtime/v1/`, `/functions/v1/`.
5. Postgres goes through Supavisor (5432 session / 6543 transaction); username is `postgres.<tenant>`.
6. Analytics (Logflare+Vector) is off by default — `sh run.sh config add logs` to enable (raises resource use).
7. In production, move secrets to a manager (Doppler, Infisical, Vault, cloud Secrets Manager).

## Connects To
- **Ch 2**: new API keys / asymmetric auth generated by `add-new-auth-keys.sh`.
- **Ch 3**: Envoy as an optional replacement for Kong.
- **Ch 8**: HTTPS via reverse proxy in front of `:8000`.
- **Ch 7**: Postgres 17 default and upgrades.
- **Architecture**: Studio, Kong, Auth (GoTrue), PostgREST, Realtime, Storage, imgproxy, postgres-meta, Postgres, Edge Runtime, Logflare, Vector, Supavisor — all open source, talking to one Postgres.
