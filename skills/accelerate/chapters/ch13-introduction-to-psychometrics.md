# Chapter 13: Introduction to Psychometrics
*Authors: Nicole Forsgren, Jez Humble, Gene Kim*

## Core Idea
Survey data can be trusted when concepts are measured as **latent constructs**. Several well-written items (manifest variables) are validated statistically for convergent and discriminant validity and for reliability, then averaged into a score. Multiple measures guard against bad items and bad actors, and the same logic applies to system data, because **all measures are proxies**.

## Frameworks Introduced
- **Latent construct measurement**: measure something that can't be measured directly (e.g., organizational culture) through its component parts, the **manifest variables**, captured by survey items.
  - When to use: use it for any multifaceted concept (culture, identity, leadership, monitoring practice) or any conceptual system property (e.g., "performance").
  - How:
    1. Define the construct clearly, grounded in theory (e.g., the Westrum typology for culture).
    2. Write one item per aspect. Items overlap like a Venn diagram around the core concept.
    3. Pilot, then collect the full data.
    4. Run validity tests (convergent, discriminant) and reliability tests *before* any analysis.
    5. Average the item scores into a single construct score.
    6. Retest periodically, especially if the system or environment changes.
  - Why it works: (1) it forces careful thought about what you measure and how you define it; (2) it gives several views into the system, which exposes rogue data; (3) it makes it harder for a single bad data source, through misunderstanding or a bad actor, to skew results.
  - Failure mode: a construct that passes a small pilot can split under the full data (see Worked Example). Constructs protect you only if they're *periodically retested* and keep showing good psychometric properties.
- **Validity and reliability tests**:
  - **Convergent validity**: items that should be related are actually related.
  - **Discriminant validity**: items that should not be related are actually unrelated.
  - **Reliability (internal consistency)**: respondents read and interpret the items similarly.
  - When a construct passes all of these, it "exhibits good psychometric properties".
- **Survey item quality checklist** (weaknesses to avoid): leading questions, loaded questions, multiple questions in one, and unclear language. See Anti-patterns.

## Key Concepts
- **Latent construct**: an unobservable concept measured through several observable items.
- **Manifest variable**: a measurable piece of a latent variable. Each survey item measures one.
- **Survey item**: what is usually called a "question" but is actually a statement rated for agreement.
- **Push poll (propaganda survey)**: a survey with an obvious agenda. Its questions are hard to answer honestly unless you already agree.
- **Quick survey**: a single-question survey. It is acceptable only when well written and well understood, and it supports only narrow conclusions. NPS is the good example.
- **Good psychometric properties**: passing the validity and reliability tests.
- **Proactive failure notification**: failure alerts from logging and monitoring systems, plus threshold and rate-of-change health monitoring. It is a technical capability that is *predictive of* software delivery performance.
- **All measures are proxies**: response time is a proxy for system performance, just as survey items are proxies for culture.
- **Team-level measurement**: Westrum items are asked about the *team*, not the organization. Organizations contain pockets of different cultures, and people answer more accurately about their own team.

## Mental Models
- Think of a construct score as an "organizational culture temperature" built by averaging items, since culture can't be read off a thermometer.
- Use several measures whenever one metric could silently break. A code change to a metrics collector goes unnoticed if that metric is your only barometer.
- Think of survey items as a Venn diagram. Each item captures one related facet, and the overlap is the concept.
- Use surveys for lived experience. Culture *is* the lived experience of a team, so asking people is the appropriate measurement.

## Anti-patterns
- **Leading questions**: they bias the respondent in a direction. Ask "How would you describe Napoleon's height?", not "Was Napoleon short?"
- **Loaded questions**: they force an answer that isn't true for the respondent. "Where did you take your certification exam?" assumes they took one.
- **Multiple questions in one (double-barreled)**: "Are you notified of failures by your customers and the NOC?" You can't tell which part was answered.
- **Unclear language**: use terms familiar to respondents, and clarify or give examples when needed.
- **Push polling**: e.g., the February 2017 "Mainstream Media Accountability Survey". Its tactics were us-vs.-them framing ("our movement"), giving information instead of asking ("Were you aware that a poll... revealed a majority..."), appeals to belonging, and polarizing words ("noise").
- **Vague single-item culture questions**: "Is your culture good?" and "Do you like your team's culture?" leave culture, good, and like undefined, so the answers are uninterpretable.
- **Single-metric dashboards**: if the one data point goes bad, you won't know.

## Code Examples
```
Westrum organizational culture construct (team level)
"On my team ..."
  - Information is actively sought.
  - Messengers are not punished when they deliver news of failures or other bad news.
  - Responsibilities are shared.
  - Cross-functional collaboration is encouraged and rewarded.
  - Failure causes inquiry.
  - New ideas are welcomed.
  - Failures are treated primarily as opportunities to improve the system.
Scale: 1 = Strongly disagree ... 7 = Strongly agree
Culture score = mean(7 items)
```
What it demonstrates: a validated, reliable 7-item construct that any team can use to take its culture's "temperature".

```
Failure notification items (pilot: ~20 professionals → loaded as one construct)
Final data → split into TWO constructs:
 A) Notifications from outside automated processes
    - We are primarily notified of failures by reports from customers.
    - We are primarily notified of failures by the NOC.
 B) Proactive failure notification (predictive of software delivery performance)
    - We get failure alerts from logging and monitoring systems.
    - We monitor system health based on threshold warnings (ex. CPU exceeds 90%).
    - We monitor system health based on rate-of-change warnings
      (ex. CPU usage has increased by 25% over the last 10 minutes).
```
What it demonstrates: statistical confirmation reshaping a construct. Validity tests revealed two distinct concepts that a single question would have hidden.

## Reference Tables
**Table 13.1 Westrum's Typology of Organizational Culture**
| Pathological (Power-Oriented) | Bureaucratic (Rule-Oriented) | Generative (Performance-Oriented) |
|---|---|---|
| Low cooperation | Modest cooperation | High cooperation |
| Messengers "shot" | Messengers neglected | Messengers trained |
| Responsibilities shirked | Narrow responsibilities | Risks are shared |
| Bridging discouraged | Bridging tolerated | Bridging encouraged |
| Failure leads to scapegoating | Failure leads to justice | Failure leads to enquiry |
| Novelty crushed | Novelty leads to problems | Novelty implemented |

**How latent constructs protect data quality**
| Mechanism | Survey data | System data |
|---|---|---|
| Careful definition | Define "culture" as high trust, information flow, bridging, novelty, and shared risk | Define what "performance" really means beyond response time |
| Several views | Multiple items expose a rogue item | Multiple metrics show similar patterns |
| Resistance to bad sources | One liar or misreader can't skew the construct | One broken collector is caught by the others |

## Worked Example
**Defining culture before measuring it.** A team wants to measure culture and drafts "Is your culture good?". Interrogate it. *Which* culture: team, organization, or national? What does *good* mean: trusting, fun? Can a culture be entirely good? The revised "Do you like your team's culture?" fixes the level but leaves culture and *like* undefined. The fix:
1. Adopt a theory-based definition: a culture that optimizes trust and information flow, builds bridges across teams, encourages novelty, and shares risks. This is Westrum's generative culture.
2. Write one item per aspect (the 7 "On my team..." items) on a 1–7 agreement scale.
3. Ask at team level, which departs from Westrum's organization-level frame.
4. Confirm convergent and discriminant validity and reliability, then average the items into the culture score.
5. Retest periodically. As the failure-notification case shows, constructs can split or drift.

## Key Takeaways
1. Never measure a multifaceted concept with one vague question. Define it from theory and write several items.
2. Audit every survey item for leading, loaded, double-barreled, and unclear wording.
3. Run convergent validity, discriminant validity, and reliability tests before analyzing, and retest periodically.
4. Ask about the team, not the organization, for more accurate answers.
5. Treat every metric (survey or system) as a proxy. Back important ones with several related measures so drift or tampering shows up.
6. Use NPS-style quick surveys only for narrow conclusions. Their advantage is comparability across teams and companies.
7. Invest in proactive failure notification (system alerts plus threshold and rate-of-change monitoring), which predicts software delivery performance.

## Connects To
- **Ch 3**: Westrum organizational culture, the construct measured here.
- **Ch 7**: proactive monitoring and failure notification as a capability.
- **Ch 10 / Ch 11**: identity and transformational leadership are latent constructs built the same way; NPS is the good quick survey.
- **Ch 12**: the Likert-type quantitative data these constructs produce.
- **Ch 14**: why surveys are used, including how they hold up against bad actors.
- **Appendix C**: the statistical tests behind validity and reliability.
- **External: Westrum (2004)**: the typology of organizational culture.
- **External: Psychometrics / construct validity**: the field these methods come from.
