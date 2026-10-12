# Chapter 15: Security & Compliance

## Core Idea

Supabase ships **secure-by-default** on its hosted platform but hands you a sharp, flexible toolset whose misconfiguration is *your* responsibility. Security splits along a **shared responsibility / compliance boundary**: everything inside the Supabase product (Postgres, Storage, Auth, Realtime, Edge Functions, Data API) is hardened, audited (SOC 2 Type 2 annually), and monitored by Supabase; everything that crosses out of the product, plus how you configure RLS, roles, and keys, is on you. Production security is therefore three concentric layers: **platform controls** (org-level: MFA, SSO, SSL, network restrictions, PrivateLink), **product controls** (per-product hardening: RLS, CLS, API exposure, Vault), and **supply-chain controls** (npm/Deno install hygiene). Compliance (SOC 2, HIPAA) does *not* transfer to your environment — it asserts Supabase's side of the boundary only.

## Frameworks Introduced

- **Shared Responsibility Model**: divides data security at the compliance boundary — Supabase secures data *inside* the product; the customer secures data *entering/leaving* it and all app-level access logic (RLS, roles, key handling).
- **SOC 2 Type 2 (Trust Services Criteria)**: security, availability, processing integrity, confidentiality, privacy — audited annually (rolling Mar 1–Feb 28 window); report available to Team/Enterprise via the org Legal Documents page.
- **HIPAA + BAA model**: Supabase = *business associate*, customer = *covered entity*; requires a signed BAA **and** the HIPAA add-on; controls enforced continuously and surfaced via the **Security Advisor**.
- **Defense-in-depth layering**: platform controls → product/RLS controls → supply-chain controls, each independently enforced.
- **Supply-chain hardening (npm)**: lockfile pinning + minimum release-age quarantine + provenance verification + lifecycle-script default-deny.

## Key Concepts

- **Compliance boundary**: the border between Supabase-managed and customer-managed data security. SOC 2/HIPAA only certify Supabase's side.
- **Security Advisor**: dashboard tool that continuously warns when project changes disable/weaken required (esp. HIPAA) controls. Warnings only — remediation is the customer's duty.
- **Row Level Security (RLS)**: per-row access policies enforced by Postgres. Mandatory on any table exposed via the Data API (PostgREST).
- **Column Level Security (CLS)**: `GRANT`/`REVOKE` column privileges to hide sensitive columns from `anon`/`authenticated` roles even when row access is granted.
- **`anon` / `authenticated` / `service_role`**: the three Data API roles. `anon` = pre-login public, `authenticated` = logged-in user, `service_role` = bypasses RLS (server-side only, never ship to a client).
- **Data API hardening**: control which schemas are exposed (`Settings → API → Exposed schemas`); keep sensitive tables in a non-exposed schema (e.g. `private`).
- **Vault**: encrypted secrets storage inside Postgres for keys/tokens — never store secrets in plaintext columns.
- **Platform controls**: org-level MFA enforcement, SSO (SAML), Postgres SSL enforcement, IP network restrictions, PrivateLink (AWS VPC Lattice, beta).
- **Audit logs**: Platform Audit Logs (org member/dashboard/API actions; Team/Enterprise) + Auth Audit Logs (auth events). No export/log-drain yet; retention is plan-dependent.
- **Provenance / sigstore attestation**: cryptographic proof tying an npm tarball to its source commit + workflow; verified with `npm audit signatures`.

## Mental Models

- **"RLS is the firewall, not the lock on the door."** The Data API exposes every table in an exposed schema to the internet; without RLS, `select *` is open to `anon`. Enabling RLS with *no* policy denies all — fail closed.
- **Keys are blast radius.** A leaked `service_role` key bypasses all RLS. Treat any install host that touched it as compromised and rotate.
- **Compliance is continuous, not point-in-time.** The Security Advisor exists because controls drift between audits.

## Anti-patterns

- Exposing a table via the Data API with RLS disabled (or enabled but policy-less and then granting broad access).
- Shipping the `service_role` key to a browser/mobile client.
- Storing secrets/API keys in plaintext table columns instead of Vault.
- Assuming Supabase's SOC 2/HIPAA covers *your* app — it stops at the compliance boundary.
- Self-hosting and assuming HIPAA controls carry over (they do **not** — hosted-only).
- `npx pkg@latest` in CI (bypasses lockfile + age gate) and running unpinned postinstall scripts.

## Code Examples

```sql
-- Lock down a table exposed via the Data API
-- 1. Enable RLS (fail-closed: no policy => no access)
alter table public.profiles enable row level security;

-- 2. Revoke blanket table grants from API roles, then grant least-privilege
revoke all on public.profiles from anon, authenticated;
grant select, update on public.profiles to authenticated;

-- 3. Column Level Security: hide sensitive columns from clients
revoke select (ssn, internal_notes) on public.profiles from anon, authenticated;

-- 4. Owner-only row policy
create policy "Users manage own profile"
  on public.profiles
  for all
  to authenticated
  using ( (select auth.uid()) = user_id )
  with check ( (select auth.uid()) = user_id );

-- 5. Move sensitive tables out of the exposed schema entirely
create schema if not exists private;
revoke all on schema private from anon, authenticated;
alter table public.billing_secrets set schema private;
```

- **What it demonstrates**: fail-closed RLS, least-privilege `GRANT`/`REVOKE`, column-level masking, and removing tables from the API surface via a non-exposed schema — the four core data-API hardening moves.

## Reference Tables

**Production hardening checklist**

| Layer | Control | Action |
|---|---|---|
| Platform | MFA | Enforce org-wide MFA (org owner) |
| Platform | SSO | Enable SAML SSO for the org |
| Platform | SSL | Enforce Postgres SSL connections |
| Platform | Network | Restrict Postgres/pooler IP ranges; PrivateLink for AWS VPC |
| Data API | Schema exposure | Remove sensitive schemas from `Exposed schemas` |
| Database | RLS | `enable row level security` on every exposed table |
| Database | CLS | `revoke select (col)` for sensitive columns |
| Database | Roles | Audit `anon`/`authenticated` grants; never expose `service_role` |
| Database | Secrets | Store keys/tokens in **Vault**, not columns |
| Auth | Hardening | Password security, rate limits, CAPTCHA, JWT config |
| Audit | Logging | Enable Platform + Auth Audit Logs (Team/Enterprise) |
| Supply chain | Lockfile | Commit lockfile; `npm ci` / `--frozen-lockfile` in CI |
| Supply chain | Quarantine | `min-release-age` ≥ 7 days |
| Supply chain | Provenance | `npm audit signatures` (verify `@supabase/*` → `supabase` org) |
| Supply chain | Scripts | `--ignore-scripts` / default-deny postinstall |
| Compliance | HIPAA | Sign BAA + enable HIPAA add-on; heed Security Advisor |

## Worked Example

**Goal: lock down a public schema, enforce RLS, rotate keys after a suspected leak.**

```sql
-- A. Audit exposure, then enforce RLS on all public tables
do $$ declare t record; begin
  for t in select tablename from pg_tables where schemaname = 'public'
  loop
    execute format('alter table public.%I enable row level security;', t.tablename);
  end loop;
end $$;

-- B. Strip blanket grants; re-grant only what the app needs
revoke all on all tables in schema public from anon, authenticated;
grant select on public.posts to anon;                 -- public read
grant select, insert, update, delete on public.posts to authenticated;

-- C. Owner policy + column masking
create policy "owner_write" on public.posts for all to authenticated
  using ( (select auth.uid()) = author_id )
  with check ( (select auth.uid()) = author_id );
revoke select (author_email) on public.posts from anon;
```

```bash
# D. Rotate the leaked service_role / anon keys (Dashboard → API → "Generate new keys")
#    then treat install host as compromised:
npm cache clean --force
rm -rf node_modules && npm ci          # reinstall from pinned lockfile
npm audit signatures                   # confirm provenance of @supabase/*
```

Verify: `select * from public.posts` as `anon` returns only granted columns/rows; `service_role` requests from the old key now fail.

## Key Takeaways

- The Data API exposes tables to the internet — **RLS + least-privilege grants are mandatory, fail closed**.
- Use **CLS** to mask sensitive columns and **non-exposed schemas** to remove tables from the API entirely.
- **`service_role` bypasses RLS** — server-only; rotate immediately on suspected leak.
- Compliance (SOC 2/HIPAA) certifies only Supabase's side of the **compliance boundary**; HIPAA needs a **BAA + add-on** and is hosted-only.
- Harden at three layers: **platform** (MFA/SSO/SSL/network), **product** (RLS/CLS/Vault/Auth), **supply chain** (lockfile/age-gate/provenance).

## Connects To

- Ch on Auth (JWTs, password security, RBAC/custom claims, MFA)
- Ch on Database (RLS, CLS, Postgres roles, Vault)
- Ch on Data API / PostgREST (schema exposure, securing the API)
- Ch on Deployment (going-into-prod checklist, shared responsibility model)
- Ch on Storage & Realtime (ownership, access control, authorization)
