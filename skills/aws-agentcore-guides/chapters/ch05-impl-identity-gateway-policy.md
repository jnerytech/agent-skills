# Chapter 5: Amazon Bedrock AgentCore Implementation Guide Part 2: Multi-Layer Security with Identity, Gateway, and Policy

## Core Idea
Agents bring three threats that classic web apps don't: token leakage via LLM output, privilege escalation via prompt injection, and impersonation via a client-supplied `userId`. Counter them with defense in depth. Identity (authentication plus Token Vault) hides tokens from the LLM. Gateway (MCP) controls tool exposure. Policy (Cedar) controls who may use which tool.

## Frameworks Introduced
- **Three-layer security architecture**: Authentication (Identity + Cognito, against impersonation and token leakage), Tool Exposure (Gateway, against unauthorized tool invocation), Authorization (Policy/Cedar, against privilege escalation). Each layer works alone, but combine all three in production.
- **Two-layer function structure (token hiding)**: the outer `@tool` function the LLM sees has no `access_token` parameter. It calls an inner `@requires_access_token` function into which Identity injects the token. Assume anything in the context window can appear in output.
- **JWT setup flow, 5 steps**: (1) Cognito User Pool + M2M client; (2) wait for OIDC discovery (up to 10 min); (3) `create_oauth2_credential_provider`; (4) Runtime with `customJWTAuthorizer`; (5) call services via `@requires_access_token`.
- **Cedar's 3 principles**: default deny; `forbid` overrides `permit`; JWT claims are attributes (`principal.getTag("scope")`, with `like` wildcards).
- **Phased rollout**: SigV4 only → add Cognito JWT → Gateway + Cedar in `LOG_ONLY` → analyze false positives → `ENFORCE`.
- **Idempotent setup script**: persist each step's output to `setup_config.json` and skip completed steps on re-run, covering Cognito → Provider → Runtime → Gateway → Policy Engine.

## Key Concepts
- **AgentCore Identity**: an OAuth 2.0 token manager that acquires, caches, and refreshes tokens behind `@requires_access_token`.
- **OAuth2 Credential Provider**: wraps the token acquisition logic (`credentialProviderVendor='CustomOauth2'`, `oauthDiscovery.discoveryUrl`).
- **`auth_flow`**: `"M2M"` for service-to-service. `"USER_FEDERATION"` (3LO) acts on the user's behalf for GitHub, Slack, or Drive, and needs `user_id`. Token Vault stores per-user refresh tokens.
- **`requestHeaderAllowlist: ["Authorization"]`**: a Runtime setting that forwards the JWT to `context.request_headers`. Without it, anti-impersonation fails silently.
- **AgentCore Gateway**: a managed MCP endpoint (`list_tools`/`call_tool`) over Lambda, OpenAPI specs, and other services. Centralizes JWT auth.
- **Triple-underscore naming**: tools are exposed as `TargetName___ToolName`. The Lambda strips the prefix with `split('___')[-1]` and reads the name from `context.client_context.custom['bedrockAgentCoreToolName']`.
- **Cedar entity mapping**: Principal `AgentCore::OAuthUser::"<client_id>"`, Action `AgentCore::Action::"<Target>___<Tool>"`, Resource `AgentCore::Gateway::"<gateway_arn>"`.
- **ENFORCE vs LOG_ONLY**: ENFORCE removes denied tools from `list_tools` entirely, with no 403. LOG_ONLY logs violations and allows the call.
- **NL2Cedar**: an LLM-generated Cedar draft (`policy_client.generate_policy(..., fetch_assets=True)`). Prompt it in English and always have a human review the result.
- **Anti-impersonation**: take the user ID from the JWT `sub` claim, not from the payload. Runtime has already verified the signature, so decode with `verify_signature: False`.

## Mental Models
- Think of the LLM as an untrusted logger: if a secret reaches its context, assume it can be printed.
- Use SigV4 for server-to-server inside AWS, Cognito JWT for browser and mobile, and an API Key provider for external partners.
- Use M2M when the agent acts as itself. Use 3LO (`USER_FEDERATION`) when it acts as the user.
- Think of ENFORCE as invisibility, not refusal. A denied user never learns the tool exists.
- Use one Cognito M2M client per role (manager, developer), each with role scopes, so Cedar can key on scope.
- Write tool descriptions that say both what the tool does and when to use it, because the LLM picks tools from them.

## Anti-patterns
| Anti-pattern | Risk | Fix |
|---|---|---|
| Token in environment variables | Manual rotation, leakage | Token Vault + `@requires_access_token` |
| Token as a `@tool` argument | Visible in LLM context | Two-layer function structure |
| Trusting `userId` in the payload | Impersonation | JWT `sub` claim (payload only as the SigV4 fallback) |
| Trust policy without conditions | Confused deputy | `aws:SourceAccount` + `aws:SourceArn` (both, not just one) |

Also avoid:
- Calling `update_gateway` with only the changed field. Omitted fields reset, so re-send `name`, `roleArn`, `protocolType`, `authorizerType`, and the optional fields (`description`, `policyEngineConfiguration`, `protocolConfiguration`, `interceptorConfigurations`, `kmsKeyArn`, `customTransformConfiguration`, `exceptionLevel`).
- Skipping the OIDC wait.
- Using `MCPClient` outside its `with` block, because the connection closes.
- Going straight to ENFORCE in production.
- Trying to scope `ecr:GetAuthorizationToken`. It requires `"Resource": "*"`.

## Code Examples
```python
@requires_access_token(provider_name=OAUTH_PROVIDER, scopes=[OAUTH_SCOPE],
                       auth_flow="M2M", force_authentication=False)
async def _call_api_with_auth(user_input: str, access_token: str = None) -> str:
    headers = {"Authorization": f"Bearer {access_token}",
               "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": session_id}
    return requests.post(RUNTIME_URL, headers=headers, json={"prompt": user_input}).text

@tool(name="call_remote_agent", description="Query a remote agent")
async def call_remote_agent(user_input: str) -> str:
    return await _call_api_with_auth(user_input)   # LLM never sees the token
```
What it demonstrates: the core token-hiding pattern.

```
permit(principal,
  action == AgentCore::Action::"MyTarget___markdown_to_email",
  resource == AgentCore::Gateway::"arn:aws:bedrock-agentcore:us-west-2:ACCOUNT_ID:gateway/GATEWAY_ID"
) when { principal.hasTag("scope") && principal.getTag("scope") like "*manager*" };
```
What it demonstrates: a scope-based per-tool permit. Pair it with a `forbid ... like "*developer*"` rule for dangerous tools.

```python
create_agent_runtime(..., authorizerConfiguration={"customJWTAuthorizer":
    {"discoveryUrl": discovery_url, "allowedClients": allowed_client_ids}},
    requestHeaderConfiguration={"requestHeaderAllowlist": ["Authorization"]})
# invoke URL: https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{urlencoded_arn}/invocations?qualifier=DEFAULT
```

Gateway target registration: `create_gateway_target(targetConfiguration={"mcp": {"lambda": {"lambdaArn": ..., "toolSchema": {"inlinePayload": [ {name, description, inputSchema} ]}}}}, credentialProviderConfigurations=[{"credentialProviderType": "GATEWAY_IAM_ROLE"}])`. `inlinePayload` takes a Python list, not a JSON string. For OpenAPI, use `{"mcp": {"openapi": {"specUri": "s3://..."}}}`.

## Reference Tables
| Auth method | Header | Config | Best for |
|---|---|---|---|
| SigV4 (IAM) | AWS SigV4 | no `authorizerConfiguration` | Server-to-server, CLI, boto3 |
| Cognito JWT | `Authorization: Bearer` | `customJWTAuthorizer` | Web, mobile |
| API Key | custom | API Key Credential Provider | External partners |

| Token approach | Exposed to LLM? |
|---|---|
| Environment variable | Yes |
| `@tool` argument | Yes |
| Two-layer structure | No |

| Limit | Value |
|---|---|
| OIDC discovery availability | 5–10 min; poll `max_wait=600, interval=30` |
| IAM propagation after Gateway creation | ~15 s (`time.sleep(15)`) |
| Cognito M2M token validity | 3,600 s by default |
| Gateway targets, tools per target, Cedar policies, `allowedClients` | See official quotas (preview → GA, values change) |

Runtime role permissions: `bedrock:InvokeModel*`, ECR pull, logs, X-Ray, `cloudwatch:PutMetricData` (namespace `bedrock-agentcore`), `bedrock-agentcore:GetWorkloadAccessToken*`, `bedrock-agentcore:*CodeInterpreter*`.

## Worked Example
Role-based email tool:
1. `update_resource_server` adds the scopes `invoke`, `manager`, and `developer`.
2. Create Cognito clients `AgentCore-manager` and `AgentCore-developer` (`client_credentials`, scopes `{rs}/invoke {rs}/{role}`), then add them to the Gateway `allowedClients` with a full-field `update_gateway`.
3. Write the Cedar permit for `MyTarget___markdown_to_email` with the scope `like "*manager*"`.
4. `PolicyClient.create_or_get_policy_engine` → `create_or_get_policy` → `GatewayClient.update_gateway_policy_engine(mode="ENFORCE")`.
5. Test: each role fetches a token via a `client_credentials` POST and lists tools through `MCPClient` with pagination. The manager sees `['MyTarget___markdown_to_email', 'MyTarget___format_report']`. The developer sees only `['MyTarget___format_report']` (default deny).

## Key Takeaways
1. Design on the assumption that anything in the LLM context can leak. Hide tokens with the two-layer `@requires_access_token` pattern.
2. Derive user identity from the JWT `sub`, never from the payload, and allowlist the `Authorization` header.
3. Gateway exposes tools as MCP `Target___Tool` with centralized JWT. OpenAPI specs convert automatically.
4. Cedar is default-deny with forbid precedence. ENFORCE hides tools rather than returning 403.
5. Roll out in order: SigV4 → JWT → LOG_ONLY → ENFORCE. Write setup scripts so they can be re-run safely.
6. Every trust policy needs both `aws:SourceAccount` and `aws:SourceArn`.

## Connects To
- ch04 Runtime basics (SigV4, entrypoint, `context`); ch06 CDK for Cognito, IAM roles, and `customJwtAuthorizer` in `CfnRuntime`
- ch07 multi-agent (A2A auth via Identity, Guardrails Shadow Mode); ch11 WAF/prompt injection (complements per-tool authorization)
- ch12 Agent Registry (tool and agent discovery); ch14 enterprise SharePoint ACL (per-user delegated access, akin to 3LO); ch10 ops
