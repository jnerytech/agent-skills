# Chapter 4: Storage

## Core Idea

Supabase Storage is an S3-compatible object store that stores file metadata as rows in the `storage.objects` Postgres table, so the same Row Level Security (RLS) engine that guards your database guards your files. You organize files into **buckets** (top-level containers, "super folders") and optional folders. Buckets are **private by default**: with no RLS policy, no operation is allowed. Assets are cached on a global CDN (285+ cities). Three bucket types exist: **Files** (general media, CDN + image transforms), **Analytics** (Apache Iceberg tables, SQL-queryable), and **Vector** (embeddings + similarity search, alpha).

## Frameworks Introduced

- **Bucket access model**: choose public vs private per bucket; access model determines caching and auth behavior, not just visibility.
- **RLS-on-objects**: every Storage operation maps to a SQL privilege (`INSERT`=upload, `SELECT`=download/list, `UPDATE`=overwrite, `DELETE`=delete) on `storage.objects`.
- **Three upload methods**: Standard (`multipart/form-data`, <6MB ideal), Resumable (TUS protocol, large/unstable), S3 (`PutObject` single or multipart parallel).
- **Image transformation pipeline**: on-the-fly resize/optimize via `/render/image/...` URLs, backed by imgproxy; auto-WebP negotiation.
- **Smart CDN**: edge-synced metadata enables automatic cache revalidation on update/delete (~60s propagation).

## Key Concepts

- **Private bucket** — all ops (including download) go through RLS. Download only via SDK `download()` with the user JWT, or via a short-lived `createSignedUrl`. Lower cache hit rate (per-user permission checks).
- **Public bucket** — read/serve bypass access control (anyone with the URL reads it); writes/deletes/moves still enforce RLS. Higher CDN hit rate.
- **`storage.objects`** — the table RLS policies attach to; rows carry `bucket_id`, `name` (path), `owner_id`, `user_metadata`.
- **Helper functions** — `storage.filename(name)`, `storage.foldername(name)` (returns path array), `storage.extension(name)`, plus operation-aware `storage.allow_only_operation('object.list')` and `storage.allow_any_operation(ARRAY[...])` for distinguishing list vs authenticated-read under one `SELECT` privilege.
- **Upload restrictions** — `allowedMimeTypes` and `fileSizeLimit` set at bucket creation; rejected if violated.
- **Signed URL** — time-limited URL (`createSignedUrl(path, expiresIn)`); signed with a dedicated internal key, so unaffected by Auth JWT key rotation. Cannot be revoked except by deleting the object or contacting support.
- **Service key** — in `Authorization` header bypasses all RLS (server-only).
- **Direct storage hostname** — `project-id.storage.supabase.co` (vs `.supabase.co`) for faster large-file uploads.
- **`upsert` / `x-upsert`** — overwrite-on-conflict; without it a duplicate path returns `400 Asset Already Exists`.
- **`cf-cache-status`** — `HIT` (served from edge) vs `MISS` (fetched from origin).

## Mental Models

- **A bucket is an RLS boundary, not a folder.** Group files by who-can-do-what, then write policies once per bucket.
- **The URL is the capability for public buckets.** Public read = anyone with the link reads; treat the path as the only secret.
- **CDN cache keys are per-token for signed URLs.** Re-use one signed URL to get cache hits; generating a fresh URL per request never warms the cache.
- **Token expiry ≠ cache eviction.** A cached response keeps serving until the CDN TTL expires even after the token expires; delete the object to truly cut access.

## Anti-patterns

- **Overwriting files in place** — CDN propagation causes stale content; upload to a new path instead (or use a `cacheNonce` query string to bust cache).
- **New signed URL per request** — defeats CDN caching, hammers origin. Re-use, or use a public bucket if there's no per-user restriction.
- **Relying on token expiry to revoke access** — cached edge response persists; delete the object.
- **Standard upload for files > 6MB** — works up to 5GB but unreliable; use TUS resumable or S3 multipart.
- **Forgetting `allow_any_operation()` on a public-read SELECT policy** — without it users can list bucket contents, not just read.

## Code Examples

```js
import { createClient } from '@supabase/supabase-js'
const supabase = createClient('your_project_url', 'your_supabase_api_key')

// Standard upload (multipart/form-data, ideal < 6MB)
const { data, error } = await supabase.storage
  .from('avatars')
  .upload('public/avatar1.png', file, { upsert: false })

// Signed URL for a private bucket (expires in 1 hour), with on-the-fly transform
const { data: signed } = await supabase.storage
  .from('bucket')
  .createSignedUrl('image.jpg', 3600, { transform: { width: 200, height: 200 } })

// Public URL with transform (Pro+ feature)
supabase.storage.from('bucket').getPublicUrl('image.jpg', {
  transform: { width: 500, height: 600 },
})
```

- **What it demonstrates**: standard SDK upload with overwrite control; generating a time-limited signed URL for private assets; embedding image-resize params into both signed and public URLs. Transform options are baked into the signed token and cannot be changed after signing.

## Reference Tables

**Upload methods compared**

| Method | Protocol | Best for | Max size (paid) | Overwrite | Resumable |
| ------ | -------- | -------- | --------------- | --------- | --------- |
| Standard | `multipart/form-data` (`upload()`) | small files < 6MB | 5 GB | `upsert`/`x-upsert` | no |
| Resumable | TUS (`tus-js-client`, Uppy) | large/unstable, progress events | (global limit) | `x-upsert` | yes (24h upload URL) |
| S3 PutObject | S3 single request | smaller server-side files | 500 GB | — | no |
| S3 Multipart | S3 parallel parts | large server-side, max speed | 500 GB | — | retry per part (24h auto-abort) |

**Bucket types**

| Type | Use case | Key feature |
| ---- | -------- | ----------- |
| Files | media, docs, user content | CDN, image transforms, RLS, direct URLs |
| Analytics | data lakes, logs, ETL | Apache Iceberg, queryable via Postgres FDW |
| Vector (alpha) | embeddings, RAG, semantic search | HNSW/Flat index, cosine/euclidean/L2, `<===>` operator, ≤500 vectors/request |

**File size limits**: Free 50 MB / Pro & Team 500 GB / Enterprise custom (global limit; per-bucket limit must be ≤ global). Transform limits: width/height 1–2500, ≤25MB, ≤50MP.

## Worked Example

Create a private `avatars` bucket, restrict it, let users write only into their own folder, then upload and share.

```sql
-- 1. Create bucket via SQL (private by default)
insert into storage.buckets (id, name, public)
values ('avatars', 'avatars', false);

-- 2. RLS: authenticated users upload only into a folder named after their user id
create policy "Allow authenticated uploads"
on storage.objects
for insert
to authenticated
with check (
  bucket_id = 'avatars' and
  (storage.foldername(name))[1] = (select auth.jwt()->>'sub')
);

-- 3. RLS: users read only files they own
create policy "Individual user Access"
on storage.objects for select
to authenticated
using ( (select auth.jwt()->>'sub') = owner_id );
```

```js
// 4. Upload into the user's own folder
const userId = (await supabase.auth.getUser()).data.user.id
await supabase.storage.from('avatars').upload(`${userId}/me.png`, file)

// 5. Share a 1-hour link (private bucket)
const { data } = await supabase.storage
  .from('avatars')
  .createSignedUrl(`${userId}/me.png`, 3600)
console.log(data.signedUrl)
```

Alternatively restrict at bucket creation with the JS SDK: `createBucket('avatars', { public: false, allowedMimeTypes: ['image/*'], fileSizeLimit: '1MB' })`.

## Key Takeaways

- Buckets are private by default; **no RLS policy = no access**. Map operations to SQL privileges and write policies per bucket.
- Use `storage.foldername(name)[1] = auth.jwt()->>'sub'` to scope users to their own folders — the canonical per-user pattern.
- Pick uploads by size/context: Standard < 6MB, TUS resumable for large/flaky clients, S3 multipart for fast server-side. Use the `.storage.supabase.co` direct host for large files.
- Public buckets cache best; private buckets check perms per user. For signed URLs, **re-use the URL** to get cache hits and **delete the object** (not expire the token) to revoke.
- Image transforms (Pro+) resize/optimize on the fly and auto-serve WebP; embed `transform` in `getPublicUrl`/`createSignedUrl`/`download`.

## Connects To

- **Database / RLS** — Storage policies are ordinary Postgres RLS on `storage.objects`; same `auth.uid()`/`auth.jwt()` helpers.
- **Auth** — user JWT drives private-bucket access; service key bypasses RLS; S3 session-token auth scopes S3 ops to a user via RLS.
- **Edge Functions** — typical place to sign URLs server-side for private assets.
- **Self-hosting** — image transforms use imgproxy (`ENABLE_IMAGE_TRANSFORMATION`, `IMGPROXY_URL`), bundled in the official Docker Compose; S3 access keys / `STORAGE_TENANT_ID`.
- **AI / Vector** — Vector buckets parallel pgvector for large-scale embedding storage and RAG retrieval.
