# Chapter 3: Context Diets

## Core Idea
Most agent failures are context failures, not model failures: the agent was told the wrong things, contradictory things, or the right things that then went stale. A **Context Diet** keeps standing instructions short, sharp, scoped and non-contradictory — organized in three tiers — because pruning context is a correctness strategy (attention degrades in the middle) and a cost strategy (prefix caching), not just a token saving.

## Frameworks Introduced
- **Context Engineering (vs. Prompt Engineering)**: the discipline of constructing the complete, coherent information system around a task — documentation, rules, examples, patterns, validation — rather than wording one ask cleverly.
  - When to use: any multi-step agent work, legacy codebase navigation, or self-validating agent loops.
  - How: when the AI fails, blame the context first — was it missing, stale, or incoherent? Design for four outcomes: reduce failures (give what it needs), consistency (project patterns in scope), complex features (coherent context across steps), self-correction (validation loops close the feedback cycle).
- **The Context Diet**: deliberately keep the AI's standing instructions short, sharp, scoped, non-contradictory. Not *less* information — the right information at the right scope.
  - When to use: whenever a rules file grows or the AI follows rules inconsistently.
  - How: apply **cut, scope, or relocate** — cut anything not load-bearing; scope anything local into a directory-level file; relocate anything element-specific into a source annotation.
- **The Three Tiers of Standing Context**:
  - When to use: structuring `CLAUDE.md`, `.cursorrules`/`.cursor/rules/`, `.windsurfrules`, `.clinerules`, `.github/copilot-instructions.md`.
  - How: **Tier 1 — project-wide invariants** (~10–20 lines, root file): rules true everywhere whose violation makes a change wrong regardless ("Money is always the Money type", "public API signatures frozen unless the prompt says otherwise", "no business logic in controllers"). Past one screen = a wish list, not invariants. **Tier 2 — directory-scoped rules**: glob-scoped rule files loaded only when working in that area (e.g. `payments/`) — the biggest lever against context fatigue because most rules are local. **Tier 3 — per-element intent**: rules on one class/method ("this class is lock-free, no synchronized block") — belongs in source as an annotation (Ch 4).
- **Prefix Determinism (cache-ordered context)**: provider prefix caching (Anthropic, DeepSeek, Google) charges as little as ~10% of input rate at ~80% lower latency for an identical prompt prefix; any changed character invalidates from that point down.
  - When to use: any automated agent loop or script that assembles prompts.
  - How: order the payload static-to-dynamic — static system instructions + Tier 1 at top, static architectural signatures + directory map next, dynamic task prompt + diff + test output as a short suffix at the bottom. Never prepend timestamps, run IDs, hostnames or branch names.
- **What to Keep in the Files by Hand**: the bounded hand-written root file.
  - How: (1) the 10–20 line Tier 1 invariant list; (2) a pointer to where rules are enforced ("boundary rules are ArchUnit tests in `src/test/java/arch/`: run them, do not just read this file"); (3) build and test commands so the AI closes its own loop; (4) a one-line statement of the directory-scoping convention. Everything more specific → a test (Ch 5) or annotation (Ch 4).

## Key Concepts
- **Context fatigue**: the more undifferentiated guidance, the less reliably the model follows any of it; contradictions get averaged "into mush."
- **Context obesity**: a bloated rules file diagnosed behaviorally, not by measurement.
- **Staleness problem**: hand-maintained context is separate from code, so it's never authoritatively in sync; rules point at renamed/moved classes and nobody notices until the AI does the forbidden thing.
- **Per-developer rule drift**: each developer's private `.cursorrules` holds separately rotting copies of the same intent.
- **Attention tax**: every irrelevant token degrades focus on relevant ones; the attention budget is finite inside a "theoretically unlimited" window.
- **Lost in the Middle** (Liu et al., 2023, arXiv 2307.03172): accuracy on a relevant doc at position 10 of 20 ≈ half that at position 1 or 20.
- **Token economy**: context cost paid first in reasoning quality, then latency, then dollars.
- **Cached prefix / dynamic suffix**: heavy static guardrail context (Tier 1, API signatures, VibeTags) on top; changing content at the bottom.

## Mental Models
- "Ruthless context pruning is not a cost optimization. It is a correctness strategy."
- Think of the context window as a token economy, not a trash can.
- Think of every stale rule as an instruction the model may follow instead of the one you meant.
- Use "I've typed this correction again though it's in the rules file" as the trigger to promote the rule to Tier 2 or Tier 3.
- A 4,000-token scoped context outperforms a 100,000-token dump that buries the relevant rule on page five.

## Anti-patterns
- **6,000-word rules files**: middle instructions weakly attended; hidden contradictions (e.g. "prefer composition" on line 40, inheritance-heavy example on line 380).
- **Local rules in the root file**: a payments-only rule dilutes attention for every unrelated prompt.
- **Element-specific rules in prompts or root file**: doesn't scale / absurd placement — use annotations.
- **Hand-maintained "frozen interface" notes in CLAUDE.md**: go stale when the class is renamed, split or moved.
- **Prepending dynamic data (timestamps, log lines) before static context**: destroys caching economics for the whole session.
- **Dumping full file trees, uncompressed test logs and long histories into every call**.

## Code Examples
```text
[Static system instructions + Tier 1 invariants]    <- cached prefix
[Static architectural signatures + directory map]   <- cached
[Dynamic task prompt + diff + test output]          <- short dynamic suffix
```
- **What it demonstrates**: prefix determinism — cacheable static guardrails on top, volatile content last.

## Reference Tables
**Prompt Engineering vs. Context Engineering**

| | Prompt Engineering | Context Engineering |
|---|---|---|
| Focus | Clever wording/phrasing | A complete system of information |
| Scope | How you phrase one task | Docs, rules, examples, patterns, validation |
| Analogy | Handing someone a sticky note | Writing a full screenplay |
| Failure mode | Suboptimal phrasing | Missing context, stale rules, incoherent instructions |

**Symptoms of a bloated context file → remedy**

| Symptom | Meaning |
|---|---|
| Rule followed inconsistently | competing with too many neighbors for attention |
| AI cites a rule that contradicts another | two instructions disagree; it picked one |
| Same correction repeated in prompts | file too long for that rule to land — promote to Tier 2/3 |
| Edits to the rules file have no effect | past the model's effective attention budget |
| Remedy (all cases) | cut, scope, or relocate |

**Context-diet tool ecosystem**

| Category | Tool | What it does |
|---|---|---|
| CLI compressor | sqz (Rust) | intercepts shell output; git status → minimal summary, tests → failures only, source → imports/signatures/call graphs; 60–70% savings |
| Session diagnostics | alexgreensh/token-optimizer | local daemon + dashboard tracking per-turn token spend, sub-agent consumption |
| Codebase packager | yamadashy/repomix | repo → single LLM-optimized file; respects .gitignore; `--compress` (Tree-sitter) keeps declarations |
| Remote packager | gitingest | GitHub URL → clean text + ASCII tree |
| Tiered memory | volcengine/OpenViking | L0/L1/L2 on-demand memory hierarchy for long-running agents |

## Worked Example
**The financial equation (15 devs × 50 agent runs/day, $3.00/M input tokens).**
- Unstructured: 80,000-token average context → 15 × 50 × 80,000 × $3/M ≈ **$180/day**, 30+ s latency per call.
- Vibe Architecture: 4,000-token dynamic payload + 40,000-token cached prefix at 10% (≈ 4,000 effective) → 15 × 50 × 8,000 × $3/M ≈ **$18/day**, sub-5 s responses.
- Result: ~10x cost and ~6x latency improvement from one discipline applied consistently.

**Staleness walk-through**: "PaymentProcessor interface is frozen" written into CLAUDE.md; six weeks later the class is renamed/split; nobody updates the file because nothing forces it; the rule points at a ghost; the AI changes the real interface. Fix: derive per-element context from source (annotations), so the rule moves with the code.

## Why It Works / Failure Mode
- **Three tiers work** because attention is finite and position-sensitive: scoping keeps irrelevant rules out of the window and keeps Tier 1 short enough to be read in full. **They fail** when Tier 1 grows into a wish list, or when hand-written rules go stale — the diet controls size, not drift.
- **Staleness is the more dangerous failure** because it's silent; human-speed discipline (review the rules file on every PR) fails at vibe-coding velocity. The real fix is architectural — rules attached to code (Ch 4), boundaries as tests (Ch 5).

## Key Takeaways
1. Most agent failures are context failures; debug the context first.
2. Tier 1 ≤ ~10–20 lines; scope local rules to directories; put per-element intent in annotations.
3. Diagnose bloat by behavior; fix by cut, scope, or relocate.
4. Pruning improves correctness (Lost in the Middle), not just cost.
5. Static context on top, dynamic at the bottom — never break the cached prefix.
6. The hand-written root file points at automated enforcement; it doesn't replace it.

## Connects To
- **Ch 1**: context-window degradation note ("the biology of the context window").
- **Ch 3b**: when the diet isn't enough — from flat files to a lat.md context graph.
- **Ch 3c / 3d / 3e**: token-economy runtime, harness configuration surface, agent memory.
- **Ch 4**: Tier 3 as annotations (VibeTags) — the fix for staleness.
- **Ch 5**: ArchUnit tests as the enforced home for boundary rules.
- **Lost in the Middle (Liu et al., 2023)**; **prompt/prefix caching**; **Tree-sitter**.
