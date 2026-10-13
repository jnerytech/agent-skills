# Patterns — Beyond Vibe Coding

## Plan-First Development
**When to use**: production features, team codebases, code that must live for years.
**How**: write a mini-PRD/checklist → one targeted prompt per item → review generated code → integrate only what you approve.
**Trade-offs**: slower start; buys sustained velocity and reliability (Ch 1).

## Vibe Scaffold, Then Engineer
**When to use**: CRUD apps, MVPs, hackathons.
**How**: generate scaffolding by vibe; hand-engineer the domain rules (concurrency, integrity, auth); recognize the switch point (traction, complexity, critical systems).
**Trade-offs**: fast, but missing the transition produces house-of-cards code (Ch 1, 6).

## Bug-Report Prompt
**When to use**: debugging with AI.
**How**: language, purpose, sample input, exact error, code, expected vs. actual, clear ask — "Fails on input X (expected Y, got Z)."
**Trade-offs**: longer prompt; targeted diagnosis instead of generic tips (Ch 2, 5).

## Rubber-Duck Prompt
**When to use**: logic bugs with no error thrown.
**How**: "Walk through line by line, track `total`" → "What causes it / how to fix?" → "Explain why that fixes it."
**Trade-offs**: more turns; surfaces subtle state bugs (Ch 2).

## Outline-Then-Implement
**When to use**: large features or complex tasks.
**How**: "List the steps…" → "Now implement step 1" → verify → next step.
**Trade-offs**: more sessions; each step verifiable; avoids overloaded prompts (Ch 2).

## Combined Role + CoT + Metaprompt
**When to use**: complex generation where quality varies.
**How**: role → "think step by step" → task → "explain, then commented code" → "add 2–3 tests."
**Trade-offs**: long output, harder to verify (Ch 2).

## Granular, Tagged AI Commits
**When to use**: whenever AI produces code quickly.
**How**: one concern per commit; tag `[AI]`/`[AI-assisted]` for traceability (signals harder review, not blame); split agent changes in unrelated areas.
**Trade-offs**: more commits; cheap bisect/revert (Ch 3).

## AI as First Drafter / Pair Programmer / Validator
**When to use**: first drafter — team features with shared standards; pair — solo or limited capacity (new session per task, frequent commits); validator — humans write, AI scans, generates tests, suggests fixes.
**Trade-offs**: validator mode still needs humans for complex functionality, UX, and AI blind spots (Ch 3).

## Intent-to-Implementation Check
**When to use**: after every generation, before running it.
**How**: trace a typical input → confirm each prompt requirement → flag unrequested extras → check edge cases (empty, None, negative) → find ambiguity choices (print vs. return) → list assumptions.
**Trade-offs**: minutes per review; catches majority-solution misfits (Ch 5).

## Six-Step Debugging / Six-Step Refactoring
**When to use**: debugging — code misbehaves; refactoring — code works but isn't yours yet.
**How**: debug: reproduce → locate → check prompt vs. code → use AI as colleague → fix → retest. Refactor: style/lint → naming/structure → remove extras → document → optimize → simplify, until no one can tell AI wrote it.
**Trade-offs**: time; produces owned, tested code (Ch 5).

## Fidelity-vs-Control Tool Choice
**When to use**: picking a prototyping tool.
**How**: designers validating interactions → fidelity (screenshot-to-code, full-app builders); developers testing feasibility → control (AI IDEs).
**Trade-offs**: high fidelity means less transparency into the code (Ch 6).

## Stub + TODO Shortcut Ledger
**When to use**: prototyping; login, payments, emails appear.
**How**: one-sentence North Star; AI generates fake flows; record every shortcut in a "things to address if we move forward" list and `// TODO`.
**Trade-offs**: stubs must be rebuilt; avoids integration surprises (Ch 6).

## Prototype-to-Production Transition
**When to use**: once a prototype validates the idea.
**How**: restructure architecture → error handling/edge cases → performance → security → docs → tests → replace hacks. Rewrite (prototype as reference) or refactor with AI-generated tests as a safety net.
**Trade-offs**: rewrite cleaner; refactor faster but carries debt (Ch 6).

## Cross-File Contract Reconciliation
**When to use**: frontend and backend generated separately.
**How**: specify the response shape for both sides; run a real end-to-end call; prompt "ensure the frontend fetch matches the route; fix discrepancies."
**Trade-offs**: needs project-wide context (Ch 7).

## Cross-Model Security Review
**When to use**: after generating security-sensitive code.
**How**: paste into a different model for an audit; combine with SAST in CI, a human checklist, fuzzing; cite current standards in prompts to beat the training cutoff.
**Trade-offs**: false positives/misses; input, never clearance (Ch 8).

## Generation / Hardening Sprint Alternation
**When to use**: after bursts of AI generation.
**How**: schedule refactor, test, and documentation sprints; track debt with TODOs.
**Trade-offs**: slows feature velocity; prevents a big ball of mud (Ch 8).

## Canary + Shadow Deployment
**When to use**: risky AI-built features or algorithms.
**How**: canary to ~5% with monitoring and a rollback plan; shadow-run risky algorithms against live inputs.
**Trade-offs**: infra cost; contains blast radius (Ch 8).

## Attribute-or-Rewrite
**When to use**: output resembles a known source.
**How**: search unique strings; MIT → keep with attribution; GPL in closed code → rewrite from the idea or depend on the library; unsure → leave it out.
**Trade-offs**: rewrite costs time; attribution is free (Ch 9).

## Plan-Gate Review for Agents
**When to use**: before a background agent writes code.
**How**: review the plan for correctness, efficiency, conventions; reject or redirect early; ensure the sandbox can run tests, linters, builds.
**Trade-offs**: upfront attention; saves rework and coherent incorrectness (Ch 10).

## Scoped Parallel Agents + Dual-Model Cross-Check
**When to use**: several agents at once; higher-stakes generation.
**How**: separate modules/layers per agent, integration order (infra before features); two models attempt, keep the one passing tests.
**Trade-offs**: coordination overhead; 2× compute (Ch 10).

## Independent Verification
**When to use**: agent- or AI-written code and tests.
**How**: humans write tests for agent code (or vice versa); check AI test assertions against the requirement, not current output.
**Trade-offs**: extra human effort; prevents locking in bugs (Ch 11).
