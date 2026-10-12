# Chapter 31: Methodology, Policy, and Politics

## Core Idea
The nontechnical side of running IT. The old philosophy — stability through **change minimization** — bred technical debt and made IT the obstacle. The modern answer is **DevOps**: merge developers and operations into one collaborative team that *drives* change rather than resisting it. Underpinning it all: ticketing, documentation, environment separation, disaster planning, policies/procedures, SLAs, and compliance. **The golden rule: enterprise needs drive IT activities, not the other way around.**

## Frameworks Introduced
- **DevOps = CLAMS**: **Culture** (silo-busting; Dev+Ops share 24×7 on-call, code/infra reviews, ChatOps — the most important tenet), **Lean** (real-time interaction, "what can we do *today*" — don't boil the ocean; a recurring weekly DevOps-planning meeting = instant failure), **Automation** (the two golden rules), **Measurement** (sub-second metrics across the whole stack, made visible to everyone), **Sharing** (internal + external knowledge sharing).
- **The two golden rules of automation**: (1) if you do a task more than twice, automate it; (2) **don't automate what you don't understand**.
- **Policies vs procedures**: a **policy** is a high-level rule ("incremental backups daily, full weekly") that changes rarely (review annually); a **procedure** is *how* you meet it ("with Backup Exec on backups01…") and evolves continuously. Confusing them breeds confusion.
- **Ticket ownership**: every task has a single well-defined owner (a coordinator, not necessarily a manager) — removes ambiguity. **Responsibility ≠ blame**; if "responsible" means "scapegoat," your pool of volunteers vanishes.
- **SLA structure**: scope/descriptions of services + standards (availability, response time) + queue prioritization + conformance measurements.

## Key Concepts
- **Ticketing system**: one system spanning all IT (enhancements, issues, bug tracking). Prevents tasks falling through the cracks and duplicated effort; becomes a searchable history of problems + solutions. A **prompt human response matters more than an immediate fix** — users will wait if not ignored.
- **Documentation value**: reduces single-point-of-failure, aids reproducibility, saves time, and (most important) keeps the system *intelligible* so changes conform to architecture instead of accreting as hacks.
- **Infrastructure as code as documentation**: config definitions (Puppet/Ansible) in version control — the documentation and environment always match (solves traditional docs' staleness).
- **Environment separation**: dev/test/prod must be **separate but identical**; config changes (OS patches → app updates) flow through the same structured release control as code.
- **Disaster recovery**: risk assessment (catalog threats — note insiders are ~half of breaches and the highest-likelihood disaster) → prioritize services → a written plan (NIST 800-34) → **off-line copies of everything** (mirroring ≠ backup; both data centers can be lost).
- **Queue priorities** (simple beats complex): "many people can't work" > "one person can't work" > "requests for improvements"; tie-break by severity; lower queues FIFO.
- **Compliance alphabet soup**: SOX, COBIT, ITIL, ISO 27001, HIPAA, PCI DSS, COPPA, FERPA, CJIS — the standard you must follow is dictated by your org type / data handled.

## Mental Models
- **DevOps is about overcoming territorial impulses.** "You are most effective if you are seen as a hero who helps everyone else succeed." The optimal Dev/Ops overlap is higher than people naturally prefer — get comfortable with cross-discipline feedback. (Shared on-call hurts for ~6 weeks, then suddenly clicks.)
- **Role separation to "protect production" is theater.** Promoters rarely have the skills/time to catch malicious code — it creates a false sense of safety and roadblocks. The DevOps fix: track all changes as code in an immutable-audit-trail repo (Git), evaluate identical changes in lower environments first, and revert by bypassing the bad commit.
- **Fight ticket "blah blah blah."** Once you guess what a ticket is about, the rest looks like noise — but misreading it sends the user back to square one. Read fully; vague tickets often need decoding (trace back the user's mental model to the real problem).
- **No news is good news to users.** They want to know *when* it'll be fixed, not which disk failed — "our customers are happiest when they don't even notice we exist."
- **Don't operate close to the wire.** Hire enough sysadmins; don't expect 12-hour days. Disaster plans assume staff are available — but people get sick, quit, or turn hostile.

## Anti-patterns
- **Change minimization as a philosophy**: accumulates untouchable technical debt; IT falls behind the business.
- **Automating what you don't understand** / not automating thrice-repeated tasks.
- **A recurring weekly meeting to plan your DevOps implementation**: you've "instantly failed" — DevOps is lean and real-time.
- **Treating ticket "responsibility" as blameworthiness**: punishes help-seeking; volunteers dry up. (Also: a sysadmin who flags an unpopular task gets stuck with it — give an anonymous/ownerless way to raise issues.)
- **Documentation as a dissertation**: ask for too much and you get none. Standardize on short, one-page, concise, *unpolished* docs; comment config files (best docs of all); use templates to beat blank-page anxiety.
- **Information redundancy in docs**: one authoritative master list, scripts to derive/check the rest (run from cron) — manual updates in multiple places drift.
- **Mirroring instead of off-line backups**: ransomware/hackers/dual-DC loss destroy orgs without read-only off-line backups.
- **Forbidding all user customization**: easy for IT but users subvert the rules — instead standardize a few configs and generously absorb users' suggested modifications.

## Reference Tables
**CLAMS tenets**: Culture (collaboration, shared on-call, ChatOps) · Lean (real-time, incremental) · Automation (two golden rules) · Measurement (sub-second, visible, targeted) · Sharing (internal + external).

**Automation strategy must cover**: automated new-machine setup (multiple types), automated config management, automated code promotion (dev→test→prod with automated testing), systematic patching (handle offline machines).

**SLA / metrics to track**: projects on time/budget, SLA elements met, uptime % per system, tickets resolved + avg resolution time, time to provision a system, security incidents handled per process.

**Disaster support data (kept off-line)**: recovery procedure + contacts, service-contract numbers, key phone numbers, cloud logins, backup inventory/schedule, network maps, license keys/passwords, install media (ISOs), service manuals, config data (OS/patch/partition), ordered startup instructions.

## Worked Example
**Replace "protect production with role separation" with the DevOps approach.** The old fear: a disgruntled developer with promotion rights inserts malicious code and pushes it to prod, so you split duties — different people have admin in dev vs test vs prod, requiring collusion to do harm. In practice this fails: the promoters lack the skill/time to actually review changes for mischief, so you get a *false* sense of protection plus roadblocks and wasted resources. The modern fix: (1) track **every** change — code *and* configuration (OS patches, app updates, admin changes) — as code in a Git repo with an immutable audit trail, so any bad change is traceable to the human who made it; (2) apply changes through an **automated, identical** mechanism across environments, so a change is evaluated in dev/test *before* promotion to catch unintended consequences; (3) if a problem surfaces, revert by identifying and temporarily bypassing the offending commit. The aspirational end state — *no human* (Dev or Ops) has admin in production, all changes go through a tracked automated process with its own privileges — is a worthy goal but not yet realistic for most orgs. Work toward it; don't get trapped by it.

## Key Takeaways
1. Abandon change-minimization for DevOps (CLAMS): one collaborative Dev+Ops team that drives change — culture is the most important tenet, automation the most recognized.
2. Automate anything done >twice, but never what you don't understand; cover setup, config management, code promotion, and patching.
3. Run one cross-IT ticketing system with single-owner tasks (responsibility ≠ blame); a prompt human reply beats an instant fix.
4. Keep documentation short, concise, unpolished, searchable, and ideally as infrastructure-as-code so it never goes stale; one authoritative source, no redundancy.
5. Keep dev/test/prod separate but identical; track all changes as code with an audit trail instead of role-separation theater.
6. Plan for disaster (risk assessment, prioritized services, NIST 800-34 plan, off-line copies of everything — mirroring isn't backup); codify policies (stable) vs procedures (evolving), SLAs, and the compliance regime your data demands.

## Connects To
- **Ch 23**: configuration management (automation, infrastructure as code).
- **Ch 26**: CI/CD (environment separation, code promotion, automated testing).
- **Ch 28**: monitoring (the Measurement tenet; ticket auto-creation).
- **Ch 27**: security (incident handling, insider threat, compliance).
- **Ch 30**: data center (disaster planning, physical risk assessment).
- **Ch 1**: the role's essential duties — this chapter is the organizational frame around all of them.
