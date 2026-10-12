# Glossary

**ACS URL** — SAML assertion consumer endpoint, `{API_EXTERNAL_URL}/sso/saml/acs`; open at gateway (Ch 5).
**add-new-auth-keys.sh** — utility generating EC P-256 keypair, JWKS, asymmetric JWTs, and new `sb_` keys; regeneration invalidates ES256 sessions (Ch 2).
**ANON_KEY** — legacy HS256 client-side API key (`role: anon`) (Ch 2).
**API_EXTERNAL_URL** — public URL Auth uses for callbacks; SAML SP entity-ID base (Ch 1, 4, 5, 8).
**api-gw** — Envoy's service name / network alias (aliases `kong`) (Ch 3).
**Attribute mapping** — SAML config mapping assertion attributes → user claims in `user_metadata` (Ch 5).
**Basic auth (dashboard)** — HTTP basic auth protecting Studio via `DASHBOARD_USERNAME`/`PASSWORD` (Ch 1, 3).
**CDS (cds.yaml)** — Envoy Cluster Discovery Service: upstream definitions (Ch 3).
**COMPOSE_FILE** — `.env` var controlling which override files layer onto `docker-compose.yml` (Ch 1).
**config add/remove** — `run.sh` subcommands toggling override files via `COMPOSE_FILE` (Ch 1).
**db-config volume** — Docker named volume holding the pgsodium root key; never destroy (Ch 7).
**Docker bridge gateway IP** — source IP when tunneling into Studio; allow-listed for MCP (e.g. `172.18.0.1`) (Ch 11).
**Edge Runtime** — Deno-based web server running Edge Functions (Ch 1, 9).
**Envoy** — optional API gateway replacing Kong via `docker-compose.envoy.yml` (Ch 3).
**FUNCTIONS_VERIFY_JWT** — toggles JWT verification for Edge Functions (Ch 9).
**generate-keys.sh** — utility creating secure passwords/secrets (`SECRET_KEY_BASE`, `VAULT_ENC_KEY`, etc.) (Ch 1).
**GoTrue / Auth** — JWT-based authentication service; all config uses `GOTRUE_` prefix (Ch 1, 4, 5, 10).
**GOTRUE_EXTERNAL_*** — env prefix for OAuth/OIDC provider config (Ch 4).
**GOTRUE_MAILER_TEMPLATES_*** — env vars pointing Auth at email-template URLs (Ch 13).
**GOTRUE_SMS_*** — env vars for SMS provider / OTP config (Ch 10).
**imgproxy** — image processing server in the stack (Ch 1).
**ip-restriction** — Kong plugin allow-listing IPs (used to enable MCP) (Ch 11).
**JWKS** — JSON Web Key Set; `/auth/v1/.well-known/jwks.json` exposes the EC public key (Ch 2).
**JWT_JWKS** — JWKS (EC public + legacy symmetric) used by PostgREST/Realtime/Storage to verify (Ch 2).
**JWT_KEYS** — JSON array of signing JWKs (EC private + symmetric) used by Auth to sign (Ch 2).
**JWT_SECRET** — symmetric secret for HS256; kept in JWKS for backward compat (Ch 2, 9).
**Kong** — default API gateway on port 8000 (Ch 1, 2, 8, 11).
**LDS (lds.template.yaml / lds.yaml)** — Envoy Listener Discovery Service template / rendered config (Ch 3).
**Logflare** — log management / analytics (optional, off by default) (Ch 1).
**Magic link** — passwordless email login flow (`MAGIC_LINK` template) (Ch 13).
**MCP server** — Model Context Protocol server behind Studio; denied by default (Ch 11).
**Metadata URL (SAML)** — IdP metadata endpoint Auth fetches/auto-refreshes (must be HTTPS) (Ch 5).
**MFA** — multi-factor auth: TOTP (default on), Phone (opt-in) (Ch 10).
**MinIO** — legacy S3-compatible backend (Chainguard image now) (Ch 6).
**Notification template** — email sent on account events (`PASSWORD_CHANGED`, etc.); needs `_ENABLED` (Ch 13).
**OAuth callback URL** — `https://<your-domain>/auth/v1/callback` (Ch 4).
**Opaque key** — `sb_publishable`/`sb_secret` random key with checksum; matched literally (Ch 2).
**OTP** — one-time SMS code; `SMS_OTP_EXP`/`LENGTH`/`MAX_FREQUENCY` tune it (Ch 10).
**Override file** — `docker-compose.<name>.yml` layered onto the base (logs, envoy, caddy, nginx, s3, rustfs, pg17) (Ch 1, 3, 6, 7, 8).
**PG_META_DB_USER** — meta-service DB role; switch to `postgres` to drop superuser (Ch 14).
**pg_upgrade** — in-place PG15→PG17 migration tool driven by `upgrade-pg17.sh` (Ch 7).
**pgsodium root key** — encryption key in `db-config` volume; loss → Vault secrets unrecoverable (Ch 7).
**PKCS#1 DER** — RSA key format required (Base64) for `SAML_PRIVATE_KEY` (Ch 5).
**POSTGRES_USER_READ_WRITE** — Studio DB role env var; set to `postgres` to remove superuser (Ch 14).
**PostgREST** — turns Postgres into a REST API (`/rest/v1/`) (Ch 1).
**Pre-signed internal JWT** — gateway-level ES256 JWT substituted for an `sb_` key; never use in app code (Ch 2).
**RBAC** — Envoy role-based access filter; `/pg/`→service_role, denies `/mcp` & Realtime mgmt (Ch 3, 11).
**reassign-owner.sh** — utility reassigning `public`-schema object ownership to `postgres` (Ch 14).
**recreate** — `run.sh`/compose op that picks up config changes (`--force-recreate`); unlike `restart` (Ch 1, 9).
**Realtime** — Elixir server broadcasting DB changes; needs WebSocket through proxies (Ch 1, 8).
**Relay state (SAML)** — token tracking an in-flight SSO request; `SAML_RELAY_STATE_VALIDITY_PERIOD` (default 2m) (Ch 5).
**reset.sh** — full teardown wrapper; destroys all data, resets `.env` (Ch 1).
**rclone** — S3 tool used for platform→self-hosted storage copy (Ch 6, 12).
**run.sh** — Compose stack management wrapper (start/stop/recreate/secrets/config/logs) (Ch 1).
**RustFS** — preferred local S3-compatible backend (`docker-compose.rustfs.yml`) (Ch 6).
**S3 backend** — where Storage keeps data (local files or S3-compatible) (Ch 6).
**S3 protocol endpoint** — `/storage/v1/s3`, S3-compatible API over any backend (Ch 6, 12).
**SAML_PRIVATE_KEY** — Base64 PKCS#1 RSA key (≥2048-bit) signing SAML requests (Ch 5).
**session_replication_role = replica** — disables triggers during DB restore (Ch 15).
**SERVICE_ROLE_KEY** — legacy HS256 server-side key (`role: service_role`); authorizes admin APIs (Ch 2, 5).
**SITE_URL** — default post-auth redirect URL (Ch 1, 4).
**SMS_TEST_OTP** — dev mapping of phone numbers to fixed OTP codes (Ch 10).
**SMTP_*** — email server config for sending auth emails (Ch 1, 13).
**Studio** — the self-hosted dashboard (Ch 1, 14).
**supabase db dump** — CLI dump with Supabase-specific filtering (roles/schema/data) (Ch 15).
**supabase_admin** — legacy superuser role historically used by Studio (Ch 14, 15).
**SUPABASE_PUBLIC_URL** — base URL passed as `supabaseUrl` to clients (Ch 1, 9).
**SUPABASE_PUBLISHABLE_KEY / SUPABASE_SECRET_KEY** — new opaque client/server keys (Ch 2).
**SUPABASE_URL (functions)** — internal `http://kong:8000` for in-function service calls (Ch 9).
**Supavisor** — Postgres connection pooler; 5432 session / 6543 transaction (Ch 1, 15).
**templates-server** — private Caddy file-server serving email templates to Auth (Ch 13).
**TOTP** — time-based one-time-password MFA (app authenticator), on by default (Ch 10).
**TUS** — resumable upload protocol; `TUS_ALLOW_S3_TAGS:"false"` needed on R2 (Ch 6).
**Vault (Supabase)** — encrypted secrets store relying on the pgsodium key (Ch 7).
**Vector** — log collector forwarding to Logflare (Ch 1).
**X-Forwarded-Prefix** — header Storage needs for S3 SigV4 signing & TUS URLs (Ch 3, 6).
**`<your-domain>`** — placeholder for domain / server IP / `localhost` (Ch 1).
