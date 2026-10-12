# Cheatsheet — Docs for Developers

## The pipeline (decide where you are)
Research → Plan → Draft → Edit → Code samples → Visuals → Publish → Feedback → Measure → Organize → Maintain/Deprecate.

## Decision rules
- **If you're the expert, you can't judge what a beginner needs** → do user research first (curse of knowledge).
- **If a user states a want** → dig for the underlying *need* (sports car vs. bus ticket).
- **If a doc has more than one goal** → split it into multiple docs (title = the single goal).
- **If a title starts with a verb** → it's a task (procedural); **if a noun** → it's reference.
- **If a tutorial exceeds ~10 steps** → scope too big, or the *product* is too complex — talk to engineers.
- **If a procedure step has 2+ actions** → split it; one action per step; end with a verify step.
- **If a code sample needs a long explanation** → the code is too complex; refactor the sample.
- **If you're writing `foo`/`bar`** → replace with descriptive placeholders (`replace_with_actual_bark`).
- **If you'd screenshot code/IPs** → don't; keep it copy-pastable.
- **If you're tempted by video** → first ask if a doc+images is cheaper (it usually is).
- **If a doc fits multiple locations** → keep one copy, link from the others (avoid automated reuse).
- **If writing and editing at once** → stop; draft first (bad is fine), edit later in passes.
- **If a release ships without the docs** → block it; dev docs ship *with* the code.
- **If nobody owns a doc** → it will go stale; assign an explicit owner.
- **If a page has low views + many issues + stale samples** → delete it, link to a lighter doc.
- **If you can't reproduce reported feedback** → ask for env/repro details (faster than guessing).
- **If automating** → understand every step first; bad automation compounds toil.

## Content type → use it for
| Type | Use for |
|---|---|
| Code comments | the *why* of code |
| README | repo summary, install, examples |
| Getting started | first-time, fastest path to working |
| Conceptual | how it works (no impl details) |
| Tutorial | learning in a safe sandbox |
| How-to guide | solving a real problem with real code |
| Reference (API/glossary/troubleshooting) | cause-and-effect lookup |
| Changelog / release notes | what changed (terse / rich context) |

## Editing — four passes in order
Technical accuracy → Completeness → Structure → Clarity & brevity. (Developer-known → user-wanted.)

## Quality model
- **A doc is good when it fulfills its purpose.**
- **Functional > structural.** Functional = Accessible · Purposeful · Findable · Accurate · Complete. Structural = the 3 Cs (Clear · Concise · Consistent).
- Beautiful-but-fails-goal = poor; rough-but-achieves-goal = good.

## Callout severity
Warning (danger / irreversible loss) > Caution (unexpected consequences) > Note (tip). Reserve for must-not-miss — avoid alert fatigue.

## Feedback triage
1. Valid? (about the docs — else route to product/support) →
2. Actionable? (Original + Reproducible + Scoped) →
3. Priority? P0 emergency · P1 needed-for-release · P2 wanted · P3 not-time-sensitive.

## Thresholds & defaults
- Reading level: **~10th grade** (Flesch-Kincaid / ARI / Coleman-Liau).
- Readers consume **≤28%** of a page; they skim in an **F-pattern**.
- Paragraphs: **≤5 sentences**.
- Code lines: wrap at **~80 chars**; use `...` for omissions.
- Lists: split if **>10 items**.
- User research sample: **3–5** well-fit participants per round.
- Color contrast: **≥4.5:1**; never color alone; publish diagrams as **SVG**.
- Freshness review reminder: e.g. every **6 months** to the owner.
- One use case per page; one idea per diagram.

## Publishing — "meet users where they are"
| Audience | Where |
|---|---|
| Internal teams | private wiki/intranet |
| External devs (code/endpoints) | same repo as code |
| End users/sysadmins installing | external to the software |
| External codebase users | website or repo |

## Tells & smells
- Users entering/leaving your site repeatedly → **findability** problem (can't get from "close" to "right").
- Rising error-page views → product/doc trouble (not success); rising getting-started views → good.
- "We documented it" but buried deep → IA failure; it's invisible to users.
- One broken/outdated sample → trust in docs *and* product collapses.
- Whack-a-mole feedback across email/Twitter/SO → you need real feedback channels.
- Docs drifting from code over releases → no owner / not release-coupled.

## Automation toolkit (kill toil)
Freshness checks · link checkers (htmltest) · prose linters (Vale) · ref generators (OpenAPI/Javadoc). Frameworks: **Diátaxis**, **Good Docs Project**, **C4** (diagrams). Community: **Write the Docs**.
