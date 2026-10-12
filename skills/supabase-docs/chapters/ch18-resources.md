# Chapter 18: Resources & Migration Guides

## Core Idea

Supabase is "Postgres + a managed platform." Its resources hub is therefore two
things at once: a **terminology layer** (a glossary that pins down the auth and
Postgres vocabulary the rest of the docs assume) and a **migration layer** (guides
for moving onto Supabase from competing databases and BaaS platforms). Because
Supabase is plain Postgres under the hood, almost any migration reduces to a
standard `pg_dump`/`pg_restore` job — the interesting work is mapping *non-Postgres*
sources (Firebase, Auth0, MySQL, MSSQL) into the relational + RLS model.

> Reference/index chapter — intentionally thin. It indexes other guides rather
> than teaching new mechanics. Auth/RLS depth lives in the Auth chapter; Postgres
> depth in the Database chapter.

## Frameworks Introduced

- **Two-layer resource model**: Glossary (shared vocabulary) + Migration guides
  (onboarding paths). Read the glossary first so other chapters parse cleanly.
- **Postgres-first migration**: any Postgres source (RDS, Heroku, Render, raw PG)
  migrates via dump/restore; non-Postgres sources need a schema + data *mapping*.

## Key Concepts

- **Tokens & sessions**: access token (short-lived JWT, ≤1h), refresh token
  (long-lived, single-use exchange), session = access+refresh pair bound to a browser.
- **JWT**: signed (HMAC-SHA256 by Supabase) string carrying identity/authz claims;
  RLS policies read these claims. The **JWT signing secret** must stay private.
- **authn vs authz**: authentication = *who you are*; authorization = *what you may do*.
- **RLS**: Postgres row-level policies that filter rows per request using JWT claims.
- **Federated identity**: identity provider, OAuth (social login), OIDC (modern SSO),
  SAML (legacy XML SSO), SSO, PKCE (secure code exchange for public clients).
- **MFA/OTP/TOTP**: extra factors; OTP = one-time code, TOTP = time-based code from
  an authenticator app; defends against **replay attacks** via **nonces**.

## Mental Models

- **"It's just Postgres"**: when the source is already Postgres, the migration is
  a database operation, not a rewrite. When it isn't, you're modeling documents/users
  into tables and policies.
- **Glossary as a contract**: each term has one canonical meaning; the docs lean on
  it instead of re-explaining. Treat unfamiliar terms as a lookup, not a guess.

## Anti-patterns

- Hand-rolling auth migration logic when an official Auth0/Firebase-Auth guide exists.
- Exposing or committing the JWT signing secret — anyone with it forges valid JWTs.
- Flattening a Firestore tree into one wide table without revisiting relationships;
  Firestore collections rarely map 1:1 to good relational schemas.

## Reference Tables

### Migration guides (migrating-to-supabase/…)

| Source | Type | Path | Nature of work |
|---|---|---|---|
| Auth0 | Auth users | `/auth0` | Export users → Supabase Auth |
| Firebase Auth | Auth users | `/firebase-auth` | Export users → Supabase Auth |
| Firestore Data | NoSQL docs | `/firestore-data` | Collection → one Postgres table |
| Firebase Storage | Object store | `/firebase-storage` | Files → Supabase Storage |
| Heroku | Postgres | `/heroku` | dump/restore |
| Render | Postgres | `/render` | dump/restore |
| Amazon RDS | Postgres | `/amazon-rds` | dump/restore |
| Postgres | Postgres | `/postgres` | dump/restore |
| MySQL | Relational | `/mysql` | Schema + type mapping |
| MSSQL | Relational | `/mssql` | Schema + type mapping |

### Resource index

| Resource | Path | Use |
|---|---|---|
| Examples | `/guides/resources/examples` | Official GitHub + community samples |
| Glossary | `/guides/resources/glossary` | Term/acronym definitions |
| Managing indexes | `/guides/database/postgres/indexes` | Query performance |
| Cascade deletes | `/guides/database/postgres/cascade-deletes` | FK delete behavior |
| Drop all tables | `/guides/database/postgres/dropping-all-tables-in-schema` | Reset a schema |
| First row per group | `/guides/database/postgres/first-row-in-group` | Group-wise top-N |
| Postgres version | `/guides/database/postgres/which-version-of-postgres` | Detect PG version |

### Glossary quick map

| Term | One-liner |
|---|---|
| Access token | Short-lived JWT authorizing resource access |
| Refresh token | Long-lived, single-use token to mint new tokens |
| Session | Access+refresh pair bound to a browser |
| RLS | Postgres policies filtering rows via JWT claims |
| OAuth / OIDC / SAML | Social login / modern SSO / legacy XML SSO |
| PKCE | Secure code-exchange for public/mobile clients |
| MFA · OTP · TOTP | Multi-factor · one-time code · time-based code |
| Nonce | Single-use string defeating replay attacks |

## Worked Example — Firebase → Supabase mapping

| Firebase concept | Supabase equivalent | Notes |
|---|---|---|
| Firebase Auth user | `auth.users` row | Use the Firebase-Auth migration guide; preserve UIDs |
| ID token | Supabase JWT | Both JWTs; Supabase signs with HMAC-SHA256 |
| Security Rules | RLS policies | Rules → SQL policies on `auth.uid()` / JWT claims |
| Firestore collection | Postgres table | One collection → one table (Firestore-Data guide) |
| Firestore document | Table row (+ `jsonb` for nested) | Denormalized fields may become `jsonb` |
| Subcollection | Child table + FK | Model relationships explicitly |
| Cloud Storage bucket | Supabase Storage bucket | File copy via Firebase-Storage guide |
| Cloud Functions | Edge Functions / DB functions | Logic moves to Deno or Postgres functions |

Migration order: provision project → migrate auth users → translate Security Rules
to RLS → move data (collections → tables) → move storage objects → port functions.

## Key Takeaways

- Read the glossary first; the rest of the docs assume its definitions.
- Postgres sources (RDS/Heroku/Render/PG) = dump/restore; NoSQL/auth sources = mapping.
- RLS + JWT claims are the backbone of Supabase authorization — keep the signing secret secret.
- Prefer the official per-platform migration guide over a bespoke script.

## Connects To

- **Auth chapter** — JWTs, sessions, OAuth/SAML/MFA mechanics in depth.
- **Database chapter** — indexes, cascade deletes, schema management for migrated data.
- **Storage chapter** — buckets/object handling for Firebase Storage migration.
- **Edge Functions chapter** — destination for ported Cloud Functions.
