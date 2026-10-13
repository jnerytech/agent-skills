# Chapter 4: Annotation-Driven Design

## Core Idea
Put the guardrail on the element it protects, and generate every platform's config file from it. Hand-edited AI config files sit beside the code, so they rot on rename and fragment across a team; per-element intent expressed as source annotations moves with the code, and a compile-time processor (VibeTags) fans it out to every assistant's native format at zero runtime cost.

## Frameworks Introduced
- **Annotation-Driven Design (one source of intent)**: express per-element AI guardrails as annotations on the source element, and generate all AI platform configs from them at compile time.
  - When to use: element-specific intent (this method's signature is frozen, this field is PII, this class is lock-free) in a team using more than one assistant, or anywhere guardrail files keep drifting from renamed code.
  - How: (1) add the annotations artifact to the compile classpath and the processor to the annotation-processor path only; (2) opt platforms in by creating their empty files (`touch CLAUDE.md .cursorrules AGENTS.md`); (3) annotate only the few high-cost boundaries; (4) `mvn compile` fills the `VIBETAGS-START/END` managed block in each file, leaving hand-written Tier 1 text untouched; (5) read compile warnings for contradictory annotations.
- **The three advantages of source annotations over config files**:
  - **Zero Synchronization Overhead**: annotate once, every platform updated (37 platforms from 44 annotations).
  - **Absolute Locality**: rules live in the class/method they guard; they move, change, or disappear with the code.
  - **Strict Compile-Time Safety**: contradictory annotations raise javac warnings instead of silent agent failures. Plus **zero runtime cost** (`RetentionPolicy.SOURCE`).
- **Granular rules (directory opt-in)**: create a directory (`mkdir .claude/rules`) instead of a file and VibeTags writes one scoped rule file per annotated element, with YAML front-matter naming the paths it applies to; the root file becomes an index.
  - When to use: when the always-loaded block grows big enough to tax the Chapter 3 context budget.
  - How: keep the **safety tier inline** in the root file (@AILocked, @AICore, @AIPrivacy, @AIIgnore, @AIAudit, @AISecure) because the agent must read them before deciding what to touch; move the verbose tier (context notes, contracts, performance) into scoped files loaded when a matching source file is opened.
- **Manual first, generator when the loop earns it**: the pattern without the processor, by hand-writing the same XML vocabulary into CLAUDE.md/AGENTS.md plus an adjacent code comment.
  - When to use: non-Java stacks (TypeScript, Python, Go, C#) or teams not ready for build integration.
  - How: name the few elements where violation is expensive, state the reason, keep it short; pair each entry with a comment next to the code; treat every rename touching a guarded element as a guardrail-file change; let PR review stand in for compiler validation.

## Key Concepts
- **Instruction file vs keep-out file**: standing guidance loaded every session vs the AI analogue of .gitignore (paths never read or sent to a model).
- **Keep-out file's two jobs**: it *sharpens* (attention goes to code that matters) and *protects* (a credentials file never read can't be pasted into a completion).
- **Opt-in by file existence**: VibeTags never creates config files; a file's presence is the signal "this team uses that tool."
- **Managed block**: the `VIBETAGS-START/END` section; only it is overwritten on each build.
- **@AIContract**: freeze the public signature (name, param types/order, return type, checked exceptions) while allowing the body to be rewritten; the most valuable annotation for published APIs.
- **Helpfully wrong**: the Ch 2 failure mode where a well-intentioned edit (e.g. double → BigDecimal in a signature) is a deployment incident for downstream consumers.
- **Guardrail on the guardrails**: compile-time contradiction checks over the annotations themselves.
- **Negative-pole annotations**: tags expressing "this is constrained" so an agent doesn't read silence as "unconstrained."
- **RetentionPolicy.SOURCE**: annotations erased at compile time; no runtime dependency leaks into the shipped artifact.

## Mental Models
- Think of an annotation as **a guardrail physically attached to its subject**: a rule in a separate file points at code by name and silently stops applying when the code is renamed.
- Use annotations **where the cost of an AI boundary violation is high and specific**; leave boilerplate unannotated so the AI moves at full speed elsewhere.
- Think of instruction files as **the floor, not the ceiling**: mandatory, but they should point at executable enforcers, not try to be them.
- An annotation set that can only say "this is safe" **teaches the agent to read silence as unconstrained**, and silence is the default state of almost every element.

## Anti-patterns
- **Hand-syncing the same intent across .cursorrules, CLAUDE.md, AGENTS.md, copilot-instructions.md...**: repetitive synchronization work that is never actually done.
- **Annotating everything**: annotation noise is its own context-fatigue problem.
- **Indexed root that keeps nothing inline**: a locked file's guardrail then loads only once the agent opens the file it protects, making the rule a comment on a decision already made (fixed in 1.0.0-RC8).
- **Putting the processor on compileClasspath**: leaks its logging dependencies into your code.
- **Contradictory annotations** (@AIDraft + @AILocked, @AIContract + @AILocked, @AITestDriven + @AIIgnore): incoherent intent a human will eventually write.
- **Using @AILocked on generated code**: "stop" makes the agent give up or route around it; use @AIGenerated to redirect to the real source.

## Code Examples
```java
public class PricingService {
  @AIContract(reason = "Signature locked by OpenAPI v2 contract. "
      + "checkout-service and mobile-app bind to this exact signature.")
  @AIPerformance(constraint = "Must complete in <5ms p99. Called on every cart update.")
  public double calculatePrice(String productId, int quantity, String customerId) {
    return 0.0; // AI may replace this entire body, never the signature
  }
}

@AIThreadSafe(strategy = AIThreadSafe.Strategy.LOCK_FREE,
    note = "Backed by ConcurrentHashMap; do not introduce a synchronized block on the cache map.")
public class SessionCache { /* ... */ }

@AIDraft(instructions = "Implement discount calculation: percentage, fixed, BOGO, tiered.")
@AITestDriven(coverageGoal = 100,
    framework = {AITestDriven.Framework.JUNIT_5, AITestDriven.Framework.ASSERTJ},
    mockPolicy = "Use fixed prices, no external pricing calls in unit tests")
public double calculateDiscount(String orderId, String discountCode) { return 0.0; }
```
- **What it demonstrates**: per-element intent (frozen signature, latency budget, concurrency strategy, test-first draft) written once next to the code it governs.

```xml
<!-- What Claude Code receives from one @AIContract (Cursor gets a Markdown "CONTRACT-FROZEN SIGNATURES" section) -->
<contract_signatures>
  <element path="com.example.PricingService.calculatePrice">
    <reason>Signature locked by OpenAPI v2 contract.</reason>
  </element>
</contract_signatures>
<rule>You may refactor the internal logic of elements listed in <contract_signatures>,
but you MUST NOT change their public signatures.</rule>
```
- **What it demonstrates**: one annotation becomes each platform's best-parsed native format; the same XML can be hand-written in any language's project (`<locked_files>`, `<contract_signatures>`, `<pii_guardrails>`).

```kotlin
dependencies {
  implementation(platform("se.deversity.vibetags:vibetags-bom:1.0.0-RC8"))
  implementation("se.deversity.vibetags:vibetags-annotations")
  annotationProcessor("se.deversity.vibetags:vibetags-processor") // kapt(...) for Kotlin
}
```
- **What it demonstrates**: annotations on compile path, processor on processor path only, both version-aligned through one BOM (Ch 4b's version-skew fix). Maven equivalent uses `<annotationProcessorPaths>`.

## Reference Tables
**AI-file landscape**

| Assistant | Standing-instruction file(s) | Keep-out file |
|---|---|---|
| Claude Code | CLAUDE.md | .claudeignore |
| Cursor | .cursorrules or .cursor/rules/*.mdc | .cursorignore |
| GitHub Copilot | .github/copilot-instructions.md | .copilotignore |
| Gemini | gemini_instructions.md | .aiexclude |
| Codex CLI | AGENTS.md, .codex/config.toml, .codex/rules/*.rules | .codexignore |

**Annotation catalogue by intent**

| Category | Annotations |
|---|---|
| Protection/access | @AILocked(reason), @AIIgnore(reason) |
| Behavioral constraints | @AIContract(reason), @AIPerformance(constraint) |
| Design intent | @AICore(sensitivity, note), @AIThreadSafe(strategy: LOCK_FREE/SYNCHRONIZED/IMMUTABLE/THREAD_LOCAL/OTHER), @AIImmutable, @AIObservability(metrics, traces, logs) |
| Security/compliance | @AIAudit(checkFor), @AIPrivacy(reason), @AIRegulation(standard, clause, description) |
| Workflow | @AIContext(focus, avoids), @AIDraft(instructions), @AITestDriven(coverageGoal, framework, mockPolicy) |
| Lifecycle | @AIDeprecated(replacedBy, migrationGuide, deadline) |
| Mined from 225 OSS CLAUDE.md files (repo count) | @AIKeepInSync (41), @AIGenerated (35), @AILoadBearing (31), @AIBannedApi (27), @AIThreadAffinity (12) |

**Compile-time contradiction warnings (never break the build)**

| Combination | Why |
|---|---|
| @AIDraft + @AILocked | "implement this" vs "never touch" |
| @AIContract + @AILocked | Locked forbids all change; Contract permits internal change |
| @AITestDriven + @AIIgnore | Ignored element is invisible; test rule can't apply |
| @AIImmutable with non-final instance field | Declaration is already a lie |
| @AIObservability with nothing listed | No-op |

**When to reach for an annotation**

| Scenario | Annotation |
|---|---|
| Legacy integration that works and must not change | @AILocked |
| Public API / microservice contract signature | @AIContract |
| Months-stabilized core algorithm | @AICore |
| Deliberately lock-free / thread-safe class | @AIThreadSafe |
| PII or credential field | @AIPrivacy |
| Regulated code (GDPR/PCI/HIPAA) | @AIRegulation |
| Hot path with latency budget | @AIPerformance |
| Logic that changes often and must stay tested | @AITestDriven |
| Boilerplate the AI may safely own | none: let it work |

## Worked Example
Asked to "optimize" `calculatePrice(String, int, String)`, an unconstrained assistant decides BigDecimal is more appropriate than double and changes the signature: clean, well-intentioned, and a deployment incident for checkout-service and the mobile app bound to that shape. With `@AIContract` on the method, every assistant's generated config states the signature is frozen while the body is free; the AI swaps the algorithm and leaves the shape alone. Move the class to another package and the next compile regenerates the path automatically.

Granular-rules result: a five-module reactor went from a 537-line always-loaded block to 137 lines plus 26 scoped files with no guardrail deleted; the destructive-edit gates stayed inline. Before RC8, GEMINI.md embedded every module's rules verbatim and in one project reached 72% of all always-loaded agent context.

## Why It Works / Failure Mode
- **Why**: locality makes drift structurally impossible for the rule's subject (no separate artifact to forget); compile-time generation removes synchronization labor; contradiction checks catch incoherent intent early. The annotations encode domain-specific boundary knowledge that exists nowhere else in the code.
- **Failure mode**: generation only helps while something runs and verifies it (Ch 4b: check mode unwired, processor version skew silently dropping annotations). Generated rules are still advisory to the agent; a hard wall needs a CI action or PreToolUse hook. Writing by hand loses four things: adjacency under refactoring, fan-out to every format, contradiction checks, and any compile step that could detect drift. VibeTags is Java-only; the pattern (decorators, attributes, Go directives) is unfilled in other ecosystems.

## Key Takeaways
1. Element-specific intent belongs on the element; architecture-spanning rules belong in tests (Ch 5).
2. One annotation, generated into every assistant's native format, beats hand-syncing N config files.
3. Opt platforms in by file existence; generated content lives in a managed block beside hand-written Tier 1 invariants.
4. Keep safety-tier rules inline; push verbose per-element rules into scoped, on-demand files.
5. Annotate only high-cost boundaries; silence elsewhere is deliberate freedom.
6. Without the processor, ten disciplined hand-written XML entries capture most of the value; the processor makes entry #200 survive the big rename.

## Connects To
- **Ch 2**: "helpfully wrong" failure mode that @AIContract targets.
- **Ch 3 / 3c**: context diet, Tier 1/2/3; annotations are Tier 3; granular rules pay down the context budget.
- **Ch 3d**: generated rules advise; hooks enforce @AILocked.
- **Ch 3f**: annotations as the placement fix for rules failing persistence.
- **Ch 4b**: the regeneration gap: generated guardrails rot without check mode.
- **Ch 5**: cross-element architectural rules as ArchUnit tests; @AITestDriven bridges to it.
- **Ch 17**: concurrency failures addressed by @AIThreadSafe / @AIThreadAffinity.
- **JSR 175 (Java 5, Bloch)**: annotation mechanism this builds on.
- **Living Documentation (Martraire)**: guardrails derived from code rather than maintained beside it.
