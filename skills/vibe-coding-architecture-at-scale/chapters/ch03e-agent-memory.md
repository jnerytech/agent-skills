# Chapter 3e: Agent Memory: The Fifth Primitive

## Core Idea
Agent memory is the one configuration primitive the harness writes *itself*: durable, cross-session, small, and with no human review gate. That makes it the cheapest way to carry hard-won context forward and the fastest way to accumulate a durable, confident falsehood. Keep it in the personal, unreviewed layer, treat every recalled fact as a lead and not a citation, and promote only facts that survive repeated verification into reviewed team law.

## Frameworks Introduced
- **Instruction / Skill / Memory placement rule** (the five-way decision): these three are stages, not competitors.
  - When to use: deciding where a learned fact should live.
  - How: an **Instruction** is curated, reviewed, durable team law that binds everyone, CI included. A **Skill** is a deliberately written multi-step procedure. **Memory** is personal, unreviewed, self-written, applies to *this agent's* future sessions, and claims nothing beyond "true when I wrote it down." Where Ch 3d's global vs. project asked *who does this bind?*, memory vs. instruction asks *has anyone signed off on this being true?*
- **The Promotion Path**: a fact starts as a memory (the only slot cheap enough to capture it mid-session), and most should die there (ticket-specific observations, workarounds for bugs fixed next sprint, one-off preferences).
  - When to use: periodically reviewing the memory store.
  - How: when a self-written fact has been independently re-confirmed across weeks of sessions and you'd put your name on it, move it into the project instruction file or a skill, where a human reviews it before it binds anyone. A memory that graduates *without* that step is "a team rule nobody wrote down on purpose." **"Memory without a promotion path is accumulated hearsay."**
- **Five Disciplines for Trustworthy Memory**: the review built into the habit, since no external gate exists.
  - How:
    1. **Age-stamp everything**: a "learned on" date at minimum, plus ideally the codebase state (commit hash, version, sprint). A memory with no timestamp is a claim with no expiration date.
    2. **Verify before asserting, not before writing**: don't demand proof at write time (that kills the cost advantage). At read time, confirm against the *code* before repeating a fact as a claim about current state. "`RetryPolicy.java:42`" is a lead to grep, not a citation.
    3. **Dedupe on write, not after**: update, overwrite, correct, or retire the existing fact in place instead of appending a near-duplicate. Accretion leads to self-contradiction ("migration done" in one file, "pending" in another).
    4. **Record the why, not only the what**: "Use LinkedHashMap here *because iteration order feeds the audit log and a plain HashMap broke it once in production*" survives a future agent that wants to "clean up."
    5. **Link related memories into a small graph**: supersedes/depends-on references give facts a shelf life ("port 5544" linked to "mid-migration, target end of quarter").
- **Memory Is a Lead, Not a Citation** (Architect's Note): the half-second after recall decides whether memory is an asset or a liability. Spend one cheap tool call (open the file, confirm) before the claim leaves the agent's mouth. The cost is one tool call, and the failure-mode difference is the whole chapter.
- **Auto-capture scorecard** (agentmemory scored against the five disciplines): automation makes dedupe (SHA-256), age-stamping (capture time), and linking (graph format) mechanical. It leaves **verify-before-asserting** untouched (better recall makes the check *more* load-bearing) and largely defeats **record-the-why** (a reason is not an event, and it never crosses a tool boundary where a hook can see it).

## Key Concepts
- **Agent memory**: small files, typically one fact per file, kept outside the context window and the instruction files, with an auto-loaded index, written by the agent for the agent.
- **Index-plus-body split**: the session loads only one-line descriptions, and full bodies load when relevant. These are the on-demand economics of skills applied to self-written knowledge.
- **Memory taxonomy**: **User** (durable preferences, ages slowest), **Feedback** (corrections from a specific mistake, a skill-in-waiting and the strongest promotion candidate), **Project state** (ages fastest, needs the most aggressive verification), **External references** (vendor quirks, deadlines, library gotchas, so re-check occasionally).
- **"How to apply" section**: beneath each fact, what a future session should *do* with it. This turns a trivia card into a tiny personal skill, usually the version worth promoting.
- **Recall-time age banner**: every recalled memory is visibly stamped with its age and the warning "point-in-time observations, verify against current code before asserting," which makes discipline 2 structural.
- **Staleness**: a memory is a photograph, not a live feed. Lehman's law of continuing change guarantees the subject moves.
- **Externalized theory**: in Naur's sense, memory is the first tooling to give an agent a thin, durable trace of the *theory* behind code (why the two-phase migration, why library X was rejected).
- **Knowledge-graph memory (MCP Memory server)**: entities with atomic observations plus directed relations stored as JSONL. It buys *reach* ("what else did I believe because of this fact?") but doesn't repeal staleness.
- **PreCompact reinjection**: a hook that fires before compaction and reinjects relevant memory, restoring specifics (exact file paths) that the summarizer paraphrased away.
- **Recall is not truth**: a retrieval benchmark (agentmemory's 95.2% LongMemEval-S) measures re-finding stored facts. A store that perfectly recalls a fact the world stopped agreeing with scores 100%.

## Mental Models
- Think of an agent with skills but no memory as **H.M. at a keyboard**: Milner's patient improved at mirror-tracing a star while never remembering the task. Procedure survives and episode doesn't, because they're different systems.
- Think of memory as the new hire's first month: not the employee handbook, but the stuff that never made it into the handbook.
- Use auto-capture for the fast-aging categories (project state, procedural feedback), where value is in the volume. Write the *why* by hand, because automation can't see it.
- Think of staleness as the tax memory pays for being the first primitive that externalizes *theory* rather than intent: a rule can be checked true or false, while a theory must be re-verified against a moving target forever.

## Anti-patterns
- **The dead workaround**: "pagination returns duplicate rows on the last page, always dedupe client-side." Two months later the upstream bug is fixed, and the agent silently discards a legitimate row with total confidence. The fixing event happened where the memory system wasn't watching.
- **The reversed decision**: "never introduce a second HTTP client; team standardized on X." The team reverses it in a meeting the agent never attended, and the memory actively argues against the team's current decision.
- **Memory as team law**: a self-written, unreviewed memory living at the project/shared level. It's a governance failure waiting on a bad session.
- **Stale memory with confidence**: it's worse than no memory, because it fills the gap invisibly to the model's own uncertainty. A wrong guess reads like a guess, and a stale memory reads like earned knowledge (Ch 2's beautifully deceptive code with a new author).
- **Unread auto-captured stores**: thousands of observations a week means nobody rereads them, so nothing is ever promoted, and dead workarounds and reversed decisions get found *faster* and ranked *better*.
- **Accepting the full tool surface**: agentmemory's 53 MCP tools plus 15 skills bill ~1,250 tokens of skill descriptions into every session. Use `--tools core` (8 tools) by default, and check whether your harness defers tool schemas.
- **Trusting headline savings**: "92% fewer tokens" is measured against pasting full context, which disciplined teams weren't doing anyway.

## Code Examples
```json
{"type":"entity","name":"staging_db","entityType":"infrastructure","observations":["moved to port 5544 on 2026-07-14"]}
{"type":"entity","name":"migration_q3","entityType":"project","observations":["target: end of quarter","status: in progress"]}
{"type":"relation","from":"staging_db","to":"migration_q3","relationType":"belongs_to"}
{"type":"relation","from":"payments_service","to":"staging_db","relationType":"depends_on"}
```
- **What it demonstrates**: MCP Memory server JSONL, with two nodes carrying facts and two edges carrying context. Mark `migration_q3` done and one traversal reaches the port change and the `payments_service` dependency, which a flat one-fact-per-file directory can't do.

```bash
npm install -g @agentmemory/agentmemory
agentmemory                       # start worker; REST on :3111, viewer on :3113
agentmemory connect claude-code   # wire lifecycle hooks + register MCP tools
agentmemory status                # connection state, memory count, health
```
- **What it demonstrates**: an auto-capture install. Hooks span SessionStart, UserPromptSubmit (secret-stripping filter), Pre/PostToolUse, PostToolUseFailure (often the most reusable observation), subagent start/stop, PreCompact, Stop, and SessionEnd, and land in a local SQLite + BM25 + vector + graph index. On a fresh install with no model-provider key, graph extraction and embeddings are flagged off and only BM25 runs.

## Reference Tables
**Placement decision**

| Slot | Written by | Reviewed? | Binds | Truth claim |
|---|---|---|---|---|
| Instruction | Human, on purpose | Yes | Everyone incl. CI | Team law |
| Skill | Human (or forged from code) | Usually | Whoever invokes the task | Procedure |
| Memory | Agent, for itself | No | This agent's future sessions | "True when written" |

**Auto-capture vs. the five disciplines**

| Discipline | Under auto-capture |
|---|---|
| Age-stamp | Mechanical (capture time) |
| Dedupe on write | Mechanical (SHA-256) |
| Link into graph | Mechanical (graph format) |
| Verify before asserting | Untouched, and more load-bearing with better recall |
| Record the why | Largely defeated, since reasons aren't tool events |

## Worked Example
**A working memory directory (the author's practice).** Each project has one Markdown file per fact plus an auto-loaded index of one-line descriptions. Here is the book's feedback example in the fact + age + "How to apply" shape (the layout is illustrative):

```markdown
---
type: feedback
learned: <date> (against <commit/version>)
---
Don't propose a migration without checking for an existing Flyway script first;
I did this once and it collided.
**How to apply:** before writing any migration, list the existing Flyway scripts
and confirm nothing already covers it.
```

On recall, the session prints the age and "point-in-time observation, verify against current code before asserting." The agent `ls`-es the folder (lead, not citation) before acting. After this fact has proved true across weeks of sessions, it gets promoted into the project's `CLAUDE.md` or a `add-migration` skill, where a human reviews it.

## Why It Works / Failure Mode
- **Promotion path + verify-before-asserting** works because it puts back the human review that memory's cheap write path skipped, at the two moments that matter: when a fact would start binding others (promotion), and when a fact would be stated as current truth (recall). It breaks when the world changes in a channel memory can't see (a fixed upstream bug, a reversed decision in a meeting) and nobody checks at read time. A stale memory carries no internal signal that it's stale.
- **Auto-capture** works for volume and for PreCompact restoration of specifics. It fails at theory (it can't see *why*) and at ratification (a huge store nobody reads promotes nothing). Its retrieval quality speeds up the delivery of stale facts.
- **Storage choice is architectural**: the MCP Memory server's local JSON file is a floor. A team can stand up its own server on a real database (transactions, indexing, access control) with no agent-side change, because the tool surface is identical ("the tool is the example," Ch 3c). Memory that survives is memory somebody chose the storage for on purpose.

## Key Takeaways
1. Memory is the only self-written, unreviewed primitive, so its home is the personal layer, full stop. Anything durable enough for the project layer has stopped being a memory.
2. Most memories should die. Promote only facts that survive repeated verification, through human review.
3. Treat every recalled fact as a lead: one cheap check against current code before asserting.
4. Age-stamp, dedupe in place, record the why, link facts, and add a "How to apply" line.
5. Staleness is inevitable (Lehman), and stale memories are dangerous because they arrive with confidence.
6. Auto-capture handles episodes and fast-aging state well, but not reasons. Keep writing the why by hand, and default to the reduced tool surface.
7. Recall is not truth: retrieval benchmarks can't measure staleness.

## Connects To
- **Ch 3d**: the four-slot × three-level grid that memory extends as a fifth row with no legitimate shared cell.
- **Ch 3c**: `/compact` paraphrase loss (3c.9), which PreCompact reinjection fixes. "The tool is the example." Tool-catalog cost (3c.10), and "a code index is the same photograph with a faster shutter."
- **Ch 3 (3.6.1)**: the attention tax charged by resident skill/tool descriptions.
- **Ch 2**: beautifully deceptive code, which is the same confident-falsehood failure.
- **Ch 4**: VibeTags annotations as memory that "graduated before it was ever informal," checked at compile time.
- **Ch 5, Ch 7**: architectural tests and specs, the other ways intent gets externalized.
- **Ch 16**: Skill Forge, whose human y/N/edit gate is the review memory lacks.
- **Ch 23**: prompt lineage, which traces why the agent believed something, memory included.
- **External**: Naur, "Programming as Theory Building" (1985); Lehman's laws of software evolution (1980): continuing change, increasing entropy; Milner and patient H.M. (procedural vs. episodic memory); MCP Memory server; agentmemory; LongMemEval.
