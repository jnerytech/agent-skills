# Chapter 4: Technical Practices
*Authors: Nicole Forsgren, Jez Humble, Gene Kim*

## Core Idea
Technical practices are not secondary to Agile management rituals: continuous delivery (CD) — a set of capabilities for getting any change into production safely, quickly and sustainably — predicts higher software delivery performance, lower change fail rates, a generative culture, stronger organizational identity, less deployment pain, less burnout and less unplanned work.

## Frameworks Introduced
- **Five principles of continuous delivery**:
  1. **Build quality in** — Deming's third point: cease dependence on inspection; detect issues quickly so they're cheap to fix.
  2. **Work in small batches** — split work into chunks that deliver measurable outcomes quickly to part of the market; the overhead pays back by avoiding zero/negative-value work. Goal: make the cost of pushing out individual changes very low.
  3. **Computers perform repetitive tasks; people solve problems** — automate regression testing and deployments; free people for design and process improvement.
  4. **Relentlessly pursue continuous improvement** — high performers are never satisfied; improvement is part of everybody's daily work.
  5. **Everyone is responsible** — throughput, quality and stability are system-level outcomes; management makes them transparent and sets measurable, achievable, time-bound goals.
  - Why it works / failure mode: it changes the economics of delivery so releasing becomes a routine, on-demand, business-hours activity. Failure mode: adopting CD as tooling while keeping big batches, siloed goals and manual gates — or skipping the ongoing architectural simplification that keeps automation affordable.
- **Three foundations of continuous delivery**:
  - **Comprehensive configuration management**: provision environments and build, test, deploy fully automatically from information in version control; manual approvals allowed, but once approved, changes apply automatically.
  - **Continuous integration (CI)**: short-lived branches (less than one day's work) integrated into trunk/master frequently; each change triggers a build with unit tests; failures fixed immediately.
  - **Continuous testing**: automated unit and acceptance tests on every commit; developers can run all tests on workstations; testers do exploratory testing continuously on latest CI builds; no one is "done" until relevant automated tests are written and passing.
- **Capabilities that drive continuous delivery** (the chapter's "nine key capabilities"):
  1. Version control (application code, system configuration, application configuration, build/config scripts)
  2. Comprehensive, reliable test automation run regularly
  3. Deployment automation
  4. Continuous integration
  5. Shifting left on security
  6. Trunk-based development
  7. Effective test data management
  8. Loosely coupled, well-encapsulated architecture (2017; Ch 5)
  9. Teams choosing their own tools (2017; Ch 5)
  - When to use: as a checklist for which technical levers to assess and invest in.
  - How: measure each via Likert constructs; prioritize those weakest in your context.
- **First-order continuous delivery construct (2017)**: CD measured directly as the ability to (a) deploy to production or end users on demand throughout the lifecycle; (b) give everyone on the team fast feedback on quality and deployability, and make acting on it their highest priority.

## Key Concepts
- **Continuous delivery**: capabilities for getting changes of all kinds — features, configuration changes, bug fixes, experiments — into production or users' hands safely, quickly, sustainably.
- **Deployment pipeline**: the pattern connecting CD's multiple feedback loops.
- **Deployment pain**: fear/anxiety around pushing code; reduced by CD because deploys stop being big-bang events.
- **Trunk-based development**: fewer than three active branches, branch lifetimes under a day, no "code freeze" or stabilization periods — independent of team size, organization size, industry.
- **Quarantine suite**: a separate, independently run suite for unreliable (flaky) tests — or just delete them, since version control keeps them.
- **Test data management**: adequate test data for full automated suites, acquirable on demand, never a limit on which tests can run.
- **Shift left on security**: infosec gives feedback at every step (design, demos, test automation) integrated into daily work without slowing delivery.
- **Unplanned work / rework**: break/fix, emergency deployments and patches, urgent audit requests — the strongest quality proxy correlated with delivery performance.
- **Failure demand (John Seddon, Vanguard Method)**: demand caused by failing to do the right thing the first time.
- **Quality**: "value to some person" (Weinberg) — contextual, so measured via proxies.

## Mental Models
- Think of CD as **changing the economics of change**: when each change is cheap and safe to release, small batches and fast feedback become rational.
- Think of unplanned work as **running out of gas on the highway vs. heeding the low-fuel light** (Visible Ops): planned fixes are calm; unplanned ones pull everyone off scheduled work.
- Use "configuration is code" when deciding what to version — system and application configuration matter *more* than app code for predicting performance.
- Think of investments in technology as **investments in people**: CD makes work sustainable (lower pain and burnout), fulfilling the Agile Manifesto's "constant pace indefinitely."

## Anti-patterns
- **Treating technical practices as secondary to management/team rituals** (common in Scrum-only adoptions; Scrum overtook XP ~2006).
- **Long-lived feature branches and code freezes**: discourage refactoring and intrateam communication; worse delivery performance. (GitHub Flow with long branches suits part-time open source contributors, not full-time teams.)
- **Flaky test suites**: false positives/negatives destroy confidence that green means releasable.
- **Tests owned only by QA or outsourced parties**: not correlated with IT performance; code is less testable and developers care less.
- **Leaving configuration out of version control**: config is often treated as secondary but correlates more strongly than app code.
- **Testing only after "dev complete"**: inspection-based quality.
- **Security as a downstream phase**: integrating it into daily work actually contributes to delivery performance.
- **Big-bang, after-hours deployments**: drive deployment pain and burnout.
- **Getting rid of testers**: testers remain essential for exploratory, usability and acceptance testing and for co-evolving automated suites.

## Code Examples
Version control capability construct — Likert items (agree/disagree):

```
- Our application code is in a version control system.
- Our system configurations are in a version control system.
- Our application configurations are in a version control system.
- Our scripts for automating build and configuration are in a version control system.
```
What it demonstrates: how a technical capability is measured as a multi-item Likert construct (most capabilities are; deployment automation is a notable exception).

Test-run cadence that predicts performance:
```
every commit      -> build + fast automated tests
every day         -> developers get feedback from comprehensive acceptance + performance suites
continuously      -> current builds available to testers for exploratory testing
```

## Reference Tables

**Time allocation: high vs. low performers (Figure 4.4)**

| | New work | Unplanned work or rework |
|---|---|---|
| High performers | 49% | 21% |
| Low performers | 38% | 27% |

**What CD predicts (Figures 4.1–4.3)**

| Drivers of CD | CD → outcomes |
|---|---|
| Version control; test automation; deployment automation; continuous integration; trunk-based development; test data management; shift left on security; loosely coupled architecture; empowered teams choosing tools | Higher software delivery performance (lead time, deploy frequency, time to restore); lower change fail rate; generative, performance-oriented culture; strong identification with the organization; lower deployment pain; reduced burnout; less unplanned work and rework |

**Quality proxies tested**: perceived quality/performance of applications; % time on rework or unplanned work (strongest correlation); % time on defects identified by end users — all correlated with delivery performance.

**Test automation practices that predict IT performance**
- Reliable automated tests (pass = releasable; fail = real defect).
- Developers primarily create and maintain acceptance tests and can reproduce/fix them on workstations (TDD forces testable designs; ownership drives maintenance).

## Worked Example
**Trunk-based development vs. GitHub Flow skeptics.** After finding trunk-based development correlated with higher delivery performance, the authors heard pushback from developers used to GitHub Flow: branching is fine if branches don't live too long. They agreed that short-lived branches merged to trunk at least daily are consistent with CI, and ran additional analysis: teams with branch integration times under a day *and* merging/integration periods under a day outperformed teams using longer-lived branches. Hypothesis (anecdotal, from experience): multiple long-lived branches discourage refactoring and communication within the team. Boundary condition: GitHub Flow with longer branches is appropriate for open source projects with part-time contributors. Practitioner rule: keep fewer than three active branches, merge within a day, no code freezes.

## Key Takeaways
1. Put application code, system and application configuration, and build/config scripts in version control — prioritize configuration.
2. Make tests reliable: quarantine or delete flaky ones; developers own and can run acceptance tests locally.
3. Run fast tests on every commit, comprehensive acceptance/performance suites daily, and keep builds available for exploratory testing.
4. Practice trunk-based development: <3 active branches, <1 day branch lifetime, no code freezes.
5. Ensure test data is available on demand and never limits which tests you run.
6. Integrate infosec into daily work from design onward.
7. Track % unplanned work/rework as your quality signal; CD should drive it down.

## Connects To
- **Ch 2**: CD drives the software delivery performance measures and lower change fail rate.
- **Ch 3**: CD is a driver of Westrum generative culture ("act your way to a better culture").
- **Ch 5**: loosely coupled architecture and tool choice — architecture is the critical obstacle to CD.
- **Ch 6**: shifting left on security in depth.
- **Ch 9**: deployment pain and burnout.
- **Ch 10**: organizational identity predicted by CD.
- **Appendix A**: technical capabilities among the 24.
- ***Continuous Delivery* (Humble & Farley 2010)**; **Extreme Programming (TDD, CI)**; **Deming's 14 points**; ***The Visible Ops Handbook***; **Seddon's Vanguard Method (failure demand)**; **Fowler on non-determinism in tests**.
