# Chapter 16: Telemetry (Logs, Metrics, Tracing)

## Core Idea
Telemetry answers "what is happening inside my app" through three signal types: **logs** (discrete events — errors, queries, requests at a moment in time), **metrics** (numerical series over time — CPU, IOPS, connections), and **traces** (the path of one request across services). Supabase exposes all three and is converging on the **OpenTelemetry** standard so its signals become first-class citizens in any external observability stack. The platform gives you a SQL-queryable log warehouse (BigQuery-backed), a Prometheus-compatible metrics endpoint, prebuilt Reports, log export ("drains") to vendors, and W3C trace-context propagation from the JS client through the server.

## Frameworks Introduced
- **Logs Explorer (BigQuery SQL):** every stack component is a separate queryable table (`edge_logs`, `postgres_logs`, etc.) with three base columns and nested `metadata`.
- **Metrics API (Prometheus):** one HTTPS endpoint per project exposing ~200 Postgres series, scraped into any Prometheus-compatible collector.
- **Log Drains:** batched export of the entire log stream to HTTP/Datadog/Loki/Sentry/S3/OTLP destinations.
- **W3C Trace Context propagation:** the JS SDK attaches `traceparent`/`tracestate`/`baggage` so a `trace_id` links client spans to server logs.
- **Reports:** prebuilt dashboards (Database, Auth, Storage, Realtime, API Gateway, Edge Functions, PostgREST) — Cloud only.

## Key Concepts
- **Log sources** are independent tables; they cannot be joined to each other.
- **`metadata` is a nested array of JSON objects.** You must `cross join unnest()` once per nesting level to reach a field.
- **`timestamp` is stored as Unix microseconds.** Wrap with `datetime()` for ISO-8601.
- **API logs flow through Cloudflare** — request/response headers are restricted to an allowlist; CF metadata lives under `metadata.request.cf.*`.
- **pgAudit** controls which Postgres statement classes get logged (`pgaudit.log`).
- **Metrics endpoint:** `https://<project-ref>.supabase.co/customer/v1/privileged/metrics`, HTTP Basic Auth, Secret API key (`sb_secret_...`) as password, scrape at **60s** to match refresh cadence. Beta; not in self-hosted.
- **Trace propagation is opt-in and silently no-ops** when there's no active span, no `@opentelemetry/api`, or no registered `TracerProvider`.

## Mental Models
- **Logs = events, Metrics = trends, Traces = request flow.** Reach for the one that matches your question.
- **`metadata` is a tree, SQL is flat.** Each `unnest` join flattens one branch so you can `select` a leaf.
- **`trace_id` is the thread** stitching a client span to API Gateway and Edge Function logs across the network boundary — and via Log Drains into your own tracing UI.
- **Drains are fire-and-forget batches** (250 logs or 1s, gzipped) — they don't replace querying, they ship the same stream elsewhere.

## Anti-patterns
- Selecting whole `metadata` objects (forces the columnar engine to scan every nested column → timeouts/OOM). Select only the leaf values you need.
- Querying entire log history with no `timestamp` filter (scans the full retention dataset).
- Expecting `with`, subqueries, `ilike`, `similar to`, or `*` column selection — none are supported; use `regexp_contains` and explicit columns.
- Setting `log_min_messages` to `LOG` and expecting to see `WARNING`/`ERROR` — `LOG` is a *higher* level, so they're hidden.
- Logging PII in the `User-Agent` header (enables fingerprinting; violates privacy law).
- Double-counting Supabase spans in Sentry when HTTP/Fetch integrations also trace them.

## Code Examples

Filter Postgres logs for errors (two-level unnest + regex):
```sql
select
  cast(postgres_logs.timestamp as datetime) as timestamp,
  parsed.error_severity, parsed.user_name, event_message
from postgres_logs
  cross join unnest(metadata) as metadata
  cross join unnest(metadata.parsed) as parsed
where regexp_contains(parsed.error_severity, 'ERROR|FATAL|PANIC')
order by timestamp desc
limit 100;
```

Enable Postgres query logging via pgAudit (permanent, then fast reboot):
```sql
alter role postgres set pgaudit.log to 'function, write, ddl';
alter role authenticator set pgaudit.log to 'write';  -- API traffic
```

Prometheus scrape config (self-hosted / vendor-agnostic):
```yaml
scrape_configs:
  - job_name: 'supabase'
    scrape_interval: 60s
    metrics_path: /customer/v1/privileged/metrics
    scheme: https
    basic_auth:
      username: username
      password: '<secret API key (sb_secret_...)>'
    static_configs:
      - targets: ['<project-ref>.supabase.co:443']
        labels:
          project: '<project-ref>'
```

Client-side trace propagation (JS SDK ≥ 2.106.0):
```ts
import { trace } from '@opentelemetry/api'
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY, { tracePropagation: true })
const tracer = trace.getTracer('my-app')
await tracer.startActiveSpan('fetch-users', async (span) => {
  const { data, error } = await supabase.from('users').select('*')
  span.end()
})
```

Sentry integration (dedup Supabase REST spans):
```ts
Sentry.init({
  dsn: SENTRY_DSN,
  integrations: [
    supabaseIntegration(SupabaseClient, Sentry, { tracing: true, breadcrumbs: true, errors: true }),
    Sentry.browserTracingIntegration({
      shouldCreateSpanForRequest: (url) => !url.startsWith(`${SUPABASE_URL}/rest`),
    }),
  ],
})
```

## Reference Tables

Log sources (Logs Explorer / `Sources` dropdown):
| Source | Contents |
| --- | --- |
| `auth_logs` | GoTrue auth/authorization activity |
| `edge_logs` | Cloudflare edge request/response metadata (REST, GraphQL) |
| `function_edge_logs` | Edge network logs for edge function executions |
| `function_logs` | `console` output from inside edge functions |
| `postgres_logs` | DB statements; `metadata.parsed.error_severity` etc. |
| `realtime_logs` | Realtime client connection info |
| `storage_logs` | Object upload/retrieval info |

Every log table has 3 base columns: `timestamp`, `event_message`, `metadata`.

Log drain destinations:
| Destination | Transport | Key config |
| --- | --- | --- |
| Generic HTTP | HTTP/1 or /2 | URL, Gzip, Headers (unsigned) |
| Datadog | HTTP | API Key, Region (gzipped) |
| Loki | HTTP | URL, Headers (needs structured metadata ≥500 fields) |
| Sentry | HTTP | DSN (Logging product; self-hosted ≥25.9.0) |
| Axiom | HTTP | Dataset, API token |
| Amazon S3 | AWS SDK | Bucket, Region, Access Key ID/Secret, Batch Timeout 2000–5000ms |
| OTLP | HTTP | Endpoint `/v1/logs`, `http/protobuf`, Gzip, Headers |

Batching: max 250 logs or 1s interval. `tracePropagation` options: `enabled` (default `false`), `respectSamplingDecision` (default `true`).

## Worked Example
Goal: find errors then stand up metrics. (1) In Logs Explorer, run the Postgres error query above, filtered by `timestamp` and limited to 100 rows. (2) Add a Supabase scrape job to `prometheus.yml` (config above) hitting `/customer/v1/privileged/metrics` with the `sb_secret_...` key at 60s. (3) In Grafana, add a Prometheus data source → **Dashboards → New → Import** → paste `supabase-grafana/dashboard.json` (200+ panels: CPU, IO, WAL, replication, bloat) → pick the Prometheus datasource. (4) Import `docs/example-alerts.md` rules (disk saturation, long-running queries, replication lag). For multi-project, add one scrape job per project ref with distinct `project` labels.

## Key Takeaways
- Three signals, three tools: Logs Explorer (SQL), Metrics API (Prometheus), trace propagation (W3C).
- Always `datetime()` the timestamp, always filter on `timestamp`, always `unnest` `metadata` and select leaves.
- Metrics endpoint is one URL with Basic Auth + Secret key, scraped at 60s; reuse the supabase-grafana dashboard JSON.
- Log Drains export the full stream in 250-log gzipped batches to HTTP/Datadog/Loki/Sentry/S3/OTLP.
- `trace_id` links client → API Gateway/Edge Function logs; opt-in, no-ops silently when misconfigured.

## Connects To
- Self-hosting (no Metrics API / Reports; logs available; Sentry drain needs self-hosted ≥25.9.0).
- Edge Functions (function logs, 10k-char message cap; drain walkthroughs use a function receiver).
- Database performance (Reports + Query Performance report + Advisors for right-sizing).
- Auth/Realtime/Storage (each has dedicated log source and Report).
