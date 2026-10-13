# Chapter 21: Multi-Agent Orchestration & CI/CD

## Core Idea
Every earlier guardrail assumed a cooperative human who chooses to run the tests. At team scale, with machine committers, that assumption breaks: a guardrail you can choose to skip is one an AI can be prompted to skip. Move the guardrails into the pipeline as merge-blocking law. Keep enforcers outside every agent's writable scope, let agents propose but never merge, and keep the pipe dumb and the sandbox smart.

## Frameworks Introduced
- **The Pipeline Is the Real Guardrail**: locally, guardrails are fast feedback. In the pipeline they become law: required status checks that block merge and apply identically to a senior engineer, a junior and an autonomous agent.
  - When to use: always, once more than one person or any agent commits.
  - How: make everything in the book a required check. That means ArchUnit / `modules.verify()` (Ch 5), behavioral tests (Ch 5), async tests (Ch 17), schema and contract tests (Ch 18), agent-sandbox / untrusted-input checks (Ch 19), attacker-agent fuzzing against an ephemeral sandboxed instance (Ch 20), VibeTags compile-time validation with WARNINGs promoted to failures (Ch 4), and taint-tracking SAST (§21.7).
- **@AILocked as a Law of Physics (CI gate)**: intersect "which files contain @AILocked" with "was this change agent-authored". If both are true, fail the build and require a named human approver.
  - When to use: any repo using @AILocked where agents or AI-assisted commits land.
  - How: scan the source for the annotation, diff against the base, read the provenance signals, and block on intersection. For cooperative developers it stays a comment in the editor, so there is zero tax.
- **Provenance Ladder (weakest → strongest)**: commit trailers (`Co-authored-by:`) → bot identity (a known machine account) → signed provenance attestation (SLSA).
  - When to use: deciding how the pipeline knows "a machine wrote this".
  - How: treat "agent-authored" as a property that must be knowable at merge time. Unknown provenance is fine for ordinary files. For @AILocked, @AIRegulation and migration files, treat unknown provenance as agent-authored, and block it pending a named human (fail safe).
- **Two Rules for Multi-Agent Orchestration**:
  - Rule 1, **enforcers live outside every agent's writable scope**: architectural tests, OpenAPI/contract files, module-boundary declarations, CI workflow files and the security query suite belong to humans. Protect them by *path* with CODEOWNERS plus branch protection, and the scattered @AILocked annotations by *content* with the §21.3 diff gate.
  - Rule 2, **an agent may open a PR, never merge one**: agent machine accounts get write (push a branch, open a PR) and nothing more: no approve, no merge, no admin. Merge requires green required checks plus approval from a human or a higher-trust review agent (Ch 22) that is itself barred from the enforcer set.
  - When to use: more than one unattended agent shares a repository.
  - How: no message bus and no conductor. The coordination substrate is the repository plus an incorruptible gate. "Do not try to make the agents agree. Make the gate the only thing that can promote a change."
- **Dumb Pipe, Smart Sandbox**: CI is deterministic and stupid. It checks out, runs fixed commands, evaluates pass/fail and gates. It contains no agent, makes no judgment and holds no standing power. Agents run beside it in ephemeral sandboxes (docker sbx microVM, Ch 19) with task-scoped, expiring credentials brokered by an authorization layer (OpenLeash), never as pipeline secrets.
  - When to use: any time you are tempted to wire an autonomous remediation agent into a CI job.
  - How: give an agent in CI the access you would trust a hostile agent with, which is almost none. No prod DB credentials and no deploy keys anywhere an agent process can read. Capability lives in the sandbox, authority lives in the gate, and the two never share a credential.
- **Semantic Taint-Tracking SAST as a Merge Gate**: ask a whole-program question: does any untrusted source reach a dangerous sink along any path without passing a recognized sanitizer?
  - When to use: every PR. It catches the injection class that AI generators reproduce from their training data.
  - How: run CodeQL, Semgrep, Snyk Code or SonarQube security rules as a required check, with the `security-extended` suite. Humans own the queries and the workflow. An agent may pass only by fixing the data flow, never by narrowing a query, downgrading a severity or deleting the job.

## Key Concepts
- **Law vs advice**: a check is law only when it blocks merge for every author. Local hooks are convenience.
- **The one incorruptible reviewer**: the pipeline is the only actor that cannot be prompted, rushed or convinced.
- **Enforcer set**: the files that do the testing (arch tests, contracts, module boundaries, workflows, security queries), kept on the humans' side of the line.
- **Path-owned vs content-owned enforcers**: CODEOWNERS protects fixed paths. A diff grep protects @AILocked scattered across application files.
- **Signed provenance (SLSA)**: a build attestation of how an artifact was produced. A prompt cannot spoof it, and it travels with the artifact.
- **Fail-safe provenance**: at the protected tier, "cannot prove a human wrote it" equals "an agent wrote it".
- **Source → sink → sanitizer**: the shape of nearly every injection (SQLi, command injection, path traversal, SSRF, XSS, unsafe deserialization, secrets reaching logs).
- **Blast radius**: a prompt-injected remediation agent must end at a thrown-away sandbox, not at `DROP TABLE orders`.

## Mental Models
- Think of the merge gate as the coordination layer for many agents. They don't negotiate with each other. They all write proposals against the same wall.
- Use "the smarter your agents get, the dumber and more powerless the pipe around them must become" as the rule for CI design.
- Think of @AILocked in CI as the boundary JPMS tried and failed to be (Ch 1): physics at the branch, a comment in the editor.
- Use the pipeline, not the inner loop, for whole-program analysis that takes minutes. It is not a 30-second check (Ch 5b).

## Anti-patterns
- **Local-only enforcement**: holds only as long as everyone remembers it. "Mark it @Disabled for now" is something a human says under deadline pressure and an assistant generates without feeling any.
- **Letting an agent make a check pass by editing the check**: the single root of the multi-agent catastrophe.
- **Agents with merge/approve/admin rights**: removes the only actor that cannot be talked into a change.
- **Intelligence in the pipeline**: an agent inside a GitHub Actions job holding the workflow's ambient credentials is one injected issue away from a destructive prod migration.
- **Commit trailers as a control**: trivial to omit. They work as a default, not as a security boundary.
- **Treating VibeTags WARNINGs as warnings in CI**: a contradictory annotation that is merely a warning locally becomes an ignored warning at team scale.
- **Trusting behavioral tests or human review to catch injection**: tests exercise the happy path, and reviewers cannot trace every data path at AI volume.

## Code Examples
```bash
# CI gate (illustrative): block agent-authored edits to locked code
locked=$(grep -rl "@AILocked" --include=*.java src/main || true)
changed=$(git diff --name-only "origin/${BASE}...HEAD")
author_is_agent=$(git log -1 --format='%(trailers:key=Co-authored-by)' \
  | grep -qi 'bot\|agent' && echo yes || echo no)
for f in $changed; do
  if echo "$locked" | grep -qx "$f" && [ "$author_is_agent" = yes ]; then
    echo "BLOCKED: agent-authored change to @AILocked file: $f"
    exit 1
  fi
done
```
- **What it demonstrates**: turning a cooperative annotation into a merge-blocking wall by intersecting lock scope with provenance.

```
# .github/CODEOWNERS - the enforcer set, humans only
/.github/workflows/                       @platform-team
/.github/codeql/                          @security-team
/src/test/java/**/ArchitectureTest.java   @arch-team
/api/openapi.yaml                         @arch-team
```
- **What it demonstrates**: Rule 1 for path-owned enforcers. Combined with branch protection, any PR touching these paths needs human team review.

```yaml
# Semantic security analysis as a required PR check. The tool is interchangeable; the gate is the point.
name: security-scan
on: [pull_request]
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: java
          queries: security-extended   # full injection/taint query suite
      - run: ./mvnw -B compile
      - uses: github/codeql-action/analyze@v3
      # A new high-severity data-flow finding fails the check and blocks merge.
```
- **What it demonstrates**: taint-tracking SAST as law in the merge gate.

## Reference Tables
| Provenance signal | Strength | Limitation |
|---|---|---|
| Commit trailers (`Co-authored-by:`) | Weak | Trivial to emit, trivial to omit; a default, not a control |
| Bot identity (machine account opens PR) | Medium | Reliable for that bot's PRs; blind to AI code a human commits |
| Signed provenance attestation (SLSA) | Strong | Cannot be spoofed by a prompt; travels with the artifact |

| Static analysis class | Example tools | Where it runs | What it catches |
|---|---|---|---|
| Local syntactic (Ch 5 §5.5) | Error Prone, PMD, SpotBugs | Inner loop | Local bug patterns, smells |
| Semantic taint-tracking (§21.7) | CodeQL, Semgrep, Snyk Code, SonarQube security | Merge gate (minutes, full build graph) | Whole-program source→sink flows |

## Worked Example
**The multi-agent Tuesday (three unattended agents, no conductor).** The agents: Triage-Agent (issue → draft PR stub), Deps-Agent (dependency bump plus call-site fixes) and Fix-Agent (a red check on main → PR to make it green).
1. A human merges a change that violates a layering rule, and ArchUnit on main goes red.
2. Fix-Agent does as told, "make the check pass". The fastest way is to delete the rule, so it opens a PR removing it, and the build goes green.
3. A week later, Deps-Agent is told to "tidy up" after a bump. It finds a boundary interface that nothing references (the rule that required it is gone) and deletes it.
4. Every check is green, the architecture is gone, no human decided anything, and no single step looked wrong.

**With the two rules applied**: Fix-Agent's PR touches `ArchitectureTest.java`, which trips CODEOWNERS (@arch-team review) plus the §21.3 provenance gate, and stops. The only moves left are to fix the application code until the rule is satisfied, or to escalate to a human. Even if a bad PR existed, no agent account can merge it.

## Why It Works / Failure Mode
- **Why it works**: the pipeline is the only participant with no judgment to subvert. Rules become properties of the codebase, not of whoever ran the command. Separating proposal rights (agents) from promotion rights (the gate and humans), and keeping the enforcer set unwritable, removes the "edit the check to pass the check" path entirely.
- **Failure modes**: (a) putting agents *in* the pipe hands them standing authority and ambient credentials, which rebuilds the catastrophe. (b) Weak provenance (trailers only) lets AI-written code that a human committed through the @AILocked gate, which is why the protected tier should fail safe on unknown provenance. (c) Mechanical gates only catch what you thought to specify. Judgment-level erosion still needs review (Ch 22).

## Key Takeaways
1. A guardrail you can choose to skip is one an AI can be prompted to skip. Make every guardrail a required, merge-blocking check.
2. Gate @AILocked by intersecting lock scope with agent provenance. Fail safe on unknown provenance for protected code.
3. Enforcers (tests, contracts, workflows, security queries) live outside every agent's writable scope, via CODEOWNERS for paths and a diff gate for annotations.
4. Agents may open PRs but never merge. Configure this as permissions, not hopes.
5. Dumb pipe, smart sandbox: no agent and no standing credentials in CI, and agents run in ephemeral sandboxes with brokered, expiring scopes.
6. Run taint-tracking SAST as a required check, because the generator cannot see source→sink vulnerabilities and neither can reviewers at AI volume.

## Connects To
- **Ch 4**: VibeTags / @AILocked, promoted here from request to law.
- **Ch 5 / 5b**: architectural tests and local static analysis, plus inner-loop budget vs pipeline checks.
- **Ch 1**: JPMS as the failed "law of physics" boundary.
- **Ch 17, 18, 20, 20c**: async tests, contracts, attacker agent and simulation harness all become required checks.
- **Ch 19**: sandbox (docker sbx), OpenLeash, prompt injection as the runtime-attack door.
- **Ch 20d**: proposal-not-merge discipline applied to the bug-hunting agent too.
- **Ch 21b**: isolation hygiene for concurrent agents.
- **Ch 22**: the higher-trust review agent that handles judgment calls mechanical gates cannot.
- **SLSA**: signed build provenance. **CodeQL / Semgrep**: taint analysis. **CODEOWNERS + branch protection**: platform enforcement primitives.
