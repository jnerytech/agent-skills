# Chapter 17: Integrations

## Core Idea
Supabase exposes itself as a programmable Platform-as-a-Service. Integrations come in two shapes: (1) you operate Supabase **on behalf of your own users** by owning the organization and driving everything through the Management API + MCP server ("Supabase for Platforms"), or (2) you operate **on behalf of the user's own organization** via an **OAuth 2.0** app that obtains delegated Management API access. Marketplaces (Vercel, Supabase Partners) are productized front-ends over these same primitives. The whole surface is the Management API (`https://api.supabase.com/v1`) plus client/Postgres/PostgREST/GraphQL endpoints.

> Scope note: the source set covers OAuth apps, partner/platform integration, OAuth scopes, and marketplaces. It contains **no material on Vault or Foreign Data Wrappers (Wrappers)** — those topics live in other docs sections and are absent here.

## Frameworks Introduced
- **OAuth 2.0 + PKCE flow:** delegated, revocable access to a user's orgs/projects via the Management API.
- **Supabase for Platforms (PaaS model):** you own the org; full programmatic lifecycle (create → branch → migrate → restore-point → merge → claim) over the Management API.
- **Partner Install flow (Redirect vs Signed Redirect):** how the Dashboard "Install Integration" button hands a user off to a partner; signed variant uses an ES256 JWT for origin verification.
- **OAuth Scopes model:** resource-typed, read/write-split permissions restricting which Management API endpoints a token may call.

## Key Concepts
- **Management API** — single programmatic control plane at `https://api.supabase.com/v1`; authenticated with a PAT (`YOUR_SECRET_TOKEN`) or an OAuth access token.
- **OAuth app** — created under org settings → **OAuth Apps**; yields `client_id` + `client_secret`; scopes fixed at creation (changing them forces re-authorization).
- **PKCE** — `code_challenge` (SHA256 of a random `code_verifier`) + `code_challenge_method=S256`; verifier replayed at token exchange. Strongly recommended.
- **Access/refresh token** — exchanged at `POST /v1/oauth/token`; refresh fails once the user revokes — always handle HTTP 401.
- **Smart region selection** — codes `americas`, `emea`, `apac`; ensures capacity at project creation.
- **Scale-to-zero** — only Nano instances; do not pass `desired_instance_size` to keep Nano. Micro and larger never scale to zero.
- **Restore point / PITR** — `restore-point` + `undo` capture only DB changes; PITR (`restore-pitr`) must be pre-enabled in prod.
- **Claim flow** — `GET /v1/oauth/authorize/project-claim` transfers a project from your org to the user's org while you retain OAuth access.
- **Platform Kit** — embeddable UI components wrapping the Management API (a mini-Dashboard inside your app).
- **`state` parameter** — round-tripped CSRF token; also the trick for encoding dynamic redirect URLs (`redirect_uri` + `state` together ≤ 4kB).

## Mental Models
- **"Branches are ephemeral servers."** Because Supabase is *stateful*, you can't roll back prod blindly. Push every change to a `DEV` branch, verify, then merge. Merge propagates **only** DB changes + deployed Edge Functions.
- **"The token is a leash, the scopes are its length."** OAuth grants Management API reach bounded by resource-typed read/write scopes; revocation cuts the leash entirely.
- **Two ownership axes:** *you own the org* (Platforms) vs *user owns the org* (OAuth). Pick before designing.

## Anti-patterns
- Reusing one DB password across projects, or trying to change it via API (impossible — only the Dashboard does, manually). Store the encrypted password yourself.
- Putting **production data in DEV branches** — security + side-effects (e.g. emailing all prod users).
- Using "Supabase" in your integration's product name — violates brand/trademark listing rules.
- Assuming a project is usable immediately after `POST /v1/projects` — poll `GET /v1/projects/{ref}/health` until `ACTIVE_HEALTHY` before configuring a service.
- Relying on legacy `anon`/`service_role` keys for new integrations — migrate to `publishable`/`secret`.

## Code Examples

### Redirect to the authorize URL (PKCE)
```ts
router.get('/connect-supabase/login', async (ctx) => {
  const { uri, codeVerifier } = await oauth2Client.code.getAuthorizationUri()
  // https://api.supabase.com/v1/oauth/authorize?response_type=code&client_id=...&redirect_uri=...&scope=all&code_challenge=...&code_challenge_method=S256
  ctx.state.session.flash('codeVerifier', codeVerifier)
  ctx.response.redirect(uri)
})
```
Required query params on `GET /v1/oauth/authorize`: `client_id`, `redirect_uri`, `response_type=code`, `state`, optional `organization_slug`, `code_challenge` + `code_challenge_method=S256`. (`scope` is deprecated — scopes are set at app creation.)

### Exchange code for tokens
```ts
const tokens = await fetch(config.tokenUri, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
    Accept: 'application/json',
    Authorization: `Basic ${btoa(`${config.clientId}:${config.clientSecret}`)}`,
  },
  body: new URLSearchParams({
    grant_type: 'authorization_code',
    code: ctx.request.url.searchParams.get('code') || '',
    redirect_uri: config.redirectUri,
    code_verifier: codeVerifier,
  }),
}).then((res) => res.json())
```
`redirect_uri` must be byte-identical to the authorize step. Client id/secret go in the Basic auth header.

### Management JS SDK
```ts
import { SupabaseManagementAPI } from 'supabase-management-js'
const client = new SupabaseManagementAPI({ accessToken: '<access token>' })
```

### Pre-filled Postgres connection string
```
postgresql://postgres:[DB-PASSWORD]@db.[REF].supabase.co:5432/postgres
```

### Create a project (Platforms model)
```sh
curl https://api.supabase.com/v1/projects \
  --request POST \
  --header "Content-Type: application/json" \
  --header "Authorization: Bearer YOUR_SECRET_TOKEN" \
  --data '{
    "name": "Todo App",
    "organization_slug": "aaaabbbbccccddddeeee",
    "db_pass": "SUPER_SECURE_PASSWORD",
    "region_selection": { "type": "smartGroup", "code": "americas" },
    "desired_instance_size": "micro"
  }'
```

### Enable modern API keys
```sh
curl 'https://api.supabase.com/v1/projects/{ref}/api-keys?reveal=true' \
  --request POST \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer YOUR_SECRET_TOKEN' \
  --data '{ "type": "secret", "name": "default",
            "secret_jwt_template": { "role": "service_role" } }'
```

### Run a migration (auto-creates + runs in `supabase_migrations`; rolls back on failure)
```sh
curl https://api.supabase.com/v1/projects/{ref}/database/migrations \
  --request POST \
  --header 'Authorization: Bearer YOUR_SECRET_TOKEN' \
  --header 'Content-Type: application/json' \
  --data '{ "query": "create table public.todos (id serial primary key, task text not null); alter table public.todos enable row level security;",
            "name": "Create a todos table" }'
```

### Partner signed-redirect: example public keys (PEM EC P-256, looked up by JWT `kid`)
```
Key ID: pik_3038669348a3ea75dbaf0655   (staging)
-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEnj3NmwrLPPH/3isvpS601ndQP9Mk
zqppdLDV9YfmoF4wavTyb9UTVE5pJ0fukpo5aOoNb4fBZgESsedIUoEn8Q==
-----END PUBLIC KEY-----
```
Signed JWT: header `alg=ES256`, `kid`; claims `iss=supabase`, `aud`, `iat`, `exp` (≤ 5 min after `iat`), optional `organization_slug`, `project_id`. Validate all six checks → else `401`.

## Reference Tables

### Integration categories / entry points
| Category | Mechanism | Notes |
|---|---|---|
| Vercel Marketplace | Managed via Vercel, unified billing | Public Alpha; auto-syncs env vars; no custom domains |
| Supabase Marketplace | Partners: Experts + Integrations | Auth/Caching/Hosting/Low-code tools |
| OAuth app | Delegated Management API access | User owns the org |
| Supabase for Platforms | Direct Management API / MCP | You own the org |
| Postgres / REST / GraphQL / Platform API | Raw integration points | "Anything that works with Postgres works with Supabase" |

### OAuth scopes (resource type → read/write)
| Scope | Read covers | Write covers |
|---|---|---|
| Auth | auth config, SAML SSO providers | update auth config, manage SAML providers |
| Database | DB/pooler config, SQL snippets, read-only/SSL/TS types | run SQL, webhooks, config, PITR backup, disable read-only |
| Domains | custom + vanity domain config | activate/init/reverify/delete domains |
| Edge Functions | function info | create/update/delete functions |
| Environment | list branches | create/update/delete branches |
| Organizations | org metadata, members | N/A |
| Projects | metadata, upgrade eligibility, network restrictions/bans | create, upgrade, manage network restrictions/bans |
| Rest | PostgREST config | update PostgREST config |
| Secrets | API keys, secrets, pgsodium config | create/update secrets + pgsodium |
| Storage | list buckets | — |

### Partner install: Redirect vs Signed Redirect
| | Method 1: Redirect | Method 2: Signed Redirect |
|---|---|---|
| Endpoints | one `GET` | `POST` (validate JWT → return one-time URL) + `GET` (handler) |
| Origin verification | none | ES256 JWT, `kid`-keyed public key |
| Use when | speed of build | production / security-sensitive (recommended) |
| Dashboard sends | `project_id`, `organization_slug` as query params | signed JWT in `POST` body `{"token": "..."}` |

## Worked Example: third-party OAuth integration end-to-end
1. **Create the OAuth app** — Dashboard → org → **OAuth Apps** → Add application; set scopes (e.g. `Projects:Write`, `Database:Write`). Capture `client_id` / `client_secret`.
2. **Connect button** — render a "Connect Supabase" button per brand guidelines.
3. **Authorize** — redirect to `GET /v1/oauth/authorize` with `client_id`, `redirect_uri`, `response_type=code`, `state`, and PKCE `code_challenge`/`S256`; stash `codeVerifier` in session.
4. **Callback** — verify returned `state` == sent `state`; `POST /v1/oauth/token` with `grant_type=authorization_code`, `code`, identical `redirect_uri`, `code_verifier`, and Basic-auth `client_id:client_secret`. Store access + refresh tokens.
5. **Call Management API** — `new SupabaseManagementAPI({ accessToken })`; create a project, poll `health` for `ACTIVE_HEALTHY`, enable `publishable`/`secret` keys, set custom SMTP via `/config/auth`.
6. **Refresh & revocation** — refresh via `POST /v1/oauth/token`; treat 401 as "user revoked" and re-trigger the flow.
7. **(Optional) Claim** — let the user pull the project into their own org via `GET /v1/oauth/authorize/project-claim` while you keep OAuth access.

## Key Takeaways
- One control plane: the Management API (`api.supabase.com/v1`); OAuth tokens and PATs are interchangeable auth, gated by scopes.
- Always PKCE, always echo `state`, always re-use the exact `redirect_uri`.
- Scopes are fixed at app creation; changing them forces every existing user to re-authorize.
- For platform builders: ship changes through ephemeral DEV branches + restore points; never roll prod back blindly.
- Marketplaces (Vercel) are convenience wrappers — same projects, different billing/permission sync, with documented limitations.

## Connects To
- **Ch. on Management API / MCP** — the underlying control plane every integration calls.
- **Auth chapter** — SMTP, SAML, the `Auth` scope.
- **Database / Branching chapter** — migrations, restore points, PITR, branch merge.
- **Platform / API Keys chapter** — `publishable`/`secret` key migration, network restrictions.
- **(Absent here) Vault & Foreign Data Wrappers** — referenced by the task but not present in this source set; see the database/security docs sections.
