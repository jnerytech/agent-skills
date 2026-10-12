# Chapter 9: Measuring Documentation Quality

## Core Idea
**A document is good when it fulfills its purpose.** Split quality into **functional** (does it achieve its goal?) and **structural** (is it well-written?) — functional matters more. Then build an **analytics strategy** that aligns org goals, reader goals, and doc goals before chasing metrics.

## Frameworks Introduced
- **Functional quality** (does the doc *work*?) — five components:
  - **Accessible**: reader's language, ~10th-grade reading level (Flesch-Kincaid / ARI / Coleman-Liau), alt text, captions.
  - **Purposeful**: title + first paragraph state the goal; goals align org + reader. Measure with **Time to Hello World (TTHW)** — how fast a new dev gets a basic example working; faster = easier adoption.
  - **Findable**: readers navigate *to* and *through* content. "The real findability problem is getting readers from the wrong place deep within your content to the right place deep within your content" (Mark Baker).
  - **Accurate**: correct, up-to-date, working samples; test and automate sample tests.
  - **Complete**: all prerequisites, all tasks, all next steps (or every command, for a reference).
- **Structural quality** = the **3 Cs**: **Clear, Concise, Consistent**.
  - Clear: logical headers, unambiguous step outcomes, no undefined jargon.
  - Concise: "brief but comprehensive" (Strunk: no unnecessary words).
  - Consistent: same structure, same term for the same thing ("authenticating", never also "connecting").
- **Analytics strategy**: define and align (1) org goals + metrics, (2) reader goals + metrics, (3) doc goals + metrics.

## Key Concepts
- **Functional > structural**: a beautiful doc that fails its goal is poor; a rough doc that achieves its goal is good. Don't over-measure structural just because it's easier to count.
- **Org goals** (revenue-tied): acquire/onboard users, drive feature adoption, retention, reduce support load.
- **Reader goals** (task-specific): "sign up for the API", "authenticate", "fix an error".
- **Metric vocabulary**: unique visitors, page views, time on page, bounce rate, search keywords, reading level, doc-related support issues, link validation, TTHW.

## Mental Models
- More metrics ≠ more answers; numbers create an "illusion of an answer." Start from the question, not the dashboard.
- Always ask: "Is this document fulfilling its purpose?"

## Reference Tables
The five tips for using metrics:

| Tip | Why |
|---|---|
| Make a plan | Why measure? What will you do with it? How does it advance org goals? (Bob Watson) |
| Establish a baseline | No before → can't judge after |
| Consider context | Rising error-page views may be bad; rising getting-started views good |
| Use clusters of metrics | One metric misleads; correlate several |
| Mix qualitative + quantitative | Hard numbers + user studies/support/feedback |

Questions → metrics mapping (Table 9-3):

| Question | Metric |
|---|---|
| How many read the docs? | unique visits |
| Which docs most? | page views |
| How long to get started? | TTHW |
| How do they find it? | findability: search keywords, links, inbound traffic |
| Problems to fix? | issues filed + link validation |

## Worked Example
**Measuring "Getting Started with the Corg.ly API."** Charlotte wonders if the docs are any good despite rising signups. Applying the framework: the doc is *purposeful* (title = goal), so she measures **TTHW** — time for a new user to reach their first API call. She maps reader goals to metrics: "sign up" → increased signups; "get access" → increased access requests; "learn basics" → increased active users. She uses a *cluster*: rising support issues after publishing troubleshooting docs could mean failure — *or* an influx of new users filing fewer cases each, *or* a findability problem. Only the cluster + qualitative feedback disambiguates.

## Anti-patterns
- **Metric-chasing without a question** — adrift in dashboards.
- **Optimizing structural quality** (word count, time on page) because it's measurable, while ignoring task success.
- **Judging one metric in isolation** without context.

## Key Takeaways
1. A doc is good when it fulfills its purpose; functional quality outranks structural.
2. Functional = Accessible, Purposeful, Findable, Accurate, Complete.
3. Structural = the 3 Cs: Clear, Concise, Consistent.
4. Use TTHW as a proxy for adoption ease.
5. Define org/reader/doc goals first; then baseline, contextualize, cluster, and mix qual+quant.

## Connects To
- **Ch 1**: org and reader goals come from user research.
- **Ch 8**: feedback is the qualitative half of measurement.
- **Ch 10**: findability is largely an information-architecture problem.
- **Ch 4**: the 3 Cs mirror the clarity/brevity editing pass.
