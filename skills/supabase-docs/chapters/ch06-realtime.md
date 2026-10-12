# Chapter 6: Realtime

## Core Idea

Supabase Realtime is a globally distributed Elixir/Phoenix cluster that lets connected clients exchange low-latency WebSocket messages and observe database state. Clients connect to the nearest cluster node; messages route to any other node via Erlang process groups (Phoenix.PubSub PG2 adapter), so a client in the US can reach one in Singapore over the shortest path. Three feature primitives sit on top of one abstraction — the **Channel** (a named room identified by a topic): **Broadcast** (ephemeral client-to-client messages), **Presence** (synchronized shared user state), and **Postgres Changes** (streamed database row events from the WAL via a logical replication slot).

## Frameworks Introduced

- **Broadcast / Presence / Postgres Changes**: the three Realtime extensions you attach to a channel via `.on(type, opts, callback)`, each solving a different real-time problem.
- **Channel authorization model (RLS on `realtime.messages`)**: private channels gate read/write/presence access through Row Level Security policies evaluated once at join time, cached for the connection.
- **Broadcast from the database**: `realtime.send()` / `realtime.broadcast_changes()` insert into the partitioned `realtime.messages` table; a replication slot reads the WAL and pushes to clients — driving real-time UI from SQL triggers.

## Key Concepts

- **Channel / Topic**: a channel is a room identified by a topic string (any string except `'realtime'`) plus a public/private flag. A public and private channel with the same topic name are distinct and don't exchange messages.
- **Public vs private**: public channels accept any subscriber; private channels require an authenticated, signed JWT and RLS authorization (`config: { private: true }`). You can force projects to private-only in Realtime Settings.
- **Send transport**: client-library `send()` uses HTTP before subscribe, WebSocket after subscribe; `httpSend()` (js ≥ 2.107.0) always uses REST.
- **Authorization at join**: on join Realtime runs an insert+select on `realtime.messages` inside a transaction it rolls back — verifying RLS without storing messages. Realtime connects as Supabase Admin regardless of the channel's public/private flag.
- **Presence events**: `sync` (full state updated), `join`, `leave`. State is a CRDT-backed in-memory KV store replicated to all nodes; `track()` publishes a payload, `untrack()` removes it.
- **Postgres Changes pipeline**: requires the table in the `supabase_realtime` publication; Realtime polls the replication slot, appends subscriber IDs to each WAL record, then delivers. Records are filtered per-subscriber by RLS.
- **`replica identity full`**: required on a table to receive `old` records on UPDATE/DELETE; with RLS enabled, the `old` record exposes only primary keys.
- **JWT lifecycle**: the access-policy cache refreshes on connect and on each new `access_token` message; if a fresh JWT never arrives, the client is disconnected at expiry — keep expiry windows short.

## Mental Models

- **Broadcast is the firehose; Presence is the slow-moving dashboard.** Both flow over WebSockets, but Presence notifies *all* subscribers on every change — never `track()` on mouse-move; use Broadcast for high-frequency or fire-and-forget data.
- **Postgres Changes is a fan-out tax.** One insert with 100 subscribers triggers 100 authorization reads on a single ordering thread, so compute upgrades barely move throughput. At scale, prefer an unsecured public table, or stream server-side and re-broadcast.
- **The `realtime.messages` table is the security boundary.** All Broadcast and Presence authorization is RLS on that one table; the `extension` column (`broadcast` / `presence`) tells you which feature a policy governs.

## Anti-patterns

- Using Presence for cursor tracking or per-frame updates — floods the channel; use Broadcast.
- Naming a channel `'realtime'` — reserved.
- Database-broadcasting public while clients subscribe private (or vice versa) — the public/private flag must match on both ends or messages are silently dropped.
- Exposing the `service_role` token client-side — it bypasses RLS.
- Relying on Postgres Changes filters for DELETE events — Delete events are not filterable.
- Heavy/complex RLS policies — raise connection latency and lower join rates.

## Code Examples

```js
// Join a room/topic. Can be anything except for 'realtime'.
const myChannel = supabase.channel('test-channel')

// Function to log any messages we receive
function messageReceived(payload) {
  console.log(payload)
}

// Subscribe to the Channel
myChannel
  .on(
    'broadcast',
    { event: 'shout' }, // Listen for "shout". Can be "*" to listen to all events
    (payload) => messageReceived(payload)
  )
  .subscribe()
```

- **What it demonstrates**: the canonical pattern — create a channel by topic, register an `.on()` handler for a feature/event, then `.subscribe()`. The same shape applies to `presence`, `postgres_changes`, and broadcast.

```js
// Listen to all changes on a specific table
const channelA = supabase
  .channel('table-db-changes')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'todos', filter: 'id=eq.1' },
    (payload) => console.log(payload)
  )
  .subscribe()
```

- **What it demonstrates**: Postgres Changes config keys — `event` (`INSERT`/`UPDATE`/`DELETE`/`*`), `schema`, `table`, and optional `filter` (`eq`,`neq`,`lt`,`lte`,`gt`,`gte`,`in`; max 100 values for `in`).

## Reference Tables

| Aspect | Broadcast | Presence | Postgres Changes |
| --- | --- | --- | --- |
| Purpose | Low-latency client-to-client messages | Synchronized shared user state | Stream DB row changes |
| Transport | WebSocket / REST / DB | WebSocket (CRDT KV) | WebSocket from WAL replication slot |
| Events | custom `event` names, `*` | `sync`, `join`, `leave` | `INSERT`, `UPDATE`, `DELETE`, `*` |
| Persistence | None (replay only for DB broadcasts, private) | In-memory, ephemeral | Source rows persist in DB |
| Auth | RLS `extension='broadcast'` | RLS `extension='presence'` | Per-row RLS on source table |
| Scaling | Excellent (no DB read per msg) | Good for slow state; floods if abused | Bottlenecked: single thread, per-subscriber reads |
| Payload limit | 256 KB free / 3,000 KB paid | 10 keys/object | 1,024 KB (then fields >64 B dropped) |

| Limit (Free / Pro) | Value |
| --- | --- |
| Concurrent connections | 200 / 500 |
| Messages per second | 100 / 500 |
| Channels per connection | 100 / 100 |
| Presence messages/sec | 20 / 50 |
| Join refusals | `too_many_channels`, `too_many_connections`, `too_many_joins`, `tenant_events` |

## Worked Example

```js
// Private channel: subscribe, broadcast, and track presence on one topic
const channel = supabase.channel('room-1', {
  config: { private: true, broadcast: { self: true } },
})

const userStatus = { user: 'user-1', online_at: new Date().toISOString() }

channel
  .on('broadcast', { event: 'shout' }, (payload) => console.log('msg', payload))
  .on('presence', { event: 'sync' }, () => console.log('who', channel.presenceState()))
  .subscribe(async (status) => {
    if (status !== 'SUBSCRIBED') return
    await channel.track(userStatus)              // publish presence
    channel.send({ type: 'broadcast', event: 'shout', payload: { message: 'Hi' } })
  })
```

Drive the same channel from SQL via a trigger:

```sql
CREATE OR REPLACE FUNCTION public.your_table_changes()
RETURNS trigger
SECURITY DEFINER SET search_path = ''
AS $$
BEGIN
    PERFORM realtime.broadcast_changes(
        'topic:' || NEW.id::text,  -- topic
        TG_OP, TG_OP,              -- event, operation
        TG_TABLE_NAME, TG_TABLE_SCHEMA,
        NEW, OLD
    );
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
```

Allow listeners with an RLS policy and subscribe (`setAuth()` required for private):

```sql
CREATE POLICY "authenticated can receive broadcasts"
ON "realtime"."messages" FOR SELECT TO authenticated USING ( true );
```

## Key Takeaways

- One abstraction (Channel/topic), three features (Broadcast, Presence, Postgres Changes); choose by frequency, persistence, and auth needs.
- Private channels = `config: { private: true }` + RLS policies on `realtime.messages` keyed by the `extension` column; auth is evaluated at join and cached per connection.
- Broadcast scales; Postgres Changes does not (single ordering thread, per-subscriber RLS reads) — re-stream via Broadcast at scale.
- Database broadcasts and client channels must agree on the public/private flag or messages vanish.
- `replica identity full` to get `old` records; mind payload limits (Broadcast 256 KB free, Postgres Changes 1,024 KB then field truncation).

## Connects To

- Chapter on Auth (JWTs, claims, custom tokens used in RLS policies).
- Chapter on Database / Postgres RLS (policies, publications, replica identity).
- Self-hosting Realtime (replication slots, connection pools, partition cleanup).
