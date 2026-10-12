# Chapter 9: Queues (pgmq)

## Core Idea
Supabase Queues is a Postgres-native, durable, pull-based message queue built on the `pgmq` extension (from tembo-io). It gives you SQS/RSMQ-style messaging with zero external infrastructure: no background worker, no broker, no extra service — just Postgres functions packaged in an extension. Messages are JSON, persisted in regular Postgres tables, and stay in the queue until a consumer explicitly removes them. The killer property is that your queue lives inside the same transactional database as your application data, so enqueueing a message can share a transaction with the business write that produced it.

## Frameworks Introduced
- **pgmq (the extension)**: lightweight queue engine. `create extension pgmq;` adds the `pgmq` schema, functions, and a per-queue pair of tables.
- **pgmq_public (the API wrapper)**: a safe subset of `pgmq` functions exposed via PostgREST/Data API for client-side consumers. Created when you enable "Expose Queues via PostgREST". Wraps message operations only — never queue create/drop.
- **Visibility Timeout (VT) model**: SQS-style "exactly once within a window" delivery. A read makes the message invisible to other consumers for `vt` seconds; if not deleted/archived in time, it reappears for redelivery.
- **Edge Function + Cron consumer pattern**: server-side polling loop — an Edge Function reads N messages, processes, deletes; scheduled via Supabase Cron.

## Key Concepts
- **Pull-based + FIFO**: consumers actively fetch messages (no push, no priority). First-In-First-Out.
- **Queue types**: *Basic* (logged table, durable) and *Unlogged* (unlogged table, faster writes, can lose messages on crash). For unlogged queues the archive table is still logged, so archived messages stay safe.
- **Two tables per queue**: `pgmq.q_<queue_name>` (active messages) and `pgmq.a_<queue_name>` (archive). Queue names must be lowercase; only hyphens and underscores allowed.
- **Delivery semantics**: `read()` → exactly-once within VT (at-least-once overall, since redelivery happens if you don't ack). `pop()` → at-most-once (deletes on read; if your app crashes mid-process, the message is gone).
- **Delete vs Archive**: delete is permanent removal; archive moves the message to `a_<queue>` for retention, auditing, and replayability.
- **Availability**: `pgmq` requires Postgres 15.6.1.143 or later.

## Mental Models
- **The to-do list**: a message is a task sitting on a list until someone checks it off (deletes) or files it away (archives). VT is the period you "claim" a task so a teammate doesn't grab it too.
- **Transactional outbox for free**: because the queue is just Postgres tables, `send()` participates in your transaction. Commit the order *and* its "send-email" message atomically — no dual-write inconsistency.
- **`pgmq_public` is the airlock**: clients never touch `pgmq` (whose tables have no RLS by default). They only reach the wrapper functions, gated by RLS on the underlying `q_` tables plus role grants.

## Anti-patterns
- **Exposing the raw `pgmq` schema to clients**: its tables ship with RLS disabled — that is open access. Always go through `pgmq_public` + RLS.
- **Granting `pgmq_public` to `anon` / `service_role` client-side**: never expose `postgres` or `service_role` keys to the browser. Default safe grant is `authenticated` only.
- **Using `pop()` when processing must be guaranteed**: pop deletes on read (at-most-once) — a crash loses the message. Use `read()` + explicit `delete()`/`archive()` for reliability.
- **Forgetting RLS after enabling the Data API**: exposing `pgmq_public` without enabling RLS on every `q_` table leaves queues unprotected.
- **Setting VT too short**: if processing outlasts the visibility timeout, the message reappears and gets processed twice. Size VT to your slowest expected processing time.

## Code Examples
```sql
-- 1. Enable the extension
create extension pgmq;

-- 2. Create a queue (makes pgmq.q_my_queue + pgmq.a_my_queue)
select from pgmq.create('my_queue');

-- 3. Send a message (returns the msg_id)
select * from pgmq.send('my_queue', '{"hello": "world"}');
-- send
-- ------
--     4

-- 4. Read up to 2 messages, hiding them for 10s (visibility timeout)
select * from pgmq.read('my_queue', 10, 2);
-- msg_id | read_ct | enqueued_at | vt | message

-- 5. Delete a processed message permanently
select pgmq.delete('my_queue', 5);
-- delete
-- --------
--  t
```
- **What it demonstrates**: the full lifecycle in raw SQL — enable, create, enqueue, dequeue-with-VT, acknowledge. Note `read` takes `(queue_name, vt, qty)` and returns the `message_record` shape; the VT means message 5 won't be visible to others for 10s after the read.

## Reference Tables

### `pgmq` schema (full SQL API, Postgres-side)
| Operation | Signature | Returns / Notes |
| :-- | :-- | :-- |
| `create` | `pgmq.create(queue_name text)` | `void` — basic logged queue |
| `create_unlogged` | `pgmq.create_unlogged(queue_name text)` | `void` — throughput over durability |
| `drop_queue` | `pgmq.drop_queue(queue_name text)` | `boolean` — drops queue + archive |
| `detach_archive` | `pgmq.detach_archive(queue_name text)` | keeps archive on `drop extension` |
| `send` | `pgmq.send(queue_name text, msg jsonb, delay int default 0)` | `setof bigint` (msg_id) |
| `send_batch` | `pgmq.send_batch(queue_name text, msgs jsonb[], delay int default 0)` | `setof bigint` |
| `read` | `pgmq.read(queue_name text, vt int, qty int)` | `setof message_record`; VT in seconds |
| `read_with_poll` | `pgmq.read_with_poll(queue_name, vt, qty, max_poll_seconds default 5, poll_interval_ms default 100)` | long-poll variant |
| `pop` | `pgmq.pop(queue_name text)` | reads + deletes one (at-most-once) |
| `delete` (single) | `pgmq.delete(queue_name text, msg_id bigint)` | `boolean` |
| `delete` (batch) | `pgmq.delete(queue_name text, msg_ids bigint[])` | `setof bigint` (ids actually deleted) |
| `purge_queue` | `pgmq.purge_queue(queue_name text)` | `bigint` — count of all deleted |
| `archive` (single) | `pgmq.archive(queue_name text, msg_id bigint)` | `boolean` — moves to `a_<queue>` |
| `archive` (batch) | `pgmq.archive(queue_name text, msg_ids bigint[])` | `setof bigint` |
| `set_vt` | `pgmq.set_vt(queue_name text, msg_id bigint, vt_offset int)` | `message_record` — reschedule visibility |
| `list_queues` | `pgmq.list_queues()` | table(queue_name, created_at, is_partitioned, is_unlogged) |
| `metrics` | `pgmq.metrics(queue_name text)` | length, msg ages, total_messages, scrape_time |
| `metrics_all` | `pgmq.metrics_all()` | same metrics for every queue |

### `message_record` type
| Attribute | Type | Description |
| :-- | :-- | :-- |
| `msg_id` | `bigint` | Unique message ID |
| `read_ct` | `bigint` | Times read; increments on each `read()` |
| `enqueued_at` | `timestamptz` | When inserted |
| `vt` | `timestamptz` | When it becomes visible again |
| `message` | `jsonb` | Payload |

### `pgmq_public` schema (client-side Data API; note different param names)
| Function | Params |
| :-- | :-- |
| `send(queue_name, message, sleep_seconds)` | `text`, `jsonb`, `integer` optional (delay) |
| `send_batch(queue_name, messages, sleep_seconds)` | `text`, `jsonb[]`, `integer` optional |
| `read(queue_name, sleep_seconds, n)` | `sleep_seconds` = VT, `n` = max to read |
| `pop(queue_name)` | reads + deletes one |
| `archive(queue_name, message_id)` | `text`, `bigint` |
| `delete(queue_name, message_id)` | `text`, `bigint` |

### Required permissions per `pgmq_public` operation (Data API roles)
| Operations | Permissions Required |
| :-- | :-- |
| `send`, `send_batch` | `Select`, `Insert` |
| `read`, `pop` | `Select`, `Update` |
| `archive`, `delete` | `Select`, `Delete` |

## Worked Example
**Goal**: enqueue a job, process it server-side, archive it for audit.

Client enqueues via the Data API wrapper (JS):
```tsx
await supabase.schema('pgmq_public').rpc('send', {
  queue_name: 'foo',
  message: { hello: 'world' },
  sleep_seconds: 30,        // delay visibility 30s
})
```

Server-side consumer (Edge Function, runnable on a Cron schedule): read 5, process, ack each.
```tsx
const { data: messages } = await supabase.schema('pgmq_public').rpc('read', {
  queue_name: 'foo', sleep_seconds: 0, n: 5,
})
for (const m of messages) {
  // ...do work with m.message...
  await supabase.schema('pgmq_public').rpc('delete', {
    queue_name: 'foo', msg_id: m.msg_id,
  })
}
```
If `processMessage` throws, you skip the delete — the message stays in the queue and the VT lets it reappear for the next run, giving automatic retry. To keep it for auditing instead of deleting, swap `delete` for `archive` (single SQL form: `select pgmq.archive('foo', 1);`), which moves the row into `pgmq.a_foo`.

**Self-host / local exposure**: `pgmq_public` is not exposed by default outside the platform. With the CLI, add it to `config.toml` `[api] schemas = ["public", "graphql_public", "pgmq_public"]` then `supabase stop && supabase start`. With Docker Compose, set `PGRST_DB_SCHEMAS=public,graphql_public,pgmq_public` and `docker compose down && docker compose up -d`.

## Key Takeaways
- Queues = `pgmq` extension; one queue = two tables (`q_` active, `a_` archive) in the `pgmq` schema.
- `read()` + explicit `delete()`/`archive()` = reliable at-least-once; `pop()` = convenient but at-most-once.
- Visibility timeout (VT) is the contract: claim a message for `vt` seconds; unacked messages reappear → free retries. Size VT > processing time.
- Clients must go through `pgmq_public` (the airlock), gated by RLS on `q_` tables + role grants; never expose raw `pgmq` or `service_role`.
- Archive instead of delete when you need retention/replayability.

## Connects To
- **Edge Functions + Cron**: the standard polling consumer (Ch. on Functions / `/docs/guides/cron`).
- **RLS & Roles**: queue authorization reuses the same Postgres RLS + Data API role model as your tables.
- **Self-Hosting**: `PGRST_DB_SCHEMAS` / `config.toml` schema exposure mirrors how any custom schema is published through PostgREST.
- **Transactional outbox / background jobs**: `send()` inside an app transaction = atomic enqueue with business writes.
