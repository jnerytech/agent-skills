# Chapter 8: Gathering and Integrating Feedback

## Core Idea
Docs are a conversation: users expect to talk back. Build scalable **feedback channels**, then **triage** each item with three questions — Is it valid? Can it be fixed? How important is it? — and follow up so users know they were heard.

## Frameworks Introduced
- **Feedback channels** (pick a few, respect users' time — they came to learn, not to give feedback):
  - **Direct page feedback** — issue/email link on each page (append title+URL); route into the same issue tracker as code; use an **issue template** to structure reports. Most granular.
  - **Monitor support issues** — partner with the support team; repeated issues need a doc or product fix.
  - **Document sentiment** — simple yes/no "was this helpful?" widget; needs many responses; highly contextual (troubleshooting pages rate low because readers arrive frustrated).
  - **User surveys** — focused, measurable questions; yields a **CSAT** (customer satisfaction) score; embed short ones, email long ones.
  - **User council** — a small group of critical users/early adopters giving ongoing feedback and evangelizing.
- **The three triage questions**: (1) Is the issue **valid** (relevant to docs)? (2) Can it be **fixed** (actionable)? (3) How **important** (priority)?
- **Actionable = Original + Reproducible + Scoped**: not a duplicate, reproducible (not their local env), and narrowed to a specific fixable change.

## Key Concepts
- **Triage**: sorting/prioritizing feedback — "not all opinions deserve consideration, and not every great idea deserves immediate action." Directs limited resources to the most impactful changes.
- **Trust but verify**: assume good intent, but confirm validity — route product/support feedback to the right team.
- **Priority scheme** (Chromium example): P0 emergency → P1 needed-for-release → P2 wanted → P3 not time-sensitive. Consistent, glance-readable.
- **Follow up**: ask for more info when you can't reproduce; tell users when fixed; praise great reporters in release notes/blog.

## Mental Models
- One-to-one feedback (a meeting with Mei) doesn't scale → build channels before "whack-a-mole" sets in.
- Triaging docs feedback is no different from triaging code issues — reuse the same system.
- Bump priority when an issue has many duplicates (a signal of real demand).

## Code Examples
Markdown issue template that guides users toward useful reports:
```markdown
## Title
<!-- Provide a short summary of the issue -->
## Document URL
<!-- Copy and paste the relevant URL(s) here -->
## What's wrong or missing?
<!-- Clearly explain the specific impact. Attach screenshots if needed. -->
## Possible solution
<!-- Not required. Describe how the document can be more helpful. -->
```
- **What it demonstrates**: structure steers users away from cryptic feedback toward originality + scope.

## Reference Tables
Triage decision flow:

| Step | Question | If "no" |
|---|---|---|
| 1 | Is it valid (about the docs)? | Route to product/support team |
| 2 | Is it actionable (original, reproducible, scoped)? | Close duplicates / ask for repro info / narrow scope |
| 3 | What priority (P0–P3)? | Backlog low-priority items |

## Worked Example
**Karthik gathers Corg.ly feedback.** Two weeks post-launch he emails Mei a short questionnaire, then meets her. Mei reports the docs don't cover bark-length formatting parameters — some of her issues are doc bugs, some product bugs. Mei herself asks: "Is there a better way to get you feedback? This won't scale." That realization drives the chapter: build channels (page feedback, sentiment, surveys, a user council Mei would be perfect for), triage each issue (valid? fixable? priority?), and close the loop by telling Mei's team what was fixed.

## Anti-patterns
- **Ad-hoc-only feedback** (email/DMs) that can't scale → whack-a-mole.
- **Implementing every channel** — wastes your and users' time; pick the useful few.
- **Acting on unscoped feedback** ("these docs didn't help") without narrowing it.
- **Not following up** — users stop bothering if they feel unheard.

## Key Takeaways
1. Give users scalable channels to talk back; choose a focused few.
2. Triage every item: valid → fixable → prioritized.
3. Actionable feedback is original, reproducible, and scoped.
4. Reuse your code issue-tracking and priority systems for docs.
5. Always follow up; thank and credit great contributors.

## Connects To
- **Ch 1**: feedback validates/corrects the user assumptions from research.
- **Ch 7**: feedback is the iteration loop after publishing.
- **Ch 9**: feedback and metrics together measure documentation quality.
- **Ch 11**: recurring issues feed maintenance priorities.
