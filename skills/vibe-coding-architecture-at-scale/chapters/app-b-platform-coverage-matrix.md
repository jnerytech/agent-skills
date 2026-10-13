# Appendix B: Platform Coverage Matrix

## Core Idea
The guardrails were developed in Java/Spring Boot, where the enforcement tooling is most mature. This appendix maps each discipline to its equivalent in TypeScript/Node, Python, and Go, gives a non-Java fastest-path starting order, and lists every tool named in the book with its chapter. Every tool is one implementation of a durable pattern (§11.8): when a name rots, the pattern holds.

## Frameworks Introduced
- **Coverage Key**: ✅ native tool or library (install and configure); 🔧 general-purpose tool (requires configuration); ✍ manual pattern (no dedicated library, implement by convention); ❌ no equivalent currently available.
  - When to use: porting a guardrail to a non-Java stack; estimating adoption effort per ecosystem.
  - How: find the discipline row, read your language column, and budget effort by the symbol (✅ < 🔧 < ✍).
- **Choosing Your Starting Point (non-Java fast path)**: a four-step priority order per ecosystem (see table). If you implement only one thing from the book, make it the **adversarial reviewer (Inquisitor) in CI**: it is ecosystem-agnostic and has the highest ROI of any single addition.

## Key Concepts
- **LLM-agnostic Inquisitor**: the same system prompt and CI integration works in every ecosystem; only the rule-extraction mechanism differs by language.
- **Infrastructure-level controls**: sandboxing and authorization (Ch 19: Docker Sandboxes, OpenLeash) wrap the agent runtime regardless of codebase language.
- **Go's built-in advantages**: unexported (lowercase) identifiers give package-private by default; `go test -race` is a built-in race detector.
- **Node concurrency caveat**: single-threaded, so race detection is less relevant; async safety is a manual `async/await` + `Promise.all` discipline.
- **Pattern over tool**: a tool name is one implementation of a durable pattern.

## Mental Models
- Think of Java as **the reference implementation**; other stacks reach the same pattern with more 🔧/✍ effort.
- Use **ecosystem-agnostic rows** (Inquisitor, git trailers, sandboxes, OpenLeash, SLSA, save-state commits) as the first wins on any stack.
- Think of the tool inventory as **an index from name to chapter to pattern**.

## Reference Tables
**Architectural boundary enforcement**

| Discipline | Java/Spring | TS/Node | Python | Go |
|---|---|---|---|---|
| Dependency rules | ArchUnit | dependency-cruiser ✅ | import-linter ✅ | go-module-graph + custom script 🔧 |
| Layer enforcement | Spring Modulith ✅ | eslint-plugin-boundaries ✅ | import-linter ✅ | module path convention + staticcheck 🔧 |
| Package-private default | Java default visibility | ES module export control ✍ | `__all__` convention ✍ | unexported identifiers (lowercase) ✅ |
| Living architecture diagram | Spring Modulith Documenter ✅ | dependency-cruiser → Graphviz ✅ | pydeps ✅ | go mod graph → Graphviz 🔧 |

**Source annotations / intent markers**

| Discipline | Java/Spring | TS/Node | Python | Go |
|---|---|---|---|---|
| AI guardrail annotations | VibeTags (`@AILocked`, `@AIContract`) ✅ | JSDoc tags + ESLint custom rule 🔧 | decorator + pylint plugin 🔧 | `//nolint`-style comment convention ✍ |
| Generated config from annotations | VibeTags annotation processor ✅ | custom codegen script 🔧 | custom codegen script 🔧 | go generate + template 🔧 |
| Frozen signature enforcement | `@AIContract` + VibeTags ✅ | TS `readonly` + contract test ✅ | Protocol class + test ✅ | interface + compilation check ✅ |

**Concurrency testing**

| Discipline | Java/Spring | TS/Node | Python | Go |
|---|---|---|---|---|
| Forced-collision testing | async-test-lib ✅ | jest-circus + manual barriers 🔧 | threading.Barrier + pytest 🔧 | sync.WaitGroup + `go test -race` ✅ |
| Race condition detection | async-test-lib detectors ✅ | single-threaded (less relevant) | threading sanitiser 🔧 | `go test -race` (built-in) ✅ |
| Virtual thread / async safety | Virtual Threads + Structured Concurrency ✅ | async/await + Promise.all patterns ✍ | asyncio + pytest-asyncio ✅ | goroutines + go vet ✅ |

**Schema and API contract enforcement**

| Discipline | Java/Spring | TS/Node | Python | Go |
|---|---|---|---|---|
| Expand-contract migrations | Flyway / Liquibase ✅ | node-pg-migrate / knex 🔧 | Alembic ✅ | golang-migrate ✅ |
| OpenAPI contract tests | Spring Contract / Pact ✅ | Pact JS ✅ | schemathesis / Pact Python ✅ | go-pact / kin-openapi 🔧 |
| Breaking-change detection | openapi-diff in CI ✅ | openapi-diff ✅ | openapi-diff ✅ | oasdiff ✅ |
| Consumer-driven contracts | Pact JVM ✅ | Pact JS ✅ | Pact Python ✅ | go-pact 🔧 |

**Adversarial review (the Inquisitor)**

| Discipline | Java/Spring | TS/Node | Python | Go |
|---|---|---|---|---|
| CI-integrated AI reviewer | GitHub Actions + LLM API ✅ | same ✅ | same ✅ | same ✅ |
| Source-resident rule export | VibeTags XML export ✅ | JSDoc extraction script 🔧 | AST annotation extraction 🔧 | go doc comment extraction 🔧 |
| Structured gripe format | Inquisitor system prompt ✅ | same ✅ | same ✅ | same ✅ |

**Agent provenance and Git discipline**

| Discipline | Java/Spring | TS/Node | Python | Go |
|---|---|---|---|---|
| Agent commit trailers | Git trailer convention ✅ | same ✅ | same ✅ | same ✅ |
| SLSA attestation | slsa-github-generator ✅ | same ✅ | same ✅ | same ✅ |
| `@AILocked` CI enforcement | VibeTags + GitHub Action ✅ | custom diff + grep check 🔧 | custom diff + grep check 🔧 | custom diff + grep check 🔧 |
| Save-state micro-commits | Git aliases ✅ | same ✅ | same ✅ | same ✅ |

**Prompt injection and sandboxing** (infrastructure-level, language-independent)

| Discipline | Java/Spring | TS/Node | Python | Go |
|---|---|---|---|---|
| Agent sandboxing | Docker Sandboxes (`docker sbx`) ✅ | same ✅ | same ✅ | same ✅ |
| Authorization sidecar | OpenLeash ✅ | same ✅ | same ✅ | same ✅ |
| Input sanitisation | OWASP Java HTML Sanitizer ✅ | DOMPurify / sanitize-html ✅ | bleach ✅ | bluemonday ✅ |

**Choosing your starting point (non-Java)**

| Priority | TypeScript/Node | Python | Go |
|---|---|---|---|
| 1 (Day 1) | dependency-cruiser + eslint-plugin-boundaries | import-linter | `go test -race` + lowercase-private discipline |
| 2 (Week 1) | Pact JS contract tests | Alembic + schemathesis | golang-migrate + oasdiff |
| 3 (Month 1) | GitHub Actions Inquisitor + LLM API | same | same |
| 4 (Month 2) | Docker Sandboxes for agent runs | same | same |

**Complete tool inventory (tool → chapter → what it is)**

| Tool | Ch | What it is |
|---|---|---|
| CLAUDE.md / .cursorrules / AGENTS.md / .github/copilot-instructions.md | 3, 4 | Per-tool standing-instruction files (context-diet tiers) |
| .aiignore / .claudeignore / .cursorignore / .aiexclude | 3b, 4 | Exclude paths from AI context |
| lat.md | 3b | Plain-text context graph; diagnostic nodes an agent resolves errors against |
| lean-ctx | 3c | Token-economy runtime: compressed reads, cached re-reads, shell-output compression (MCP + hook) |
| CodeGraph | 3c | Pre-built code knowledge graph (symbols, call paths, blast radius) behind one MCP tool; index-ahead vs. compress-on-read |
| context-compression skill | 3c | Anchored iterative summarization preserving file paths |
| MCP Memory server (`@modelcontextprotocol/server-memory`) | 3e | Local knowledge-graph agent memory (JSONL) |
| agentmemory | 3e | Hook-captured session memory; hybrid BM25 + vector + graph retrieval |
| Claude Code hooks / skills / subagents | 3d | Harness config surface; the hook is the only enforcing slot |
| VibeTags | 4 | Compile-time AI-guardrail annotations; Java-specific, hand-authorable (§4.8) |
| ArchUnit | 5 | Dependency/layer rules as failing tests |
| Spring Modulith | 5, 6 | `modules.verify()` boundaries; `Documenter` living diagrams |
| Error Prone / PMD / Checkstyle / SpotBugs / NullAway | 5 | Inner-loop static analysis |
| Codecov | 5b | Patch coverage on the diff |
| PlantUML / Mermaid / jQAssistant / C4 | 6 | Text- or AST-sourced living diagrams |
| CodeKarta | 8b | Generates structure diagrams from code |
| OpenAPI / AsyncAPI / JSON Schema / Gherkin | 7 | Spec and contract formats (repo as constitution) |
| Spec Kit (`specify-cli`) | 7, 8 | Constitution → specify → plan → tasks → implement, each human-gated |
| Kiro (with EARS) | 9 | Spec-native agentic IDE |
| Zenflow | 10 | Spec as a schema-validated executable DAG |
| Get-Shit-Done (GSD) | 11 | Context-engineering runtime; persisted state files |
| Superpowers | 12 | Cross-platform workflow plugin |
| Vibe Coding Prompt Template / Playbook | 13, 14 | Pre-build prompt scaffold and execution mechanics |
| Vibe Kanban | 15 | Parallel-agent kanban with workspace isolation |
| Skill Forge | 16 | Evidence-cited skill generator from your codebase |
| Matt Pocock's skills (`/grill-me`) | 16 | Small universal process skills |
| ralph-wiggum / loop engineering (`/goal`) | 16 | Autonomous loop: success predicate, stop conditions, contained blast radius |
| async-test-lib | 17 | Forced-collision concurrency testing for JUnit 5 |
| Java Virtual Threads / Structured Concurrency | 17 | Runtime concurrency model under test |
| QuickPerf / JMH / k6 / Gatling | 17b | Operation-count assertions and load benchmarks |
| Pact / Spring Cloud Contract | 18 | Consumer-driven contract tests |
| Flyway / Liquibase | 18 | Expand-contract migrations |
| openapi-diff / oasdiff | 18 | API breaking-change detection |
| Nexus / Artifactory proxy; lockfile + CVE/license CI gate | 18b | Supply-chain gating |
| Docker Sandboxes (`docker sbx`) | 19 | Ephemeral microVM for autonomous runs |
| OpenLeash | 19 | Authorization sidecar with scoped, expiring credentials |
| OWASP sanitizers (Java HTML Sanitizer / DOMPurify / bleach / bluemonday) | 19 | Untrusted-input sanitization |
| VibeKit | 19b | Sandbox + execution-layer observability + cryptographic trail |
| attacker agent / simulation harness | 20, 20c | Adversarial fuzzing of own contracts, and a tested simulation of it |
| CodeQL / Semgrep / Snyk Code / SonarQube | 21 | Taint-tracking SAST as merge gate |
| GitHub Actions / CODEOWNERS / branch protection | 21 | Deterministic CI law; enforcers outside agents' writable scope |
| SLSA | 21 | Signed build-provenance attestation |
| git worktrees | 21b | Filesystem isolation for parallel agents |
| the Inquisitor | 22 | Adversarial AI reviewer citing source-resident rules |
| prompt lineage (`prompts/`) / model routing / FrugalGPT | 23, 23b | Versioned prompts, pinned roster, verifier-in-the-loop cascade |
| Git (`reset --hard`, micro-commits) | 24 | Save-state engine |

## Worked Example
*Illustrative application of the starting-point table:* **a Python team wanting the fastest meaningful stack.** Day 1: add import-linter contracts for layer and dependency rules (✅ native, equivalent to ArchUnit + Spring Modulith), and use pydeps for the living diagram. Week 1: Alembic for expand-contract migrations plus schemathesis for OpenAPI contract tests (and openapi-diff for breaking changes). Month 1: the GitHub Actions Inquisitor with an LLM API, reusing the same system prompt as Java teams and only swapping rule export to AST annotation extraction (🔧). Month 2: Docker Sandboxes and OpenLeash for autonomous runs, unchanged from Java. Annotations become a decorator + pylint plugin (🔧) or hand-written rules in CLAUDE.md (§4.8).

## Key Takeaways
1. Every discipline has a non-Java path; only effort (✅/🔧/✍) differs.
2. The Inquisitor, git trailers, SLSA, save-state commits, sandboxes, and OpenLeash are ecosystem-agnostic.
3. Go gets package-private and race detection nearly free; Node relies on manual export control and async discipline.
4. Fast path for non-Java: boundary tool → contracts and migrations → Inquisitor → sandboxes.
5. If you implement only one thing, make it the adversarial reviewer in CI.
6. Treat tool names as replaceable; the pattern in each chapter is what lasts (§11.8).

## Connects To
- **Ch 4 / §4.8**: VibeTags and the hand-authored equivalent off Java.
- **Ch 5 / 6 / 17 / 18 / 19 / 21 / 22 / 24**: source chapters for each matrix section.
- **§11.8**: durable-pattern tool-evaluation checklist.
- **App A**: the scorecard rows these implementations satisfy.
- **Ch 25**: roadmap phases mirrored by the starting-point priorities.
