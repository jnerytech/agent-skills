# Chapter 5: Architecture
*Authors: Nicole Forsgren, Jez Humble, Gene Kim*

## Core Idea
High delivery performance is possible with any type of system (mainframe, packaged, embedded, greenfield) provided the systems, and the teams that build them, are **loosely coupled**. Architectural *characteristics* (testability, deployability, team autonomy) matter; architectural *implementation details* (microservices, containers, Kubernetes) do not.

## Frameworks Introduced
- **Loosely coupled architecture (the architectural capability)**: in the 2017 analysis this was the *biggest contributor to continuous delivery*, larger even than test and deployment automation. A team scores highly if it can:
  1. Make large-scale changes to the design of its system without the permission of somebody outside the team
  2. Make large-scale changes to the design of its system without depending on other teams to make changes in their systems, or creating significant work for other teams
  3. Complete its work without communicating and coordinating with people outside the team
  4. Deploy and release its product or service on demand, regardless of other services it depends upon
  5. Do most of its testing on demand, without requiring an integrated test environment
  6. Perform deployments during normal business hours with negligible downtime
  - When to use: as a checklist for assessing whether your architecture is a bottleneck, and as the target state for any re-architecture (SOA, microservices, modular monolith).
  - How: decouple large domains with **bounded contexts and APIs**; test in isolation with **test doubles and virtualization**; make teams **cross-functional** (design, develop, test, deploy, operate within one team).
  - Why it works: it keeps the scarce inter-team communication bandwidth from being consumed by fine-grained implementation decisions, freeing it for higher-level shared goals. Failure mode: a "so-called SOA" or microservices estate where services still cannot be tested and deployed independently delivers none of the benefit.

- **Testability and deployability**: the two architectural characteristics that predict high performance. High performers agree with:
  - "We can do most of our testing without requiring an integrated environment."
  - "We can and do deploy or release our application independently of other applications/services it depends on."
  - When to use: the minimal two-question diagnostic of an architecture.
  - How: design systems that can be changed and validated independently of each other.

- **Inverse Conway Maneuver**: evolve team and organizational structure to achieve the desired architecture (supported by the research), building on **Conway's Law** (organizations "are constrained to produce designs which are copies of the communication structures of these organizations", Conway 1968).
  - When to use: when restructuring teams or planning a re-architecture.
  - How: shape teams so that each can go from design through deployment without high-bandwidth communication with other teams.

- **Let teams choose their own tools**: when teams can decide which tools they use, this contributes to software delivery performance and, in turn, organizational performance.
  - When to use: when governing tool/framework approval lists.
  - How: standardize where it pays (infrastructure architecture and configuration, a standard operational platform, preapproved security libraries/toolchains), but make internal tools good enough that engineers *choose* them; treat engineers as internal customers.

- **Architects focus on engineers and outcomes, not tools or technologies**: "microservices or serverless? Kubernetes or Mesos? which CI server?" are the wrong questions. What matters is enabling teams to change their products without depending on other teams or systems.

## Key Concepts
- **Integrated environment**: an environment where multiple independent services are deployed together (e.g., staging); expensive and slow to set up in many enterprises.
- **Loose coupling**: systems that can be changed and validated independently of each other.
- **Well-encapsulated architecture**: components hide internals behind stable interfaces, so changes stay local.
- **Big ball of mud**: tightly coupled enterprise environment of thousands of systems (Foote and Yoder 1997).
- **Conway's Law**: system designs mirror the communication structures of the organizations that build them.
- **Inverse Conway Maneuver**: design the org structure to get the architecture you want.
- **Bounded context**: a domain boundary used, with APIs, to decompose large domains into smaller, loosely coupled units.
- **Test doubles / service virtualization**: techniques to test a service or component in isolation from its dependencies.
- **Deploys per developer per day**: the productivity metric used to test how delivery scales with team size.
- **Standardized operational platform**: the legitimate place for standardization (e.g., Yegge on Amazon: a universal, debuggable way to run every service).

## Mental Models
- Think of architecture as a **communication budget**: loose coupling spends inter-team bandwidth on goals, not implementation details.
- Use **characteristics over implementation** when evaluating an architecture: ask "can we test and deploy independently?" rather than "are we on microservices?".
- Think of internal tools as **products with customers**: if engineers would not adopt them voluntarily, they are chosen for someone else's convenience.
- Use the **scaling curve** as a health check: if deploys per developer fall as headcount grows, coupling (technical or organizational) is the likely constraint.

## Anti-patterns
- **Assuming system type determines performance**: there was no significant correlation for most system types; legacy and packaged software can achieve the characteristics.
- **Fake SOA / microservices**: services that cannot be tested and deployed independently do not enable higher performance.
- **Treating new tech as a guarantee**: "the latest whizzy microservices architecture deployed on containers" is no guarantee of performance if the characteristics are ignored.
- **Outsourcing strategic software**: low performers were more likely to build or integrate against custom software developed by another company.
- **Mandatory approved-tool lists chosen for other stakeholders' convenience** (complexity reduction, purchasing power, licensing): blocks teams from choosing suitable tools and experimenting.
- **Debating tools instead of outcomes**: a technology people hate using, or that does not enable the desired behaviors, is irrelevant.

## Reference Tables

**System types studied (as primary system and as integrated service)**

| System type | Finding |
|---|---|
| Custom software developed by another company (e.g., outsourcing partner) | Low performers more likely to build/integrate against it |
| Mainframe software (as primary system) | Low performers more likely to be working on it |
| Integrating *against* mainframe systems | Not significantly correlated with performance |
| Greenfield, systems of engagement, systems of record, in-house custom, packaged COTS, embedded, user-installed (incl. mobile), non-mainframe on own/others' servers | No significant correlation with delivery performance |

**Deploys per developer per day as developer count grows** (respondents deploying at least once per day, Figure 5.1)

| Performer group | Trend as # developers increases |
|---|---|
| Low | Deploy with decreasing frequency |
| Medium | Deploy at a constant frequency |
| High | Deploy at a significantly increasing frequency |

**Why organizations standardize tools (and the cost)**

| Purpose of approved lists | Downside |
|---|---|
| Reduce environment complexity; ensure skills to manage tech through its lifecycle; increase purchasing power; ensure correct licensing | Prevents choosing the most suitable tools and experimenting with new approaches |

## Worked Example
**Scaling with headcount.** The orthodox view says adding developers raises total output but lowers per-developer productivity through communication and integration overhead. The team computed **deploys per day per developer** for respondents deploying at least daily. Low performers' per-developer deploy rate fell as teams grew; medium performers stayed flat; high performers' rate rose significantly. The conclusion: by focusing on what predicts high delivery performance (a goal-oriented generative culture, a modular architecture, continuous delivery engineering practices, and effective leadership) organizations can scale deployments per developer per day **linearly or better** with the number of developers, so the business moves faster as it adds people instead of slowing down.

## Key Takeaways
1. Audit your teams against the six architectural-capability statements; fix whichever "needs permission / needs another team / needs an integrated environment" blocker appears most.
2. Make independent testing and independent deployment hard requirements for any SOA or microservices effort; do not accept the label without the outcome.
3. Use the Inverse Conway Maneuver: structure cross-functional teams around bounded contexts before (or alongside) re-architecting.
4. Bring strategic, differentiating software capability in-house rather than outsourcing it.
5. Let teams choose their tools; standardize only the operational platform and provide preapproved security components that engineers want to use.
6. Track deploys per developer per day as headcount grows to detect coupling.
7. Judge architects by engineer outcomes, not by technology choices.

## Connects To
- **Ch 2**: delivery performance metrics (tempo and stability) that architecture enables; software delivery predicts organizational performance, motivating in-house capability.
- **Ch 4**: continuous delivery practices; loose coupling is the largest contributor to CD.
- **Ch 6**: preapproved, easy-to-consume security libraries and toolchains (shift left).
- **Ch 9**: loosely coupled architectures and independent teams reduce deployment pain; deployments outside business hours signal architectural problems.
- **Ch 3**: generative culture listed among the factors enabling linear scaling.
- **Ch 11**: effective leadership as a scaling factor.
- **Conway's Law / Team Topologies**: organizational design shaping system design.
- **Domain-Driven Design**: bounded contexts as decoupling mechanism.
- **Steve Yegge's "platform rant"**: practical advice on achieving independent services.
