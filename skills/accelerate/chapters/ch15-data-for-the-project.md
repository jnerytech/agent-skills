# Chapter 15: The Data for the Project
*Authors: Nicole Forsgren, Jez Humble, Gene Kim*

## Core Idea
The research used a four-year cross-sectional survey of a deliberately targeted population (professionals familiar with DevOps), recruited through snowball sampling. The authors compensated for the known limitations of that design and traded breadth for explanatory power.

## Frameworks Introduced
- **Targeted population design**: recruit professionals and organizations familiar with the word "DevOps" (2014 onward), across technology and technology-driven industries (retail, banking, telecom, healthcare, etc.).
  - When to use: when concepts need shared vocabulary and long explanations would cause respondents to drop out. If a respondent needs 15 minutes to learn a concept, they get frustrated and won't finish.
  - How: (1) focus collection on people in the business of software development and delivery; (2) focus on people already familiar with modern practice terminology.
  - Why it works / trade-off: you gain explanatory power from a tighter population definition. You lose the cohort that doesn't use configuration management, infrastructure-as-code, or CI, who likely perform *worse* than the low performers. As a result, comparisons understate how drastic transformations can be.
- **Ask about behaviors, not labels**: never ask "Do you practice continuous integration?" in any item used for prediction. Ask about core components instead (e.g., "are automated tests kicked off when code is checked in?").
  - When to use: whenever respondents may want to look good or have their own definition of a buzzword.
  - Why it works: it removes social-desirability and definitional bias that a DevOps-familiar sample would otherwise introduce.
- **Snowball (referral) sampling with mitigations**: a nonprobability method in which the initial sample grows through referrals.
  - When to use: (a) the population cannot be enumerated (no central accrediting board like CPA/PE, job titles that are nontraditional or too generic, e.g., "software engineer"); (b) the population is averse to being studied. Technical workers have a history of "Lean transformations" that really meant layoffs, and referrers can vouch that the questions are not propaganda and that the researchers are reputable.
  - How: seed with as large and diverse an initial set as possible (the authors' own lists, prior respondents, Puppet's marketing database, Gene Kim's and Jez Humble's databases, professional group lists, outreach to underrepresented groups and minorities in technology) plus social media (Twitter, LinkedIn), then invite referrals.
- **Triangulation against blind spots**: (1) engage with industry and community, and compare notes with emerging trends without relying on one source; revisit hypotheses on mismatch; (2) external subject matter experts review the hypotheses each year; (3) review the literature in other fields; (4) solicit research ideas from the community each year.

## Key Concepts
- **Cross-sectional design**: data collected at a single point in time. Repeating it over 4 years shows industry patterns, but responses aren't linked year over year, so no longitudinal analysis is possible. Its benefit is reduced variability in the research design.
- **Longitudinal design**: the same individuals sampled each year. It was avoided because of privacy-driven response-rate drops and people changing teams or jobs.
- **Target population**: the defined group a research design draws from. Every good design has one.
- **Probability sampling**: random selection in which every population member has an equal chance of selection. It is generally preferred, but it requires the population to be known.
- **Nonprobability sampling**: any method without random selection.
- **Snowball / referral sampling**: the sample grows through referrals, like a rolling snowball.
- **Initial informants**: the seed invitees. Their representativeness shapes the whole sample.

## Mental Models
- Think of research design as trade-offs: no design answers all questions. Name what you give up (the non-DevOps cohort) and what you gain (explanatory power).
- Use snowball sampling when the population is unlistable or study-averse, and make the seed huge and diverse.
- Think of a buzzword in a survey item as a bias vector: measure the observable practice instead.
- Generalization: findings like version control, automated testing, and a culture of transparency and trust likely help any paradigm (waterfall, Agile, DevOps) and any industry. Westrum's framework predicts outcomes in healthcare and aviation too.

## Anti-patterns
- **Asking "Do you do CI?"**: everyone claims CI, so the answer measures self-image, not practice.
- **Long concept explanations in the survey**: respondents abandon it.
- **Small or homogeneous snowball seed**: the data is strongly shaped by the initial invitees and won't represent the community.
- **Relying on a single data source each year**: blind spots go unnoticed.
- **Recruiting by job title**: titles are nontraditional, missing "DevOps," or too generic.

## Worked Example
**Why probability sampling was impossible and how the authors compensated.** Probability sampling needs a complete list of DevOps practitioners worldwide. No such list exists: there is no national certification, and org charts are private and full of generic or nontraditional titles. So the team (1) emailed several merged lists (prior respondents, Puppet's configuration-management database, Kim's and Humble's reader databases, professional groups, underrepresented-group organizations); (2) had authors and sponsors post on Twitter and LinkedIn; and (3) invited referrals. Each limitation got a specific mitigation:
| Limitation | Mitigation |
|---|---|
| Seed not representative of its communities | Initial set as large and diverse as possible (company sizes, countries, minorities) |
| Data shaped by initial invitations | Very large, diverse seed rather than a small group asked for referrals |
| Blind spots vs. the real industry | Community triangulation, annual SME review of hypotheses, literature review, community-sourced research ideas |

Data was collected four times, over 4–6 weeks each time.

## Key Takeaways
1. Define a target population explicitly and state what the exclusion costs.
2. Write survey items about concrete practices, never about branded methodologies.
3. When the population can't be enumerated, use snowball sampling with a large, diverse, multi-channel seed.
4. Triangulate survey results with community feedback, external experts, and other literatures every cycle.
5. Read cross-sectional findings as patterns across the industry, not as individual trajectories over time.
6. Apply core findings broadly: version control, test automation, and a trusting culture help regardless of methodology.

## Connects To
- **Ch 4**: CI measured via its component practices.
- **Ch 12**: inferential prediction and research design types.
- **Ch 13**: latent constructs built from behavior items.
- **Ch 14**: why surveys, trust, and anonymity.
- **Ch 16**: Part III bridge. Applying findings to change an organization (Bell & Bell, ING).
- **Ch 17 / Appendix C**: data collection and bias tests (early vs. late responders).
- **Sampling theory**: probability vs. nonprobability, snowball sampling.
