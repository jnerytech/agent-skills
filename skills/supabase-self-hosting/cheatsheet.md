# Cheatsheet — Decision Rules & Quick Reference

## Decision rules
- **Config var "not working"?** → 99% missing passthrough. `docker compose exec <svc> env | grep <PREFIX>`; if absent, add `GOTRUE_X: ${X}` to `docker-compose.yml`.
- **Changed env/compose?** → `recreate` (`up -d --force-recreate --no-deps <svc>`). **Changed only function code?** → `restart functions --no-deps`. Never trust plain `restart` for config.
- **Need HTTPS?** → reverse proxy terminating TLS at 443; backend stays HTTP:8000. Caddy if you want zero-config; Nginx if you need control; self-signed ONLY for dev.
- **OAuth callback rejected?** → must be HTTPS and exactly `${API_EXTERNAL_URL}/auth/v1/callback`; restart all after changing `API_EXTERNAL_URL`.
- **Rotating keys:** compromise of `sb_` keys → `rotate-new-api-keys.sh` (sessions survive). EC key compromise → `add-new-auth-keys.sh` (ES256 sessions die → maintenance window).
- **Add a SAML IdP?** → admin API at runtime (no restart). **Enable SAML engine?** → env var + restart. OAuth = env only (no runtime API).
- **MCP access?** → allow-list Docker bridge IP + SSH tunnel. Never Internet-expose (no auth).
- **Storage upload fails on a "Public" bucket?** → Public only allows anon downloads; add an RLS INSERT policy on `storage.objects`.
- **Migrating storage?** → rclone S3-to-S3, never file copy. **Migrating DB?** → `supabase db dump`, never raw `pg_dump`.
- **Need direct Postgres (bypass pooler)?** → comment out `supavisor`, expose `db` port; restrict by firewall. Else use Supavisor 5432 (session) / 6543 (transaction).

## Gateway error → cause
| Error | Cause |
|---|---|
| `401` protected route | `apikey` missing/unmatched (opaque keys need full new-key config) |
| `403` on `/pg/` | needs service_role key (anon/publishable rejected) |
| `403` on `/mcp`, Realtime `/api/tenants`,`/api/openapi` | denied by default (RBAC) |
| `SignatureDoesNotMatch` (Storage S3) | check `REGION`/keys + `X-Forwarded-Prefix` + `STORAGE_PUBLIC_URL` |
| `400` underscore headers (Envoy) | use hyphens, not underscores |
| `400` "missing function name" | URL needs name after `/functions/v1/` |
| `401` "invalid JWT" (functions) | check `FUNCTIONS_VERIFY_JWT` + Bearer key |

## Ports & endpoints
| Port | Use |
|---|---|
| 8000 | API gateway (Kong/Envoy) — all APIs + Studio |
| 8443 | Kong self-signed HTTPS (dev) |
| 5432 | Supavisor session mode (direct-like) |
| 6543 | Supavisor transaction mode (pooled) |
| 9901 | Envoy admin (in-container only — NEVER expose) |
| 443/80 | reverse proxy (TLS / ACME) |

APIs: `/rest/v1/` `/auth/v1/` `/storage/v1/` `/realtime/v1/` `/functions/v1/` `/pg/` (meta) `/graphql/v1`.

## Key materials
| Var | Job | Consumer |
|---|---|---|
| `JWT_KEYS` | sign (EC private+sym) | Auth |
| `JWT_JWKS` | verify (EC public+sym) | PostgREST, Realtime, Storage |
| `ANON_KEY`/`SERVICE_ROLE_KEY` | legacy HS256 keys | client / server |
| `SUPABASE_PUBLISHABLE_KEY`/`SECRET_KEY` | new opaque keys | client / server |

## Thresholds & defaults
- System: 4 GB RAM / 2 CPU / 40 GB min; 8 GB / 4 CPU / 80 GB recommended.
- PG upgrade disk: ≥ 2× DB size + 5 GB.
- OTP: 60 s expiry (raise for prod), length 6 (6–10), 60 s min frequency, 30/hr global SMS.
- SAML key: PKCS#1 RSA ≥2048-bit (4096 prod); relay state 2m.
- Functions: 150 MB / 60 s default; dashboard password must contain a letter.

## Danger smells (never do)
- `docker compose down -v` → destroys named volumes + pgsodium key (Vault unrecoverable).
- Delete `data.bak.pg15` before verifying upgrade → no rollback.
- Start with `.env.example` defaults → insecure.
- Expose Envoy `:9901` / MCP to Internet → plaintext secrets / no-auth access.
- Internal function calls via `SUPABASE_PUBLIC_URL` → use `SUPABASE_URL` (`kong:8000`).
