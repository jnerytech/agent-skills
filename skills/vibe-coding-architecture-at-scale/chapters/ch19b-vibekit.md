# Chapter 19b: VibeKit: Sandbox, Redact, Observe

## Core Idea
VibeKit turns Ch 19's three requirements into one command: contain the execution (sandbox), keep secrets out (redaction proxy plus scoped secrets), and record the run (observability). The checklist outranks the tool. If VibeKit disappears, use any wrapper that satisfies the same three, or wire them up yourself. VibeKit makes the wall nearly free to maintain, but it doesn't solve injection, and redaction is probabilistic.

## Frameworks Introduced
- **The Three-Requirement Checklist (Contain / Redact / Record)**: any agent runtime wrapper should provide no ambient secrets, a real sandbox bounding reach, and an audit trail.
  - When to use: when choosing or building an agent execution environment.
  - How: verify each one independently. (1) Can the agent reach anything outside its workspace or network allowlist? (2) Can a secret reach the process, or leave through the completion channel? (3) Can you answer "what did it do, and was any of it suspicious?" after the fact?
- **Three Tiers of Isolation**: pick by cost/security tradeoff.
  - When to use: every `vibekit` invocation.
  - How: **Local** (default): a file-isolated workspace, instant startup, nothing reaches the project tree until `vibekit sync` applies approved changes, and a wrong write can't reach `~/.ssh` or credentials. **Docker** (maximum security): no host filesystem, no host network beyond an allowlist, CPU and memory limits, separate kernel namespace. **None**: an explicitly named *dangerous* mode for when you know you need the full system. A blunt name beats an `--unsafe` flag that invites `--force`.
- **Redaction Proxy (second line of secret defense)**: a proxy between the agent and its API endpoints pattern-matches all HTTP responses against `rules-stable.yml` (200+ definitions) and replaces matches with tokens before they reach the terminal.
  - When to use: always on (it starts automatically, and disabling it is a deliberate setting change). It covers a threat sandboxing doesn't: credential-shaped strings in *output*, hallucinated or pulled from context.
  - How: it covers AWS keys, ARNs and RDS endpoints, OpenAI and Anthropic keys, GitHub PATs, Google service-account credentials, DB connection strings with passwords, emails and card numbers. It complements keeping secrets out of context and doesn't replace it.
- **Declarative Security Envelope (SDK builder)**: express the security configuration explicitly in code with `.withAgent().withSandbox().withSecrets().withGithub().withWorktrees()`.
  - When to use: embedding an agent in a product that must execute code safely.
  - How: `.withSecrets()` declares exactly which credentials the agent receives, so it sees `DATABASE_URL` but not `ANTHROPIC_API_KEY` or `AWS_SECRET_ACCESS_KEY` from the outer environment. Passing a credential without naming it fails at compile time. `.withWorktrees({cleanup: true})` gives each run its own git worktree (the Superpowers model, Ch 12). A failed run leaves its branch for inspection, and a successful one is cleaned up.

## Key Concepts
- **`vibekit sync`**: the explicit step that applies approved sandbox changes to the real project tree.
- **`rules-stable.yml`**: the regex pattern library (with confidence levels) the redaction proxy uses.
- **Scoped credential injection**: the agent gets only named secrets instead of inheriting the process environment.
- **Provider abstraction**: seven sandbox providers behind one interface. Swapping one changes an import and a config object, while agent, secrets, worktree and PR workflow stay the same.
- **Session logs**: structured JSON per agent session (timestamp, level, agent, sessionId, message, metadata), plus an analytics CLI and dashboard (sessions, duration, success rate, files changed, errors, per-agent performance).
- **Proxy traffic observability**: the *shape* of network behavior (endpoints, counts, response codes, redaction stats, SSE monitoring), with contents sanitized before storage.
- **Binary vs probabilistic completeness**: container isolation either blocks the host network or it doesn't. Pattern redaction catches only known shapes.

## Mental Models
- Think of the tool as an example of the requirements. The checklist is the asset, and the CLI is this year's convenience.
- Sandbox = the wall, OpenLeash-style policy = the warrant, Parts II and III deterministic guardrails = the verification layer. VibeKit provides only the wall (plus redaction and logs).
- Use Local isolation by default for speed, and Docker when the agent runs untrusted code or adversarial input (Ch 20). Use None only knowingly.
- Prefer an interface-guaranteed security property (provider abstraction) over each team correctly configuring each provider.

## Anti-patterns
- **Treating redaction as a guarantee**: unusual formats, new key prefixes and base64-wrapped secrets slip past the patterns.
- **Relying on the proxy instead of scoping secrets**: the proxy is a second line. `.withSecrets()` and no ambient credentials come first.
- **Assuming a sandbox stops injection**: an agent in a Docker sandbox can still be injected and make lateral moves within its permission scope.
- **Ambiguous escape hatches** (`--unsafe`): the dangerous mode should be named dangerous.
- **Containment without visibility**: a sandboxed agent that leaves no audit record can't answer the security team's question.

## Code Examples
```typescript
import { VibeKit } from "@vibe-kit/sdk";
import { createE2BProvider } from "@vibe-kit/e2b";

const vibeKit = new VibeKit()
  .withAgent({
    type: "claude", provider: "anthropic",
    apiKey: process.env.ANTHROPIC_API_KEY,
    model: "claude-sonnet-4-20250514",
  })
  .withSandbox(e2bProvider)                 // execution boundary
  .withSecrets({ DATABASE_URL: "…" })       // scoped credential injection
  .withGithub({ token: "…", repository: "owner/repo" })
  .withWorktrees({ cleanup: true });        // isolated branch per run
```
```bash
npm install -g vibekit && vibekit claude
vibekit claude --sandbox docker   # Full container isolation
vibekit claude --sandbox local    # File isolation only (default)
vibekit claude --sandbox none     # No sandbox: the dangerous mode
```
```yaml
patterns:
  - pattern: { name: OpenAI API Key, regex: "sk-[a-zA-Z0-9]{48}", confidence: high }
  - pattern: { name: AWS Access Key ID Value,
      regex: "(A3T[A-Z0-9]|AKIA|AGPA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}", confidence: high }
```
- **What it demonstrates**: the security envelope as explicit, type-checked code, isolation tiers as named CLI flags, and the redaction rules.

## Reference Tables
| Provider | Environment | Characteristic |
|---|---|---|
| E2B | Cloud microVMs | Fast startup, ephemeral, managed (consumer default) |
| Northflank | Kubernetes containers | Persistent workspaces, enterprise scale |
| Daytona | Dev environment platform | Full toolchain, configurable images |
| Cloudflare | Workers + containers | Edge-native, global |
| Dagger | Container pipelines | CI/CD integration, composable |
| Modal | Serverless compute | Autoscaling, GPU-capable |
| Fly.io | Edge compute | Low latency, geographic distribution |

| Aspect | VibeKit |
|---|---|
| Isolation tiers | Local (default), Docker (max), None (dangerous) |
| Redaction | Proxy over all HTTP; 200+ patterns; replaced before terminal |
| SDK | `.withAgent().withSandbox().withSecrets()`: compile-time credential scoping |
| Observability | JSON session logs, analytics CLI/dashboard, proxy traffic shape |
| Limit | Doesn't prevent injection; redaction isn't complete |

## Worked Example
An agent generating an OpenAI integration emits "Configure the client with API key sk-1234567890abcdef…". The proxy matches the `OpenAI API Key` pattern, and what reaches the terminal (and therefore any session log or CI artifact) is "Configure the client with API key [OPENAI_API_KEY_REDACTED]…". Separately, the SDK run only received `DATABASE_URL`, so even an injected instruction to print the environment can't reveal `AWS_SECRET_ACCESS_KEY`. Afterwards, the session logs and proxy traffic stats can answer "how many agent runs touched the payments module in the last 30 days?"

## Why It Works / Failure Mode
- **Isolation tiers** work because the guarantee comes from the environment (separate filesystem or kernel namespace), not from model behavior, and it's binary. The failure mode is choosing `none`, or Local where adversarial execution needs Docker.
- **The redaction proxy** works as a cheap, always-on catch for known secret shapes in the completion channel. It fails on unknown formats, new prefixes and encoded blobs, so it never replaces scoping secrets out of the process.

## Key Takeaways
1. Requirements over tools: contain, redact, record.
2. Default to Local file isolation, use Docker for maximum security, and treat `none` as explicitly dangerous.
3. A redaction proxy is a second line for credential-shaped output, not a substitute for scoped secrets.
4. Declare secrets explicitly (`.withSecrets()`). Never let the agent inherit the environment.
5. One worktree per run keeps main untouched and failed runs inspectable.
6. Observability (session logs plus traffic shape) completes containment.
7. VibeKit is the wall only. You still need authorization policy and deterministic guardrails.

## Connects To
- **Ch 19**: the three requirements, Docker Sandboxes, OpenLeash (the warrant), no ambient secrets.
- **Ch 12**: Superpowers' worktree isolation, available as `.withWorktrees()`.
- **Ch 20**: the Attacker Agent needs maximum isolation.
- **Ch 18b**: sandbox agents that run `npm install`.
- **Parts II–III**: deterministic guardrails as the verification layer.
- **Secret scanning (gitleaks/trufflehog-style patterns)**; **least privilege**; **E2B / Firecracker microVMs**.
