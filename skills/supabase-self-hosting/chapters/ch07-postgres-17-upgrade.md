# Chapter 7: Upgrade to Postgres 17

## Core Idea
Postgres 17 is the default for new self-hosted deployments. Upgrading an existing PG15 install uses an automated `pg_upgrade` script (two phases, in-place) — but the whole operation hinges on protecting the `db-config` named volume (it holds the pgsodium key) and keeping the PG15 backup until verified.

## Frameworks Introduced
- **New deploy vs in-place upgrade**:
  - New: `docker compose up -d` starts on PG17, no override (note: `pg_graphql` is OFF by default on fresh PG17 — enable in Studio or `create extension pg_graphql;`).
  - Upgrade: `sudo bash utils/upgrade-pg17.sh` (`--yes` to skip prompts) runs `pg_upgrade` migrating data in place.
- **Two-phase upgrade**:
  - Phase 1 (PG15 container): disable incompatible extensions (`pg_graphql`, `pg_stat_monitor`, `pg_backtrace`), grant temp superuser, `initdb`, `pg_upgrade --check`, then `pg_upgrade`.
  - Phase 2 (PG17 container): move data in place, patch extensions (Wrappers, `pg_net`, `pg_cron`, Vault), run generated catalog SQL, re-enable extensions, grant predefined roles, revoke temp superuser, `vacuumdb --analyze-in-stages`.
- **Triple backup discipline**: data dir (`cp -a`), pgsodium key (from `db-config` named volume), optional logical dump (`pg_dumpall`).

## Key Concepts
- **`db-config` named volume**: holds `pgsodium_root.key`. Lose it + have Vault secrets → unrecoverable. `cp -a` of data dir does NOT back it up.
- **Backups kept by the script**: `./volumes/db/data.bak.pg15`, `pgsodium_root.key.bak.pg15`, `pg17_upgrade_bin_*.tar.gz`.
- **Disk requirement**: ≥ 2× current DB size + 5 GB (`pg_upgrade` copies the data dir; tarball ~1.2 GB compressed).
- **PG17-dropped extensions**: `timescaledb`, `plv8`, `plcoffee`, `plls` — none default; if manually installed and needed, do NOT upgrade.

## Mental Models
- Treat the upgrade as irreversible-until-verified: rollback only works while `data.bak.pg15` exists. Never delete it before confirming PG17 works.
- `down -v` is the cardinal sin here — it destroys `db-config` and your pgsodium key.

## Anti-patterns
- **`docker compose down -v`**: destroys named volumes incl. pgsodium key → Vault secrets unrecoverable.
- **Deleting `data.bak.pg15` before verifying**: removes the only rollback path.
- **Upgrading with `timescaledb`/`plv8` installed and needed**: not built for PG17.
- **Ignoring leftover `db-config` on a fresh PG17 start**: causes startup failure — remove the old volume.

## Code Examples
```sh
# Back up first
cp -a ./volumes/db/data ./volumes/db/data-manual-backup
docker compose run --rm db cat /etc/postgresql-custom/pgsodium_root.key > ./pgsodium_root.key.backup
docker exec supabase-db pg_dumpall -h localhost -U supabase_admin > ./pg15_dump.sql
# Run the upgrade (root)
sudo bash utils/upgrade-pg17.sh
# Verify
docker compose -f docker-compose.yml -f docker-compose.pg17.yml exec db psql -U postgres -c "SELECT version();"
```
- **What it demonstrates**: the mandatory backup trio + upgrade + verify.

## Reference Tables
| Item | Path / value |
|---|---|
| PG15 data backup (auto) | `./volumes/db/data.bak.pg15` |
| pgsodium key backup (auto) | `./volumes/db/pgsodium_root.key.bak.pg15` |
| Upgrade binaries cache | `./volumes/db/pg17_upgrade_bin_*.tar.gz` |
| Disk needed | 2× DB size + 5 GB |
| Staging dir | `/tmp` (override with `TMPDIR=`) |

Dropped in PG17: `timescaledb`, `plv8`, `plcoffee`, `plls`.

## Worked Example — rollback to Postgres 15
If PG17 misbehaves and the backup still exists (run as root):
```sh
docker compose down && \
rm -rf ./volumes/db/data && \
mv ./volumes/db/data.bak.pg15 ./volumes/db/data && \
docker compose -f docker-compose.yml -f docker-compose.pg15.yml run --rm db \
  chown -R postgres:postgres /etc/postgresql-custom/ && \
docker compose -f docker-compose.yml -f docker-compose.pg15.yml up -d
```
The PG15 override is required because PG15 and PG17 images use **different UIDs** — the `chown` and startup must run under PG15. This restores the original data dir, fixes ownership on `db-config`, and boots the old image.

## Key Takeaways
1. New deploys are PG17 already; `pg_graphql` is off on fresh PG17.
2. Back up data dir AND the pgsodium key (separate named volume) AND optionally a logical dump.
3. Need 2× DB size + 5 GB free disk.
4. Never `down -v`; never delete `data.bak.pg15` until verified.
5. Rollback needs the PG15 override (`chown` for UID differences).
6. `timescaledb`/`plv8`/`plcoffee`/`plls` aren't in PG17 — don't upgrade if you rely on them.

## Connects To
- **Ch 1**: base Docker setup and override files.
- **Ch 15**: restoring a platform project; match PG versions (consider PG17 if platform is 17).
- **Custom config**: PG17 loads `/etc/postgresql-custom/conf.d/*.conf` (on `db-config` volume) — PG15 does not.
