# Chapter 14: Platform (Managed Cloud)

## Core Idea
Supabase Cloud is a fully managed platform: every project = one dedicated Postgres instance plus auto-APIs, Auth, Storage, Realtime, Edge Functions. Operational scaling, security hardening, billing, and disaster recovery happen at two levels — the **organization** (billing, plan, members, SSO) and the **project** (compute/disk, replicas, backups, domains, network restrictions). Optimize software before hardware; isolate plans/projects via separate organizations; never restore blind.

## Frameworks Introduced
- **Two-tier governance**: Organization owns plan + billing + members + SSO; Project owns compute, replicas, backups, domains, restrictions. One plan per org — mix plans = separate orgs.
- **Scale decision (vertical vs horizontal)**: Diagnose bottleneck first → tune queries/connections (software) → upgrade compute (vertical) → add read replicas (horizontal, geo).
- **PITR over Daily Backups**: Enable PITR add-on when daily-granularity data loss is unacceptable; PITR replaces daily backups (RPO ~2 min).
- **Defense-in-depth at the edge**: Network Restrictions (IP CIDR, pre-auth, DB+pooler only) + SSL Enforcement (`verify-full`) + custom domain branding.
- **Spend Cap cost control**: Pro-plan toggle; ON = hard-stop overage on covered items; OFF = pay overage. Compute/replicas/domains/IPv4/PITR are never capped (explicitly opted-in).
- **RBAC role ladder**: Owner > Administrator > Developer > Read-Only, with org-scoped vs project-scoped assignment.

## Key Concepts
- **Compute upgrade downtime**: Usually <2 min, can be longer per cloud provider. Compute changes do NOT change disk type/size.
- **Burst vs sustained**: Nano–2XL CPUs burst then return to baseline; ≥Large CPU dedicated, ≥4XL sustained predictable disk IOPS/throughput.
- **Disk effective limits**: min(compute-supported, provisioned). gp3 default 125 MB/s + 3000 IOPS; io2 throughput scales with IOPS free.
- **Replication lag**: Async replication → read replicas trail Primary; replicas are read-only (SELECT only), `GET`-only via REST.
- **Geo-routing load balancer**: Since 2025-04-04, routes Data API `GET` to nearest DB; non-GET + all Auth → Primary always. Custom domain bypasses the load balancer.
- **Physical backups default**: Postgres `15.8.1.079`+ uses physical backups (WAL-G); custom-role passwords NOT in daily backups; Storage objects NOT in DB backups.
- **Network Restrictions scope**: Postgres + pooler only; NOT HTTPS APIs (PostgREST/Storage/Auth). Edge Function direct DB access always blocked when restrictions on.
- **Custom domain = CNAME-only, single subdomain** (e.g. `api.example.com`); changes SAML `EntityID`.
- **Quotas are org-wide**, summed across all projects; overage billed per unit unless Spend Cap on.

## Mental Models
- **"Software before silicon"**: Fix connection counts and slow queries before paying for bigger compute. Check `Disk IO % consumed` > 1% as the real upgrade signal.
- **"PITR rewinds to disaster, daily rewinds to yesterday"**: choose granularity by acceptable data-loss window.
- **"Restrictions filter, credentials still gate"**: IP allow-listing runs before auth but does not replace it.

## Anti-patterns
- Mixing plans in one organization (impossible — create separate orgs, use project transfer).
- Restoring a daily backup with custom roles and forgetting to reset their passwords afterward.
- Running both PITR and daily backups (redundant — PITR disables daily).
- Forgetting IPv6 CIDRs in network restrictions when DB resolves to IPv6 (locks yourself out unless IPv4 add-on).
- Activating a custom domain before adding the new callback URL to OAuth/SAML providers (breaks login; SAML `EntityID` changes).
- Routing requests through the load balancer while using a custom domain (custom domain bypasses it — use dedicated endpoints).
- Downgrading compute while using more replication slots than the smaller tier allows (server won't start).

## Code Examples
PITR restore via Management API (Unix timestamp target):
```bash
export SUPABASE_ACCESS_TOKEN="your-access-token"
export PROJECT_REF="your-project-ref"
curl -X POST "https://api.supabase.com/v1/projects/$PROJECT_REF/database/backups/restore-pitr" \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "recovery_time_target_unix": "1735689600" }'
```
Network restrictions (CLI replaces full list; include existing CIDRs to add):
```bash
supabase network-restrictions --project-ref {ref} update \
  --db-allow-cidr 183.12.1.1/24 \
  --db-allow-cidr 2001:db8:3333:4444:5555:6666:7777:8888/64 --experimental
# Remove all restrictions:
supabase network-restrictions --project-ref {ref} update \
  --db-allow-cidr 0.0.0.0/0 --db-allow-cidr ::/0 --experimental
```
SSL enforcement + verify-full connection:
```bash
supabase ssl-enforcement --project-ref {ref} update --enable-db-ssl-enforcement --experimental
cat prod-ca-2021.crt >> ~/.postgres/root.crt
psql "postgresql://aws-0-eu-central-1.pooler.supabase.com:6543/postgres?sslmode=verify-full" -U postgres.<user>
```
Custom domain lifecycle (CLI):
```bash
supabase domains create   --project-ref {ref} --custom-hostname api.example.com  # returns _acme-challenge TXT
supabase domains reverify  --project-ref {ref}   # issues SSL cert, up to 30 min
supabase domains activate  --project-ref {ref}   # old .supabase.co keeps working
supabase domains delete    --project-ref {ref}
```

## Reference Tables
Compute tiers (hourly USD / CPU / RAM / recommended max DB):
| Size | $/hr | CPU | RAM | Max DB |
|---|---|---|---|---|
| Nano | 0 | Shared | ≤0.5 GB | 500 MB |
| Micro | 0.01344 | 2-core ARM shared | 1 GB | 10 GB |
| Small | 0.0206 | 2-core shared | 2 GB | 50 GB |
| Medium | 0.0822 | 2-core shared | 4 GB | 100 GB |
| Large | 0.1517 | 2-core dedicated | 8 GB | 200 GB |
| XL | 0.2877 | 4-core | 16 GB | 500 GB |
| 2XL | 0.562 | 8-core | 32 GB | 1 TB |
| 4XL | 1.32 | 16-core | 64 GB | 2 TB |
| 8XL | 2.562 | 32-core | 128 GB | 4 TB |
| 12XL | 3.836 | 48-core | 192 GB | 6 TB |
| 16XL | 5.12 | 64-core | 256 GB | 10 TB |

Connection/replication limits: Nano/Micro 60 conns / 5 slots; Small 90/5; Medium 120/5; Large 160/8; XL 240/24; 2XL 380/80; 4XL 480/80; 8XL 490/80; 12XL–16XL 500/80. Pooler clients 200→12,000.

Backup retention by plan: Pro 7 days, Team 14, Enterprise 30; PITR add-on = seconds granularity, RPO ~2 min (WAL every 2 min or on size threshold). Free plan = self-export via `supabase db dump`.

Disk: gp3 (16 TB max, 125→1000 MB/s, 16k IOPS; $0.125/GB, $0.024/IOPS, $0.95/MB·s after included) vs io2 (60 TB, 80k IOPS, throughput scales free; $0.195/GB, $0.119/IOPS). Modify disk ≤4× per rolling 24h; size increase-only.

SSL modes: `disable`/`allow`/`prefer`(default)/`require`(encrypt, no verify)/`verify-ca`(verify CA)/`verify-full`(verify CA+hostname, recommended).

Roles: Owner (all), Administrator (all except org settings/external transfer/add owners), Developer (read org + content access project), Read-Only (read-only; Team/Enterprise only). Project-scoped roles = Team/Enterprise only.

## Worked Example
Harden + scale a production project:
1. `supabase domains create --project-ref ref --custom-hostname api.example.com`; add returned `_acme-challenge` TXT + CNAME → `ref.supabase.co.`; add `https://api.example.com/auth/v1/callback` to every OAuth provider; then `reverify` (wait ≤30 min for cert) and `activate`.
2. Enforce SSL: `ssl-enforcement update --enable-db-ssl-enforcement`; clients switch to `sslmode=verify-full` with the downloaded CA. Triggers a fast reboot.
3. Lock the network: confirm IPv4+IPv6 CIDRs (both, unless IPv4 add-on), `network-restrictions update --db-allow-cidr <office>/32 --db-allow-cidr <v6>/64`. Edge Functions must now use supabase-js, not direct DB.
4. Scale reads: add a Read Replica in the user's region; route `GET` via the load balancer endpoint (NOT the custom domain) for geo-routing; writes/Auth auto-go to Primary.
5. Protect recovery: enable PITR add-on (requires ≥Small compute). To recover from a bad migration, POST `restore-pitr` with the Unix timestamp just before it — plan for downtime proportional to DB size.

## Key Takeaways
- One dedicated Postgres per project; billing and plan live at the org, not the project.
- Diagnose before upgrading: software (queries, connections, pooler) before vertical compute before horizontal replicas.
- PITR (RPO ~2 min) supersedes daily backups; retention 7/14/30 days by plan; backups exclude Storage objects and custom-role passwords.
- Network Restrictions are pre-auth IP filtering for DB+pooler only; pair with SSL enforcement (`verify-full`) for defense-in-depth.
- Custom domains are CNAME single-subdomain, bypass the load balancer, and change SAML EntityID — prep providers before activating.
- Spend Cap (Pro) caps usage-quota items only; compute/replicas/domains/IPv4/PITR are always billed.

## Connects To
- Ch01 Getting Started (project/org creation), Ch03 Auth (OAuth/SAML callback URLs, SSO, MAU billing), Ch04 Storage (objects excluded from DB backups, egress quota), Ch05 Edge Functions (blocked from direct DB under network restrictions); self-hosting skill (the managed alternative to Docker compose).
