# Cheatsheet — Beyond Vibe Coding

## Where on the spectrum? (Ch 1)
| Situation | Mode |
|---|---|
| Idea validation, hackathon, demo, throwaway script | **Vibe code** — optimize short-term velocity |
| Code lives for years / others build on it | **Plan-first AI-assisted engineering** |
| Novel algorithms, finance/health/security, legacy, low-level, perf-critical | **AI as explainer/reviewer, not generator** |
| MVP gains traction, PoC → production | **Transition now** — the art is recognizing when |

## Who does what with AI (Ch 3, 10)
| Mode | Use when |
|---|---|
| AI first drafter | Team features, shared standards |
| AI pair programmer | Solo/limited capacity; new session per task |
| AI validator | QA, review, security scans (humans still own nuance) |
| Background agent | Well-defined, encapsulated, measurable (coverage, dep bumps, bulk refactors, lint) |
| Human-led | Architecture, ambiguous stakeholder needs, novel algorithms |

## Prompting decision rules (Ch 2)
- Prompt fits dozens of scenarios → too vague; add specifics until it fits only yours.
- Several "and"s → split into sequential prompts.
- Fundamental misunderstanding → rephrase from scratch; never resend verbatim.
- Format matters → few-shot (2–5 examples) or explicit format. Tricky logic → CoT. Quality varies → role. Non-compliance → split, simplify, stronger wording.
- Success criteria measurable ("linear time, currently quadratic"), never "faster/cleaner".
- Niche/new framework → paste its docs (AI hallucinates outdated APIs).
- Keep chat state for refinements; start fresh to drop wrong assumptions.

## Review rules (Ch 3, 4, 5)
- Treat AI output as an intern's/junior's work: nothing works until proven.
- **Never merge code you don't understand** — nonnegotiable.
- Polished output → verify against intent first; AI's confidence ≫ its reliability.
- Fix spawns new bugs (two steps back) → stop prompting, find root cause.
- Ambiguous prompt → find where the AI picked an interpretation (majority default).
- Unrequested extra with no reason → remove it.
- Tight loop / large data → check complexity (set vs. list lookup).
- Obvious fix → do it by hand; else prompt "input X, expected Y, got Z".
- "Too good to be true" → dig in; intuition is right "nine times out of ten".

## Security tells (Ch 8)
| If you see | Do |
|---|---|
| String-built SQL | Parameterize |
| Specific login errors / plain compare | Generic "Invalid credentials", bcrypt/Argon2, constant-time compare, rate limit |
| `verify=false`, CORS `*`, HTTP, MD5/SHA1 | Insecure defaults — fix |
| `err.toString()` to client | Leaks internals — sanitize |
| Unfamiliar package | Verify it exists on npm/PyPI (hallucination squatting) |
| Author "can't explain it" | Red flag — block merge |

## Thresholds & numbers
- 70/30 split; future gap maybe 5–10%, never zero (Ch 3, 11).
- 25–33% of Copilot code had potential CWEs; ~40% vulnerable (2021) (Ch 6, 8).
- Canary ~5% with rollback ready (Ch 8).
- Prototype loop ~a dozen iterations/hour (Ch 6).
- Few-shot: 2–5 examples (Ch 2).

## Prototype → production (Ch 6)
Architecture → errors/edge cases → performance → security → docs → tests → replace hacks. Keep a North Star sentence; stub non-core; log every shortcut as TODO.

## Ethics quick calls (Ch 9)
- Near-verbatim/author comments → search, then attribute, rewrite, or drop ("when in doubt, leave it out").
- GPL/AGPL into closed product → don't.
- PII/secrets in prompts → synthetic data.
- Automated decisions about people → notify, consent, override path.
- OSS contribution → check AI policy, disclose.

## Agents (Ch 10, 11)
- Review the **plan** before code. Sandbox can't run tests → fix environment first.
- Parallel agents → disjoint scopes, integration order.
- 80%-right PR on low-value task → weigh discard vs. last 20% (sunk cost).
- Agents write code → humans write tests (or vice versa).
