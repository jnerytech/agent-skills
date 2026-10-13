# Chapter 11b: When to Switch Off the AI

## Core Idea
For some code categories the right constraint is the absence of the AI. The question is never "can the AI do this?" but "what happens when it gets this wrong, and will the guardrails catch it before it matters?" Autonomy is a function of blast radius, not model capability.

## Frameworks Introduced
- **Risk Asymmetry Test**: decide AI involvement by the cost and visibility of failure.
  - When to use: before handing any code category to an agent.
  - How: (1) Ask what a wrong implementation costs: a failing test or structured gripe (cheap) vs a breach, regulatory fine, corrupted financial record, or exploitable crypto weakness (expensive). (2) Ask whether any gate would catch it: the Inquisitor catches only what it was pointed at. (3) Cheap + caught → let the agent run. Expensive + invisible → human authorship or supervised use.

- **The No-AI List** (current state, not permanent prohibitions):
  - When to use: as the default human-authored categories.
  - How:
    - **Cryptographic implementations**: never let AI implement primitives, KDFs, token schemes, or signatures; use audited libraries and let the AI *call* them.
    - **Legally regulated output paths** (financial reporting, medical records, accessibility, GDPR decisions, tax): the AI doesn't know which field triggers which statute; requires human authorship plus legal review.
    - **Safety-critical control paths** (aircraft, medical devices, physical infrastructure): the verification process (formal methods, DO-178C, IEC 62443) is incompatible with "generate, test, ship".
    - **Security boundary decisions**: humans decide where the boundary is (untrusted data, authorization, sensitive fields); the AI may implement the check once placed.
    - **Key rotation and secret management**: AI puts secrets in env vars instead of a secrets manager, logs them "for debugging", caches past rotation.
    - **Production data migrations**: AI may draft; the final one needs human review of every transformation and non-negotiable sign-off, plus expand-contract (Ch 18).

- **Supervised Use Zone**: AI drafts; a qualified human reviews against a risk class named in advance.
  - When to use: between "AI authors freely" and "human authors exclusively".
  - How: (1) Add a directory-scoped Tier 2 context file stating it is a supervised zone, the specific risk, and the extra verification required. (2) Mark classes with VibeTags `@AIRegulation` (or the same rule written by hand in the Tier 2 file, §4.8). (3) Add a CI check that flags changes to annotated classes for mandatory specialist review, separate from normal PR approval. (4) The specialist checks the named risk (e.g. timing attacks and key handling for crypto; edge cases against the rule for finance), not "does it look right".

- **AI Commit Percentage by Risk Tier**: replace aggregate AI-commit percentage with a per-tier breakdown.
  - When to use: any org measuring AI adoption.
  - How: report freely-generated code, supervised-zone code (human-led, AI-assisted), and prohibited-category code (human-authored, full stop) separately.

## Key Concepts
- **Quiet, fluent failure**: AI code that looks correct, passes checks, and is silently wrong.
- **Guardrail ceiling**: automated review catches only what rules describe; novel crypto flaws pass every check.
- **Blast radius**: the damage scope of a mistake, which determines allowed autonomy.
- **Supervised use**: targeted specialist review of a pre-identified risk class, unlike general PR review.
- **`@AIRegulation`**: VibeTags annotation marking regulated classes for specialist sign-off.
- **Prohibited category**: code that stays human-authored regardless of adoption targets.

## Mental Models
- Think of the AI as a power tool, not a replacement for architectural judgment; part of judgment is knowing which tasks to keep.
- Use "let it implement, don't let it design" for security: it can write the access check, not decide where it belongs.
- Treat the No-AI list as a snapshot; revisit as models improve.

## Anti-patterns
- **Aggregate AI-commit-percentage targets**: create pressure to use AI in the no-AI categories.
- **AI-implemented crypto**: right imports, right parameter names, explanatory comment, and subtle timing/edge-case vulnerabilities.
- **Generic PR review for high-risk code**: reviewers looking for "any problems" miss the specific risk class.
- **AI-authored final production migrations**: the failure is unrecoverable data, not a test failure.

## Reference Tables
| Zone | Who authors | Review | Examples |
|---|---|---|---|
| Free | AI | Standard gates | Feature code |
| Supervised | AI drafts, human-led | Specialist verifies the named risk; CI-flagged | Financial calc, crypto *usage* |
| Prohibited | Human, full stop | Specialist/legal | Crypto primitives, security model design, key management, safety-critical control |

## Worked Example
A team uses AI for 90% of its feature code and 0% of its cryptographic implementations: correct Vibe Architecture. Another uses AI for 95% of everything including its key-management layer: incorrect, whatever the aggregate number looks like.

## Key Takeaways
1. Gate AI autonomy by blast radius and detectability, not capability.
2. Keep crypto primitives, regulated outputs, safety-critical control, security-boundary design, secrets handling, and final production migrations human-authored.
3. Use supervised zones with Tier 2 context, `@AIRegulation`, and CI-forced specialist review.
4. Measure AI usage per risk tier, never as a single adoption number.

## Connects To
- **Ch 22**: Inquisitor and the guardrail ceiling.
- **Ch 3**: Tier 2 directory-scoped context files.
- **Ch 4 (§4.8)**: VibeTags `@AIRegulation` and its hand-written form.
- **Ch 18**: expand-contract for migrations.
- **Ch 11e**: measuring Vibe Architecture.
- **DO-178C, IEC 62443**; **Use audited crypto libraries ("don't roll your own crypto")**.
