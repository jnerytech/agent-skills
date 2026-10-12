# Chapter 5: Configure SAML SSO

## Core Idea
SAML 2.0 SSO is configured in **two layers**: a small set of env vars enable the engine + signing key (restart needed), and individual IdPs are registered/updated/deleted at **runtime via the Auth admin API** (no restart). This runtime-managed model is the key difference from OAuth.

## Frameworks Introduced
- **Two-layer SAML config**:
  - Global enable: `GOTRUE_SAML_ENABLED=true` + `GOTRUE_SAML_PRIVATE_KEY` in `.env`/`docker-compose.yml`, then `docker compose down && up -d`.
  - Per-IdP: `POST /auth/v1/admin/sso/providers` with `SERVICE_ROLE_KEY` — add IdPs live.
- **IdP registration: metadata URL vs inline XML**:
  - When to use: metadata URL (recommended) when the IdP exposes one — Auth fetches, caches, auto-refreshes (must be HTTPS). Inline `metadata_xml` when you only have the XML.
- **Attribute mapping**: map SAML assertion attributes → user claims stored in `raw_user_meta_data` (`user.user_metadata`). Each key supports `name`, `names` (fallback list), `default`, `array`.

## Key Concepts
- **SP entity ID**: `{API_EXTERNAL_URL}/sso/saml/metadata`. **ACS URL**: `{API_EXTERNAL_URL}/sso/saml/acs`.
- **`SAML_PRIVATE_KEY`**: Base64-encoded PKCS#1 DER RSA key, ≥2048-bit (4096 recommended for prod).
- **Domain-based vs provider-based lookup**: `signInWithSSO({domain})` (extract from email) vs `({providerId})` (dedicated button).
- **SP metadata endpoint**: `{API_EXTERNAL_URL}/sso/saml/metadata` (add `?download=true` for a file with 5-year validity).

## Mental Models
- Think: env vars are the *engine* (set once, restart); the admin API is the *control panel* (add/remove IdPs anytime, no restart).
- The ACS and metadata routes are **open** at the gateway (no key-auth) — if the IdP can't reach them, that's the first thing to check.

## Anti-patterns
- **Committing/leaking `SAML_PRIVATE_KEY`**: anyone with it can forge SAML requests as your SP.
- **Multi-line base64 key**: must be single line, no breaks, PKCS#1 (`openssl pkey ... -traditional`), ≥2048-bit — else "Invalid private key" on startup.
- **`localhost` `API_EXTERNAL_URL` for real IdPs**: IdP can't reach the ACS endpoint.
- **Clock skew**: SAML assertions have `NotBefore`/`NotOnOrAfter` windows — keep server/IdP time synced.

## Code Examples
```sh
# 1. Generate the key
openssl genpkey -algorithm RSA -out pk_pkcs8.pem -quiet && \
openssl pkey -in pk_pkcs8.pem -out pk_rsa1.der -outform DER -traditional && \
base64 -w 0 -i pk_rsa1.der
```
```yaml name=docker-compose.yml
auth:
  environment:
    GOTRUE_SAML_ENABLED: ${SAML_ENABLED}
    GOTRUE_SAML_PRIVATE_KEY: ${SAML_PRIVATE_KEY}
```
```sh
# Register IdP (metadata URL, recommended)
curl -X POST 'http://<your-domain>/auth/v1/admin/sso/providers' \
  -H 'Authorization: Bearer your-service-role-key' -H 'apikey: your-service-role-key' \
  -H 'Content-Type: application/json' \
  -d '{"type":"saml","metadata_url":"https://idp.example.com/saml/metadata","domains":["example.com"]}'
```
- **What it demonstrates**: key generation, engine enable, runtime IdP registration.

## Reference Tables
Env vars:
| Variable | Default | Purpose |
|---|---|---|
| `SAML_ENABLED` | `false` | Enable engine |
| `SAML_PRIVATE_KEY` | - | Base64 PKCS#1 RSA ≥2048-bit |
| `SAML_ALLOW_ENCRYPTED_ASSERTIONS` | `false` | Accept encrypted assertions |
| `SAML_RELAY_STATE_VALIDITY_PERIOD` | `2m0s` | Relay-state token lifetime |
| `SAML_EXTERNAL_URL` | `API_EXTERNAL_URL` | Override entity ID / ACS base |
| `SAML_RATE_LIMIT_ASSERTION` | `15` | ACS requests/sec (anti-replay) |

Registration params: `type`(req `"saml"`), `metadata_url`|`metadata_xml`(one req), `domains`, `attribute_mapping`, `name_id_format`(`persistent`/`emailAddress`/`transient`/`unspecified`), `resource_id`, `disabled`.

Admin API: `POST` (create), `GET` (list / `?resource_id=` / `?resource_id_prefix=`), `GET /{id}`, `PUT /{id}` (update or `{"disabled":true}`), `DELETE /{id}`.

## Worked Example — attribute mapping with fallbacks and arrays
```json
{"attribute_mapping":{"keys":{
  "email":{"name":"http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress"},
  "groups":{"name":"http://schemas.microsoft.com/ws/2008/06/identity/claims/groups","array":true},
  "role":{"names":["http://schemas.microsoft.com/ws/2008/06/identity/claims/role","role","Role"],"default":"member"}
}}}
```
`name` = primary attribute (matched case-insensitively vs `Name` and `FriendlyName`); `names` = ordered fallbacks; `array: true` collects all values (groups); `default` fills when absent (`role`→`member`). Result lands in `user.user_metadata`. Verify a session: `GET /auth/v1/user` → `app_metadata.provider: "sso:saml"`.

## Key Takeaways
1. Two layers: env (engine, restart) + admin API (IdPs, live).
2. SP entity ID = `.../sso/saml/metadata`; ACS = `.../sso/saml/acs`; both open at gateway.
3. Private key: single-line base64 PKCS#1 RSA ≥2048-bit; keep it secret.
4. Prefer `metadata_url` (HTTPS, auto-refresh) over inline XML.
5. Use `domain` lookup for email-first login forms, `providerId` for dedicated buttons.
6. Watch clock skew and the relay-state validity window for slow-network timeouts.

## Connects To
- **Ch 4**: contrast with OAuth (env-var only, no runtime API).
- **Ch 8**: HTTPS / reachable `API_EXTERNAL_URL` for IdP callbacks.
- **Ch 1**: `SERVICE_ROLE_KEY` from `.env` authorizes the admin API.
