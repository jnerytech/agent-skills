# Chapter 9: Self-Hosted Functions

## Core Idea
Edge Functions work out of the box: drop a `index.ts` in `volumes/functions/<name>/`, restart the `functions` service, invoke at `/functions/v1/<name>`. The one concept to internalize is internal (`SUPABASE_URL=http://kong:8000`) vs external (`SUPABASE_PUBLIC_URL`) URLs.

## Frameworks Introduced
- **Function lifecycle**: create dir + `index.ts` (Deno) → restart functions → `curl /functions/v1/<name>`.
  - How: `mkdir -p volumes/functions/my-function`, write `Deno.serve(...)`, `docker compose restart functions --no-deps`.
- **Env var injection — two ways**:
  - When to use env file: many vars/secrets → `.env.functions` + `env_file:` (loads first, `environment:` overrides).
  - When to use inline: 1–2 vars → directly under `environment:` referencing main `.env`.
  - All container env vars are forwarded to workers by `main/index.ts`; read with `Deno.env.get()`.
- **Internal vs external URL rule**:
  - `SUPABASE_URL` (`http://kong:8000`) → server-side calls to other services (use in the JS client inside functions).
  - `SUPABASE_PUBLIC_URL` → build URLs reachable by outside HTTP clients.

## Key Concepts
- **`recreate` vs `restart`**: code edits → `restart functions --no-deps`; env/config changes → `up -d --force-recreate --no-deps functions`.
- **`FUNCTIONS_VERIFY_JWT`**: toggles JWT verification; if true, pass `Authorization: Bearer <anon/service_role key>`.
- **Default limits**: 150 MB memory, 60 s timeout per invocation — set in `volumes/functions/main/index.ts` (`memoryLimitMb`, `workerTimeoutMs`).
- **Studio mount**: Studio mounts the same `volumes/functions` dir — functions appear under Edge Functions > Functions.

## Mental Models
- Inside a function, "talk to siblings via `kong:8000`, build outside-facing links via the public URL." Mixing them up is the classic bug.
- A code change not showing up = you didn't restart the functions service.

## Anti-patterns
- **Committing `.env.functions` with secrets**: add to `.gitignore`.
- **Expecting code changes without restart**: edits aren't hot-reloaded.
- **Using `SUPABASE_PUBLIC_URL` for internal calls** (or vice-versa): internal calls should hit `kong:8000`.
- **Calling `/functions/v1/` with no function name**: 400 "missing function name".

## Code Examples
```typescript
// volumes/functions/my-function/index.ts
Deno.serve(async (req: Request) => {
  const { name } = await req.json()
  return new Response(JSON.stringify({ message: `Hello, ${name}!` }),
    { headers: { 'Content-Type': 'application/json' } })
})
```
```sh
docker compose restart functions --no-deps
curl -X POST http://<your-domain>/functions/v1/my-function \
  -H 'Content-Type: application/json' -d '{"name":"World"}'   # -> {"message":"Hello, World!"}
```
- **What it demonstrates**: the create→restart→invoke loop.

## Reference Tables
Pre-configured function env vars:
| Variable | Value | Purpose |
|---|---|---|
| `SUPABASE_URL` | `http://kong:8000` | Internal gateway (use in-function) |
| `SUPABASE_PUBLIC_URL` | `http(s)://<your-domain>` | External base URL |
| `JWT_SECRET` | legacy symmetric key | HS256 |
| `SUPABASE_ANON_KEY` / `SUPABASE_SERVICE_ROLE_KEY` | keys | client / server role |
| `SUPABASE_DB_URL` | `postgresql://...` | DB connection |
| `SUPABASE_PUBLISHABLE_KEYS` / `SUPABASE_SECRET_KEYS` | `{"default":"sb_..."}` | new keys |

Deploy/copy: `scp -r ./my-function user@host:/path/.../volumes/functions/` then restart; platform functions via Dashboard Download or `supabase functions download <name> --project-ref <ref>`.

## Worked Example — querying the DB from a function (internal URL)
```typescript
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
Deno.serve(async () => {
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,                  // http://kong:8000 — internal
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  )
  const { data, error } = await supabase.from('todos').select('*')
  return new Response(JSON.stringify({ data, error }),
    { headers: { 'Content-Type': 'application/json' } })
})
```
Note it uses `SUPABASE_URL` (the internal Docker hostname) for the server-side call, with the service-role key for full access.

## Key Takeaways
1. Add a dir + `index.ts`, restart functions, invoke at `/functions/v1/<name>`.
2. `restart` for code, `--force-recreate` for env/config changes.
3. Internal calls → `SUPABASE_URL` (`kong:8000`); external links → `SUPABASE_PUBLIC_URL`.
4. Prefer `.env.functions` (gitignored) for multiple secrets.
5. Defaults: 150 MB / 60 s, editable in `main/index.ts`.
6. `FUNCTIONS_VERIFY_JWT` decides whether a Bearer key is required.

## Connects To
- **Ch 1**: functions are pre-wired in the base setup; `recreate functions` picks up new code.
- **Ch 2**: keys passed to functions (anon/service_role + new `sb_` keys).
- **Ch 3**: gateway bypasses auth on `/functions/v1/` (Edge Runtime self-verifies).
