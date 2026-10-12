# Chapter 3: Living documentation

## Core Idea
The long-term payoff of Specification by Example isn't regression testing — it's a **living documentation** system: an authoritative, low-cost-to-maintain body of documentation derived from executable specifications that always describes what the system actually does. Treat that documentation as a first-class deliverable, as vital as the code itself.

## Frameworks Introduced
- **Documentation-centric model**: View the artifacts of Specification by Example (specs + examples) primarily as living documentation of business processes, not as tests or acceptance criteria.
  - When to use: when things run smoothly and you want the long-term benefits — supporting, evolving, and rewriting systems over years; especially for systems automating complex business processes.
  - How: (1) treat living documentation as a separate, key artifact; (2) keep specs focused on business intent, not test scripting; (3) version-control the specs; (4) organize/structure them well; (5) budget how much to invest up front to avoid both gold-plating and neglect.

- **Three models of looking at Specification by Example** (choose by purpose, none is superior):
  - **Acceptance-testing-centric model (ATDD / A-TDD)**: focuses on the automated tests. When to use — initial adoption when a team has many functional quality issues. Benefits: clearer development targets, preventing functional regression.
  - **System-behavior-specification model (BDD)**: focuses on specifying scenarios of system behavior. When to use — explaining short/mid-term delivery activities once quality is under control. Benefits: shared understanding via collaboration and clarification.
  - **Documentation-centric model**: focuses on business-process documentation. When to use — securing the long-term benefits and avoiding test-maintenance problems.

## Key Concepts
- **Living documentation**: documentation built from executable specifications that stays consistent with the system because it's continuously validated; "as relevant and reliable as the code but much easier to understand."
- **Executable specification**: a specification with examples that can be continuously validated against the system, so it's always either passing (consistent) or visibly failing (out of sync).
- **Authoritative documentation**: a source you can trust because it's "exercised" — automatically validated — and so never carries the "not entirely correct" warning.
- **System archeology** (Christian Hassa): reverse-engineering business functionality out of source code because no trustworthy documentation exists.
- **Business-process documentation**: documentation of what the system does from a business perspective, grown incrementally alongside the software.

## Mental Models
- **Specs-as-pages, living-documentation-as-the-book**: each specification with examples is a page; assembled and cross-linked, they form the authoritative book describing the system.
- **Documentation ages like cheap wine**: long paper documentation degrades fast and gives you a headache a year later; executable specs don't age because differences surface immediately and at low cost.
- **"If it isn't exercised, don't trust it"** (Tim Andersen): documentation that isn't automatically validated cannot be trusted, because nothing keeps it honest.
- **Tests vs. documentation framing**: when information guides development, supports the system, or estimates the impact of changes, calling it a "test" is misleading — tests don't support and evolve systems, documentation does.

## Anti-patterns
- **Reverse-engineering from code**: relying on "system archeology" to learn what a system does — impossible for business users, testers, support, and most developers, and the old system may be wrong anyway.
- **Long paper documentation**: comprehensive docs are costly to maintain; most cost is finding what's outdated, not changing it — and it drifts out of sync.
- **Tests that aren't designed to be maintainable**: the core pitfall of the acceptance-test-centric approach — easy to find what to update, but expensive to update unless tests reveal their purpose.
- **Over-investing / gold-plating the tests**: polishing tests at the expense of the primary product; avoid by deciding up front how much to invest in the documentation system.
- **Piling thousands of incomprehensible tests in one directory**: useful documentation must be well organized.
- **Delegating acceptance tests to junior developers/testers**: obviously flawed once you see the specs as key documentation.
- **Keeping specifications too abstract**: a real pitfall of the documentation model; UI-centric projects with little process complexity benefit less.

## Worked Example
Adzic's argument runs as a chain. **First**, we genuinely need to know what a system does — to analyze change impact, support, and troubleshoot. The usual fallback, reading source code, is "system archeology": Christian Hassa's team had to replace a legacy system whose calculations no one understood; reverse-engineering the requirements was horrible and revealed the old system was partly wrong. So paper docs ("not entirely correct") fail, and undocumented code fails.

**Second**, automated tests have the opposite property: it's easy to find what's out of sync (failing tests show it instantly), but they're costly to update unless designed to reveal their purpose. Once teams make tests maintainable and purpose-revealing, the tests *become* documentation. Adam Knight (RainStor) produced HTML reports listing tests and their purpose, making regression investigation and conflict resolution easy — "they don't have to use any other kind of documentation." Lisa Crispin (ePlan) opens the FitNesse test to see exactly what the code does. Andrew Jackman's Sierra team answers "where does this data come from?" by sending a link to a test result — "We don't have specifications in Word documents."

**Third**, the synthesis: when a software system is **continuously validated against executable specifications**, the team can be certain the system does what the specs say — and equivalently, the specs keep describing the system. Differences surface immediately, so consistency is maintained at low cost. Tim Andersen: "If I cannot have the documentation in an automated fashion, I don't trust it. It's not exercised." This body of always-consistent, authoritative information is the living documentation — the *book* assembled from spec *pages*. It's incremental and cheap because specs grow with the software; no six-month, 500-page documentation freeze. Tools already export specs to HTML/PDF or websites (e.g., **Relish** assembling a documentation website from executable specs), bootstrapping the system.

**Finally**, the benefit: teams that rewrote the heart of their systems kept the specs with examples and used them to guide the whole effort — instead of months of system archeology, the living documentation already supplied the requirements. That's where the investment pays off.

## Key Takeaways
1. Regression prevention is real but not the long-term justification — Capers Jones puts regression testing's average defect-removal efficiency at only 23%; the durable payoff is documentation.
2. Continuously validating a system against executable specifications keeps specs and system consistent automatically and cheaply, producing **authoritative** documentation free of the "not entirely correct" problem.
3. Well-designed, purpose-revealing tests *are* good documentation; once they're easy to maintain, the other long-term benefits appear.
4. Call it documentation, not tests — what guides development, supports the system, and estimates change impact is documentation.
5. Treat living documentation as a separate first-class artifact, as important as the code; this single shift answers many practical questions (version-control the specs, organize them, don't delegate them to juniors, clean them up as standard work).
6. Build it incrementally and alongside the software, and budget the investment to avoid both neglect and gold-plating.
7. The model fits complex business-process automation best; beware overly abstract specs and low payoff on UI-centric projects.

## Connects To
- **Ch 2**: Living documentation is the seventh key process pattern — "evolving a documentation system" — introduced there; this chapter develops it as the central long-term goal.
- **Ch 10**: Validating frequently — the continuous validation that keeps documentation consistent and trustworthy.
- **Ch 11**: Evolving a documentation system — restructuring and cross-linking key examples into the living documentation in increments.
- **Ch 12**: Managing the spec/test set over time (e.g., uSwitch disabling tests after first implementation) — maintenance practices that protect the documentation.
