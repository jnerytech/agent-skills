# Chapter 1: Accelerate
*Authors: Nicole Forsgren, Jez Humble, Gene Kim (includes context from the Preface)*

## Core Idea
Software is the engine of organizational acceleration, and improvement comes from investing in a set of evidence-based **capabilities** (24 of them) that predict software delivery and organizational performance — not from climbing a maturity model. Improvement is possible for every team, provided leadership gives consistent support (time, actions, resources) and team members commit to the work.

## Frameworks Introduced
- **Capabilities model (vs. maturity model)**: measure and improve a set of capabilities ("levers") tied to outcomes, continuously, rather than aiming to "arrive" at a mature level. Four reasons it beats maturity models:
  1. **Continuous vs. terminal** — maturity models aim to reach a state and declare "done"; capability models assume the landscape keeps changing and improvement never ends.
  2. **Multidimensional vs. lock-step** — maturity models prescribe the same linear "Level 1 → Level 2" path for everyone; capability models let each team pick the capabilities that pay off most in its own context, systems, goals and constraints.
  3. **Outcome-based vs. vanity metrics** — capability models link levers to key outcomes; maturity models typically count tooling installed or technical proficiency, which says nothing about business impact.
  4. **Dynamic vs. static** — what is "high-performing" this year is not good enough next year.
  - When to use: planning or assessing any technology/DevOps transformation; choosing what to improve next.
  - How: (a) measure outcomes (software delivery performance, Ch 2); (b) assess the 24 capabilities (Appendix A); (c) pick the constraining capabilities for your context; (d) set team-level, time-bound improvement goals; (e) remeasure and repeat.
  - Why it works / failure mode: it keeps the organization in a continuous-improvement loop tied to measured outcomes. Failure mode: treating a capability list as a new checklist/maturity ladder, or optimizing measures not linked to outcomes.
- **Evidence-based transformation**: choose capabilities based on statistically validated predictors of performance, not on vendor products, consultant offerings, homegrown assessments, internal champions' skill sets — and avoid analysis paralysis from too many improvement areas.
  - When to use: when stakeholders disagree on what to fix first.
  - How: anchor decisions in the research findings; reject factors shown not to predict performance (see Reference Tables).
- **Organizations must accelerate** four things: (1) delivery of goods and services to delight customers; (2) engagement with the market to detect and understand customer demand; (3) anticipation of compliance and regulatory changes; (4) response to potential risks (security threats, economic changes).

## Key Concepts
- **24 key capabilities**: the research-identified levers that drive software delivery performance and, in turn, organizational performance; easy to define, measure and improve (listed in Appendix A).
- **Software delivery performance**: the outcome measure of tempo and stability (defined in Ch 2); the gap between high and low performers keeps growing.
- **Organizational performance**: profitability, productivity, market share — plus noncommercial outcomes (effectiveness, efficiency, customer satisfaction).
- **Cross-sectional study**: the research design used (same as in healthcare/workplace research) — survey data at points in time, analyzed with academic rigor and published in peer-reviewed journals.
- **Snowball sampling**: invitations via mailing lists and social media, with respondents inviting peers (justified in Ch 15).
- **Likert-type questions**: introduced in 2014 instead of yes/no items, giving "shades of gray" and enabling deeper analysis.
- **Executive overestimation gap**: executives overestimate DevOps progress versus practitioners (Forrester, Klavens et al. 2017) — implying more untapped value than leaders realize and the need for accurate measurement.
- **Tempo vs. stability**: tempo = deployment frequency + lead time; stability = time to recover + change failure rate. High performers get both by building quality in.

## Mental Models
- Think of capabilities as **levers**: you pull the ones that move your outcomes most in your context, rather than climbing a ladder.
- Use "never mature, never done" as the stance: the best keep getting better year over year; those who don't improve fall further behind.
- Think of the executive-vs-practitioner gap as a **measurement problem**: trust the people closer to the work and instrument the capabilities so leaders decide on data.
- Use "speed and stability are not a trade-off" as the default assumption — when low performers push tempo without building quality in, stability collapses.

## Anti-patterns
- **Maturity models**: encourage "arrive and stop," impose one linear path on all teams, measure tool install base (vanity metrics), and ignore a changing landscape.
- **Vendor- or consultant-driven capability selection**: picks levers that fit someone's product or offering, not your constraints.
- **Analysis paralysis**: trying to improve everything at once.
- **Increasing tempo without building quality in**: low performers in 2017 narrowed the tempo gap but widened the stability gap — larger deployment failures and longer restores.
- **Blaming legacy tech, deployer role or lack of a CAB**: none of these predicted performance.

## Reference Tables

**2017: high performers vs. low performers**

| Measure | High performers vs. low |
|---|---|
| Deployment frequency | 46 times more frequent code deployments |
| Lead time (commit to deploy) | 440 times faster |
| Mean time to recover from downtime | 170 times faster |
| Change failure rate | 5 times lower (1/5 as likely for a change to fail) |

Versus 2016: gap **narrowed for tempo** (deployment frequency, lead time) and **widened for stability** (MTTR, change failure rate).

**Factors that did NOT predict performance**

| Often-cited factor | Finding |
|---|---|
| Age/technology of the application (mainframe "systems of record" vs. greenfield "systems of engagement") | Not predictive |
| Whether ops or dev teams perform deployments | Not predictive |
| Whether a change approval board (CAB) is implemented | Not predictive |

**Research timeline (Preface) — State of DevOps Reports with Puppet, 2014–2017; 23,000+ survey responses, 2,000+ unique organizations (from <5 to >10,000 employees), regulated and unregulated industries, greenfield and legacy**

| Year | Focus | Key questions / results |
|---|---|---|
| 2014 | Laying the foundation: delivery performance and organizational performance | Can software delivery be measured? Does it impact organizations? Does culture matter and how to measure it? Which technical practices matter? Found: delivery is measurable in a statistically meaningful way; throughput and stability move together; delivery capability impacts profitability, productivity, market share; culture and technical practices matter. Switched to Likert-type items. |
| 2015 | Extending and deepening | Revalidate delivery → organizational performance; do technical practices/automation and Lean management practices impact delivery; do they affect deployment anxiety and burnout? Hypotheses supported. |
| 2016 | Technical practices and the "fuzzy front end" | Security integration, trunk-based development, test data management; Lean product management; quality measures (defects, rework, security remediation); employee Net Promoter Score (eNPS) and work identity. |
| 2017 | Architecture, leaders, not-for-profit | Which architectural practices drive delivery? How does transformational leadership impact delivery? Does delivery impact noncommercial outcomes? |

Pre-history: in 2012 Puppet invited Gene Kim into the second iteration of its DevOps study; Jez Humble joined; ~4,000 responses — then the largest survey of its kind. Nicole Forsgren joined in late 2013 for the 2014 report.

**Book structure**: Part I = findings; Part II = science and research behind them; Part III = case study of a transformation.

## Worked Example
**Reading the 2016→2017 gap shift.** In 2017 low performers began increasing deployment frequency and shortening lead time (tempo gap narrowed), but their time to restore and change failure rate got relatively worse (stability gap widened). The authors' interpretation (speculative, flagged as such): low performers pushed tempo ("work harder") without investing in building quality into the process — producing bigger deployment failures that take longer to restore. High performers, by contrast, maintained or improved on all four measures. Practitioner lesson: when you start shipping faster, track stability measures in parallel; if change failure rate or MTTR worsens, invest in test automation, architecture and process, not more pressure.

## Key Takeaways
1. Replace maturity assessments with a capabilities model tied to measured outcomes; never declare the transformation "done."
2. Pick the next capabilities to improve based on your team's context and the evidence, not vendor or consultant preference.
3. Measure DevOps capabilities directly and report them to leaders — executives tend to overestimate progress.
4. Don't attribute low performance to legacy stacks, who deploys, or the absence of a CAB — those factors don't predict performance.
5. Improve tempo and stability together; speed gained without built-in quality leaks out as failures and slow recovery.
6. Expect the bar to move every year: last year's "high performer" level is next year's average.
7. Secure consistent leadership support (time, actions, resources) — it is the precondition for improvement anywhere.

## Connects To
- **Ch 2**: defines the four software delivery performance measures and performer clusters behind the 46x/440x/170x/5x figures.
- **Ch 3**: culture as a measurable, predictive construct (2014 question "does culture matter?").
- **Ch 4**: technical practices / continuous delivery capabilities.
- **Ch 5, 6, 7, 8, 11**: architecture, infosec, Lean management, Lean product management, transformational leadership — the year-by-year research extensions.
- **Ch 12–15**: inferential prediction, psychometrics, why surveys, snowball sampling.
- **Appendix A**: the full list of 24 capabilities.
- **Continuous improvement / Kaizen** (Lean): the paradigm capability models embody.
- **James Bessen (2017); McAfee & Brynjolfsson (2008)**: external evidence that strategic technology use explains revenue, productivity and profitability.
