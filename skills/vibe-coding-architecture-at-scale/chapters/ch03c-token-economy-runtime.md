# Chapter 3c: The Token Economy Runtime

## Core Idea
The token is the single meter for cost, latency, and accuracy at once, and it prices architecture: coupling decides what enters the agent's window. Measure the context, then control it, first through habits (session length, loops, subagents), then with a runtime layer that either compresses on read (lean-ctx) or indexes ahead of time (CodeGraph). Pick one; don't stack them.

## Frameworks Introduced
- **Three Cost-Hygiene Rules** (from Anthropic's Claude Code cost guidance; they apply to any harness): habits that decide how many requests exist and how long their histories grow, before any tool compresses them.
  - When to use: always, and before installing anything. They capture the larger share of savings.
  - How: (1) **Watch session length**: the full history rides on every request and cache reads are discounted, never free. Run `/compact` mid-task once early history stops paying for itself, and `/clear` when you switch tasks. (2) **Make continuous sessions intentional**: a loop that wakes every 5 minutes issues 288 requests a day whether anything changed or not. Budget that on purpose. (3) **Be deliberate with subagents**: five parallel agents mean five parallel meters. Spawn them only when the task earns it, and assign a cheaper model to simple roles (a log summarizer doesn't need your architecture-review model).
- **Context Locality**: a measurable architecture characteristic, a cousin of Richards & Ford's: *the fraction of the knowledge a change requires that lives inside one module boundary.*
  - When to use: to justify boundary enforcement in currency, and to diagnose a high token bill.
  - How: a well-partitioned feature package means the agent loads that package, its public signatures, and the directory's Tier 2 rules, a few thousand tokens. A tangled codebase forces it to drag in every file the change might touch. If a session keeps re-reading the same files, the code is either badly partitioned or badly compressed. Find out which before you fix anything.
- **Two Layers, One Budget (lean-ctx)**: a Rust binary between editor and agent that intercepts both token sources transparently.
  - When to use: when the bill is dominated by repeated file reads and noisy command output.
  - How: the **MCP layer** replaces native Read/search/shell with `ctx_*` tools. `ctx_read` goes through a tree-sitter AST cache, and an unchanged file costs ~13 tokens to re-read whatever its size. The **shell hook layer** compresses command output with 56 modules and 270 passthrough rules. Prefix determinism comes automatically: cached reads go at the top, dynamic tool output at the bottom.
- **Anchored Iterative Summarization** (context-compression skill, Agent-Skills-for-Context-Engineering): compress the *conversation*, not just the reads.
  - When to use: long autonomous sessions where history is the biggest line item and plain `/compact` keeps making the agent re-explore.
  - How: keep ONE persistent structured summary. When the window fills, fold only the newly truncated span into it (never regenerate it wholesale). Use checklist sections (Session Intent, Files Modified, Decisions Made, Current State, Next Steps) and keep file paths and identifiers verbatim in dedicated sections. Optimize **tokens-per-task**, not tokens-per-request, and track **re-fetching frequency**.
- **The Two Bets: Compress-on-Read vs. Pre-Indexing**: the just-in-time approach (make each look cheap) against the ahead-of-time approach (remove discovery with a queryable symbol/call graph such as CodeGraph).
  - When to use: when choosing a context-runtime tool for a codebase.
  - How: if the bill is dominated by noisy command output and repeated reads, compress. If it's dominated by an agent opening 15 files to answer "where is this handled," you're paying for low context locality, so index. Never run both.

## Key Concepts
- **Token**: a subword fragment produced by a BPE tokenizer. English prose averages ~4 characters per token. Invented identifiers splinter (`getUserByIdAsync` becomes 4–5 tokens), and a 400-line class comes to ~3,000–5,000 tokens.
- **Token economy**: one number drives billing (per input/output token), latency (the full input is processed before the first output token), and accuracy (the attention tax per irrelevant token). That's why it's an economy and not a quota.
- **ROI of an AI workflow**: the value of what ships minus the token bill. The bill is the term you control. As the per-token price falls, spend expands unless someone budgets it (Ch 1b).
- **ctx_read modes**: ten read granularities (auto, full, map, signatures, diff, aggressive, entropy, task, reference, lines:N-M), each cached separately.
- **Compression ratio / prefix hit rate**: the two dashboard numbers worth watching. A low prefix hit rate means something dynamic sits above the static guardrail block.
- **Governance profile / SLO**: per-agent or per-workspace enforced limits (max tokens per session, cost ceiling per turn, context-completeness gates). An agent that exceeds them is blocked until the context is pruned or an operator overrides.
- **Cryptographic context proof**: `ctx_proof` signs a hash of every file, rule, and compressed output in scope, and `ctx_verify` fails if anything changed. It proves after the fact what the agent knew.
- **Verification levels 0–4**: schema validity, completeness vs. task scope, coherence across rules, staleness vs. git state, compression fidelity.
- **Context transfer bundle (.lctxpkg)**: a SHA-256-verified package of one agent's context state (files, modes, artifacts, profile) used for handoff. It is a knowledge-transfer layer that sits on top of worktree isolation and doesn't replace it.
- **Diary system**: typed agent-activity entries (discovery, decision, blocker, progress, insight) offered as structured context to the next agent or a human reviewer.

## Mental Models
- Think of coupling as a **per-run surcharge**: the blast radius of your worst dependency cycle is charged to every agent that goes near it. Parnas's information hiding is now priced in tokens.
- Use habits first and tools second: the three rules decide request count and history length, and compression only thins each request after that.
- Think of a code index as **"the same photograph with a faster shutter"**: it's a cache, and a cache is a claim about a moving target.
- Compression thins each request and caching discounts the unchanged part. A summarizer blind to caching can spend more on cache misses than it saves.

## Anti-patterns
- **Blind `/compact` on long sessions**: paraphrase drops the exact file path the agent spent 20 minutes finding, so it re-explores and pays for discovery twice.
- **Regenerating the summary wholesale**: summarizing the previous summary compounds paraphrase drift until the specifics blur.
- **Volatile summary at the top of the window**: rewriting it every turn moves the bytes under it and forfeits the ~10× cache discount on the whole tail.
- **Stacking compression and indexing tools**: two overlapping "explore the code" catalogs in every window, a routing decision the model can't make well, and two indexes that may disagree about the code.
- **Huge tool surfaces**: every tool description is resident in every window, a permanent attention-tax line item before a single file is read (lean-ctx's 59 tools against CodeGraph's 1).
- **Treating an index as truth**: branch switches, rebases, codegen, and vendored-dependency upgrades move code without the tidy per-file events a watcher expects.
- **Accepting a vendor's token-savings baseline**: CodeGraph's reported 60% reduction is measured against naive grep-and-read, which is the right baseline for "should I index at all?" and the wrong one for "index or compress?"

## Code Examples
```bash
# lean-ctx: compress on read
curl -fsSL https://leanctx.com/install.sh | sh
lean-ctx init --agent claude   # auto-detects Claude Code; configures MCP + shell hook
lean-ctx doctor                # verifies MCP registration and hook installation
lean-ctx gain --live           # real-time per-module savings in the terminal
lean-ctx dashboard             # browser UI: tokens by file/tool/module/role
lean-ctx benchmark report .    # where token overhead concentrates in this repo

# CodeGraph: index ahead of time (choose ONE of the two)
curl -fsSL https://codegraph.sh/install.sh | sh
codegraph install              # wire MCP server into detected agents
codegraph init                 # index this repository
```
- **What it demonstrates**: the two competing context runtimes. Each installs in a few commands, and you pick one per codebase.

## Reference Tables
**ctx_read modes**

| Mode | Returns | Best for |
|---|---|---|
| auto | Optimal mode per file type (tree-sitter) | Default |
| full | Complete text, cached | Files you are about to edit |
| map | Imports, exports, dependency edges | Context-only files |
| signatures | Function/type signatures | API surface review, contract checks |
| diff | Changed lines since last read | Post-edit verification |
| aggressive | Maximum compression | Deep context held for many turns |
| entropy | High-entropy fragments highlighted | Security/config review |
| task | Information-bottleneck filtered to task | Narrow task scope |
| reference | Quote-friendly minimal excerpts | Citing a specific line |
| lines:N-M | Line range | Known location |

**Compress-on-read vs. index-ahead**

| | lean-ctx | CodeGraph |
|---|---|---|
| When work happens | Every read/command, every session | Once at init, then incrementally |
| Optimizes | Cost of a read | Number of reads needed |
| Sees | File in front of it | Whole graph |
| Cold start | None | Full index pass |
| Wasted question costs | One compressed read | One traversal, ~free |
| Failure mode | Compression drops a needed detail | Stale index, or non-structural question |
| Tool surface | 59 tools | 1 tool (`codegraph_explore`) |

## Worked Example
**Mixing read modes on a 12-file task.** A naive agent issues 12 full `Read` calls. With lean-ctx, the 3 files it will edit get `full`, the 5 it needs for module structure get `map`, and the 4 it checks for type compatibility get `signatures`. Read cost drops by 70–80% on the reads that didn't need full text. An 800-line Java class re-checked five times costs ~5,000 tokens on the first read and ~13 tokens on each of the next four.

**Shell compression.** A 400-test `cargo test` run shrinks to the failures only. `git status` shrinks to a minimal diff summary, and `kubectl get pods` loses columns the agent never acts on. Failing test messages, stack traces, and warnings always pass through verbatim, whatever their length, because the compression is structural, not length-based. For custom CLIs, define a TOML module with the same passthrough-rule format.

**Cost framing (from 3.6.3).** For a 15-developer team, undisciplined context costs ~$180/day against ~$18/day for a scoped, cached flow.

## Why It Works / Failure Mode
- **Two-layer compression** works because the agent's behavior doesn't change: it issues its usual calls, and the interception plus caching make re-reads nearly free and strip the structurally irrelevant lines. It fails when compression drops a detail the task needed (verification level 4, compression fidelity, exists to catch that), on commands outside the 56 modules, and when governance stays at permissive defaults. Profiles and SLOs don't self-configure. Proofs are overhead you can rarely justify for solo sessions.
- **Summarization vs. caching**: anchored summaries keep history small, but prefix caching serves an unchanged leading span at ~1/10 of the input price, and the first changed byte invalidates everything after it. You keep both through placement and timing: put the volatile summary *below* the static prefix (system prompt and tool definitions) and re-summarize in batches, not every turn.
- **Pre-indexing** works by removing discovery entirely, and framework-aware routing (17 web frameworks) and cross-language bridging (Swift↔ObjC, React Native) add the edges that a plain syntax parse misses. It fails on staleness and on semantic questions ("is this correct, should it exist?"). An index shrinks discovery, not judgment.

## Key Takeaways
1. One number, tokens, drives cost, latency, and accuracy, so manage it as an economy.
2. Structure is priced per interaction. High context locality keeps the agent cheap, fast, and accurate at once, and clean boundaries make either runtime strategy work.
3. Apply the three hygiene rules (session length, intentional loops, deliberate subagents with cheaper models) before installing tools.
4. Mix read granularities (full/map/signatures) instead of reading every file in full.
5. Compress the conversation with anchored, structured, verbatim-identifier summaries placed below the cached prefix and refreshed in batches. Measure tokens-per-task and re-fetching frequency.
6. Choose compress-on-read OR pre-index based on what dominates the bill, and never both.
7. Tools rot and the requirement doesn't: measure the context, then control it.

## Connects To
- **Ch 3 (3.6)**: the Context Diet, the Attention Tax (3.6.1), prefix determinism (3.6.2), and the financial equation (3.6.3) that this runtime enforces.
- **Ch 1b**: falling per-token prices expand spend unless it's budgeted.
- **Ch 3d**: the context-compression skill belongs in the on-demand skill tier of the configuration surface, and subagent model choice lives there too.
- **Ch 3e**: the "index is a cache of a moving target" argument applied to agent memory.
- **Ch 5**: fitness functions enforce the boundaries that the token meter prices.
- **Ch 6**: the living-diagram problem, since a structural picture is only as honest as its knowledge of framework wiring.
- **Ch 15**: Vibe Kanban parallel agents, and why multi-agent context sync matters.
- **Ch 19**: VibeKit's execution-layer observability trail, paralleled by context proofs.
- **External**: Parnas (1972) information hiding; Boehm's *Software Engineering Economics*; BPE tokenization (Gage 1994; Sennrich et al. 2016); Richards & Ford's architecture characteristics; Anthropic prompt caching.
