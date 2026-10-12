# Chapter 10: Cron (pg_cron)

> Note: This is a thin section in the source docs (one overview page + install + quickstart). The chapter below synthesizes all available material; depth is bounded by source coverage.

## Core Idea

Supabase Cron is a Postgres *module* that schedules recurring Jobs using cron syntax — entirely inside the database. It wraps the [`pg_cron`](https://github.com/citusdata/pg_cron) extension, which is the scheduling and execution engine. A Job runs a SQL snippet or database function with **zero network latency**, or makes an outbound HTTP request (e.g. invoking a Supabase Edge Function) via `pg_net`. Jobs can run as often as every second or as rarely as once a year. Everything is managed via SQL or the Dashboard (Integrations → Cron); both write to the same underlying tables.

## Frameworks Introduced

- **pg_cron module**: A Postgres extension that creates a `cron` schema, stores Job definitions in `cron.job`, and records every run + status in `cron.job_run_details`.
- **Schedule-execute model**: One function call (`cron.schedule`) binds a unique name + cron expression + a command string; the engine fires the command on the schedule.

## Key Concepts

- **Job**: A named, scheduled unit of work. The name is **case-sensitive and immutable** — re-scheduling with the same name *overwrites* (upserts) the existing Job.
- **`cron` schema**: Auto-created on install; holds `cron.job` (definitions) and `cron.job_run_details` (run history).
- **Command**: The text executed on schedule — a SQL statement, `SELECT fn()`, `CALL proc()`, or a `net.http_post(...)` call.
- **Sub-minute scheduling**: Intervals of `[1-59] seconds` (e.g. `'30 seconds'`) are supported on Postgres `15.1.1.61` or later — distinct from standard 5-field cron.
- **`pg_net`**: Separate extension required for HTTP requests (`net.http_post`); enables async outbound calls from inside Postgres.
- **Run history**: `cron.job_run_details` is **never auto-cleaned**, persists even after a Job is unscheduled, and consumes disk space — you must prune it yourself.
- **Concurrency guidance**: For best performance, no more than **8 Jobs concurrent**, each running no longer than **10 minutes**.

## Mental Models

- **The job table IS the cron tab**: There is no crontab file — `cron.job` is the source of truth. Reading/altering rows = reading/editing the schedule.
- **In-DB beats network**: Prefer SQL / database functions (zero latency) over HTTP. Reach for `net.http_post` only when the work genuinely lives outside the DB (Edge Function, third-party API).
- **Upsert by name**: Treat the Job name as a primary key. Same name = replace, not add.

## Anti-patterns

- **Scheduling system maintenance blindly**: e.g. terminating idle connections with `pg_terminate_backend(pid)` can kill critical background processes like nightly backups. Prefer an existing Postgres setting (e.g. `idle_session_timeout`) when one exists.
- **Ignoring run-history growth**: Letting `cron.job_run_details` accumulate unbounded; it survives unscheduling and bloats the database.
- **Overloading the scheduler**: More than ~8 concurrent Jobs or Jobs exceeding 10 minutes degrades performance.
- **Assuming name edits work**: Job names cannot be edited after creation; a "rename" silently creates/overwrites a different Job.

## Code Examples

```sql
-- Install the module
create extension pg_cron with schema pg_catalog;

grant usage on schema cron to postgres;
grant all privileges on all tables in schema cron to postgres;

-- Schedule a sub-minute job that calls a stored procedure
select cron.schedule('permanent-cron-job-name', '30 seconds', 'CALL do_something()');
```

- **What it demonstrates**: Enabling `pg_cron` and granting access, then creating a named Job with a sub-minute (seconds) interval that executes a stored procedure. The name is permanent and acts as the upsert key.

## Reference Tables

### Cron expression fields (standard 5-field)

```
 ┌───────────── min (0 - 59)
 │ ┌────────────── hour (0 - 23)
 │ │ ┌─────────────── day of month (1 - 31)
 │ │ │ ┌──────────────── month (1 - 12)
 │ │ │ │ ┌───────────────── day of week (0 - 6) (0 to 6 are Sunday to
 │ │ │ │ │                  Saturday, or use names; 7 is also Sunday)
 │ │ │ │ │
 │ │ │ │ │
 * * * * *
```

Sub-minute: use `[1-59] seconds` (e.g. `'30 seconds'`) as the schedule string instead of a 5-field expression (Postgres ≥ 15.1.1.61).

### Common schedule strings

| Expression       | Meaning                                  |
|------------------|------------------------------------------|
| `* * * * *`      | Every minute                             |
| `*/5 * * * *`    | Every 5 minutes                          |
| `0 3 * * *`      | Daily at 3:00 AM (GMT)                    |
| `30 3 * * 6`     | Saturday at 3:30 AM (GMT)                 |
| `'30 seconds'`   | Every 30 seconds (sub-minute)            |

### Lifecycle functions

| Function | Purpose |
|----------|---------|
| `cron.schedule(name, schedule, command)` | Create (or upsert by name) a Job |
| `cron.alter_job(job_id, schedule, command, database, username, active)` | Modify a Job; all but `job_id` default null |
| `cron.unschedule(name)` | Delete the Job from `cron.job` (run history remains) |

`cron.alter_job` full signature:

```sql
cron.alter_job(
  job_id bigint,
  schedule text default null,
  command text default null,
  database text default null,
  username text default null,
  active boolean default null
)
```

### Inspect / manage Jobs

```sql
-- Change schedule
select cron.alter_job(
  job_id := (select jobid from cron.job where jobname = 'permanent-cron-job-name'),
  schedule := '*/5 * * * *'
);

-- Activate / deactivate
select cron.alter_job(
  job_id := (select jobid from cron.job where jobname = 'permanent-cron-job-name'),
  active := true   -- or false to pause
);

-- Inspect last 10 runs
select *
from cron.job_run_details
where jobid = (select jobid from cron.job where jobname = 'permanent-cron-job-name')
order by start_time desc
limit 10;

-- Delete the job
select cron.unschedule('permanent-cron-job-name');
```

### Practical SQL examples

```sql
-- Delete old data every Saturday at 3:30AM (GMT)
select cron.schedule (
  'saturday-cleanup', -- name of the cron job
  '30 3 * * 6', -- Saturday at 3:30AM (GMT)
  $$ delete from events where event_time < now() - interval '1 week' $$
);

-- Vacuum every day at 3:00AM (GMT)
select cron.schedule('nightly-vacuum', '0 3 * * *', 'VACUUM');

-- Call a database function every 5 minutes
select cron.schedule('call-db-function', '*/5 * * * *', 'SELECT hello_world()');

-- Call a stored procedure every 5 minutes
select cron.schedule('call-db-procedure', '*/5 * * * *', 'CALL my_procedure()');
```

## Worked Example

Schedule a Job that invokes a Supabase Edge Function every 30 seconds via an HTTP POST (requires the `pg_net` extension):

```sql
select
  cron.schedule(
    'invoke-function-every-half-minute',
    '30 seconds',
    $$
    select
      net.http_post(
          url:='https://project-ref.supabase.co/functions/v1/function-name',
          headers:=jsonb_build_object('Content-Type','application/json', 'apikey', 'YOUR_PUBLISHABLE_KEY'),
          body:=jsonb_build_object('time', now() ),
          timeout_milliseconds:=5000
      ) as request_id;
    $$
  );
```

**Why it works**: The command is a dollar-quoted (`$$ ... $$`) SQL block so the inner `net.http_post(...)` call — with its own quoted strings — needs no escaping. `net.http_post` (from `pg_net`) fires an async POST to the Edge Function endpoint. The `apikey` header authenticates the call; `body` builds a JSON payload with `jsonb_build_object`; `timeout_milliseconds` caps the request. The Job name is the upsert key, so re-running this statement updates the same Job rather than creating a duplicate.

## Key Takeaways

- One function — `cron.schedule(name, schedule, command)` — creates/upserts every Job; the **name is immutable and case-sensitive**.
- Prefer in-DB SQL/functions (zero latency); use `net.http_post` (needs `pg_net`) only for outbound HTTP / Edge Functions.
- Sub-minute (`'N seconds'`) schedules need Postgres ≥ 15.1.1.61.
- Manage Jobs with `cron.alter_job` (change schedule / pause via `active`) and `cron.unschedule`; definitions live in `cron.job`, runs in `cron.job_run_details`.
- `cron.job_run_details` grows forever and survives unscheduling — prune it. Keep ≤ 8 concurrent Jobs, each ≤ 10 minutes.
- Disabling `pg_cron` (`drop extension if exists pg_cron;`) permanently deletes all Jobs.

## Connects To

- **Edge Functions**: Cron is the canonical way to trigger Edge Functions on a schedule via `net.http_post`.
- **`pg_net`**: Required dependency for any HTTP-based Job.
- **Database Functions / Stored Procedures**: Most efficient Job targets (`SELECT fn()` / `CALL proc()`).
- **Database maintenance**: `VACUUM`, cleanup deletes — but defer to native Postgres settings (e.g. `idle_session_timeout`) for connection management.
```