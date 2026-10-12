# Chapter 1: Getting Started

## Core Idea
Supabase is an open-source Firebase alternative built on Postgres: a project is a real Postgres database surrounded by composable services (Auth, auto-APIs, Realtime, Storage, Edge Functions) that each work in isolation yet integrate. Getting started means create a project, connect a client library with a URL + API key, and query.

## Frameworks Introduced
- **Framework Quickstarts (StepHike pattern)**: Every quickstart follows the same shape — (1) create project + run SQL to make/seed an `instruments` table, (2) scaffold the app, (3) install/configure `supabase-js` (or platform SDK), (4) set `URL` + publishable key env vars, (5) query `supabase.from("instruments").select()`, (6) run dev server.
  - When to use: starting any new app on a supported framework (React, Next.js, Nuxt, SvelteKit, SolidJS, Vue, Hono, RedwoodJS, TanStack Start, Refine, Flutter, iOS SwiftUI, Kotlin, Laravel, Rails, Flask, Astro, Expo).
  - How: see Worked Example below.
- **Client libraries (`supabase-js` et al.)**: `createClient(url, key)` gives a typed interface to DB/Auth/Storage/Realtime. Official: JavaScript, Flutter (`supabase_flutter`), Swift; Python in beta; community libs otherwise.
  - When to use: any time you talk to Supabase from app code instead of raw REST/GraphQL.
- **Server-Side Auth helpers**: cookie-based auth clients for Next.js / SvelteKit / Remix; the Next.js `with-supabase` template wires this up automatically.
  - When to use: SSR frameworks where auth state must survive on the server.
- **Supabase CLI**: develop locally, manage migrations, deploy to the platform; works with self-hosted.
  - When to use: local dev, migrations, CI.

## Key Concepts
- **Postgres-as-core**: Supabase does not abstract Postgres; you get full privileges and direct access.
- **PostgREST**: standalone server that auto-generates a RESTful API from your schema (no code).
- **pg_graphql**: Postgres extension giving an auto-generated GraphQL API.
- **GoTrue (Auth)**: JWT-based user management; integrates with Postgres RLS and the API servers.
- **Realtime**: WebSocket engine for Postgres Changes, Broadcast, and Presence.
- **Storage API**: S3-compatible object storage with metadata in Postgres; CDN + image transforms.
- **Edge Functions (Deno)**: globally distributed TypeScript functions for custom logic; support NPM.
- **Kong**: API gateway (NGINX-based) fronting all services; Supavisor is the connection pooler.
- **Row Level Security (RLS)**: Postgres policies decide which rows each user/role can access — the real data guard behind public keys.
- **API key vs Auth**: API key answers *what* component is connecting; Auth answers *who* the user is.

## Mental Models
- **Use a publishable key (`sb_publishable_...`) when** code is public (browser, mobile, CLI, source) — it maps to the `anon`/`authenticated` Postgres role and relies on RLS for safety.
- **Use a secret key (`sb_secret_...`) when** code runs on a backend you control — it uses `service_role`, has `BYPASSRLS`, and returns HTTP 401 if used in a browser.
- **Choose your comfort level**: treat Postgres as a simple table-store or use its full power — both are valid.
- **Pick by service availability when** comparing cloud vs self-hosted: most features are GA on both; PITR/CDN need external tools, and Custom Domains/Network Restrictions/Branching/Read Replicas/Management API are platform-only.

## Anti-patterns
- **Putting a secret/`service_role` key in client code, URLs, logs, or source control**: full data access bypassing RLS; leak = full compromise.
- **Sending a publishable/secret key in `Authorization: Bearer`**: they aren't JWTs and get rejected — use the `apikey` header (e.g. `pg_net`/Database Webhooks).
- **Shipping tables without RLS enabled**: publishable keys offer no protection on their own; RLS is the guard.
- **Relying on Edge Function JWT verification with new keys**: Edge Functions verify JWTs only via legacy `anon`/`service_role`; with publishable/secret keys use `--no-verify-jwt` and check `apikey` yourself.

## Code Examples
```ts name=app/instruments/page.tsx
import { createClient } from "@/lib/supabase/server";
import { Suspense } from "react";

async function InstrumentsData() {
  const supabase = await createClient();
  const { data: instruments } = await supabase.from("instruments").select();
  return <pre>{JSON.stringify(instruments, null, 2)}</pre>;
}

export default function Instruments() {
  return (
    <Suspense fallback={<div>Loading instruments...</div>}>
      <InstrumentsData />
    </Suspense>
  );
}
```
- **What it demonstrates**: the canonical query — get a client, then `.from(table).select()` returns `{ data, error }`; works the same in React (`createClient(import.meta.env.VITE_SUPABASE_URL, import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY)`) and Flutter (`Supabase.instance.client`).

## Reference Tables

API keys:
| Type | Format | Privileges | Use |
|------|--------|-----------|-----|
| Publishable | `sb_publishable_...` | Low | Safe to expose: web/mobile/CLI/source |
| Secret | `sb_secret_...` | Elevated | Backend only; bypasses RLS via `service_role` |
| `anon` | JWT (long-lived) | Low | Legacy publishable |
| `service_role` | JWT (long-lived) | Elevated | Legacy secret |

Legacy → new migration mapping:
| Legacy | Replace with | Used by |
|--------|-------------|---------|
| `anon` | Publishable key | Browsers, mobile/desktop, CLIs, public source |
| `service_role` | Secret key | Servers, Edge Functions, workers, backend |

Env var conventions: Next.js `NEXT_PUBLIC_SUPABASE_URL` / `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`; Vite `VITE_SUPABASE_URL` / `VITE_SUPABASE_PUBLISHABLE_KEY`.

## Worked Example
Next.js quickstart end-to-end:
1. Create a Supabase project; in the SQL editor create + seed an `instruments` table.
2. `npx create-next-app -e with-supabase` (gives cookie-based Auth, TypeScript, Tailwind).
3. Rename `.env.example` → `.env.local`, fill `NEXT_PUBLIC_SUPABASE_URL=...` and `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=...` from **Settings > API Keys** (or the **Connect** dialog).
4. Add `app/instruments/page.tsx` (code above).
5. `npm run dev`, visit `http://localhost:3000/instruments`.

React variant differs only at scaffold/install: `npm create vite@latest my-app -- --template react` then `cd my-app && npm install @supabase/supabase-js`, view at `:5173`.

## Key Takeaways
1. A Supabase project = Postgres + bundled services behind Kong; you never lose direct Postgres access.
2. Connecting is always `createClient(url, key)` then `.from(...).select()` returning `{ data, error }`.
3. Two key tiers: publishable (public, RLS-guarded) vs secret (backend, RLS-bypassing) — never mix them up.
4. New `sb_publishable_`/`sb_secret_` keys replace legacy `anon`/`service_role`; both work simultaneously so migrate clients one at a time.
5. RLS, not the API key, is what actually protects data accessed with a publishable key.
6. Quickstarts across ~20 frameworks share one shape — pick by framework, the Supabase steps are identical.
7. Most features are GA and available self-hosted; design principles: isolated, integrated, extensible, portable, long-game, developer-first.

## Connects To
- **Ch (Auth)**: API keys are the "what"; Auth/RLS is the "who" layered on top.
- **Ch (Database)**: PostgREST/pg_graphql auto-APIs and RLS policies queried by the client.
- **Ch (Self-Hosting)**: same services (Kong, GoTrue, PostgREST, Realtime, Storage, Supavisor) run via Docker, validating the portability principle.
