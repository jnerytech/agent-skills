# Chapter 16: Skill Forge: Skills Forged From Your Own Codebase

## Core Idea
"Skills should be ergonomics for your team, not tourism brochures from someone else's stack." A skill tells the agent *how this team already does things*; a borrowed generic skill fights the codebase it is meant to fit. Skill Forge (github.com/jarvis823/skill-forge) drafts project-convention skills from your repository, each cited to a real `file:line`, behind an explicit human y/N gate. The chapter then completes the skill taxonomy with hand-crafted universal process skills (`/grill-me`) and loop engineering (Ralph Wiggum → `/goal`), where the human moves *above* the loop rather than out of it.

## Frameworks Introduced
- **Evidence-Cited Skills (Ergonomics vs Tourism)**: project-convention skills must be derived from your source and cite a real file and line.
  - When to use: any skill that encodes naming, placement, structure or testing conventions specific to your codebase.
  - How: draft from repo evidence only (not chat history, internet, or "best practice"); write "this project's handlers look like `Features/Order/CreateOrderHandler.cs:42`; follow that shape," not "controllers should be thin." Citation makes the skill non-generic and makes it go stale *loudly* when that file's convention moves. If the tool disappears, generate them by hand — the evidence-cited, derived-from-source property is the asset.
- **The Forge Loop**: recon → system prompt → tier → draft → human gate → install → index.
  - When to use: bootstrapping or refreshing a project skill library.
  - How: run `forge.sh`/`forge.ps1` to write 5 scoped recon files; import the SYSTEM.md prompt into CLAUDE.md; pick a tier (1/2/3/custom = how much to forge); agent drafts evidence-cited skills to `.claude/skills-draft/`; approve each explicitly (y/N/edit); approved ones move to `.claude/skills/`; track in `skill-forge-index.md` outside the skills dir.
- **Three Kinds of Skill**: forged (how your team builds), hand-crafted universal (how to work with you), and loops (when you build unattended).
  - When to use: designing a mature skill library — carry both of the first two; use the third only under strict conditions.
  - How: forge convention skills from source; write process skills once, well, each killing one named failure mode (Matt Pocock's library: "small, easy to adapt, and composable… work with any model"); use loops only when the three Ralph conditions hold.
- **`/grill-me`**: invert the agent from executor to interrogator until every branch of the design tree is resolved.
  - When to use: before building, to surface silent misalignment between what you said and what you meant.
  - How: one question at a time; walk each branch and resolve dependencies; **provide a recommended answer for each question** (rejecting a wrong recommendation is faster than inventing a right one, and it exposes the diverging assumption); **explore the codebase instead of asking** when evidence can answer.
- **Ralph Wiggum Loop / Loop Engineering**: "Ralph is a Bash loop" (Geoffrey Huntley) — a Stop hook refeeds the same prompt so the agent iterates on persisted work until a completion condition or iteration limit.
  - When to use: only when all three conditions hold: (1) **machine-verifiable success criterion** ("all tests passing", not "looks good"); (2) **task tolerates iteration** (feature from spec, class of failing tests, language from a grammar — not live production debugging or design/trade-off calls); (3) **contained blast radius** (git worktree or VibeKit sandbox; discard the branch when iteration 14 goes wrong).
  - How: design the *stop*, not the start — a completion predicate (fitness function/spec), an iteration ceiling, a no-progress detector (halt and escalate when N passes produce no measurable change), and per-iteration verifiers (CI gates, Inquisitor). Keep permission and security controls *outside* anything the agent can rewrite.

## Key Concepts
- **Skill vs spec**: a spec says what to build; a skill says how this team does things.
- **Tourism brochure**: a pasted generic skill (e.g. scaffolding `*Controller.cs` when the team standardized on `*Handler.cs`) that biases every generation wrongly.
- **Recon files**: `01-tree`, `02-languages`, `03-manifests`, `04-entrypoints`, `05-tests` in `.claude/forge-recon/` — the context diet in miniature (pull, not push).
- **y/N/edit gate**: nothing reaches `.claude/skills/` without explicit approval, because a wrong skill biases every future generation, not just one.
- **Stop hook**: a Claude Code hook that intercepts exit; Ralph uses it to refeed the prompt.
- **Completion promise / `/goal`**: a declared predicate — "what should be true, how success should be checked, and what constraints must stay intact" — re-checked each turn and cleared when it holds.
- **Loop engineering**: designing the loop instead of writing prompts; 2023 prompt engineering → 2024 orchestration → 2025 harness → 2026 loop.
- **Move up the stack**: the human relocates the gate from per-diff approval to one-time design of the loop's scope, done-ness and stop (Lilian Weng).
- **Mirror, not corrective**: Skill Forge codifies how the code *is*, including inconsistencies.

## Mental Models
- Think of Skill Forge as **Ch 4 for skills**: VibeTags reads annotated code and emits per-platform config; Skill Forge reads unannotated code and emits per-project skills — both replace hand-maintained generic files with regenerated evidence-bound artifacts.
- Think of skills as Ch 3's **on-demand tier**: scoped capabilities loaded when needed, not standing context; a library pasted from ten blog posts is context rot.
- Use `/grill-me` before you build, forged skills for how you build, and a loop for when you build unattended.
- Think of a loop as only as good as its stop condition and blast radius — "an autonomous iterator without an isolation boundary is not a productivity technique, it is an incident with a retry count."
- When a program can edit its own harness, "abstraction boundaries are broken": enforcement must sit outside the thing the agent may rewrite.

## Anti-patterns
- **Pasting popular skills from strangers**: they worked on a toy project and fight your conventions.
- **Handing the agent the whole repo to "figure out conventions"**: violates the context diet; use scoped recon.
- **Auto-installing drafted skills (yolo)**: a wrong skill compounds across every future generation.
- **Comprehensive workflow frameworks that own the process**: Pocock's critique of GSD/BMAD/Spec Kit — they take control from the developer.
- **Executor-mode alignment**: the agent does what it understood and never surfaces the gap.
- **Loops on "looks good" criteria**: no way to know it's done; it runs to the iteration limit and stops arbitrarily.
- **Loops without a no-progress detector**: burns its budget and reports success.
- **Treating Skill Forge as a corrective**: it faithfully forges inconsistencies, with a citation proving them.

## Code Examples
```text
forge.sh / forge.ps1               → writes 5 recon files to .claude/forge-recon/
                                     (01-tree, 02-languages, 03-manifests, 04-entrypoints, 05-tests)
@tools/skill-forge/prompts/SYSTEM.md → imported into the project CLAUDE.md
pick a tier                        → 1 / 2 / 3 / custom (how much to forge)
agent drafts skills                → .claude/skills-draft/<name>/SKILL.md, evidence-cited
y / N / edit                       → you approve each one explicitly
approved skills                    → .claude/skills/<name>/ (Claude Code Skills spec)
skill-forge-index.md               → tracking manifest, kept outside .claude/skills/
```
- **What it demonstrates**: scoped recon (pull not push) and a human keep-or-kill gate before anything becomes standing agent behavior.

```markdown
---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me".
---
Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer. Ask the questions one at a time. If a question can be answered by exploring the codebase, explore the codebase instead.
```
- **What it demonstrates**: a complete universal skill in six body lines, killing one named failure mode (misalignment).

```bash
/ralph-loop "implement the feature in SPEC.md until all tests pass" \
  --max-iterations 20 \
  --completion-promise "all tests passing"
# /cancel-ralph breaks the loop manually
```
- **What it demonstrates**: a machine-verifiable completion predicate plus an iteration ceiling — the two stops that make an unattended loop safe.

```text
agent receives prompt → works → tries to exit → Stop hook intercepts
→ refeeds the same prompt → agent sees modified files + git history
→ works again → tries to exit → repeat
```
- **What it demonstrates**: previous work persists; each iteration resumes, not restarts.

## Reference Tables
| Skill kind | Answers | Source | Example |
|---|---|---|---|
| Forged (project-convention) | How your team builds | Your repo, cited file:line | Handler naming/placement, test layout |
| Hand-crafted universal (process) | How to work with you | Engineering judgment, written once | `/grill-me` |
| Loop | When to build unattended | Completion predicate + isolation | Ralph Wiggum, `/goal` |

| Ralph condition | Passes | Fails |
|---|---|---|
| Machine-verifiable success | "All tests passing" | "Looks good" |
| Tolerates iteration | Feature from spec, failing-test class, grammar → language | Live production debugging, design/trade-off calls |
| Contained blast radius | Worktree / VibeKit sandbox | Shared branch |

Part III at a glance — three patterns across the nine tool chapters: (1) every tool has a human gate (y/N before implementation, approval before code, review before merge) — the gate is the principle; (2) seven of nine are agent-agnostic (exceptions: Kiro's IDE, Skill Forge's `.claude/skills/` format — depth of integration, not accidental lock-in); (3) isolation appears exactly where multiple agents run at once (Ch 12 worktrees, Ch 15 workspaces) — isolation is the natural response to concurrency.

## Worked Example
A team's skill library includes a popular scaffolder that generates `OrderController.cs`; the team moved to `*Handler.cs` three refactors ago, so every generation must be corrected. Running Skill Forge: recon captures the tree, languages, manifests, entrypoints and tests; at Tier 1 the agent drafts a `add-handler` skill citing `Features/Order/CreateOrderHandler.cs:42` for shape, naming and test placement. The developer reviews the draft, edits one line, answers `y`; it lands in `.claude/skills/add-handler/` and is indexed. When the handler convention later changes, the cited file no longer matches — the skill visibly goes stale instead of silently misleading. Separately, before a new feature, `/grill-me` walks the design tree one question at a time with a recommended answer each, checking the codebase instead of asking where it can.

## Why It Works / Failure Mode
- **Evidence-cited forging works** because it grounds procedural knowledge in a file and a line — same move as the Inquisitor's cited gripe (Ch 22), VibeTags from annotations (Ch 4), and diagrams extracted from code (Ch 6). It fails as a *mirror*: inconsistent conventions get codified with a citation. It tells the agent how the code is, not how it should be — exactly where codebases most need help. It presupposes the enforcers: the architectural test (Ch 5) decides handlers must sit behind a port; the annotation (Ch 4) freezes signatures.
- **Loop engineering works** when the human's judgment is spent once on the loop's shape — what it may touch, what counts as done, when it must stop — rather than per diff. Evidence: six repos overnight at a YC hackathon, a $50k contract for $297 of API costs, a programming language over three months unattended — wins in calendar time, not code volume. It breaks without a machine-checkable predicate, a no-progress halt, or an isolation boundary, and catastrophically if enforcement lives inside a harness the agent can rewrite.

## Key Takeaways
1. Forge project-convention skills from your own repo, cited to real `file:line`; never paste strangers' conventions.
2. Feed the drafter scoped recon, not the whole repo; gate every skill with explicit y/N.
3. Keep a separate set of small, composable universal process skills, each killing one failure mode.
4. Use `/grill-me` before building: one question at a time, recommended answer each, explore code before asking.
5. Run unattended loops only with a machine-verifiable predicate, an iteration-tolerant task and contained blast radius.
6. Engineer the stop: completion predicate, iteration cap, no-progress detector, per-iteration verifiers, controls outside the loop.
7. Forged skills are a fast draft of conventions; the real enforcers keep them honest.

## Connects To
- **Ch 2**: the architect's job is above the cycle — where loop engineering puts the human.
- **Ch 3**: context diet and on-demand tier; pasted skills as context rot.
- **Ch 4**: same derive-don't-hand-maintain move (VibeTags); annotations freeze signatures.
- **Ch 5**: architectural tests and fitness functions = loop completion predicates.
- **Ch 6**: living diagrams extracted from code.
- **Ch 7**: spec as the executable statement of intent behind `/goal`.
- **Ch 8**: human gate between /specify and /plan, relocated (not retired) by loops.
- **Ch 11 / 11b**: yolo as the dangerous setting; the stop rule moved to the machine side.
- **Ch 17 / 17b**: Part IV opens with what survives a perfect input side — concurrency and performance.
- **Ch 19 / 21 / 21b / 22**: sandbox, branch-level CI law, isolation, and the Inquisitor as per-iteration verifier.
- **Fitness functions (Ford/Parsons)**: the completion predicate of a loop.
