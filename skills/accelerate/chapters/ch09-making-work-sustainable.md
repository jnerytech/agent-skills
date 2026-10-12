# Chapter 9: Making Work Sustainable
*Authors: Nicole Forsgren, Jez Humble, Gene Kim*

## Core Idea
Delivery performance must not come through brute force: **deployment pain** and **burnout** are measurable, are highly correlated with poor IT performance, organizational performance, and culture, and are reduced by the same technical (continuous delivery) and Lean practices that improve delivery. Fix the work environment, not the person.

## Frameworks Introduced
- **Deployment pain**: the fear and anxiety engineers and technical staff feel when pushing code to production; it measures friction at the point where development meets IT operations.
  - Measured by asking whether deployments are feared, disruptive to work, or easy and pain-free (2015, 2016, 2017 surveys).
  - Finding: where deployments are most painful you find the poorest software delivery performance, organizational performance, and culture (high correlation).
  - Reduced by: comprehensive test and deployment automation; continuous integration including trunk-based development; shifting left on security; effective test data management; loosely coupled architectures; teams that can work independently; version control of everything required to reproduce production.
  - Warning sign also: developers/testers who *don't know* what deployments are like ("I've never thought about it!") indicates barriers hiding deployment work and isolating developers from downstream consequences.
  - Why it works / failure mode: the practices that give speed and stability also remove the stress of deploying; if left unchecked, deployment pain leads to burnout.

- **Three root causes of a complex, brittle deployment process**:
  1. Software not written with deployability in mind (expects a very particular environment, tolerates no deviation, gives administrators little useful diagnostic information; also poor distributed-systems design).
  2. Manual changes to production during deployment (typos, copy/paste errors, stale docs; causes **configuration drift**).
  3. Multiple handoffs between siloed teams (DBAs, network, sysadmins, infosec, QA, developers).

- **Three remedies for deployment pain**:
  1. Build systems designed to deploy easily into multiple environments, detect and tolerate environmental failures, and update components independently.
  2. Ensure production state (except production data) can be reproduced automatically from version control.
  3. Build intelligence into the application and platform so deployment is as simple as possible (PaaS apps deploy with a single command; see 12factor.net).

- **Maslach's six organizational risk factors for burnout** (Leiter and Maslach 2008): work overload, lack of control, insufficient rewards, breakdown of community, absence of fairness, value conflicts. All are within management's power to change; fixing the environment beats fixing the person.

- **Five factors most highly correlated with burnout** (this research): organizational culture, deployment pain, effectiveness of leaders, organizational investments in DevOps, organizational performance.
  - When to use: to decide where managers should intervene.
  - How: see table below.

- **Manager focus areas to avert burnout**: respectful, supportive environment that learns from failure rather than blaming; strong sense of purpose; investment in employee development; ask employees what blocks them, then fix it; give time, space, and resources to experiment and learn; give authority over decisions affecting their work, especially where they own outcomes.

## Key Concepts
- **Deployment pain**: fear/anxiety around pushing code to production.
- **Burnout**: physical, mental, or emotional exhaustion from overwork or stress, beyond merely being overworked; manifests as helplessness; correlated with pathological cultures and unproductive, wasteful work.
- **Configuration drift**: manually managed environments diverging from each other, causing deploy-time debugging and more manual change.
- **Deployability**: software designed to be deployed into many environments and tolerate deviation.
- **Postdeployment pain**: broken systems constantly paging on-call staff after hours; also disruptive and unhealthy.
- **Lived values vs. stated values**: the actual values employees experience count, not mission statements on placards.
- **Values alignment**: match between organizational and individual values; misalignment raises burnout, alignment can lessen or counteract it.
- **Duty of care / fiduciary obligation**: employers' two reasons to prevent burnout.
- **20% time / THINK Friday**: Google and IBM examples of creating space for new, creative work within the work week.

## Mental Models
- Use **"how painful are your deployments?"** as a cheap team diagnostic: ask, then fix what hurts most.
- Think of **after-hours deployments as an architecture smell**: zero-downtime automated deployment is achievable with sufficient investment.
- Think of **burnout as an environment problem**, not an individual-resilience problem: Maslach's risk factors are all management levers.
- Use **lived values** when diagnosing culture: a gap between stated and actual values is itself a burnout risk.

## Anti-patterns
- **Fixing the person, ignoring the environment**: most organizations do this; changing the environment has a higher likelihood of success.
- **Deployments outside normal business hours**: sign of architectural problems; contributes to high stress and lack of control.
- **Manual production changes during deployment**: errors and configuration drift.
- **Siloed handoffs** across DBA, network, sysadmin, infosec, QA, and dev teams.
- **Hiding deployment from developers**: isolates them from downstream consequences.
- **Expecting innovation after hours** instead of creating space in the work week.
- **Blaming human error**: human error is never the root cause of failure in systems.
- **Values mismatch** between employee and organization, or between stated and actual values.

## Code Examples
**Burnout survey construct** (what respondents were asked):
```
- Do you feel burned out or exhausted?
- Do you feel indifferent or cynical about your work, or feel ineffective?
- Is your work having a negative effect on your life (outside work)?
```
**Deployment pain construct**:
```
- Are deployments feared?
- Are deployments disruptive to your work?
- (Contrast) Are deployments easy and pain-free?
```
What it demonstrates: both outcomes are measured via short perceptual survey items capturing exhaustion, cynicism/ineffectiveness, and life spillover (burnout) and fear/disruption (deployment pain).

## Reference Tables

**Maslach's six risk factors**

| Factor | Meaning |
|---|---|
| Work overload | Job demands exceed human limits |
| Lack of control | Inability to influence decisions that affect your job |
| Insufficient rewards | Insufficient financial, institutional, or social rewards |
| Breakdown of community | Unsupportive workplace environment |
| Absence of fairness | Lack of fairness in decision-making processes |
| Value conflicts | Mismatch between organizational and individual values |

**Five factors most correlated with burnout and what to do**

| Factor | Manager action |
|---|---|
| Organizational culture | Pathological, power-oriented cultures show strong burnout; create blame-free environment, learn from failure, shared purpose |
| Deployment pain | Ask teams how painful deployments are; fix what hurts most |
| Effectiveness of leaders | Limit work in process, eliminate roadblocks |
| Organizational investments in DevOps | Fund training, support, resources, and time to acquire skills |
| Organizational performance | Lean management + CD; give time/resources to improve own work; space for creative work in the week (Google 20%, IBM THINK Friday) |

**Key numbers**

| Item | Value |
|---|---|
| Bing team work/life balance satisfaction, before vs. after CD | 38% -> 75% |
| Cost of job stress to US economy | $300 billion per year (Maslach 2014) |
| Health impact of stressful jobs | Comparable to secondhand smoke (Goh et al. 2015) and obesity (Chandola et al. 2006) |

## Worked Example
**Microsoft Bing and continuous delivery.** Thiago Almeida (Senior Software Development Engineer Lead, Azure) described the internal benefits of CD. Before the Bing team implemented the technical practices and discipline of continuous delivery, engineers reported work/life balance satisfaction of just **38%**; afterward it rose to **75%**. Staff could handle professional duties within work hours, no longer performed deployments manually, and kept work stress at work. The lesson: CD's benefits are not only for customers; they directly reduce deployment pain and its spillover into burnout.

## Key Takeaways
1. Ask your teams how painful deployments are and which specific things cause the pain; fix the worst first.
2. Eliminate after-hours deployments by investing in automated, zero-downtime deployment and deployable architecture.
3. Make production reproducible from version control and remove manual production changes to stop configuration drift.
4. Address burnout through the environment: culture, leadership effectiveness, investment in skills, and decision authority.
5. Use Maslach's six risk factors as an audit list for teams showing burnout symptoms.
6. Create in-week time for creative and improvement work instead of relying on after-hours effort.
7. Close gaps between stated and lived organizational values.

## Connects To
- **Ch 3**: Westrum culture; pathological cultures correlate with burnout; blameless learning.
- **Ch 4**: technical practices (test/deploy automation, CI, trunk-based development, test data, version control) that reduce deployment pain.
- **Ch 5**: loosely coupled architecture, independent teams, deployments in business hours.
- **Ch 6**: shift left on security reduces deployment pain.
- **Ch 7**: Lean management reduces burnout; leaders limit WIP.
- **Ch 8**: Lean product management reduces burnout.
- **Ch 10**: identity and employee satisfaction (next topic).
- **Ch 11**: leadership and management impact on burnout.
- **The Twelve-Factor App (12factor.net)**: architectural patterns for single-command deployment.
- **Maslach Burnout research / Marie Asberg**: external burnout models.
