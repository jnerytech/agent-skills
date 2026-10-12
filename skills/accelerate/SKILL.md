---
name: accelerate
description: "Knowledge base from \"Accelerate: The Science of Lean Software and DevOps\" by Nicole Forsgren, Jez Humble & Gene Kim. Use when applying the authors' frameworks for the four key metrics (DORA), the 24 capabilities, continuous delivery, loosely coupled architecture, Westrum culture, Lean management, transformational leadership, or survey-based measurement — studying the book, or referencing its concepts."
---

<!-- argument-hint: [topic, framework name, or chapter number] -->

# Accelerate: The Science of Lean Software and DevOps
**Authors**: Nicole Forsgren, Jez Humble, Gene Kim | **Pages**: ~315 | **Chapters**: 16 + Conclusion & Appendices A–C | **Generated**: 2026-10-05

## How to Use This Skill

- **Without arguments** — load core frameworks for reference
- **With a topic** — ask about `lead time`, `Westrum`, `trunk-based development`, etc.; I find and read the relevant chapter
- **With chapter** — ask for `ch05`; I load that specific chapter
- **Browse** — ask "what chapters do you have?" to see the full index

When you ask about a topic not covered in Core Frameworks below, I will read
the relevant chapter file before answering.

---

## Core Frameworks & Mental Models

**Thesis:** Software delivery performance is measurable, it predicts organizational performance (profitability, productivity, market share — high performers are 2× as likely to exceed goals), and it is improved by specific, learnable capabilities. Based on four years of State of DevOps surveys (2014–2017, 23,000+ responses, 2,000+ organizations).

### The four key metrics (Ch 2)
- **Lead time for changes** (commit → running in production), **deployment frequency**, **time to restore service**, **change fail rate**. Tempo = first two; stability = last two.
- **Speed and stability are not a trade-off** — high performers win on both: 46× more frequent deploys, 440× faster lead time, 170× faster recovery, 5× lower change fail rate (2017).
- A good measure is a **global outcome** (dev and ops share it) and an **outcome, not output**. Reject lines of code, velocity, utilization as productivity measures.
- Measure the **delivery** part of lead time, not the "fuzzy front end" of design.
- Use metrics for learning, never control: "whenever there is fear, you get the wrong numbers."

### Capabilities, not maturity (Ch 1, 17)
Prefer a **capabilities model** (outcome-based, multidimensional, continuous) over a **maturity model** (linear, static, "done"). The research found **24 capabilities** that drive delivery performance:
- **Continuous delivery (8)**: version control for all production artifacts; deployment automation; continuous integration; trunk-based development; test automation; test data management; shift left on security; continuous delivery.
- **Architecture (2)**: loosely coupled architecture; architect for empowered teams (teams choose tools).
- **Product & process (4)**: customer feedback; visible flow through the value stream; small batches; team experimentation.
- **Lean management & monitoring (5)**: lightweight change approval; monitoring to inform business decisions; proactive system-health checks; WIP limits; visualizing work.
- **Culture (5)**: generative (Westrum) culture; learning; collaboration among teams; meaningful work with good tools; transformational leadership.

### Culture: Westrum typology (Ch 3)
- **Pathological** (power-oriented) → **bureaucratic** (rule-oriented) → **generative** (performance-oriented), defined by how information flows. Generative culture predicts delivery and organizational performance and lower burnout.
- Measure with 7 Likert items (information actively sought, messengers not punished, shared responsibilities, cross-functional collaboration, failure → inquiry, new ideas welcomed, failures as system-improvement opportunities).
- **Change culture by changing practices** — CD and Lean management improve culture ("act your way to a better culture").

### Technical practices (Ch 4–6)
- CD = deployable at all times + fast feedback + deploy on demand, built on configuration management, CI and continuous testing. Trunk-based development: < 3 active branches, merged within a day, no code freezes. Developers own the tests.
- CD predicts lower change fail rate, less rework (21% vs 27%), less deployment pain, less burnout, and stronger identification with the organization.
- **Loosely coupled architecture** was the biggest contributor to CD in 2017: teams can test and deploy on demand without coordination. Coupling matters more than technology type. Use the **Inverse Conway Maneuver**.
- **Shift left on security**: infosec in design, preapproved tools/libraries, automated security tests.

### Lean management & product (Ch 7, 8)
- **WIP limits + visual displays + monitoring feedback** together predict performance and reduce burnout.
- **CABs** don't improve stability and hurt tempo; use peer review + deployment pipeline (satisfies segregation of duties).
- **Lean product management**: small batches (≤ 1 week), visible flow, customer feedback, team experimentation without outside approval. It forms a virtuous cycle with delivery performance.

### Sustainability, people and leadership (Ch 9–11, 16)
- **Deployment pain** signals poor practices; burnout is an organizational problem (Maslach's six risk factors), fixed by fixing the system.
- High performers' employees are 2.2× more likely to recommend their organization (eNPS).
- **Transformational leadership** — vision, inspirational communication, intellectual stimulation, supportive leadership, personal recognition — enables, but doesn't by itself produce, high performance. Invest in learning, cross-functional collaboration and tools.
- **ING case (Ch 16)**: Obeyas, stand-ups, catchball, Hoshin Kanri + PDCA, leaders as coaches; avoid copying practices ("implementation thinking").

### The science (Ch 12–15)
- Findings are **inferential prediction** (theory + regression), not proven causation — say "predicts/drives".
- Use validated **latent constructs** (several items, validity and reliability tested). Surveys measure culture and the full stack; system data is objective but partial; triangulate.

---

## Chapter Index

| # | Title | Key Frameworks |
|---|-------|----------------|
| [ch01](chapters/ch01-accelerate.md) | Accelerate (+ Preface) | Capabilities vs maturity, 24 capabilities |
| [ch02](chapters/ch02-measuring-performance.md) | Measuring Performance | Four key metrics, performer clusters |
| [ch03](chapters/ch03-measuring-changing-culture.md) | Measuring and Changing Culture | Westrum typology, survey items |
| [ch04](chapters/ch04-technical-practices.md) | Technical Practices | Continuous delivery, trunk-based dev, test automation |
| [ch05](chapters/ch05-architecture.md) | Architecture | Loose coupling, deployability, Inverse Conway |
| [ch06](chapters/ch06-integrating-infosec.md) | Integrating Infosec into the Delivery Lifecycle | Shift left, Rugged DevOps |
| [ch07](chapters/ch07-management-practices.md) | Management Practices for Software | WIP limits, visual displays, lightweight change approval |
| [ch08](chapters/ch08-product-development.md) | Product Development | Lean product management, small batches, experimentation |
| [ch09](chapters/ch09-making-work-sustainable.md) | Making Work Sustainable | Deployment pain, burnout risk factors |
| [ch10](chapters/ch10-employee-satisfaction-identity-engagement.md) | Employee Satisfaction, Identity, and Engagement | eNPS, identity, diversity |
| [ch11](chapters/ch11-leaders-and-managers.md) | Leaders and Managers | Transformational leadership, investing in teams |
| [ch12](chapters/ch12-science-behind-this-book.md) | The Science Behind This Book | Types of analysis, inferential prediction |
| [ch13](chapters/ch13-introduction-to-psychometrics.md) | Introduction to Psychometrics | Latent constructs, validity, reliability |
| [ch14](chapters/ch14-why-use-a-survey.md) | Why Use a Survey | Survey vs system data, bad actors |
| [ch15](chapters/ch15-data-for-the-project.md) | The Data for the Project | Snowball sampling, triangulation |
| [ch16](chapters/ch16-high-performance-leadership-management.md) | High-Performance Leadership and Management | ING Obeya, catchball, Hoshin Kanri |
| [ch17](chapters/ch17-conclusion-and-appendices.md) | Conclusion + Appendices A–C | 24 capabilities list, the stats, statistical methods |

## Topic Index

- **24 capabilities** → ch01, ch17
- **Architecture / loose coupling** → ch05
- **Burnout / deployment pain** → ch09, ch04
- **Change approval / CAB** → ch07
- **Continuous delivery / CI / trunk-based development** → ch04
- **Culture (Westrum)** → ch03, ch13
- **eNPS / identity / job satisfaction** → ch10
- **Diversity** → ch10
- **Four key metrics** → ch02, ch17
- **Leadership (transformational)** → ch11, ch16
- **Lean management / WIP / visual displays** → ch07, ch16
- **Lean product management / small batches** → ch08
- **Maturity vs capabilities models** → ch01
- **Psychometrics / survey design** → ch13, ch14, ch15
- **Security (shift left)** → ch04, ch06
- **Statistics / research methods** → ch12, ch17
- **Test automation / test data** → ch04

## Supporting Files

- [glossary.md](glossary.md) — all key terms with definitions
- [patterns.md](patterns.md) — all techniques and design patterns
- [cheatsheet.md](cheatsheet.md) — quick reference tables and decision guides

---

## Scope & Limits

This skill covers the book content only (research through 2017; later DORA reports added a fifth metric — reliability — and an "elite" cluster, which are not in this book). For hands-on implementation in your codebase,
combine with project-specific tools. For SRE practices, see the `google-sre` skill. For topics beyond this book, check related skills
or ask the agent directly.
