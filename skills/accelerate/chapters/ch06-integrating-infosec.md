# Chapter 6: Integrating Infosec into the Delivery Lifecycle
*Authors: Nicole Forsgren, Jez Humble, Gene Kim*

## Core Idea
Building security into daily development work ("shifting left") positively impacts continuous delivery, which in turn improves delivery performance, and it also improves security quality: high performers spend **50% less time remediating security issues** than low performers.

## Frameworks Introduced
- **Shifting left on security**: build information security into the software delivery process instead of making it a separate phase downstream of development. Three components:
  1. **Security reviews for all major features**, performed in a way that does not slow down development.
  2. **Infosec integrated into the entire lifecycle, from development through operations**: infosec experts contribute to application design, attend and give feedback on software demonstrations, and ensure security features are tested as part of the automated test suite.
  3. **Make it easy for developers to do the right thing**: provide easy-to-consume, preapproved libraries, packages, toolchains, and processes for developers and IT operations.
  - When to use: whenever security/compliance is a bottleneck between "dev complete" and live, or security is a late-stage gate.
  - How: shift infosec's role from doing reviews themselves to giving developers the means (tools, training, support) to build security in.
  - Why it works: (a) it is much easier to ensure builders do the right thing than to inspect nearly completed systems for architectural defects requiring substantial rework; (b) infosec lacks the capacity to review every change when deployments are frequent; (c) involving infosec throughout improves communication and information flow. Failure mode: security as an end-of-lifecycle phase, where changes are painful and expensive.
  - Causal chain modeled: shift left on security -> continuous delivery -> software delivery performance.

- **Compliance via platform (18F / cloud.gov pattern)**: push security controls down into a shared platform so individual systems inherit them.
  - When to use: regulated environments with large control catalogs (e.g., FISMA / NIST RMF).
  - How: build a PaaS that satisfies most controls at the platform level; application teams only address the remainder.

- **Rugged DevOps**: DevOps combined with the **Rugged Manifesto** (coined by Josh Corman and James Wickett). Related name: **DevSecOps** (Topo Pal of Capital One, Shannon Lietz of Intuit). Being rugged is *everybody's responsibility*.

## Key Concepts
- **Infosec staffing ratio**: about 1 infosec person per 10 infrastructure people per 100 developers in large companies (Wickett 2014).
- **OWASP Top 10**: common security risks that many developers are unaware of and do not know how to prevent.
- **Shift left**: moving a concern earlier into the delivery process rather than treating it as a downstream phase.
- **Preapproved components**: libraries, packages, toolchains and processes vetted by infosec and made easy to consume.
- **FISMA**: Federal Information Security Management Act of 2002; requires agencies to follow NIST's Risk Management Framework.
- **Risk Management Framework (RMF)**: NIST process including a System Security Plan and an assessment producing a security assessment report.
- **System Security Plan (SSP)**: documents how required controls (325 for a moderate-impact system) are implemented.
- **Security Assessment Report (SAR)**: documents validation of the controls' implementation.
- **cloud.gov**: 18F's PaaS on open-source Cloud Foundry, hosted on AWS, that handles most controls at platform level.
- **DevSecOps / Rugged DevOps**: proposed names extending DevOps to cover infosec.

## Mental Models
- Think of DevOps as **any cross-functional wall in the value stream**, not just dev vs. ops: infosec, testing, and product management suffer the same "throw it over the wall" dynamic.
- Use **infosec as an enabler/toolsmith** when deployments are frequent: reviewers cannot scale, but paved roads can.
- Think of **platform-level controls as compliance leverage**: every control solved once in the platform is removed from every application's path to production.

## Anti-patterns
- **Security as a final phase**: infosec involved only at the end, when changes are painful and expensive.
- **Infosec doing all reviews itself**: lacks capacity at high deployment frequency; becomes the bottleneck from "dev complete" to live.
- **Starting compliance at "dev complete"**: the RMF process taking months to over a year, begun only after development.
- **Developers ignorant of common risks** (OWASP Top 10) with no tools or training provided.
- **Treating ruggedness as a specialist's job**: it must be everybody's responsibility.

## Reference Tables

| Metric | Value |
|---|---|
| Security remediation time, high vs. low performers | High performers spend 50% less time |
| Typical large-company ratio | 1 infosec : 10 infrastructure : 100 developers |
| Controls for a moderate-impact federal system | 325 |
| Controls handled by cloud.gov platform | 269 of 325 |
| Traditional RMF duration | Several months to over a year |
| cloud.gov dev complete -> live | Weeks, not months |

**Rugged Manifesto (condensed)**: I am rugged and my code is rugged; software is a foundation of the modern world, with awesome responsibility; my code will be used in unanticipated ways and for longer than intended; it will be attacked by talented, persistent adversaries; I refuse to be a source of vulnerability or weakness; my code will support its mission and persist in spite of these challenges; I am rugged not because it is easy but because it is necessary (Corman et al. 2012).

## Worked Example
**18F and cloud.gov.** Federal systems fall under FISMA, which requires NIST's Risk Management Framework: write a System Security Plan showing how each required control (325 for a moderate-impact system) is implemented, then undergo an assessment producing a SAR. This often takes months to over a year and typically begins only once the system is dev complete. A small team of civil servants at 18F built cloud.gov, a PaaS based on open-source Cloud Foundry hosted on AWS, that implements **269 of the 325** controls at the platform level. Systems hosted on it go from dev complete to live **in weeks, not months**, sharply reducing the work and cost of meeting the RMF. This is shift-left security at organizational scale: the secure path is built in once and made the easy default.

## Key Takeaways
1. Run security reviews on all major features, designed so they do not slow development.
2. Embed infosec in design sessions, demos, and the automated test suite rather than at a final gate.
3. Have infosec publish preapproved, easy-to-consume libraries, packages, and toolchains; measure their adoption.
4. Train developers on common risks such as the OWASP Top 10.
5. In regulated contexts, push controls into a shared platform so applications inherit compliance.
6. Track time spent remediating security issues as an outcome metric; expect it to fall as delivery performance rises.
7. Make security everybody's responsibility, not a separate team's phase.

## Connects To
- **Ch 4**: shift left on security is one of the continuous delivery capabilities.
- **Ch 5**: preapproved security toolchains as legitimate standardization; teams still choose their own tools.
- **Ch 7**: lightweight change approval and deployment pipelines as audit evidence in regulated industries.
- **Ch 9**: shifting left on security reduces deployment pain.
- **Ch 2**: delivery performance as the downstream outcome.
- **Appendix A**: shift left on security among the 24 capabilities.
- **DevSecOps / Rugged DevOps**: industry movements formalizing the same idea.
- **OWASP Top 10, NIST RMF, FISMA, FedRAMP**: external security and compliance frameworks.
