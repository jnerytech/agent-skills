# Chapter 3: Measuring and Changing Culture
*Authors: Nicole Forsgren, Jez Humble, Gene Kim*

## Core Idea
Culture can be measured as a valid, reliable construct using Ron Westrum's typology (pathological / bureaucratic / generative); generative culture predicts software delivery performance, organizational performance and job satisfaction — and you change culture by changing what people *do* (Lean management and continuous delivery practices), not by first changing how they think.

## Frameworks Introduced
- **Westrum organizational culture (typology, 1988)**: organizations sit on a continuum of three types, distinguished by how information flows:
  - **Pathological (power-oriented)**: fear and threat; information hoarded, withheld for political reasons, or distorted to look good.
  - **Bureaucratic (rule-oriented)**: departments protected; people defend their "turf," insist on their own rules, do things by the book — *their* book.
  - **Generative (performance-oriented)**: focus on the mission; everything subordinated to good performance.
  - When to use: diagnosing a team's culture; predicting delivery and organizational outcomes; deciding where to invest in trust and information flow.
  - How: run the Westrum Likert survey (below), average items per respondent, analyze across the team; compare rows of Table 3.1 to locate behaviors to change.
  - Why it works / failure mode: culture predicts information flow, and information flow is critical to safe, effective operation in high-tempo, high-consequence environments. Failure mode: equating "bureaucracy" with "government" — bureaucracy (fair, consistent rules) isn't inherently bad; Westrum's rule-oriented culture is where *following rules matters more than achieving the mission*. Generative federal teams and pathological startups both exist.
- **Westrum's three characteristics of good information**: (1) it answers the questions the receiver needs answered; (2) it is timely; (3) it is presented so the receiver can use it effectively.
- **Three mechanisms by which culture enables information processing**: (1) more effective collaboration and higher trust across the organization and up/down the hierarchy; (2) emphasis on the mission lets people set aside personal and departmental issues; (3) a "level playing field" where hierarchy plays less of a role (Westrum 2014).
- **Schein's three levels of organizational culture**: basic assumptions (least visible; things we "just know"), values (visible, debatable norms that shape behavior — the level Westrum targets), artifacts (most visible: mission statements, technology, formal procedures, heroes, rituals).
- **Act your way to a better culture (John Shook)**: "the way to change culture is not to first change how people think, but instead to start by changing how people behave." Lean management and continuous delivery practices measurably improve Westrum culture.
  - How: implement technical practices (Ch 4) and Lean management practices (Ch 7–8); culture follows.
- **Construct validation before analysis**: before testing any relationship (correlation, prediction), confirm the measure via discriminant validity, convergent validity and reliability.

## Key Concepts
- **Construct**: a measure that passes statistical validity and reliability tests and can be used in further research (e.g., "Westrum organizational culture").
- **Likert-type question**: respondent rates agreement with a strongly worded statement on 1 ("Strongly disagree") to 7 ("Strongly agree").
- **Discriminant validity**: items not supposed to be related are actually unrelated.
- **Convergent validity**: items supposed to be related are actually related.
- **Reliability (internal consistency)**: items are read and interpreted similarly by respondents.
- **Westrum continuum**: the three types are points on a scale, which makes Likert measurement appropriate.
- **Software delivery performance construct**: only lead time, deployment (release) frequency and time to restore form a valid, reliable construct; change fail rate is excluded but strongly correlated with it. All later references to "software delivery performance" mean these three.
- **Emergent failure**: in complex adaptive systems, accidents arise from an interplay of contributing factors, not a single person's error (Perrow).
- **Team dynamics (Google, Project Aristotle 2015)**: who is on a team matters less than how members interact, structure their work and view their contributions.

## Mental Models
- Think of culture as **the plumbing of information flow**: a generative culture gets the right information to the right person in time and in a usable form.
- Use "human error is the start of the investigation, not the end" whenever something fails; ask how to improve information flow or tooling.
- Think of practices as **the lever on culture**: change behavior (CD, Lean management) and values shift afterward.
- Use the Table 3.1 rows (messengers, bridging, failure, novelty) as quick behavioral probes in retrospectives.

## Anti-patterns
- **"Throat to choke" investigations**: hunting a person to blame and punish in a pathological culture; misreads emergent failure and suppresses information.
- **Stopping at "human error"**: not just bad but dangerous — the systemic cause stays in place.
- **Shooting or neglecting messengers**: bad news stops flowing.
- **Turf protection / rules over mission**: the bureaucratic failure mode.
- **Trying to change mindsets first**: exhortation without changing practices doesn't shift culture.
- **Analyzing unvalidated survey items**: drawing correlations before establishing validity and reliability.

## Code Examples
Westrum culture survey items (Figure 3.1), each rated on a 7-point Likert scale:

```
Scale: 1 = Strongly disagree ... 4 = Neither agree nor disagree ... 7 = Strongly agree

On my team...
- Information is actively sought.
- Messengers are not punished when they deliver news of failures or other bad news.
- Responsibilities are shared.
- Cross-functional collaboration is encouraged and rewarded.
- Failure causes inquiry.
- New ideas are welcomed.
- Failures are treated primarily as opportunities to improve the system.

Score per respondent = mean(item values 1..7)
```
What it demonstrates: how to operationalize Westrum's typology as strongly worded statements suited to a Likert scale, and how to score it (mean across items) for statistical analysis. The construct has consistently tested valid and reliable, so you can reuse it in your own surveys.

## Reference Tables

**Table 3.1 Westrum's Typology of Organizational Culture**

| Pathological (Power-Oriented) | Bureaucratic (Rule-Oriented) | Generative (Performance-Oriented) |
|---|---|---|
| Low cooperation | Modest cooperation | High cooperation |
| Messengers "shot" | Messengers neglected | Messengers trained |
| Responsibilities shirked | Narrow responsibilities | Risks are shared |
| Bridging discouraged | Bridging tolerated | Bridging encouraged |
| Failure leads to scapegoating | Failure leads to justice | Failure leads to inquiry |
| Novelty crushed | Novelty leads to problems | Novelty implemented |

**2016 distribution of respondents**: 31% pathological, 48% bureaucratic, 21% generative.

**Prediction relationships**

| Driver | → Outcome |
|---|---|
| Westrum organizational culture | Software delivery performance (predicts) |
| Westrum organizational culture | Organizational performance (predicts) |
| Westrum organizational culture | Job satisfaction (predicts) |
| Lean management practices | Westrum organizational culture (impacts) |
| Continuous delivery practices | Westrum organizational culture (impacts) |

Why culture is a good proxy (Westrum's prerequisites): it reflects (1) trust and cooperation across the organization; (2) higher-quality decision-making — better information available, and decisions more easily reversed when wrong because the team is open and transparent; (3) better treatment of people — problems are discovered and addressed faster.

## Worked Example
**Building and validating the culture construct.** (1) Choose a model that is well-defined in the literature, measurable and predictive: Westrum, originally developed to predict safety outcomes in aviation and healthcare (where safety outcomes *are* performance outcomes). (2) Turn each generative characteristic into a strongly worded statement (e.g., "Failure causes inquiry"). (3) Collect 1–7 Likert responses from dozens to hundreds of people. (4) Test discriminant validity, convergent validity and reliability; the items passed, so "Westrum organizational culture" is a construct. (5) Only then test hypotheses grounded in prior theory: culture predicts software delivery performance, organizational performance and job satisfaction — both hypotheses supported. The same process exposed that the four delivery metrics do *not* all form one construct (change fail rate dropped out), showing the discipline catches flawed measures.

## Key Takeaways
1. Measure team culture with the seven Westrum Likert items; score as the mean and track it over time.
2. Train and protect messengers; make bad news safe to deliver.
3. Treat every failure as a trigger for blameless inquiry into information flow and tooling — never stop at "human error."
4. Encourage bridging: reward cross-functional collaboration and shared risk.
5. Change culture by changing practices — adopt continuous delivery and Lean management rather than running culture campaigns.
6. Validate any survey measure (validity, reliability) before you draw conclusions from it.
7. Don't confuse fair rules with bureaucratic culture; the test is whether rules outrank the mission.

## Connects To
- **Ch 2**: culture is the precondition for honest metrics ("whenever there is fear, you get the wrong numbers"); delivery-performance construct refined here.
- **Ch 4**: continuous delivery practices that improve culture.
- **Ch 7, 8**: Lean management and Lean product development practices that drive culture.
- **Ch 10**: job satisfaction and identity outcomes.
- **Ch 11**: transformational leadership shaping culture.
- **Ch 12, 13**: inferential prediction; psychometrics, validity and reliability.
- **Google Project Aristotle**: team dynamics over team composition; psychological safety.
- **Blameless postmortems (SRE)**: practical form of "failure leads to inquiry."
- **Schein's model of organizational culture; Perrow's *Normal Accidents***.
