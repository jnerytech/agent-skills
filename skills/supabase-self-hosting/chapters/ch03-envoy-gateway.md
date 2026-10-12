# Chapter 3: Envoy API Gateway

## Core Idea
Envoy is an optional drop-in replacement for the default Kong gateway, enabled via the `docker-compose.envoy.yml` override. It does the same job — route to internal services, enforce API keys, translate opaque keys into internal JWTs — but through an ordered HTTP filter chain with stronger built-in security hardening.

## Frameworks Introduced
- **Filter chain (ordered)**: CORS → Basic Auth (dashboard) → Lua (copy `?apikey`→header) → Lua (401 on missing/invalid key) → Lua (translate opaque in query) → Lua (translate opaque in header) → Lua (mirror apikey→`x-api-key` for Realtime WS) → Lua (synthesize `Authorization`) → RBAC → Router.
  - When to use: when you want Envoy's hardening or are standardizing on it; understand this order before customizing.
- **Drop-in gateway swap**: Envoy registers as `api-gw` and aliases `kong`; base Kong also aliases `api-gw`. Internal configs hardcoding `kong:8000` keep working.
  - How: `docker compose -f docker-compose.yml -f docker-compose.envoy.yml up -d` (down first if Kong is running).
- **Template-rendered config**: Envoy can't read env vars natively. `docker-entrypoint.sh` SHA1+base64-hashes `DASHBOARD_PASSWORD`, `sed`-substitutes vars into `lds.template.yaml` → `lds.yaml`, then starts. Config changes need a container restart to re-render.
- **Translation-enabled gate**: opaque translation turns on only if ALL four of `SUPABASE_SECRET_KEY`, `SUPABASE_PUBLISHABLE_KEY`, `ANON_KEY_ASYMMETRIC`, `SERVICE_ROLE_KEY_ASYMMETRIC` are set; else legacy-only (printed to log at startup).

## Key Concepts
- **Config files** under `./volumes/api/envoy/`: `envoy.yaml` (bootstrap), `cds.yaml` (clusters/upstreams), `lds.template.yaml` (listener/routes/RBAC/CORS), `docker-entrypoint.sh` (renderer).
- **RBAC**: global rule — `service_role`→`/pg/`, any valid key→other API routes; per-route DENY on `/mcp`, `/realtime/v1/api/tenants`, `/realtime/v1/api/openapi`.
- **Admin interface**: `127.0.0.1:9901` (in-container only) — `/ready`, `/clusters`, `/stats`, `/config_dump`.
- **First-match routing**: routes matched in declared order; place custom routes before catch-all `/`.

## Mental Models
- Think of the chain as: normalize the key → reject if bad → translate opaque→JWT → synthesize `Authorization` → authorize (RBAC) → route. The translation chain is entirely skipped on `/functions/v1/` (Edge Runtime self-authenticates).
- `X-Forwarded-Prefix` is not cosmetic — Storage needs it for S3 SigV4 signing and TUS upload URLs.

## Anti-patterns
- **Exposing port `9901`**: `/config_dump` leaks all keys, JWTs, and the basic-auth hash in plaintext.
- **`allow_credentials: true` with wildcard origin**: browsers and Envoy reject it — restrict `allow_origin_string_match` to specific origins.
- **Underscore headers** (`X_Forwarded_For`): rejected with 400 (`headers_with_underscores_action: REJECT_REQUEST`) — use hyphens.
- **Editing `lds.yaml` directly**: it's regenerated from the template; edit `lds.template.yaml`.

## Code Examples
```sh
# Enable Envoy; restart after config changes
docker compose -f docker-compose.yml -f docker-compose.envoy.yml up -d
docker compose -f docker-compose.yml -f docker-compose.envoy.yml restart api-gw

# Query admin from a sidecar curl container (image lacks curl)
docker run --rm --network container:supabase-envoy curlimages/curl http://127.0.0.1:9901/clusters
```
- **What it demonstrates**: enabling Envoy and reaching its in-container admin API.

## Reference Tables
Key routes:
| Path prefix | Upstream | Access |
|---|---|---|
| `/auth/v1/verify|callback|authorize`, `/.well-known/...`, `/sso/saml/*` | auth | Open |
| `/functions/v1/`, `/storage/v1/` | functions/storage | Bypass (self-auth) |
| `/auth/v1/`, `/rest/v1/`, `/graphql/v1`, `/realtime/v1/api`, `/realtime/v1/` | various | API key |
| `/pg/` | meta | service_role only (403 else) |
| `/realtime/v1/api/tenants|openapi`, `/api/mcp`, `/mcp` | - | Denied (RBAC) |
| `/` catch-all | studio | Basic auth (strips inbound `Authorization`) |

Security hardening:
| Setting | Purpose |
|---|---|
| `normalize_path`/`merge_slashes: true` | Prevent path-confusion RBAC bypass |
| `path_with_escaped_slashes_action: REJECT_REQUEST` | Reject URL-encoded slashes |
| `use_remote_address: true` | Trust peer IP; strip untrusted `x-envoy-*` |
| `headers_with_underscores_action: REJECT_REQUEST` | Block header smuggling |
| `per_connection_buffer_limit_bytes: 32768` | 32 KiB buffer cap |
| `max_active_downstream_connections: 30000` | Overload limit |
| Admin bound `127.0.0.1:9901` | Not reachable off-container |

## Worked Example — common gateway errors and their cause
- `401` on a protected route → `apikey` header missing or doesn't match `ANON_KEY`/`SERVICE_ROLE_KEY`/`SUPABASE_PUBLISHABLE_KEY`/`SUPABASE_SECRET_KEY` (opaque keys only accepted when full new-key config is set).
- `403` on `/pg/` → used anon/publishable; route needs a service_role key.
- `403` on `/mcp` or Realtime `/api/tenants`,`/api/openapi` → blocked by design (RBAC DENY).
- `SignatureDoesNotMatch` on Storage S3 → Storage missing `REQUEST_ALLOW_X_FORWARDED_PATH=true` + `STORAGE_PUBLIC_URL`; it relies on the gateway's `X-Forwarded-Prefix`.
- `400` with underscore headers → `headers_with_underscores_action` rejecting them; switch to hyphens.

## Key Takeaways
1. Envoy and Kong are interchangeable; `api-gw`/`kong` aliases make the swap transparent.
2. Edit `lds.template.yaml`, never `lds.yaml`; restart `api-gw` to re-render.
3. Opaque translation needs all four keys; the functions route skips the whole chain.
4. RBAC: `/pg/` is service_role-only; `/mcp` and Realtime mgmt are denied by default.
5. Never expose `:9901` — `/config_dump` is plaintext secrets.
6. Envoy terminates plain HTTP only — TLS belongs to an upstream reverse proxy.

## Connects To
- **Ch 2**: opaque-key translation and pre-signed internal JWTs.
- **Ch 8**: Caddy/Nginx in front of Envoy (uncomment `api-gw:` block in the proxy override).
- **Ch 11**: enabling `/mcp` by editing the RBAC rule on the route.
