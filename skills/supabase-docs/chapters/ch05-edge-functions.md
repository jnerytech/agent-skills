# Chapter 5: Edge Functions

## Core Idea
Supabase Edge Functions are server-side **TypeScript** functions running on the **Deno**-compatible Supabase Edge Runtime, distributed globally so each invocation executes on the node closest to the user (low latency). A function is a `.ts` file that exports a `fetch` handler (or uses `Deno.serve`). The request path is: client → edge gateway/relay (routes traffic, validates JWTs via `verify_jwt`, applies rate limits) → regional Edge Runtime isolate executes your code → response returns through the gateway, emitting logs/metrics. Use them for low-latency HTTP endpoints, webhook receivers (Stripe, GitHub), OG image generation, AI inference/LLM orchestration, transactional email, and bots. Design for short-lived, idempotent work; offload long jobs to background tasks. Functions are portable (run locally or on any Deno-compatible host, including self-hosted).

## Frameworks Introduced
- **`withSupabase` (`@supabase/server`)**: wraps a `fetch` handler, verifies caller credentials against a declared `auth` mode, handles CORS/preflight, and injects a pre-configured `ctx` (clients + claims).
- **`createSupabaseContext`**: lower-level alternative returning `{ data, error }` so you control the 401/error response shape.
- **Supabase CLI**: scaffolds (`functions new`), serves locally with hot reload (`functions serve`), deploys globally (`functions deploy`), and manages secrets (`secrets set/list`).
- **Web routing frameworks (Hono / Oak / Express)**: build multi-route REST APIs inside one "fat function" to minimize cold starts; Hono ships a `@supabase/server@^1/adapters/hono` adapter for per-route auth.
- **`EdgeRuntime.waitUntil(promise)`**: marks a promise as a background task so the isolate stays alive past the response.
- **`pg_cron` + `pg_net`**: Postgres-side scheduler that invokes functions over HTTP on a cron schedule.

## Key Concepts
- **Cold start**: each function must boot before serving; rarely-hit functions cold-start often — combine actions into one "fat function" to keep an instance warm.
- **Isolate**: per-invocation execution unit; `SB_EXECUTION_ID` is its UUID.
- **`verify_jwt`**: platform-level JWT check (default `true`) applied at the gateway before your handler; set `false` per-function in `config.toml` or via `--no-verify-jwt`.
- **Auth modes** (`withSupabase`): `'user'` (user JWT on `Authorization`), `'secret'` / `'publishable'` (key on `apikey`), `'none'` (no check — for signed webhooks). Arrays try modes in order; `ctx.authMode` reports the match. Named keys: `'secret:automations'`.
- **`ctx` object**: `supabase` (RLS-scoped to user), `supabaseAdmin` (bypasses RLS / secret key), `userClaims`, `jwtClaims`, `authMode`.
- **Default secrets**: `SUPABASE_URL`, `SUPABASE_DB_URL`, `SUPABASE_PUBLISHABLE_KEYS` (JSON dict), `SUPABASE_SECRET_KEYS` (JSON dict, bypasses RLS, never in browser), `SUPABASE_JWKS`. Hosted-only: `SB_REGION`, `SB_EXECUTION_ID`, `DENO_DEPLOYMENT_ID`.
- **Background tasks**: continue after response via `waitUntil`; locally require `[edge_runtime] policy = "per_worker"` or they get killed when the request ends.
- **Regional invocation**: defaults to nearest region; force with `x-region` header or `FunctionRegion` enum (or `forceFunctionRegion` query param when headers can't be set). Verify via `x-sb-edge-region` response header. Explicit regions are NOT re-routed during outages.
- **WebSockets**: `Deno.upgradeWebSocket(req)`; browser clients can't send headers, so `withSupabase` can't authenticate them — pass JWT via query param or `Sec-WebSocket-Protocol` and verify manually; deploy with `--no-verify-jwt`.

## Mental Models
- **"Fat functions, not microfunctions"**: fewer/larger functions = fewer cold starts; route internally with Hono/Oak/Express or the URL Pattern API.
- **Gateway-then-handler security**: `verify_jwt` is the outer gate; `withSupabase` auth modes are the inner gate. Webhooks bypass both and self-authenticate via signature.
- **Edge Postgres is remote**: treat the DB as a pooled remote service; use serverless-friendly drivers/pools, and consider regional invocation for write-heavy/multi-round-trip work.

## Anti-patterns
- Using `auth: 'none'` (or `verify_jwt = false`) on endpoints touching sensitive data without verifying the caller another way.
- `console.log(JSON.stringify(req.headers))` — prints `{}`; Headers aren't enumerable. Use `Object.fromEntries(req.headers)`.
- Long-running blocking work in the handler instead of `EdgeRuntime.waitUntil`; or expecting background tasks/WebSockets to survive locally without `policy = "per_worker"`.
- A global `deno.json` / `import_map.json` / `.npmrc` for deployment — each function should own its config for isolation.
- Committing `.env` files; serving HTML (rewritten to `text/plain` without a custom domain).

## Code Examples
```ts
import { withSupabase } from 'npm:@supabase/server'

export default {
  fetch: withSupabase({ auth: 'user' }, async (_req, ctx) => {
    const { supabase, supabaseAdmin, userClaims, jwtClaims, authMode } = ctx
    // supabase      — RLS-scoped to the authenticated user
    // supabaseAdmin — bypasses RLS (service role)
    return Response.json({ email: ctx.userClaims?.email })
  }),
}
```
- **What it demonstrates**: the canonical `withSupabase` + `Deno`-runtime handler — declares an auth mode, gets a ready `ctx` with RLS-scoped and admin clients plus JWT claims, and handles CORS/preflight automatically.

## Reference Tables

CLI commands:
| Command | Purpose |
| --- | --- |
| `supabase init` | Create project (`supabase/config.toml`) |
| `supabase functions new hello-world` | Scaffold `functions/hello-world/index.ts` |
| `supabase start` | Boot full local stack (needs Docker) |
| `supabase functions serve [name]` | Serve locally, hot reload, `:54321/functions/v1/[name]` |
| `supabase functions serve --env-file .env.local` | Load custom env file |
| `supabase functions serve name --no-verify-jwt` | Skip JWT check locally |
| `supabase login` / `supabase link --project-ref <id>` | Auth + connect to remote |
| `supabase functions deploy [name]` | Deploy one / all functions |
| `supabase functions deploy name --use-api` | API-based deploy (no Docker; no static files) |
| `supabase secrets set --env-file .env` / `set KEY=val` / `list` | Manage production secrets |

Limits (hosted):
| Limit | Value |
| --- | --- |
| Memory | 256 MB |
| Wall-clock duration | 150s free / 400s paid |
| CPU time / request | 2s |
| Request idle timeout | 150s → 504 |
| Function size (bundled) | 20 MB |
| Functions/project | 100 free / 500 Pro / 1000 Team |
| Log message | 10,000 chars; 100 events / 10s |
| Recursive calls | ~5000 req/min |
| Secrets | 100/project, 256-char name, 48 KiB; no `SUPABASE_` prefix |
| Blocked | ports 25/587, Web Worker/`vm` API, multithreaded libs (sharp/libvips) |

## Worked Example
Write, configure a secret, deploy, and invoke a Stripe webhook receiver.
```bash
supabase functions new stripe-webhook
```
```ts
// supabase/functions/stripe-webhook/index.ts
import { withSupabase } from 'npm:@supabase/server'
import Stripe from 'npm:stripe'
const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY')!)

export default {
  fetch: withSupabase({ auth: 'none' }, async (req, ctx) => {
    const sig = req.headers.get('stripe-signature') ?? ''
    const body = await req.text()
    try {
      stripe.webhooks.constructEvent(body, sig, Deno.env.get('STRIPE_WEBHOOK_SECRET')!)
    } catch { return new Response('bad signature', { status: 400 }) }
    return Response.json({ received: true })  // ctx.supabaseAdmin for DB work
  }),
}
```
```toml
# supabase/config.toml — webhook is public; provider signs the body
[functions.stripe-webhook]
verify_jwt = false
```
```bash
supabase secrets set STRIPE_SECRET_KEY=sk_live_... STRIPE_WEBHOOK_SECRET=whsec_...
supabase functions deploy stripe-webhook   # secrets are live immediately, no redeploy
curl --request POST 'https://<project_id>.supabase.co/functions/v1/stripe-webhook' \
  --header 'Content-Type: application/json' --data '{}'
```

## Key Takeaways
- One handler exporting `fetch`, Deno/TypeScript runtime, globally distributed; CLI is the primary workflow (`new` → `serve` → `link` → `deploy`).
- `withSupabase` is the modern path: declare an `auth` mode, get RLS + admin clients and claims, free CORS handling; `verify_jwt` is the separate gateway gate.
- Combine routes into fat functions to cut cold starts; secrets via `Deno.env.get`, set with `supabase secrets set` (effective immediately).
- `EdgeRuntime.waitUntil` for background work; WebSockets need manual JWT verification + `--no-verify-jwt`; `per_worker` policy to test both locally.
- Schedule via `pg_cron` + `pg_net`; pin region with `x-region`/`FunctionRegion` for DB-heavy work; mind 256 MB / 2s CPU / 400s wall-clock limits.

## Connects To
- Auth & RLS (Chapter on Auth) — JWT verification, publishable/secret keys, `ctx.supabase` scoping.
- Database (Postgres) — `connect-to-postgres`, pooling, `pg_cron`/`pg_net` scheduling, read replicas via `SB_REGION`.
- CLI & local development — `config.toml`, `supabase start`, import maps/`deno.json`.
- Self-hosting — Edge Runtime is open source and runs on any Deno-compatible host.
