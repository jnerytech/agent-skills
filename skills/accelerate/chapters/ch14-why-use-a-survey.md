# Chapter 14: Why Use a Survey
*Authors: Nicole Forsgren, Jez Humble, Gene Kim*

## Core Idea
Well-designed psychometric surveys are a fast, trustworthy, and sometimes the *only* way to measure software delivery and culture, and they complement "system data" from toolchains rather than being inferior to it.

## Frameworks Introduced
- **Five reasons to use survey data**: (1) Surveys allow you to collect and analyze data quickly. (2) Measuring the full stack with system data is difficult. (3) Measuring completely with system data is difficult. (4) You can trust survey data. (5) Some things can only be measured through surveys.
  - When to use: deciding how to baseline delivery performance or culture, or answering "why not just instrument the pipeline?"
  - How: use surveys for one-off, cross-organizational, or perception-based measurement; use system data for high-precision, in-boundary signals; triangulate the two.
  - Why it works: every respondent answers the same vetted items with the same definitions, so naming drift between teams disappears. Failure mode: poorly worded or leading ("propaganda") items. Survey quality depends entirely on item quality.
- **Three trust questions (thought exercise)**: ask a technologist (1) "Do you trust survey data?" (usually no), (2) "Do you trust your system/log data?" (usually yes), (3) "Have you ever seen bad data come from your system?" (almost always yes).
  - When to use: to challenge the bias that system data is objective and survey data is suspect.
  - How: point out that humans build systems, humans make mistakes, and one bad actor with root access can corrupt the few data points a business watches.
  - Why it works: it shows people are inconsistent about which data they trust, and that systems can produce bad data too.
- **Bad-actor exposure comparison**: system data can be corrupted by *one or a few* people (a mistake or a malicious change), and the error may go unnoticed for months or years. Survey data pooled across a large sample (23,000+ respondents) would need *several hundred* coordinated liars, all shading every item of a latent construct by the same amount in the same direction, to move the results.
  - How: use latent constructs, careful wording, psychometric validity/reliability tests, a large and global sample, and anonymous responses.

## Key Concepts
- **System data**: data gathered by instrumenting the delivery process and toolchain (e.g., tool-reported lead time).
- **Lead time (book definition)**: time from code commit to code in a deployable state.
- **Cycle time**: defined by some as time from development starting work on code to code in a deployable state. It is often confused with lead time.
- **Definitional drift**: teams use the same name for different measures, or different names for the same measure. This corrupts pooled system data.
- **Common method variance (CMV) check**: an analysis that confirms the survey instrument itself has not introduced bias. Early-vs-late responder bias checks are also run (see Appendix C).
- **Full-stack blind spot**: system data only sees what is inside the instrumented boundary.
- **Objective vs. subjective data**: objective data is not influenced by feelings. Subjective data captures perceptions or feelings, and it is the only way to measure culture.
- **Proxy metric**: an indirect stand-in (e.g., turnover for culture). Proxies rarely map directly to the construct.
- **Anonymity**: a safeguard that encourages honest answers.

## Mental Models
- Use surveys when data must cross organizational or legal boundaries, or must be collected once at scale in weeks. Collecting system data from thousands of organizations in 4–6 weeks is effectively impossible.
- Think of people as sensors outside the system boundary: they can report what logs cannot, such as the interface, the denominator, or the "why."
- Use system data for precision and survey data for coverage and meaning. Imprecise human reports (minute-level) can still tell you *where to look* when precise logs (millisecond-level) say all is well.
- Think of turnover as a confounded signal: many non-culture causes move it, and managers can game it.

## Anti-patterns
- **Trusting system data blindly**: humans build systems, and bugs or one malicious insider (the *Office Space* "rounding error") silently corrupt the few metrics the business watches.
- **Pooling tool metrics with inconsistent definitions**: "lead time" in team A ≠ "lead time" in team B, so the analysis is meaningless.
- **Proxying culture with retention/turnover**: people leave for pay, a partner's relocation, or a career change. A *great* culture can even cause turnover by encouraging people to grow. Managers can game the metric by laying off job-seekers or blocking transfers.
- **Measuring version control use from the system**: the system cannot count files *not* in version control, so it cannot compute the percentage.
- **Coercive surveys**: "Beatings will continue until morale improves." Forcing positive answers produces meaningless data. Collect anonymously and with an eye toward improvement.
- **Surveying only a few people**: a small number of overly positive or negative responses skews results. Survey everyone on the team.

## Worked Example
**IBM disk-storage "the box is fast" case.** One author worked as a performance engineer on enterprise disk storage (read, write, cache, RAID rebuild). Metrics at every level showed excellent performance, yet customers kept reporting slowness. The team dismissed the first reports because "the logs showed it." The reports kept coming and showed a consistent pattern, though only at minute-level precision versus millisecond logs. That told the team where to look. Root cause: the box was fine. The **interface**, meaning how customers interacted with the box, was not instrumented and was introducing major degradations. The team set up a small group to own the interface, and the full system reached peak performance. Lesson: periodically ask the technologists and users about system performance to find bottlenecks that system data cannot see.

**Version control coverage.** To learn what share of production artifacts are in version control, ask the team. They see all the work. The system only sees what has been checked in and has no denominator.

## Key Takeaways
1. Pair toolchain metrics with periodic, anonymous surveys of everyone who builds and delivers the software.
2. Fix definitions in the survey items themselves. Ask about the precise behavior rather than relying on each team's local term.
3. Treat system data as fallible. Validate it the same way you would validate survey data.
4. Measure culture, feelings, and the "why" behind behavior only through surveys. Don't substitute HR proxies.
5. Make survey data trustworthy with latent constructs, careful item writing, psychometric validity/reliability tests, a large sample, and anonymity.
6. Culture is worth measuring: it is predictive of technology and organizational performance, and team dynamics and psychological safety are the most important factors in team performance (Google 2015).

## Connects To
- **Ch 2**: delivery performance metrics (lead time defined precisely here).
- **Ch 3**: Westrum culture, the canonical "only measurable by survey" construct.
- **Ch 4**: version control and CI, measured by asking about core practices.
- **Ch 13**: latent constructs, validity and reliability, which justify trusting surveys.
- **Ch 15**: sampling design that produced the 23,000+ responses.
- **Ch 17 / Appendix C**: CMV and early/late-responder bias tests.
- **Google Project Aristotle (2015)**: psychological safety as the top team-performance factor.
- **Kahneman (2011)**: using retention to evaluate interview processes.
