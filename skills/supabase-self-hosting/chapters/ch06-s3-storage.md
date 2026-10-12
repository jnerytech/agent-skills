# Chapter 6: Configure S3 Storage

## Core Idea
Storage has **two independent** S3 features: the S3 *protocol endpoint* (`/storage/v1/s3`, lets `rclone`/AWS CLI talk to Storage) and the S3 *backend* (where files actually live — local files by default, or AWS S3/RustFS/MinIO/R2). You can enable either, both, or neither.

## Frameworks Introduced
- **Protocol endpoint vs backend** — orthogonal choices:
  - When to use protocol endpoint: you want S3 tooling against Storage, regardless of backend. Set `REGION`, `S3_PROTOCOL_ACCESS_KEY_ID`, `S3_PROTOCOL_ACCESS_KEY_SECRET`.
  - When to use S3 backend: durability/scale/existing infra. Set `STORAGE_BACKEND=s3` + `GLOBAL_S3_*` + `AWS_*` + `REGION`.
- **Backend selection**:
  - AWS S3: omit `GLOBAL_S3_ENDPOINT`/`GLOBAL_S3_FORCE_PATH_STYLE` (auto-resolved, virtual-hosted style).
  - Non-AWS (RustFS/MinIO/R2): set `GLOBAL_S3_ENDPOINT`, usually `GLOBAL_S3_FORCE_PATH_STYLE: 'true'`.
  - RustFS override `docker-compose.rustfs.yml` (preferred); MinIO override `docker-compose.s3.yml` (legacy — Chainguard image, no longer OSS).
- **Session-token auth**: authenticate S3 ops with a user JWT to enforce RLS per user.

## Key Concepts
- **S3 protocol endpoint**: `/storage/v1/s3` — works with any backend incl. default files; the REST API/SDK do NOT use it.
- **`X-Forwarded-Prefix`**: gateway header (`/storage/v1`) Storage needs for SigV4 signature reconstruction.
- **`STORAGE_PUBLIC_URL`**: must be set correctly or signed URLs break.
- **RLS on `storage.objects`**: uploads always require an INSERT policy; "Public" buckets only allow unauthenticated *downloads*.

## Mental Models
- Think of the two features as a matrix: {protocol on/off} × {backend file/s3}. They don't depend on each other.
- For non-AWS providers, "MinIO-style config + your endpoint" is the universal recipe.

## Anti-patterns
- **Assuming Public bucket = uploadable**: it only enables anon downloads; uploads need an RLS INSERT policy.
- **Mismatched S3 creds**: `REGION`/`S3_PROTOCOL_ACCESS_KEY_ID`/`SECRET` in `.env` must equal what the client uses → else `SignatureDoesNotMatch`.
- **localhost URLs for browser uploads**: `API_EXTERNAL_URL`/`SUPABASE_PUBLIC_URL` as `localhost:8000` breaks CORS/mixed content.
- **TUS uploads on R2 without `TUS_ALLOW_S3_TAGS:"false"`**: R2 lacks `x-amz-tagging` → HTTP 500.

## Code Examples
```yaml name=docker-compose.yml
# Protocol endpoint (any backend)
storage:
  environment:
    REGION: ${REGION}
    S3_PROTOCOL_ACCESS_KEY_ID: ${S3_PROTOCOL_ACCESS_KEY_ID}
    S3_PROTOCOL_ACCESS_KEY_SECRET: ${S3_PROTOCOL_ACCESS_KEY_SECRET}
# S3 backend (non-AWS)
storage:
  environment:
    STORAGE_BACKEND: s3
    GLOBAL_S3_BUCKET: your-bucket
    GLOBAL_S3_ENDPOINT: https://your-account.r2.cloudflarestorage.com
    GLOBAL_S3_FORCE_PATH_STYLE: 'true'
    AWS_ACCESS_KEY_ID: ...
    AWS_SECRET_ACCESS_KEY: ...
    REGION: ...
```
```sh
aws s3 ls --endpoint-url http://localhost:8000/storage/v1/s3 --region $REGION s3://your-bucket
```
- **What it demonstrates**: both features and a protocol-endpoint smoke test.

## Reference Tables
| Backend | Endpoint var | Force path style | Override file |
|---|---|---|---|
| Local files (default) | - | - | - |
| AWS S3 | omit (auto) | omit | - |
| RustFS | set | `'true'` | `docker-compose.rustfs.yml` (preferred) |
| MinIO | set | `'true'` | `docker-compose.s3.yml` (legacy) |
| R2 / other | set | `'true'` | use MinIO-style config |

## Worked Example — RLS-scoped S3 client with a session token
```javascript
import { S3Client } from '@aws-sdk/client-s3'
const { data: { session } } = await supabase.auth.getSession()
const client = new S3Client({
  forcePathStyle: true,
  region: 'stub',                                  // REGION in .env
  endpoint: 'http://<your-domain>/storage/v1/s3',
  credentials: {
    accessKeyId: 'stub',                           // STORAGE_TENANT_ID in .env
    secretAccessKey: 'your-anon-key',              // ANON_KEY in .env
    sessionToken: session.access_token,            // user JWT -> RLS applies
  },
})
```
Every operation is scoped to the authenticated user and honors `storage.objects` RLS policies — useful for per-user access from server or frontend.

## Key Takeaways
1. Protocol endpoint and backend are independent — mix freely.
2. AWS S3: skip endpoint/path-style; non-AWS: set both.
3. RustFS is the preferred local S3-compatible backend; MinIO is legacy.
4. Uploads need RLS INSERT policy even on Public buckets.
5. `SignatureDoesNotMatch` → check `REGION`/keys and `X-Forwarded-Prefix`/`STORAGE_PUBLIC_URL`.
6. Session-token S3 auth (region=REGION, key=STORAGE_TENANT_ID, secret=ANON_KEY, token=user JWT) enforces RLS.

## Connects To
- **Ch 12**: copying objects from a platform project via rclone S3-to-S3 (needs protocol endpoint).
- **Ch 3**: Envoy/Storage need `REQUEST_ALLOW_X_FORWARDED_PATH=true` + `STORAGE_PUBLIC_URL`.
- **Ch 1**: `S3_PROTOCOL_*` and `MINIO_ROOT_PASSWORD` secrets.
