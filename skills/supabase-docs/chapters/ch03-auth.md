# Chapter 3: Authentication & Authorization

## Core Idea
Supabase splits identity into two halves and connects them with one artifact: a **JWT**. *Authentication* (who you are) is handled by the Auth server, which issues short-lived access tokens. *Authorization* (what you can touch) is handled by **Postgres Row Level Security (RLS)**, which reads claims out of that same JWT. The client library attaches the access token on every request; Postgres maps it to a role (`anon` / `authenticated`) and a `sub` (user UUID), then evaluates per-row policies. This means access control lives *in the database*, not scattered across API code, so it holds even when data is reached through third-party tooling ("defense in depth").

## Frameworks Introduced
- **Row Level Security (RLS)**: per-row authorization enforced by Postgres.
  - When to use: ALWAYS on any table in an exposed schema (`public`). Without it, enabling the API exposes all rows.
  - How: `alter table t enable row level security;` then attach `create policy` rules. A policy is an implicit `WHERE` clause appended to every query. Use `using` (which rows are visible / can be acted on) and `with check` (which new rows are allowed).
- **JWT / claims model**: `<header>.<payload>.<signature>`, Base64URL JSON. Key claims: `sub` (user UUID), `role` (Postgres role for RLS), `exp`, `iss`, `aal` (MFA level), `amr` (auth methods), `session_id`, `is_anonymous`.
- **Session model**: access token (short-lived JWT, 5min–1h) + refresh token (one-time use, never expires). Refreshing exchanges the refresh token for a new pair. Reuse-detection revokes the whole session if a token is reused outside the 10s grace window.
- **OAuth / social login**: delegate identity to Google/GitHub/etc. via `signInWithOAuth`. Provider tokens are NOT stored server-side.
- **MFA (AAL)**: layered factors raise Authenticator Assurance Level `aal1` → `aal2`, encoded in the JWT and enforced via RLS.
- **SSO / SAML 2.0**: enterprise IdP login via `signInWithSSO({ domain })`; per-IdP `sso_provider_id` drives multi-tenant RLS.

## Key Concepts
- **Roles**: Supabase maps each request to `anon` (logged out) or `authenticated` (logged in). Use the `TO` clause in policies to scope them. An *anonymous user* (from `signInAnonymously()`) still uses the `authenticated` role — distinguish it via the `is_anonymous` JWT claim, NOT the role.
- **`app_metadata` vs `user_metadata`**: `raw_app_meta_data` cannot be edited by the user → safe for authorization data (teams, roles). `raw_user_meta_data` is user-editable → NEVER trust it in RLS.
- **Helper functions**: `auth.uid()` (current user UUID), `auth.jwt()` (full token). Wrap them in `(select ...)` so Postgres caches the result per-statement.
- **JWT freshness**: claims reflect the token at issue time. Removing a user from a team won't take effect in `auth.jwt()` until the next refresh.
- **Verification**: prefer `supabase.auth.getClaims()` or a JWKS-based library (asymmetric keys via `/auth/v1/.well-known/jwks.json`). Avoid HS256 shared-secret verification.

## Mental Models
- **Policy = WHERE clause.** `using ((select auth.uid()) = user_id)` literally becomes `where auth.uid() = todos.user_id`.
- **Permissive vs restrictive policies.** Permissive policies OR together (any pass = allow). `as restrictive` policies AND with everything (all must pass) — required for hard gates like MFA enforcement.
- **JWT as portable session.** Because authz data is encoded in the token, an Auth-server outage doesn't take down data access; tokens self-verify.

## Anti-patterns
- Leaving RLS off on a `public` table (full data exposure).
- Using `user_metadata` for authorization (user-editable → privilege escalation).
- Forgetting `auth.uid()` returns `null` when unauthenticated; `null = user_id` is silently false. Add `auth.uid() IS NOT NULL AND ...`.
- Omitting `as restrictive` on MFA/security gate policies (a permissive policy elsewhere re-opens access).
- Calling `auth.uid()` unwrapped in policies (re-runs per row; wrap in `select`).
- Verifying JWTs with an HS256 shared secret (leak = full impersonation; blocks SOC2/HIPAA).
- Treating SSO emails as unique — SSO accounts don't identity-link, so use the user UUID.

## Code Examples
```sql
-- Enable RLS + own-row CRUD
alter table profiles enable row level security;

create policy "Users can see their own profile only."
on profiles for select
to authenticated
using ( (select auth.uid()) = user_id );

create policy "Users can update their own profile."
on profiles for update
to authenticated
using ( (select auth.uid()) = user_id )
with check ( (select auth.uid()) = user_id );
```
- **What it demonstrates**: the canonical own-row pattern. `using` filters visible/updatable rows; `with check` blocks reassigning `user_id` to someone else. Note: an UPDATE policy also requires a SELECT policy to work.

```sql
-- Hard MFA gate (restrictive = ANDs with all other policies)
create policy "Require aal2."
on table_name as restrictive to authenticated
using ((select auth.jwt()->>'aal') = 'aal2');
```
- **What it demonstrates**: enforcing MFA in the database via the `aal` claim.

## Reference Tables

Auth methods → JWT `amr` method:
| Method | `amr` | Sign-in call |
|---|---|---|
| Email+password | `password` | `signInWithPassword` |
| Magic link / email OTP | `otp`, `magiclink` | `signInWithOtp` → `verifyOtp(type:'email')` |
| Phone OTP (SMS/WhatsApp) | `otp` | `signInWithOtp({phone})` → `verifyOtp(type:'sms')` |
| Social / OAuth | `oauth` | `signInWithOAuth({provider})` |
| SSO (SAML) | `sso/saml` | `signInWithSSO({domain})` |
| Anonymous | `anonymous` | `signInAnonymously()` |
| TOTP / phone second factor | `totp` | MFA challenge+verify |

MFA factors: **App Authenticator (TOTP)** and **Phone** (Supabase-generated code). APIs: `mfa.enroll`, `mfa.challenge`, `mfa.verify`, `mfa.listFactors`, `mfa.unenroll`, `mfa.getAuthenticatorAssuranceLevel`. Only `verified` factors count.

Roles: `anon` (logged out), `authenticated` (logged in, incl. anonymous users), `service_role` (bypasses RLS — server only).

## Worked Example
Goal: a `todos` table each user can only see/manage their own rows, with email-OTP login.

```sql
create table todos (id uuid primary key, user_id uuid references auth.users, task text);
alter table todos enable row level security;

create policy "own todos - select" on todos for select to authenticated
  using ( (select auth.uid()) = user_id );
create policy "own todos - insert" on todos for insert to authenticated
  with check ( (select auth.uid()) = user_id );
create index todos_user_id on todos using btree (user_id);  -- RLS perf
```
```js
// 1. send OTP
await supabase.auth.signInWithOtp({ email: 'user@example.com' })
// 2. verify -> creates session, attaches JWT to all later requests
const { data:{ session } } = await supabase.auth.verifyOtp({
  email: 'user@example.com', token: '123456', type: 'email',
})
// 3. query — RLS auto-filters to this user's rows
const { data } = await supabase.from('todos').select().eq('user_id', session.user.id)
```
The `.eq` duplicates the policy but lets Postgres build a better plan.

## Key Takeaways
- RLS is mandatory, not optional, on exposed tables; policies are implicit `WHERE` clauses.
- The JWT is the bridge: `auth.uid()`/`auth.jwt()` in SQL read its claims; `role` selects the Postgres role.
- Always scope policies with `TO authenticated`/`anon`, wrap `auth.*()` in `select`, and index policy columns.
- Use `app_metadata` (not `user_metadata`) and `as restrictive` policies for real authorization gates.
- Prefer asymmetric signing keys + JWKS verification over HS256 shared secrets.

## Connects To
- **Ch. (Database/Postgres)**: roles, indexes, security-definer functions, views (`security_invoker`).
- **Ch. (API / PostgREST)**: the auto-generated REST API that RLS guards.
- **Self-hosting skill**: GoTrue config, SMTP, SAML/OAuth env vars for Docker deployments.
