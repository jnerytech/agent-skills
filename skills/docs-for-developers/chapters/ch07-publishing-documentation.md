# Chapter 7: Publishing Documentation

## Core Idea
Publishing = making content available electronically, like a software release. Build a **content release process**, coordinate with the code release, assign a **single final approver**, test the docs, and **meet your users where they are** — then publish and iterate (no doc is perfect at release).

## Frameworks Introduced
- **Content release process**: the plan for publishing. Answers: **When** publish? **Who** does final review/publication? **Where**? **What** tools? **How** to announce? Can be a lightweight checklist or a full integration with the software release. Scale it to the size of the launch.
- **Publishing timeline (Gantt chart)**: work backward from the publish date through all tasks (research, plan, draft, edit, review, upload) so you reserve enough time. Build it into the *software* release timeline with stakeholder buy-in.
- **Single final approver**: one named person with final say to allow or halt the release; also tests/reviews beforehand. "No document is perfect, but no released document should be harmful."
- **Meet your users where they are**: choose the publishing destination by how readers want to consume it.

## Key Concepts
- **Coordinate with code releases**: dev docs must ship *with* the software they describe — "no UI design can cover up missing documentation." Small doc updates → just note in release notes.
- **Documentation triage for release**: reuse your code bug-triage categories — would it cause harm? data loss? system damage? Define stop-the-release criteria in advance.
- **Test the docs**: run procedures manually if no automated tests; watch for skipped "obvious" steps (`brew install --cask firefox` assumes macOS + Homebrew + CLI + permissions). Err toward overexplaining, but don't bury the core use case in sandwich-bag-fastener detail.
- **Test document first**: when publishing to a new location/toolchain, push a single test doc through the process first; note the gaps ("your documentation needs documentation").
- **Critical-response planning**: some docs are incident-worthy; if yours is critical, have a runbook and pager plan like ops.

## Mental Models
- Publishing is no longer a printed artifact — patch and update docs like software.
- Don't fall into "just a few more fixes" paralysis; ship and iterate on feedback.
- Don't automate the publishing process until you've felt the real friction points — "you can't automate toil away until you understand where toil exists."
- If you wouldn't ship code without peer review + tests, don't ship docs that way.

## Reference Tables
"Meet your users where they are" — destination by audience:

| Audience | Where to publish |
|---|---|
| Internal teams | Private wiki / intranet |
| External devs working with code/endpoints | Same repo as the code |
| End users / sysadmins installing software | *External* to the software (avoid a dependency loop) |
| External users of your codebase | Website or code repository |

## Worked Example
**Corg.ly ships.** Charlotte and Karthik weigh publishing options and pick the simplest that works: a new docs section on the company website, managed in the *same version control system* as their code. Karthik writes a short company-blog post so everyone knows it's live and where to find it. For new users, the announcement links to the most logical entry point — the **Getting Started** page. They keep the release process light here but plan a full timeline (software + content), final reviewers, and the announcement because it's a major launch.

## Anti-patterns
- **Perfection paralysis**: never shipping because of "a few more fixes."
- **Publishing docs separately from the software** they describe.
- **No single approver**: nobody owns the go/no-go.
- **Premature automation** of publishing before understanding the toil.
- **Publishing where it isn't indexed/findable**: effort wasted if no one can find it.

## Key Takeaways
1. Build a content release process aligned with the software release.
2. Use a timeline (Gantt) and reserve writing/review time inside the release schedule.
3. Assign one final approver; define harm-based stop criteria in advance.
4. Test the docs (procedures + samples) before release.
5. Meet users where they are; announce on launch; run a test doc through new toolchains first.
6. Iterate the process; automate only after you find real friction.

## Connects To
- **Ch 4**: release testing extends the editing/review process.
- **Ch 8**: post-publish, gather and triage user feedback.
- **Ch 9**: announce → then measure quality.
- **Ch 11**: publication cadence and runbooks feed maintenance.
