# Chapter 2: New API Keys and Asymmetric Authentication

## Core Idea
Self-hosted Supabase can run the new opaque `sb_publishable`/`sb_secret` API keys and ES256 asymmetric JWT signing **alongside** the legacy HS256 `ANON_KEY`/`SERVICE_ROLE_KEY` — fully backward compatible, configured entirely at the gateway + service layer with no database changes.

## Frameworks Introduced
- **Dual-key model**: legacy HS256 keys and new opaque keys both accepted simultaneously, enabling incremental client migration.
  - When to use: any time you want platform-style keys, third-party JWT verification, or to rotate API keys without invalidating user sessions.
  - How: `sh utils/add-new-auth-keys.sh --update-env` generates EC P-256 keypair, JWKS, asymmetric JWTs, and `sb_` keys; writes to `.env`; uncomment the JWT env entries; `docker compose down && up -d`.
- **Two key materials, two jobs**:
  - `JWT_KEYS` (JSON array of signing JWKs: EC private + legacy symmetric) → Auth uses to **sign**.
  - `JWT_JWKS` (EC public + legacy symmetric) → PostgREST/Realtime/Storage use to **verify** (both ES256 and HS256).
- **Rotation vs Regeneration**:
  - Rotate (`rotate-new-api-keys.sh --update-env`): new `sb_` keys only, keypair untouched → **does not** invalidate user sessions.
  - Regenerate (`add-new-auth-keys.sh --update-env`): new EC keypair → **invalidates all ES256 sessions** (plan a maintenance window); legacy-HS256 sessions survive since `JWT_SECRET` unchanged.

## Key Concepts
- **Opaque key**: short random key with checksum, matched as a literal string by the gateway (checksum NOT validated self-hosted). Format `sb_publishable_<22>_<8>` / `sb_secret_<22>_<8>`.
- **Pre-signed internal JWT**: gateway-level ES256 JWT substituted for an `sb_` key before reaching upstream; auto-set in `.env`, must NOT be used in app code.
- **JWKS endpoint**: `/auth/v1/.well-known/jwks.json` returns EC public key (symmetric excluded) for third-party verification.
- **Legacy-only mode**: when new vars are empty, only `ANON_KEY`/`SERVICE_ROLE_KEY` work.

## Mental Models
- Think of the gateway as a translator: client sends an opaque `apikey`; gateway swaps it for a real JWT the upstream can verify. The `Authorization` header decides "is there a user session?" independent of which `apikey` type was used.
- `JWT_SECRET` is the hinge of backward compat — keep it in the JWKS and old HS256 tokens keep verifying.

## Anti-patterns
- **Changing `JWT_SECRET` without regenerating JWKS**: the script embeds it inside `JWT_KEYS`/`JWT_JWKS`; a mismatch breaks verification.
- **Configuring `JWT_KEYS` (Auth signs ES256) but not `JWT_JWKS` on verifiers**: PostgREST/Realtime/Storage can't verify the new tokens.
- **Using internal pre-signed JWTs in application code**: they're gateway-only.
- **Nested interpolation under Podman**: `${A:-${B}}` unsupported — substitute the variable directly.

## Code Examples
```yaml name=docker-compose.yml
auth:    { environment: { GOTRUE_JWT_KEYS: ${JWT_KEYS:-[]} } }
rest:    { environment: { PGRST_JWT_SECRET: ${JWT_JWKS:-${JWT_SECRET}} } }
realtime:{ environment: { API_JWT_JWKS: ${JWT_JWKS:-{"keys":[]}} } }
storage: { environment: { JWT_JWKS: ${JWT_JWKS:-{"keys":[]}} } }
```
```sh
sh utils/add-new-auth-keys.sh --update-env   # generate + write .env
docker compose down && docker compose up -d
curl http://<your-domain>/auth/v1/.well-known/jwks.json   # EC public key
```
- **What it demonstrates**: which service consumes which key material, and the verify step.

## Reference Tables
| Variable | Type | Role |
|---|---|---|
| `JWT_SECRET` | symmetric | Sign/verify HS256 (existing) |
| `ANON_KEY` / `SERVICE_ROLE_KEY` | HS256 JWT | Legacy client / server keys |
| `SUPABASE_PUBLISHABLE_KEY` / `SUPABASE_SECRET_KEY` | opaque | New client / server keys |
| `JWT_KEYS` | JSON array | Auth signing JWKs (EC private + symmetric) |
| `JWT_JWKS` | JWKS | Verify keys (EC public + symmetric) |

Kong route → API-key behavior:
| Route | Service | Key required | Auth substitution |
|---|---|---|---|
| `/auth/v1/*`, `/rest/v1/*`, `/graphql/v1` | Auth/PostgREST | Yes | `Authorization` |
| `/realtime/v1/api/*` | Realtime REST | Yes | `Authorization` |
| `/realtime/v1/*` | Realtime WS | Yes | `x-api-key` (apikey via `?apikey=`) |
| `/storage/v1/*` | Storage | No (self-auth) | `Authorization` |
| `/functions/v1/*` | Edge Functions | No (self-auth) | - |
| `/realtime/v1/api/tenants`,`/api/openapi` | Realtime | Denied | - |

## Worked Example — the gateway's Authorization logic
The `request-transformer` in `kong.yml` resolves the upstream `Authorization` header with one conditional:
```lua
if authorization exists AND not starts_with "Bearer sb_" then
  keep authorization                       -- real user session JWT, pass through
elseif apikey == secret key then
  set authorization = "Bearer <service_role ES256 JWT>"
elseif apikey == publishable key then
  set authorization = "Bearer <anon ES256 JWT>"
else
  set authorization = apikey               -- legacy JWT key copied as-is
end
```
So an unauthenticated request (only `apikey: sb_publishable_xxx`) gets a pre-signed anon ES256 JWT; an authenticated request (`Authorization: Bearer eyJ...`) is passed through untouched. The upstream verifies against `JWT_JWKS` (ES256) or `JWT_SECRET` (legacy HS256) — both live in the JWKS.

## Key Takeaways
1. New and legacy keys coexist; migrate clients incrementally.
2. Auth signs with `JWT_KEYS`; all verifiers need `JWT_JWKS`.
3. Rotation keeps sessions alive; regeneration kills ES256 sessions.
4. `JWT_SECRET` stays in the JWKS → legacy HS256 tokens keep working.
5. Opaque keys are matched literally (no checksum validation self-hosted); one key per role.
6. Internal pre-signed JWTs are gateway-only — never in app code.

## Connects To
- **Ch 1**: keys generated during Docker setup.
- **Ch 3**: Envoy performs the same opaque→internal translation as Kong.
- **Ch 6**: Storage session-token S3 auth uses `ANON_KEY`.
