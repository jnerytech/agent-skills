# Chapter 6: Amazon Bedrock AgentCore Implementation Guide Part 3: Building a 4-Stack CDK Architecture with an Observability Pipeline

## Core Idea
Production AgentCore needs four things CLI deploys lack: reproducibility, ordered dependencies (the ECR image must exist before the Runtime), automated config injection (Memory, Guardrail, and Model IDs), and observability. Split the CDK app into 4 stacks by change frequency. Wire the three Vended Log types to CloudWatch, Firehose→DynamoDB, and X-Ray.

## Frameworks Introduced
- **4-stack architecture**:
  - **Foundation**: Cognito, DynamoDB usage table, IAM execution role. Rarely changes.
  - **Bedrock**: Guardrails, Memory.
  - **Agent**: ECR, CodeBuild, Lambda Waiter, Runtime, plus all observability resources, because they depend on the Runtime ARN. Changes most often.
  - **ChatApp**: the frontend.
  - Pass values with `CfnOutput` + `Fn.importValue`. A full `cdk deploy --all` takes ~11 min (Agent stack ~485 s).
- **Lambda Waiter pattern**: CDK doesn't wait for CodeBuild, so split trigger from wait.
  - (1) An `AwsCustomResource` calls `CodeBuild:startBuild` on both `onCreate` and `onUpdate`, with `physicalResourceId` taken from `build.id`.
  - (2) A Python Lambda, called through `cr.Provider`, polls `batch_get_builds` every 30 s up to 28 times, with a 14-min timeout.
  - (3) `runtime.node.addDependency(buildWaiter)`.
  - A `Timestamp: Date.now()` property forces a rebuild on each deploy.
- **Vended Logs triad**: each log type needs `CfnDeliverySource` (resource ARN + `logType`), `CfnDeliveryDestination` (type `CWL` | `XRAY` | `FH`), and `CfnDelivery` (the link). Missing any one means nothing is delivered.
- **Three-mode evaluation (LLM-as-a-Judge)**: Local (dev feedback), On-demand (Evaluate API as a CI/CD gate; use `convert_strands_to_adot`), Online (samples live Runtime traffic and scores it into CloudWatch).
- **Frontend pattern choice**: Lambda Web Adapter → ECS Express → Fargate+ALB, scaling with traffic and consistency needs.

## Key Concepts
- **L1 vs L2**: L1 `aws-cdk-lib/aws-bedrockagentcore` (`CfnRuntime`, `CfnMemory`) gives full property control and is recommended for production. L2 `@aws-cdk/aws-bedrock-agentcore-alpha` (`agentcore.Runtime`, `AgentRuntimeArtifact.fromAsset()`) auto-builds ECR and CodeBuild and suits prototypes. Memory and Gateway may be L1-only.
- **ARM64 build**: use `codebuild.LinuxArmBuildImage.AMAZON_LINUX_2_STANDARD_3_0`, `privileged: true`, and `docker build --platform linux/arm64`. An x86 image crashes on the Runtime.
- **`eventExpiryDuration`**: CDK L1 takes seconds (`604800` = 7 days). The Python SDK takes days (`7`).
- **`memoryExecutionRoleArn`**: a separate role the Memory service uses to call Bedrock for extraction.
- **Log types**: APPLICATION_LOGS (print/logging → CloudWatch Logs), USAGE_LOGS (vCPU-hours and memory GB-hours, not tokens → Firehose), TRACES (→ X-Ray). Memory resources can also emit APPLICATION_LOGS and TRACES.
- **`/aws/vendedlogs/` prefix**: required on Vended Logs log group names, or the deploy fails.
- **ADOT auto-instrumentation**: put `aws-opentelemetry-distro` in requirements and use `CMD ["opentelemetry-instrument", "python", "-m", "my_agent"]`. Runtime injects `OTEL_EXPORTER_OTLP_ENDPOINT`.
- **Session → Trace → Span**: the observability hierarchy. `trace_attributes` (`user.id`, `session.id`, `deployment.environment`) tag every span.
- **X-Ray Transaction Search**: session-level trace search.
  - Requires a `CfnResourcePolicy` letting `xray.amazonaws.com` call `logs:PutLogEvents` on `aws/spans:*` and `/aws/application-signals/data:*`.
  - Also requires a Custom Resource calling `update_trace_segment_destination(Destination='CloudWatchLogs')` and `update_indexing_rule(Name='Default', Probabilistic 100%)`.
  - New accounts also need `application-signals:StartDiscovery` and `iam:CreateServiceLinkedRole`.

## Mental Models
- Split stacks by change frequency: agent code deploys shouldn't touch auth or data.
- Think of USAGE_LOGS as your compute bill per session. Token cost lives elsewhere.
- Use `RemovalPolicy.DESTROY` in dev for clean `cdk destroy`, and consider `RETAIN` in production.
- Agents are non-deterministic: the same input can take different tool paths. Without traces you cannot answer "why this response".
- Sample online evaluation at 100% in dev and 10–30% in production.

## Anti-patterns
- Building on x86 CodeBuild.
- Creating the Runtime without a waiter dependency, so no image exists in ECR yet.
- Setting the Lambda waiter timeout to 15 min (the max). Use 14.
- Mixing up seconds and days in `eventExpiryDuration`. Events then expire instantly or live far too long.
- Defining only a source and destination without `CfnDelivery`.
- Trying to fan one `CfnDeliverySource` out to two destinations. Create multiple sources instead.
- Expecting Transaction Search to be on by default. Enable it explicitly via a Custom Resource.
- Using CloudFront → Lambda Function URL with AWS_IAM but no `PayloadSigner` Lambda@Edge (SHA256 signing). You get signature mismatches.
- Using Lambda Layers with container-image Lambdas. Copy the Web Adapter into the image instead.
- Scoping `ecr:GetAuthorizationToken`. It needs `*`.

## Code Examples
```typescript
const runtime = new bedrockagentcore.CfnRuntime(this, 'AgentRuntime', {
  agentRuntimeName: 'my-agent',
  roleArn: executionRole.roleArn,
  networkConfiguration: { networkMode: 'PUBLIC' },
  protocolConfiguration: 'HTTP',
  agentRuntimeArtifact: { containerConfiguration: { containerUri: `${ecrRepo.repositoryUri}:latest` } },
  environmentVariables: {
    BEDROCK_AGENTCORE_MEMORY_ID: memory.attrMemoryId,
    GUARDRAIL_ID: guardrail.attrGuardrailId,
    GUARDRAIL_VERSION: guardrailVersion.attrVersion,
    MODEL_ID: 'us.anthropic.claude-sonnet-4-20250514-v1:0',
  },
  authorizerConfiguration: { customJwtAuthorizer: { discoveryUrl, allowedClients: [userPoolClient.userPoolClientId] } },
});
runtime.node.addDependency(buildWaiter);
```
What it demonstrates: automated config injection from other stacks' resources, plus explicit build ordering.

```typescript
const src = new logs.CfnDeliverySource(this, 'UsageLogSource',
  { name: `${runtimeId}-usage-logs-source`, resourceArn: runtime.attrAgentRuntimeArn, logType: 'USAGE_LOGS' });
const dst = new logs.CfnDeliveryDestination(this, 'UsageLogDestination',
  { name: `${runtimeId}-usage-firehose-destination`, deliveryDestinationType: 'FH', destinationResourceArn: usageFirehose.attrArn });
const d = new logs.CfnDelivery(this, 'UsageLogDelivery',
  { deliverySourceName: src.name, deliveryDestinationArn: dst.attrArn });
d.addDependency(src); d.addDependency(dst);
```
What it demonstrates: the source/destination/delivery triad. For APPLICATION_LOGS use `'CWL'` + log group ARN. For TRACES use `'XRAY'` with no destination ARN.

Firehose settings:
- `deliveryStreamType: 'DirectPut'`, GZIP, buffer 60 s / 1 MB.
- Hive prefix `usage-logs/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/`, which makes Athena queries cheap.
- Lambda processor; call `transformFn.grantInvoke(firehoseRole)` manually, since L1 doesn't auto-grant it.

## Reference Tables
| Log type | Content | Destination | Use |
|---|---|---|---|
| APPLICATION_LOGS | print/logging | CloudWatch Logs (`CWL`) | Debugging |
| USAGE_LOGS | vCPU, memory, session | Firehose (`FH`) → DynamoDB + S3 | Cost |
| TRACES | X-Ray spans | X-Ray (`XRAY`) | Performance |

| Frontend pattern | ~Monthly cost | Scaling | Choose when |
|---|---|---|---|
| A: ECS Express | ~$46 | Auto | Consistent latency, no cold start, no VPC |
| B: Lambda Web Adapter | ~$12 | To zero | "Just get it running"; use `RESPONSE_STREAM` for SSE |
| C: Fargate + ALB | ~$80+ | High (min 2 / max 10, CPU 70%) | Enterprise production, HA |
| D: API Gateway + Lambda | Pay-per-use | High | An API Gateway already exists, or REST/WebSocket |

| Limit | Value |
|---|---|
| Lambda max timeout | 900 s (waiter set to 14 min) |
| CodeBuild max | 480 min; AgentCore builds take 3–10 min (5–15 worst case) |
| Firehose buffering | 60–900 s; 1–128 MB |
| X-Ray `DesiredSamplingPercentage` | 0–100 (100 recommended; watch cost) |
| ECR `maxImageCount` | 3–5 dev, 10–20 prod (sample uses 5) |
| CloudFormation stacks/Region | 2,000 |

## Worked Example
The Usage cost pipeline:
1. The Foundation stack creates the DynamoDB table `agentcore-usage` (PK `session_id` STRING, SK `timestamp` NUMBER, `PAY_PER_REQUEST`).
2. The Agent stack wires USAGE_LOGS → Firehose `agentcore-usage-stream`.
3. The transform Lambda base64-decodes each record. It normalizes `event_timestamp` to ms (`if ts < 1e10: ts*1000`). It writes `vcpu_hours` from `agent.runtime.vcpu.hours.used` and `memory_gb_hours` from `agent.runtime.memory.gb_hours.used` as `Decimal`, along with `time_elapsed_seconds`, `agent_name`, and `region`.
4. The Lambda returns `result: 'Ok'` for each record so the raw data also lands in S3, partitioned Hive-style.
5. Querying by session (e.g., `user123_20260322T120000_chat`) returns that session's compute cost, e.g., 0.0125 vCPU-h and 0.025 GB-h over 45 s.

## Key Takeaways
1. Use 4 stacks split by change frequency: Foundation / Bedrock / Agent / ChatApp. Keep observability in the Agent stack.
2. Use L1 `CfnRuntime` for production control and L2 alpha for fast prototypes.
3. Build ARM64 images, and gate Runtime creation on the Lambda Waiter (30 s × 28, 14-min timeout).
4. Every Vended Log type needs Source + Destination + Delivery, with log groups under `/aws/vendedlogs/`.
5. USAGE_LOGS measure compute, not tokens. Route them through Firehose to DynamoDB (per session) and S3 (Hive partitions).
6. Transaction Search must be enabled explicitly (resource policy plus Custom Resource). Tag spans via `trace_attributes`.
7. Pick the frontend by cost and latency: ~$12 LWA, ~$46 ECS Express, ~$80+ Fargate+ALB.

## Connects To
- ch04 Runtime/Memory (entrypoint, ARM64, `/ping` 8080, days vs seconds expiry); ch05 IAM, confused deputy, Cognito/JWT design implemented here
- ch07 multi-agent (Guardrails Shadow Mode, LangGraph); ch08 Harness export-to-code
- ch10 production ops/cost/DR (usage logs, retention, RETAIN policies, evaluation sampling); ch15 cloud selection/cost/ops
