# Chapter 18: Software Engineering in SRE
*Authors: Dave Helstroom and Trisha Weir, with Evan Leonard and Kurt Delimon (edited by Kavita Guliani)*

## Core Idea
SREs know production firsthand, which makes them well suited to build full-fledged software products (not one-off hacks) that keep production running. They should approach this work with a product mindset: internal customers and a roadmap. The case study is **Auxon**, an **intent-based capacity planning** tool. The chapter also gives guidance on making SRE software projects succeed: launch and iterate, drive adoption, staff the team, and keep standards.

## Frameworks Introduced
- **Why SREs should build software**:
  - Deep production knowledge helps them design for scalability, graceful degradation, and integration with other infrastructure.
  - They are embedded in the subject matter, so they understand the requirements.
  - Their users are fellow SREs, which gives frank, high-signal feedback and faster launch and iteration. Internal users tolerate a minimal UI.
  - Guiding principle: "**team size should not scale directly with service growth**." Linear team growth under exponential service growth requires constant automation.
  - For individual SREs: career development, a balance against interrupts and on-call, and a draw for diverse hires. Teams mix SWE-background and systems-background engineers.
- **Intent-based Capacity Planning**: "Specify the requirements, not the implementation." Encode a service's dependencies and parameters (its **intent**) in a program, and **autogenerate** the allocation plan. When demand, supply, or requirements change, regenerate the plan.
  - When to use: capacity planning that is brittle, laborious, and imprecise when done by hand in spreadsheets.
  - How: capture the three **precursors to intent**:
    1. **Dependencies**: nested placement constraints (Foo needs Bar within 30 ms; Bar depends on Baz and Qux).
    2. **Performance metrics**: the "glue between dependencies" that converts higher-level resource types to lower-level ones (CPU for N queries of Foo; Mbps on Bar per N Foo queries). Get them from load testing and usage monitoring.
    3. **Prioritization**: which requirements to sacrifice when capacity is short (for example, Foo's N+2 versus Bar's N+1). This makes trade-offs transparent, open, and consistent instead of ad hoc and opaque.
  - Why it works: computers do the bin packing, which is NP-hard. This cuts toil drastically, yields more precise and cheaper plans, and lets service owners focus on SLOs and dependencies instead of scrounging for resources.
- **Chain of intent abstraction** (move up the ladder for more flexibility):
  1. "I want 50 cores in clusters X, Y, and Z for service Foo." This is an explicit resource request.
  2. "I want a 50-core footprint in any 3 clusters in region YYY." More freedom, but no rationale.
  3. "I want to meet Foo's demand in each geographic region, with **N + 2** redundancy." This is understandable in human terms. **Most services get the best wins here.**
  4. "I want to run Foo at **5 nines** of reliability." The most abstract level, for sophisticated services. N+2 might not even be optimal.
- **Launch and iterate / Approximation**: "Don't focus on perfection and purity of solution, especially if the bounds of the problem aren't well known."
  - How: build a simple placeholder (Auxon's "**Stupid Solver**", a heuristic solver) behind an **abstracted interface**, so you can later swap in the real one (the linear-programming solver). Use fuzzy requirements as a reason to design general, modular software, but ground every general solution in a concrete real-world implementation.
  - Why it works / failure mode: it proves the vision is feasible early without blocking on unknowns. Without the abstraction, the approximation becomes permanent technical debt.
- **Driving adoption of internal tools**: one presentation or email is not enough. You need a consistent and coherent approach, user advocacy, and sponsorship from senior engineers and management. Provide documentation: "SREs are busy, and if your solution is too difficult or confusing, they will write their own."
  - **Set expectations**: separate aspirational goals from the **Minimum Viable Product**. Promise too much, too soon and you lose credibility. Promise too little and you can't overcome the "activation energy." Ship small, steady releases, and pair a long-term roadmap with short-term wins.
  - **Identify appropriate customers**: first target teams with *no* existing process, since they have to invest configuration effort anyway. Teams with passable home-grown tools aren't in enough pain to switch. Turn early wins into advocates and quantified before/after case studies.
  - **Customer service**: give early adopters white-glove support. Address the fear of being "replaced by a shell script." Teams own configurations and outcomes instead of toil. Early adopters become local experts across distributed teams.
  - **Designing at the right level ("agnosticism")**: generalize to accept many data sources. "Come as you are; we'll work with what you've got." Don't over-customize for one or two big users, and don't define success as 100% adoption, because the long tail gives diminishing returns.
- **Good vs. poor candidate projects**:
  - Good: engineers with firsthand domain experience, a highly technical user base (high-signal bug reports), and noticeable benefit (less toil, better infrastructure, a streamlined process). The project fits org-level objectives, so leaders will advocate for it, and cross-org review prevents overlapping efforts.
  - Poor: touches many moving parts at once; all-or-nothing design that blocks iteration; **overly specific** (helps one service, a risk because SRE teams are organized per service); or **overly generic** (fits no use case, grand scope and abstract goals without concrete use cases).
- **Getting There (introducing software development into an SRE org)**:
  1. **Create and communicate a clear message**: explain the benefits to skeptical SREs (consistent tools speed ramp-up, and fewer ways to do one task make knowledge portable). You have cleared the first hurdle when SREs ask *how* it will work, not *whether*.
  2. **Evaluate your organization's capabilities**: you are creating a product team. Do you have a PM or customer advocate, and someone who can run agile? Borrow coaching and PM consulting from product teams, and hire once experiments succeed.
  3. **Launch and iterate**: start with uncontroversial targets that have no existing solution, release on a **six-month** cadence, and later move to **push-on-green**.
  4. **Don't lower your standards**: would you onboard this product if a separate dev team had built it? Require code review and end-to-end or integration tests, and have another SRE team do a production readiness review. Credibility takes a long time to build and a moment to lose.

## Key Concepts
- **Intent**: the rationale for how a service owner wants to run their service, as opposed to concrete resource demands.
- **Bin packing**: fitting constrained resource requests into available supply. It is NP-hard and hopeless by hand.
- **Auxon**: Google's intent-based capacity planning and allocation tool. It was built by a small group of SWEs and a TPM within SRE over two years, and it plans many millions of dollars of machine resources.
- **Mixed-integer / linear program**: Auxon's internal representation of intent. Resource Supply is the **upper bound** and Resource Pricing is the **objective** to minimize.
- **Stupid Solver**: a deliberately simple heuristic stand-in for the optimal solver, placed behind a swappable interface.
- **Agnosticism**: designing the tool to accept any data source or automation tool, so customers don't have to commit to a specific stack.
- **Allocation Plan**: the solver output saying which resources go to which service, where, plus any *unsatisfiable* requirements.
- **Seed team**: generalists who learn fast plus engineers with breadth. Specialists (Operations Research, statistics, optimization) are added once the project is demonstrably successful.
- **Dedicated project time**: non-interrupted time is essential and "must be aggressively defended."

## Mental Models
- Think of **intent as moving up the "why" ladder**. Each "but… why?" removes an arbitrary constraint and adds degrees of freedom for the optimizer.
- Use **approximation behind an interface** when a core dependency is poorly understood. Ship the stupid version and keep the smart version swappable.
- Think of **SRE developers as both creator and customer**. They must keep doing SRE work (on-call, design reviews) rather than becoming full-time developers embedded in SRE. The Auxon team stayed in on-call rotations.
- Use **"first customers are those with no current solution"** to find early adopters for any internal tool.

## Anti-patterns
- **Traditional demand-driven, manual capacity planning**: it is *brittle* (efficiency drops, adoption spikes, cluster delivery slips, and changed performance goals each force cross-checking or replanning, with effects rippling into later quarters), *laborious* (slow, error-prone forecasts; spreadsheets that don't scale and lose freshness), and *imprecise* (the reason behind "X cores in cluster Y" is lost, and there are no known bounds on optimality).
- **"I have a design doc; why do we need requirements?"**: the typical SRE blind spot. Partner with PMs, TPMs, or product SWEs.
- **Ad hoc quick-fix coding at scale**: it produces narrow, unshareable tools and duplicated effort.
- **Defining success as 100% adoption**: the long tail has diminishing returns.
- **Over-customizing for one or two big users**: it limits broad adoption.
- **Cutting corners because it's "internal"**: widely adopted tools become critical to SREs, and one misstep destroys credibility.
- **Engaging specialists too early**: bring them in once the project is off the ground and demonstrably successful.

## Reference Tables

**Traditional capacity planning cycle (never-ending):**

| Step | Question |
|---|---|
| 1. Collect demand forecasts | How many resources, when, and where? (several quarters to years) |
| 2. Devise build/allocation plans | How much supply, and in what locations? |
| 3. Review and sign off | Is the forecast reasonable, and aligned with budget, product, and technical constraints? |
| 4. Deploy and configure resources | Which services get them, and how do raw CPU and disk become useful? |

**Auxon components:**

| Component | Role |
|---|---|
| Performance Data | How a service scales (per unit of demand X in cluster Y, how many units of dependency Z) |
| Per-Service Demand Forecast Data | Usage trend, e.g. QPS by continent (Colossus-like services derive demand from their dependents) |
| Resource Supply | Available base resources over time, which is the LP **upper bound** |
| Resource Pricing | Cost of base resources (space and power per facility), which is the LP **objective** to minimize |
| Intent Config | Human-readable wiring layer: what a service is and how services relate |
| Auxon Configuration Language Engine | Sanity-checks the config and emits a protocol-buffer optimization request |
| Auxon Solver | Builds and solves the mixed-integer/LP model, scaling across hundreds or thousands of machines |
| Allocation Plan | Output: resources to services and locations, plus unmet requirements |

## Worked Example
**Auxon's development path:** an SRE and a TPM who had each done manual capacity planning in spreadsheets imagined the tool. Linear programming was unknown territory, so the team first shipped the heuristic **Stupid Solver** behind an abstracted solver interface, then swapped in an LP solver once they trusted the model. Automation systems were in flux at the time, so the **Allocation Plan** was made universally consumable ("agnostic"), and each automation system built its own integration. Machine-performance data was scarce, so it sat behind a single swappable interface that later grew into a simple modeling library. For adoption, the team first targeted teams with no capacity process. They promised immediate relief from manual bin packing of short-term requests, and said that the same config files would later yield broader long-term cost savings. They published a before/after case study with one Business Area and gave early adopters white-glove support. As the feature set grew, they added statistics and optimization specialists after consulting Google's Operations Research and Quantitative Analysis teams. Throughout, the team stayed on-call for production services, acting as both builders and users.

**Broad-use success:** a layer-3 load balancer built by Google SREs became Google Cloud Load Balancer.

## Key Takeaways
1. Fund SRE software projects as real products with roadmaps, users, documentation, and production readiness reviews, and keep SRE developers in production work.
2. For capacity planning (and similar problems), capture intent (dependencies, performance metrics, priorities) and let a solver generate the plan. Aim for at least intent level 3 (demand per region plus N+2).
3. Launch and iterate. Approximate unknowns behind swappable interfaces, and keep general designs grounded in a concrete use case.
4. Drive adoption deliberately: set MVP expectations, target users with no current solution, give white-glove support, design agnostically, and don't chase 100%.
5. Choose projects that are neither too service-specific nor too generic, that fit org objectives, and that have technical users and visible toil reduction.
6. Protect dedicated, uninterrupted project time, and partner with PMs and TPMs to fill product-team gaps.
7. Never lower engineering standards for internal tools.

## Connects To
- **Ch 1 (Introduction)**: the 50% cap on ops work leaves room for engineering projects.
- **Ch 2 (The Production Environment)**: service and cluster terminology.
- **Ch 5 (Eliminating Toil)**: software that removes toil keeps team size sublinear.
- **Ch 7 (The Evolution of Automation at Google)**: automation as the path to scaling SRE.
- **Ch 8 (Release Engineering)**: push-on-green.
- **Ch 17 (Testing for Reliability)**: load testing feeds performance metrics, and SRE tools need testing.
- **Ch 19 (Load Balancing at the Frontend)**: the SRE-built load balancer turned into Cloud Load Balancer.
- **Ch 29 (Dealing with Interrupts)**: protecting project time from interrupts.
- **Ch 32 (The Evolving SRE Engagement Model)**: production readiness reviews.
- **Linear / mixed-integer programming and bin packing (Operations Research)**: the solver behind intent-based planning.
- **Lean startup MVP**: setting expectations and launch-and-iterate.
