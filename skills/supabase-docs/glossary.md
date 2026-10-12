# Glossary

Key terms across the Supabase docs. Format: **Term** — definition (chapter).

**aal (Authenticator Assurance Level)** — MFA strength claim in the JWT (aal1/aal2); RLS can require aal2 (Ch3).
**amr** — JWT array of authentication methods used in the session (Ch3).
**ANN index** — approximate nearest-neighbor vector index (HNSW/IVFFlat); trades recall for speed (Ch8).
**anon / authenticated / service_role** — the three Postgres request roles; service_role bypasses RLS (Ch2, Ch7).
**apikey header** — mandatory, non-JWT key on every Data API request; carries publishable/secret key (Ch1, Ch7).
**app_metadata vs user_metadata** — non-user-editable (safe for authz) vs user-editable (never trust for authz) JWT data (Ch3).
**auth.uid() / auth.jwt()** — policy helpers: requesting user's UUID (null if anon) and the full token (Ch2, Ch3).
**Branch (preview/persistent)** — ephemeral per-PR data-less instance vs long-lived staging branch via `[remotes]` (Ch12, Ch17).
**Broadcast / Presence / Postgres Changes** — Realtime's three channel extensions: ephemeral msgs / shared state / DB row events (Ch6).
**Bucket** — Storage container; the RLS + caching + upload-restriction boundary; private by default (Ch4).
**Channel / Topic** — a Realtime room keyed by a topic string, public or private (Ch6).
**CLS (column-level security)** — GRANT/REVOKE on columns to mask fields RLS can't (rows only) (Ch2, Ch15).
**Compliance boundary** — border between Supabase-managed and customer-managed security; certs cover only Supabase's side (Ch15).
**config.toml** — local/project config; supports `env(VAR)`; committed to git (Ch11, Ch13).
**Cold start / Fat function** — Edge Function boot cost; mitigated by combining actions into fewer large functions (Ch5).
**cron.schedule / pg_cron** — Postgres extension scheduling SQL/HTTP jobs by cron expression (Ch10).
**db diff / db push / db reset** — CLI: generate migration from schema diff / apply to remote / rebuild+reseed locally (Ch11, Ch12).
**Declarative schema** — desired end-state in `supabase/schemas/*.sql`; CLI generates migrations via migra (Ch11).
**Deployment DAG** — directed acyclic graph of branch deploy steps; failed parent skips children (Ch12).
**Edge Function / Edge Runtime** — globally distributed Deno/TypeScript function on the nearest node (Ch1, Ch5).
**Embedding / Dimensions** — float vector capturing meaning; `vector(N)` must match the model's output size (Ch8).
**Envoy** — optional self-host gateway override translating opaque `sb_` keys to internal creds (Ch13).
**GoTrue (Auth)** — JWT-based user-management service integrated with RLS (Ch1).
**Grant** — privilege on a DB object to a role; required before a table is exposed via the API (Ch7).
**Hybrid search (RRF)** — fuse full-text + vector results via Reciprocal Ranked Fusion `1/(k+rank)` (Ch8).
**HNSW vs IVFFlat** — robust build-anytime vector index vs cluster-based index needing representative data (Ch8).
**JWT / claims** — signed token carrying sub, role, exp, aal, amr; the bridge between Auth and RLS (Ch3, Ch18).
**JWT_KEYS / JWT_JWKS** — self-host signing set (Auth) vs verification set (PostgREST/Realtime/Storage) (Ch13).
**Kong** — NGINX-based API gateway fronting all services on `:8000` (Ch1, Ch13).
**Log source** — independent SQL-queryable log table (edge_logs, postgres_logs…); tables can't be joined (Ch16).
**Log Drain** — batched gzipped export of the log stream to HTTP/Datadog/Loki/Sentry/S3/OTLP (Ch16).
**Management API** — control plane at api.supabase.com/v1; auth via PAT or OAuth token (Ch17).
**Maturity Model** — practices scale by stage: Prototyping → Collaborating → Production → Enterprise (Ch12).
**message_record / VT** — pgmq message (msg_id, read_ct, vt, message jsonb) and its visibility timeout (Ch9).
**metadata (logs)** — nested JSON in log rows needing `cross join unnest()` per level (Ch16).
**Metrics endpoint** — Prometheus `/customer/v1/privileged/metrics`, Basic Auth with secret key (Ch16).
**Migration / schema_migrations** — versioned forward-only SQL DDL file; applied state tracked in `supabase_migrations.schema_migrations` (Ch11, Ch12).
**migra** — diff tool behind declarative schemas; can't track DML, RLS alters, views, comments, partitions (Ch11).
**Network Restrictions** — pre-auth IP CIDR allow-list on Postgres + pooler (not HTTPS APIs) (Ch14).
**OAuth / OIDC / SAML** — social login / modern SSO / enterprise XML SSO (Ch3, Ch18).
**Operator class** — vector index pairing: `vector_cosine_ops`, `vector_ip_ops`, `vector_l2_ops` (Ch8).
**pg_graphql** — Postgres extension exposing the schema as GraphQL at `/graphql/v1` (Ch1, Ch7).
**pg_net** — async HTTP from SQL (`net.http_post`); responses in `net._http_response` (Ch2, Ch10).
**pgmq / pgmq_public** — Postgres queue engine and its PostgREST-safe wrapper schema (Ch9).
**pgvector** — Postgres extension adding the `vector` type, distance operators, ANN indexes (Ch8).
**PITR** — Point-in-Time Recovery; WAL-G physical backup + WAL archiving, RPO ~2 min; replaces dailies (Ch14).
**PKCE** — SHA256 code-challenge flow securing public/mobile OAuth clients (Ch17, Ch18).
**Policy (using vs with check)** — RLS rule; `using` filters visible rows, `with check` gates new/modified rows (Ch3).
**PostgREST** — turns a Postgres schema into a REST API; one request → one SQL statement (Ch1, Ch7).
**Publishable / Secret key** — `sb_publishable_…` (low-priv, public-safe) vs `sb_secret_…` (backend-only, bypasses RLS) (Ch1).
**Read Replica** — read-only synced DB; SELECT/GET only; deployed per region (Ch14).
**Replica identity full** — table setting to receive old records on UPDATE/DELETE in Postgres Changes (Ch6).
**Resumable (TUS) / S3 upload** — large-file upload protocols; standard upload is for <6MB (Ch4).
**RLS (Row Level Security)** — per-row Postgres authorization; an implicit WHERE on every query; deny-all with no policy (Ch2, Ch3, Ch15).
**RPC** — Postgres function called via `.rpc()`; RLS doesn't apply, gated by EXECUTE grant (Ch7, Ch8).
**SECURITY DEFINER** — function running with owner privileges; lock with `set search_path = ''` + qualified names (Ch2).
**Security Advisor** — dashboard tool warning when changes weaken required (esp. HIPAA) controls (Ch15).
**Session (access + refresh token)** — short-lived access token + one-time refresh token with reuse detection (Ch3, Ch18).
**Shared Responsibility Model** — split of operational/security duties between customer and Supabase (Ch12, Ch15).
**Signed URL** — time-limited Storage URL via `createSignedUrl`; signed with a dedicated key, immune to Auth rotation (Ch4).
**Smart CDN** — edge-synced asset metadata that auto-revalidates cache on update/delete (Ch4).
**SOC 2 Type 2 / HIPAA + BAA** — annual audited trust criteria / health-data compliance needing a signed BAA + add-on (Ch15).
**Spend Cap** — Pro toggle hard-stopping overage on quota items (not compute/replicas/PITR) (Ch14).
**SSL Enforcement** — rejects non-SSL DB/pooler connections; verify-full recommended (Ch14).
**Supavisor** — multi-tenant Postgres connection pooler; transaction `6543`, session `5432` (Ch1, Ch2, Ch13).
**supabase_realtime publication** — publication tables must join to receive Postgres Changes (Ch6).
**tsvector + GIN** — generated full-text-search column precomputed and GIN-indexed for scale (Ch2).
**Visibility timeout (VT)** — seconds a read pgmq message stays invisible before redelivery (Ch9).
**Vault** — encrypted in-Postgres secrets storage; never store secrets in plaintext columns (Ch15).
**verify_jwt** — gateway-level Edge Function JWT check (default on); toggled per function (Ch5).
**W3C Trace Context** — `traceparent`/`tracestate` propagation linking client spans to server logs via `trace_id` (Ch16).
**Webhook (DB)** — AFTER trigger calling pg_net-backed `http_request` to notify external services on change (Ch2).
**withSupabase** — `@supabase/server` wrapper handling auth mode, CORS, and injecting clients/claims into `ctx` (Ch5).
