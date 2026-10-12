# Appendix A: Setting up a Kafka test environment

## Core Idea
A thin, hands-on guide: run a **three-broker KRaft cluster in dual mode** (each node is broker + controller) on one laptop so you can watch Kafka survive partial failures. Test-only — never production. Tested with Kafka 3.9.0 on macOS 15.2 and Ubuntu 24.04; use WSL on Windows.

## Frameworks Introduced
- **Local 3-node dual-mode cluster**: brokers on 9092/9093/9094, controllers on 9192/9193/9194, all three in `controller.quorum.voters`.
  - How: download → configure 3 property files → create data dirs + cluster ID → `kafka-storage.sh format` each → start in foreground to check errors → restart as `-daemon` → verify with `kafka-broker-api-versions.sh`.
  - Why: multi-node (unlike most blog setups) lets you kill a broker and observe failover.

## Key Concepts
- **Dual mode**: `process.roles=broker,controller` — one process acts as both.
- **Cluster ID**: random UUID baked into each formatted data dir so a directory can't be reused by another cluster.
- **`kafka_2.13-3.9.0.tgz`**: 2.13 = Scala version, 3.9.0 = Kafka version; prefer the latest Scala build.

## Code Examples
```bash
wget "https://downloads.apache.org/kafka/3.9.0/kafka_2.13-3.9.0.tgz"
tar xfz kafka_2.13-3.9.0.tgz && rm kafka_2.13-3.9.0.tgz
mv kafka_2.13-3.9.0/ ~/kafka
export PATH=~/kafka/bin:"$PATH"      # add to ~/.bashrc / ~/.zshrc
```

`~/kafka/config/kafka1.properties` (kafka2/kafka3: `broker.id=2|3`, `kafka2|kafka3` dir, ports `9093,9193` / `9094,9194`):
```properties
broker.id=1
log.dirs=<PATH-TO-YOUR-USER-DIRECTORY>/kafka/data/kafka1
listeners=PLAINTEXT://:9092,CONTROLLER://:9192
process.roles=broker,controller
controller.quorum.voters=1@localhost:9192,2@localhost:9193,3@localhost:9194
controller.listener.names=CONTROLLER
listener.security.protocol.map=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
```
(No TLS in the test environment; listener names are arbitrary.)

```bash
mkdir -p ~/kafka/data/kafka1 ~/kafka/data/kafka2 ~/kafka/data/kafka3
export KAFKA_CLUSTER_ID="$(kafka-storage.sh random-uuid)"
kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c ~/kafka/config/kafka1.properties
# ... repeat for kafka2/kafka3 -> "Formatting metadata directory ... with metadata.version 3.9-IV0."

kafka-server-start.sh ~/kafka/config/kafka1.properties          # foreground first
kafka-server-start.sh -daemon ~/kafka/config/kafka1.properties  # then background
kafka-broker-api-versions.sh \
  --bootstrap-server localhost:9092,localhost:9093,localhost:9094   # lists online brokers
kafka-server-stop.sh                                             # stops ALL brokers
```

Stop a single broker — `~/kafka/bin/kafka-broker-stop.sh` (then `chmod +x`, run `kafka-broker-stop.sh 1`):
```bash
#!/bin/bash
BROKER_ID="$1"
if [ -z "$BROKER_ID" ]; then
   echo "usage ./kafka-broker-stop.sh [BROKER-ID]"
   exit 1
fi
PIDS=$(ps ax | grep -i 'kafka\.Kafka' | grep java \
    | grep "kafka${BROKER_ID}.properties" | grep -v grep | awk '{print $1}')
if [ -z "$PIDS" ]; then
   echo "No kafka server to stop"
   exit 1
else
   kill -s TERM $PIDS
fi
```
- **What it demonstrates**: full lifecycle of a local KRaft cluster plus targeted failure injection.

## Reference Tables
| Node | Broker listener | Controller listener | Data dir | JMX exporter (App. B) |
|---|---|---|---|---|
| 1 | 9092 | 9192 | ~/kafka/data/kafka1 | 9101 |
| 2 | 9093 | 9193 | ~/kafka/data/kafka2 | 9102 |
| 3 | 9094 | 9194 | ~/kafka/data/kafka3 | 9103 |

## Worked Example
Start broker 1 alone: it logs `WARN [RaftManager nodeId=1] Connection to node 2 (localhost/127.0.0.1:9193) could not be established` — expected, peers are down (an immediate crash instead means misconfiguration). Start broker 2 → `[KafkaRaftServer nodeId=2] Kafka Server started`; start broker 3 → warnings stop. Run `kafka-broker-stop.sh 1`, then `kafka-broker-api-versions.sh`: `Connection to node -1 (localhost/127.0.0.1:9092) could not be established` while 9093/9094 (ids 2, 3) still answer — broker 1 is gone, the cluster lives on.

## Key Takeaways
1. Format every data dir with the same `KAFKA_CLUSTER_ID` before first start.
2. Start in the foreground first to catch config errors; switch to `-daemon` afterward.
3. Use `kafka-broker-api-versions.sh` as a quick "which brokers are up" check.
4. `kafka-server-stop.sh` kills every broker; use a per-ID script to simulate single-node failure.

## Connects To
- **ch02**: first steps run on this environment.
- **ch07**: KRaft controllers, quorum voters, dual mode vs. dedicated controllers.
- **ch05**: killing a broker to observe replication/failover.
- **ch20**: adds the Prometheus JMX exporter to these three brokers.
