# Chapter 4: Configure Social Login (OAuth) Providers

## Core Idea
Server-side OAuth/OIDC setup is a fixed pattern: register your app with the provider, put `*_CLIENT_ID/SECRET` in `.env`, add the matching `GOTRUE_EXTERNAL_*` passthroughs in `docker-compose.yml`, recreate the `auth` service. The single most common failure is a `.env` var with no matching passthrough.

## Frameworks Introduced
- **The `GOTRUE_EXTERNAL_<PROVIDER>_` convention**: every provider needs at minimum `ENABLED`, `CLIENT_ID`, `SECRET`, `REDIRECT_URI`.
  - When to use: enabling any of the ~20 supported OAuth/OIDC providers.
  - How: `.env` holds `GOOGLE_ENABLED/CLIENT_ID/SECRET`; `docker-compose.yml` maps them to `GOTRUE_EXTERNAL_GOOGLE_*`; `REDIRECT_URI = ${API_EXTERNAL_URL}/auth/v1/callback`.
- **Two-layer config rule**: a `.env` value is invisible inside the container without a passthrough line in `docker-compose.yml`. This is THE recurring gotcha.
- **HTTPS requirement**: most providers reject `http://` callbacks (except `localhost`). Callback URL is always `https://<your-domain>/auth/v1/callback`.

## Key Concepts
- **OAuth callback URL**: `https://<your-domain>/auth/v1/callback` — registered identically at every provider.
- **`SITE_URL` / `ADDITIONAL_REDIRECT_URLS`**: where Auth redirects post-login; mismatches cause redirect errors.
- **Multi-word prefixes**: LinkedIn and Slack OIDC use `LINKEDIN_OIDC_` and `SLACK_OIDC_` → `GOTRUE_EXTERNAL_LINKEDIN_OIDC_CLIENT_ID`, not `LINKEDIN_CLIENT_ID`.
- **Provider `URL` extra var**: Keycloak (realm URL, **required**), Azure (tenant), GitHub Enterprise, self-hosted GitLab.

## Mental Models
- Think "two places, every time": value in `.env`, passthrough in `docker-compose.yml`. If a provider shows `false`, you forgot one of them.
- The OAuth flow always lands at `/auth/v1/callback`; Auth then redirects to `SITE_URL` or an allowed redirect.

## Anti-patterns
- **`.env` var without passthrough**: provider silently disabled. Verify with `docker compose exec auth env | grep GOTRUE_EXTERNAL`.
- **`GOTRUE_EXTERNAL_SKIP_NONCE_CHECK=true` left on**: weakens replay protection. Short-lived debugging only; prefer fixing client nonce / using auth-code+PKCE.
- **Keycloak without `KEYCLOAK_URL`**: login won't work — Auth needs the realm URL to discover OIDC endpoints.
- **`http://` callback in production**: rejected by providers.

## Code Examples
```sh name=.env
GOOGLE_ENABLED=true
GOOGLE_CLIENT_ID=your-id.apps.googleusercontent.com
GOOGLE_SECRET=your-secret
```
```yaml name=docker-compose.yml
auth:
  environment:
    GOTRUE_EXTERNAL_GOOGLE_ENABLED: ${GOOGLE_ENABLED}
    GOTRUE_EXTERNAL_GOOGLE_CLIENT_ID: ${GOOGLE_CLIENT_ID}
    GOTRUE_EXTERNAL_GOOGLE_SECRET: ${GOOGLE_SECRET}
    GOTRUE_EXTERNAL_GOOGLE_REDIRECT_URI: ${API_EXTERNAL_URL}/auth/v1/callback
```
```sh
docker compose up -d --force-recreate --no-deps auth      # apply
curl -H 'apikey: your-anon-key' https://<your-domain>/auth/v1/settings  # verify -> "external":{"google":true}
```
- **What it demonstrates**: the canonical two-layer setup + verification.

## Reference Tables
OAuth request flow:
1. App calls `signInWithOAuth()` → browser → `/auth/v1/authorize`
2. Auth → provider consent
3. Provider → `https://<your-domain>/auth/v1/callback`
4. Auth exchanges code for tokens → redirects to `SITE_URL`/allowed URL

Providers needing an extra `URL` var:
| Provider | Prefix | Extra |
|---|---|---|
| Azure | `AZURE_` | tenant `URL` (default `common`) |
| GitHub | `GITHUB_` | `URL` (Enterprise) |
| GitLab | `GITLAB_` | `URL` (self-hosted) |
| Keycloak (OIDC) | `KEYCLOAK_` | realm `URL` **required** |
| LinkedIn (OIDC) | `LINKEDIN_OIDC_` | multi-word prefix |
| Slack (OIDC) | `SLACK_OIDC_` | multi-word prefix |

(Also: Apple, Bitbucket, Discord, Facebook, Figma, Google, Kakao, Notion, Snapchat, Spotify, Twitch, Twitter, WorkOS, Zoom.)

## Worked Example — debugging "provider seen as false"
1. Check `docker-compose.yml` has `GOTRUE_EXTERNAL_GOOGLE_ENABLED: ${GOOGLE_ENABLED}` (not commented).
2. Confirm `.env` value isn't empty: `docker compose exec auth env | grep GOOGLE`.
3. Confirm it reached the container: `docker compose exec auth env | grep GOTRUE_EXTERNAL`.
4. If login succeeds but redirect errors → set `SITE_URL`; add other targets to `ADDITIONAL_REDIRECT_URLS` (comma-separated).
5. If `auth` won't start → `docker compose logs auth`; usual cause: empty `CLIENT_ID`/`SECRET` or invalid `API_EXTERNAL_URL`.

## Key Takeaways
1. Every provider: `.env` value + `docker-compose.yml` passthrough — both, every time.
2. Callback is always `${API_EXTERNAL_URL}/auth/v1/callback`; HTTPS required.
3. Recreate `auth` (`--force-recreate --no-deps`) after changes; verify via `/auth/v1/settings`.
4. Keycloak needs the realm `URL`; LinkedIn/Slack use `_OIDC_` prefixes.
5. `SKIP_NONCE_CHECK` is a temporary workaround, not a fix.
6. Set `SITE_URL`/`ADDITIONAL_REDIRECT_URLS` to avoid post-login redirect errors.

## Connects To
- **Ch 5**: SAML SSO (configured at runtime via admin API, not env vars).
- **Ch 8**: HTTPS is a prerequisite for OAuth.
- **Ch 10**: phone login & MFA share the same `GOTRUE_*` passthrough pattern.
