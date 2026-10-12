# Appendix B: Monitoring setup

## Core Idea
A thin, hands-on guide: wire the Appendix A cluster into **Prometheus** (scrape + alert rules) via the **Prometheus JMX Exporter** Java agent, route alerts through **Alertmanager**, and visualize with **Grafana** (Strimzi dashboards). Foundation only, not a full monitoring guide.

## Frameworks Introduced
- **Prometheus pull-based monitoring stack**: Prometheus periodically scrapes HTTP metric endpoints, stores name + labels in a time-series DB, queried/alerted with PromQL; exporters translate non-Prometheus formats (Kafka's JMX) to HTTP; Alertmanager groups, routes, silences and inhibits; Grafana builds multi-source dashboards.
  - How: (1) configure `prometheus.yml` + `rules.yml`; (2) download JMX exporter jar + `kafka-kraft-3_0_0.yml`; (3) restart each broker with `KAFKA_OPTS=-javaagent:...=<port>:<config>`; (4) start Alertmanager on non-conflicting ports; (5) import Grafana dashboards.
  - Failure mode: metric names vary by exporter config and some metrics may be missing; Alertmanager's default ports 9093/9094 collide with brokers 2/3.

## Key Concepts
- **PromQL**: Prometheus query language for queries, aggregation and alert expressions.
- **Alert states**: *Inactive* (expr false), *Pending* (true but `for` not reached), *Firing* (true for ≥ `for`).
- **Prometheus JMX Exporter**: Java agent exposing Kafka's JMX MBeans as Prometheus metrics.
- **Blackbox Exporter**: probes endpoints (TCP to HTTPS) → `probe_success`, plus timing metrics (DNS, TCP connect) for end-to-end availability.
- **Node Exporter**: host CPU, memory, network, filesystem metrics; *Textfile Collector* builds metrics from text files.
- **Inhibit rules**: suppress secondary alerts when a root-cause alert fires (define carefully to avoid hiding real problems).
- **Silences**: temporarily mute notifications, e.g., during maintenance.

## Code Examples
`prometheus.yml`:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
alerting:
  alertmanagers:
    - static_configs:
        - targets: ["localhost:9095"]
rule_files:
  - "rules.yml"
scrape_configs:
  - job_name: "kafka"
    static_configs:
      - targets: ["localhost:9101","localhost:9102","localhost:9103"]
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]
```
`rules.yml` (fires when any Kafka metrics endpoint is down for 1 minute; groups may override the evaluation interval for expensive queries):
```yaml
groups:
  - name: Kafka
    rules:
      - alert: Kafka Metrics Not Reachable
        expr: up{job="kafka"} == 0
        for: 1m
```
JMX exporter as Java agent:
```bash
cd ~/kafka
wget https://github.com/prometheus/jmx_exporter/releases/download/1.1.0/jmx_prometheus_javaagent-1.1.0.jar
wget https://raw.githubusercontent.com/prometheus/jmx_exporter/refs/heads/main/examples/kafka-kraft-3_0_0.yml
kafka-server-stop.sh
export KAFKA_OPTS="-javaagent:$HOME/kafka/jmx_prometheus_javaagent-1.1.0.jar=9101:$HOME/kafka/kafka-kraft-3_0_0.yml"
~/kafka/bin/kafka-server-start.sh -daemon ~/kafka/config/kafka1.properties
# repeat with =9102 for kafka2.properties, =9103 for kafka3.properties
curl localhost:9101        # long list of metrics
./alertmanager --web.listen-address=:9095 --cluster.listen-address=<address>
```
- **What it demonstrates**: end-to-end scrape path broker JMX → exporter HTTP → Prometheus → alert → Alertmanager.

## Reference Tables
| Component | Port |
|---|---|
| Prometheus UI/API | 9090 |
| JMX exporter brokers 1/2/3 | 9101 / 9102 / 9103 |
| Alertmanager (moved from default 9093) | 9095 |
| Kafka brokers (App. A) | 9092 / 9093 / 9094 |

## Worked Example
Stop broker 1 (or its exporter). `up{job="kafka"}` for `localhost:9101` drops to 0 → the alert goes **Pending**; after 1 minute it turns **Firing** and appears in the Alertmanager UI on :9095, where it can be silenced during planned maintenance.

## Key Takeaways
1. Give each broker its own exporter port and list them all as `kafka` job targets.
2. Start with an `up == 0` alert — if you can't scrape, you're blind.
3. Add Blackbox (`probe_success`) and Node Exporter for availability and host metrics.
4. Use inhibit rules so a root-cause outage doesn't bury you in secondary alerts.
5. Adopt Strimzi's Kafka Grafana dashboards, but adapt them and learn them *before* an incident — dashboards are the first stop when diagnosing and the basis for good alerts.

## Connects To
- **ch15**: which Kafka metrics to watch and what to alert on.
- **ch19**: the three-broker environment being instrumented.
- **Prometheus / Grafana / Strimzi**: external tooling ecosystem.
