# Chapter 12: Copy Storage Objects from Platform

## Core Idea
Migrate storage objects from a managed Supabase project to self-hosted using `rclone` S3-to-S3 copy — NOT direct file copy. Self-hosted Storage uses an internal file layout, so going through the S3 protocol is what makes Storage write the correct metadata records.

## Frameworks Introduced
- **S3-to-S3 copy with rclone**: configure two remotes (`platform`, `self-hosted`), create matching buckets, `rclone copy`.
  - When to use: any storage migration from platform → self-hosted.
  - How: get platform S3 creds, enable the self-hosted S3 protocol endpoint, create destination buckets, set up `rclone.conf`, copy, verify.
- **Bucket pre-creation requirement**: destination buckets must exist first — S3 protocol does NOT auto-create on copy.

## Key Concepts
- **Why not direct copy**: downloaded files lack the internal structure/metadata Storage expects; the S3 protocol path creates correct records.
- **Platform endpoint**: `https://<ref>.supabase.co/storage/v1/s3` (or faster `https://<ref>.storage.supabase.co/storage/v1/s3`).
- **Self-hosted endpoint**: `http://<your-domain>:8000/storage/v1/s3`, using `REGION`/`S3_PROTOCOL_ACCESS_KEY_ID`/`SECRET`.
- **Restore overlap**: if you already ran the DB restore (Ch 15), bucket rows exist — skip bucket creation.

## Mental Models
- Think "two S3 endpoints, one rclone bridge." The metadata correctness comes free *because* you used the protocol, not the filesystem.

## Anti-patterns
- **Dropping files into `volumes/storage/`**: breaks — wrong internal structure, missing metadata.
- **Copying before creating buckets**: rclone reports "bucket not found"; S3 won't auto-create.
- **Mismatched self-hosted S3 creds**: `SignatureDoesNotMatch` — `REGION`/keys in `.env` must match `rclone.conf`.

## Code Examples
```ini name=rclone.conf
[platform]
type = s3
provider = Other
access_key_id = platform-key-id
secret_access_key = platform-secret
endpoint = https://your-ref.supabase.co/storage/v1/s3
region = your-project-region

[self-hosted]
type = s3
provider = Other
access_key_id = self-hosted-key-id
secret_access_key = self-hosted-secret
endpoint = http://your-domain:8000/storage/v1/s3
region = your-self-hosted-region
```
```sh
rclone lsd platform: && rclone lsd self-hosted:                 # verify both
rclone copy platform:your-bucket self-hosted:your-bucket --progress
rclone size platform:your-bucket && rclone size self-hosted:your-bucket   # compare
```
- **What it demonstrates**: the two-remote config and a single-bucket copy + verify.

## Reference Tables
| Step | Action |
|---|---|
| 1 | Platform S3 creds: Storage > S3 Configuration > Access keys |
| 2 | Create matching buckets on self-hosted (UI or SQL) |
| 3 | Configure `rclone.conf` (both remotes) |
| 4 | `rclone copy` per bucket (or loop) |
| 5 | Verify with `rclone size` + Studio browse |

Tuning: `--transfers 4` (parallelism), `--checkers 8` (faster compare), `--timeout 30m` (large files).

## Worked Example — create buckets then copy all of them
```sql
-- On self-hosted DB, mirror each platform bucket:
insert into storage.buckets (id, name, public)
values ('your-bucket','your-bucket', false)
on conflict (id) do nothing;
```
```sh
# Copy every bucket
for bucket in $(rclone lsf platform: | tr -d '/'); do
  echo "Copying: $bucket"
  rclone copy "platform:$bucket" "self-hosted:$bucket" --progress
done
```
(List platform buckets first with `select id, name, public from storage.buckets order by name;` — set `public` true/false to match.)

## Key Takeaways
1. Use rclone S3-to-S3; never copy files directly into `volumes/storage/`.
2. Create destination buckets first — no auto-create over S3.
3. Self-hosted needs the S3 protocol endpoint enabled (Ch 6).
4. Match `REGION`/`S3_PROTOCOL_*` between `.env` and `rclone.conf`.
5. Verify with `rclone size` on both sides + Studio.
6. If DB was already restored (Ch 15), bucket rows exist — skip step 2.

## Connects To
- **Ch 6**: enabling the S3 protocol endpoint (prerequisite).
- **Ch 15**: DB restore brings bucket definitions; storage objects copied separately here.
