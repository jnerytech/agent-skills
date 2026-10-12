# Conclusion and Appendices A–C
*Authors: Nicole Forsgren, Jez Humble, Gene Kim*

## Conclusion
Nearly every company relies on software, so delivery performance is critical to any organization. Leadership, tools, automation, and a culture of continuous learning and improvement all affect it. Delivering quality software at high tempo with stability drives organizational performance (profitability, productivity, market share) and noncommercial goals (efficiency, effectiveness, customer satisfaction, mission). The book has three parts: Part I covers findings, Part II the science, and Part III change management (Bell & Bell). The core message: **you can't buy or copy high performance.** Develop your own capabilities in your own context through sustained effort, investment, focus, and time. The research is unequivocal that the results are worth it.

## Appendix A: Capabilities to Drive Improvement
These are the **24 key capabilities** that drive improvement in software delivery performance in a statistically significant way. There are 5 categories, and capabilities within each category are in no particular order.

**Continuous delivery (8)**
1. **Use version control for all production artifacts**: app code, app and system configs, and build/config automation scripts (Ch 4).
2. **Automate your deployment process**: deployments with no manual intervention (Ch 4).
3. **Implement continuous integration**: regular check-ins, each triggering quick tests. Developers fix regressions immediately, and canonical builds are produced (Ch 4).
4. **Use trunk-based development methods**: fewer than three active branches, branches/forks living less than a day, and rarely or never a "code lock" (Ch 4).
5. **Implement test automation**: reliable tests run continuously. Developers are primarily responsible for creating and maintaining them (Ch 4).
6. **Support test data management**: adequate data, available on demand, conditionable in the pipeline, not limiting the number of tests. Minimize the test data you need (Ch 4).
7. **Shift left on security**: security reviews, infosec in design and demos, preapproved libraries, security tests in the automated suite (Ch 4).
8. **Implement continuous delivery (CD)**: software is deployable throughout its lifecycle, deployability is prioritized over new features, fast feedback, deploy on demand (Ch 4).

**Architecture (2)**
9. **Use a loosely coupled architecture**: teams test and deploy on demand without orchestration with other services (Ch 5).
10. **Architect for empowered teams**: teams choose their own tools (Ch 5; product counterpart in Ch 8).

**Product and process (4)**
11. **Gather and implement customer feedback** (Ch 8).
12. **Make the flow of work visible through the value stream**, from the business all the way to customers (Ch 8).
13. **Work in small batches**: pieces completed in a week or less; MVPs (Ch 8).
14. **Foster and enable team experimentation**: developers try ideas and change specs without outside approval (Ch 8; technical counterpart in Ch 4).

**Lean management and monitoring (5)**
15. **Have a lightweight change approval process**: peer review (pair programming or intrateam review) beats external CABs (Ch 7).
16. **Monitor across application and infrastructure to inform business decisions** (Ch 7).
17. **Check system health proactively**: threshold and rate-of-change warnings (the book cites Ch 13).
18. **Improve processes and manage work with WIP limits** (Ch 7).
19. **Visualize work to monitor quality and communicate throughout the team**: dashboards, internal sites (Ch 7).

**Cultural (5)**
20. **Support a generative culture (as outlined by Westrum)**: predictive of IT performance, organizational performance, and decreasing burnout. Hallmarks: good information flow, high cooperation and trust, bridging between teams, conscious inquiry (Ch 3).
21. **Encourage and support learning**: is learning seen as an investment rather than a cost? (Ch 10).
22. **Support and facilitate collaboration among teams**: dev, ops, and infosec (Ch 3, 5).
23. **Provide resources and tools that make work meaningful**: challenging work, room to use your skills and judgment, the tools to do the job (Ch 10).
24. **Support or embody transformational leadership**: five factors: vision, intellectual stimulation, inspirational communication, supportive leadership, personal recognition (Ch 11).

## Appendix B: The Stats
**Correlation vs. prediction.** *Correlation* means two variables move together. It may be due to a third variable or chance, and it says nothing about prediction or causation. *Prediction* here means **inferential prediction**, the impact of one construct on another, used when true experiments aren't possible. It is tested with simple linear regression and PLS regression.

**Organizational performance**
- High performers are **twice as likely** to exceed organizational performance goals (profitability, productivity, market share, number of customers) and noncommercial goals (quantity and quality of products/services, operating efficiency, customer satisfaction, organizational/mission goals).
- 2014 follow-up (just over 1,000 respondents, 355 companies, publicly traded): high performers had **50% higher market capitalization growth over three years** than low performers. This was not replicated later because the dataset was too small.

**Software delivery performance**
- The four measures (deploy frequency, lead time, MTTR, change fail %) classify high, medium, and low performers, which differ significantly on all four each year.
- **No trade-off** between tempo and stability: they move in tandem.
- Software delivery performance **predicts** organizational and noncommercial performance.
- The construct = lead time + release frequency + MTTR. Change fail rate is excluded but highly correlated.
- Deploy frequency is highly correlated with CD and comprehensive version control. Lead time is highly correlated with version control and automated testing. MTTR is highly correlated with version control and monitoring.
- Correlated with organizational investment in DevOps. **Negatively** correlated with deployment pain.

**Quality**
| Time split | New work | Unplanned work/rework |
|---|---|---|
| High | 49% | 21% |
| Medium | — | 32% (J-curve) |
| Low | 38% | 27% |

Table B.1, Manual work (high performers lowest on every item, statistically significant; medium performers do more manual deployment and change-approval work than low performers, the J-curve):
| Manual work | High | Medium | Low |
|---|---|---|---|
| Configuration | 28% | 47%* | 46%* |
| Testing | 35% | 51%* | 49%* |
| Deployments | 26% | 47% | 43% |
| Change approval process | 48% | 67% | 59% |

**Burnout and deployment pain**
- Deployment pain is negatively correlated with delivery performance and Westrum culture.
- The five factors most correlated with burnout: Westrum culture (−), leaders (−), organizational investment (−), organizational performance (−), deployment pain (+).

**Technical capabilities**
- Trunk-based development: high performers have branch life and integration of hours to a day. Low performers have days to weeks.
- Technical practices **predict** CD, Westrum culture, identity, job satisfaction, delivery performance, less burnout, less deployment pain, and less rework.
- High performers spend **50% less time** remediating security issues.

**Architecture**
- There is no correlation between system type (engagement vs. record) and performance. Integrating with mainframes is not a significant indicator. Low performers were more likely to work on mainframes or outsourced custom software.
- A loosely coupled, well-encapsulated architecture drives IT performance. It was the **biggest contributor to CD in 2017**.
- Among teams deploying at least once per day, as developer count grows: low performers deploy with decreasing frequency, medium performers at a constant frequency, high performers at **significantly increasing** frequency.
- High performers agree more with: testing without an integrated environment; deploying/releasing independently of dependencies; custom software using microservices.

**Lean management**
- Predicts Westrum culture, job satisfaction, delivery performance, and less burnout.
- CABs are negatively correlated with performance. Approval only for high-risk changes is not correlated. No approval or peer review gives higher performance. A lightweight change approval process **predicts** delivery performance.

**Lean product management**
- An experimental approach is highly correlated with CD technical practices. Lean product development **predicts** Westrum culture, delivery performance, organizational performance, and less burnout.

**Culture**
- Strongly correlated with culture: DevOps investment, team leader experience and effectiveness, CD capabilities, dev/ops/infosec win-win outcomes, organizational performance, deployment pain, Lean management.
- Westrum culture **predicts** delivery performance, organizational performance, and job satisfaction. It is negatively correlated with deployment pain.

**Identity, eNPS, job satisfaction**
- Identity predicts organizational performance. Job satisfaction predicts organizational performance.
- Employees in high performers are **2.2×** more likely to recommend their organization and **1.8×** more likely to recommend their team as a great place to work.
- eNPS is significantly correlated with customer feedback use, visibility of flow to the customer, and identification with organizational values and goals.

**Leadership**
- High performers report the strongest levels of all five transformational leadership dimensions. Low performers report the lowest. All differences are significant.
- Transformational leadership is highly correlated with delivery performance and with eNPS.
- Teams in the **top 10%** of transformational leadership were equally or *less* likely to be high performers than the overall population. Leadership alone is not enough.
- Leadership **predicts** Lean product development capabilities (small batches, team experimentation, customer feedback) and technical practices (test and deployment automation, TBD, shift-left security, loose coupling, empowered teams, CI).

**Diversity**
- Women: 5% (2015), 6% (2016), 6.5% (2017). 33% of respondents are on teams with no women, 56% on teams that are less than 10% female, 81% on teams that are less than 25% female.
- Gender: 91% male, 6% female, 3% non-binary/other. Underrepresented: 77% no, 12% yes, 11% NA.

**Other**
- DevOps investment is highly correlated with delivery performance. People working in DevOps teams: 16% (2014), 19% (2015), 22% (2016), 27% (2017).
- 78% of respondents deploy on 1–4 operating systems (top: Enterprise Linux, Windows 2012, Windows 2008, Debian/Ubuntu).
- High, medium, and low performers all include large enterprises, startups, and highly regulated industries. Industry and size don't determine performance.

## Appendix C: Statistical Methods (condensed)
**Pipeline: survey prep → data collection → bias tests → measurement model → relationships → classification.**

- **Survey preparation**: reuse previously validated items when possible (organizational performance from Widener 2007; noncommercial from Cavalluzzo & Ittner 2004). New items follow Dillman (1978). The model is chosen each year from the literature, prior findings, and debate.
- **Data collection**: snowball sampling, nonprobabilistic (see Ch 15).
- **Tests for bias**: chi-square (categorical differences, e.g., gender); t-tests (scale/Likert differences, early vs. late responders); common method bias/variance via **Harman's single-factor test** (does one factor load on all items?) and the **marker variable test** (do significant correlations survive adjusting for the second-lowest positive correlation?). No early/late bias was found, and CMB was not a problem.
- **Two-stage analysis** (Gefen & Straub 2005): (1) validate the measurement model and latent constructs; (2) test hypotheses.
- **Measurement model**:
  | Test | Purpose | Threshold |
  |---|---|---|
  | PCA, varimax rotation, IV/DV separately; EFA (CFA only for transformational leadership) | Convergent validity | Loadings > 0.60, no cross-loading |
  | AVE | Convergent / discriminant validity | AVE > 0.50; √AVE > inter-construct correlations |
  | Pearson correlation | Divergent validity | < 0.85 (Brown 2006) |
  | Cronbach's alpha | Reliability | ≥ 0.70 (Nunnally 1978); biased against small scales |
  | Composite reliability (CR) | Reliability / convergent | ≥ 0.70 (Chin et al. 2003) |
  A construct must pass all tests to "exhibit good psychometric properties." All of the book's constructs passed.
- **Relationships**: Pearson's r (−1 to 1). Prediction is claimed only when supporting theory exists; otherwise only correlation is reported. **PLS regression** (2015–2017): optimizes prediction of the outcome, needs no multivariate normality, and suits exploratory research. **Linear regression** (2014).
- **Classification**: **hierarchical cluster analysis**. Five methods were compared (Ward's, between-groups, within-groups, centroid, median) on change in fusion coefficients, cluster sizes, and univariate F-statistics. **Ward's** won. Hierarchical clustering was chosen for its explanatory power, because there was no predetermined number of clusters, and because the dataset was not too large. **ANOVA** post hoc with **Tukey's** test (no normality needed), cross-checked with Duncan's, at **p < 0.10**. Every year except 2016, high performers were best on all variables and low performers worst.

## Key Takeaways
1. Use the 24 capabilities as an improvement menu, grouped as CD, architecture, product/process, Lean management/monitoring, and culture.
2. Keep the distinction straight: "predicts" (inferential, theory-backed) vs. "correlates."
3. Expect a J-curve: medium performers may do more manual work and rework than low performers.
4. Leadership is necessary but not sufficient. Top-10% leadership alone didn't produce high performance.
5. Industry, size, and regulation don't determine performance.

## Connects To
- **Ch 2**: four key metrics, clusters, the 2016 surprise. **Ch 3**: Westrum. **Ch 4–5**: CD and architecture capabilities. **Ch 7–8**: Lean management and product. **Ch 9–10**: burnout, identity, eNPS. **Ch 11**: transformational leadership. **Ch 12–13**: inference and psychometrics. **Ch 15**: snowball sampling. **Ch 16**: applying it all (ING).
