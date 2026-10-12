# Chapter 11: Maintaining and Deprecating Documentation

## Core Idea
Maintenance is the #1 cause of doc failure. Keep docs in sync with code by planning them together, releasing them together, assigning **owners**, automating **toil**, and deliberately **deprecating then deleting** stale content (with notice and redirects).

## Frameworks Introduced
- **User impact analysis**: a short version of Ch 1 research, run per change. Answer: How are users impacted? How does it affect existing functionality? What existing docs does it affect? What new docs are needed?
- **Align docs with the release process**: code + docs ship together so they never diverge. Track each doc update as an issue/bug or in a feature spreadsheet.
- **Document owners**: explicit, unambiguous responsibility ("everyone's job = no one's job"). Use `CODEOWNERS` or an owner comment in the doc.
- **Automate to eliminate toil** — toil = "manual, repetitive, automatable, tactical, devoid of enduring value, scales linearly as a service grows" (SRE definition). Tools: freshness checks, link checkers, prose linters, reference doc generators.
- **Deprecate → notify → delete**: mark superseded content, tell users (don't hide it), then remove safely with redirects.

## Key Concepts
- **Content freshness check**: `last modified` dates + future review reminders (e.g. Google's 6-month metadata ping to the owner). Freshness-checked docs are more trustworthy.
- **Link checker**: flags 404s; runs in CI/CD pre-publish or crawls post-publish.
- **Prose/documentation linter**: like a code linter ("fancy regex") — catches style, template, and exclusionary-language issues; teach it custom words (e.g. "Corg.ly").
- **Reference doc generators**: OpenAPI, Javadoc — auto-generate accurate API reference, less hand-maintenance.
- **Migration guide**: helps users move off a deprecated feature; publish it *before* announcing the deprecation.
- **Reward maintenance**: build doc work into performance expectations, not an "extra"; recognize it.

## Mental Models
- Plan docs early so you can budget time and prevent drift.
- "Good automation saves people from toil, but bad automation can compound toil into a crisis" — understand every step before automating.
- Deleting content you wrote feels sad, but tidiness helps users find what's relevant. Delete when migrated-away or not worth fixing.

## Code Examples
Owner and freshness metadata embedded in a doc:
```html
<!-- Owners: Charlotte@corgly.com, Karthik@corgly.com -->
<!--Freshness: {owner: "karthik" reviewed: 2021-06-15} -->
```
Deprecation callout linking to the replacement:
```text
Deprecated: the Corg.ly Audio API was deprecated on August 20, 2021.
It has been replaced by the Corg.ly Multimedia API, which supports audio and video.
```
- **What it demonstrates**: clear ownership, automated freshness review, and a non-hidden deprecation notice with a forward path.

## Reference Tables
Automation tools for maintenance:

| Tool | Eliminates | How |
|---|---|---|
| Freshness checks | Stale content | `last modified` + timed owner reminders |
| Link checkers | Broken links | CI/CD pre-publish or post-publish crawl |
| Prose linters | Style/grammar/exclusionary language | Regex-based, custom dictionary |
| Reference doc generators | Hand-maintained reference | OpenAPI / Javadoc from source |

## Worked Example
**Kubernetes' release-coupled docs process** (43,000+ contributors): (1) a tracking spreadsheet lists proposed enhancements; (2) each enhancement has a GitHub Issue requiring a design doc, owner, unit tests, and a docs-needed assessment; (3) if docs are needed, the feature owner must open and get approval on a docs PR *before* the enhancement is approved; (4) code + tests + docs all approved → enhancement approved; (5) on release day all approved enhancements ship together. Tightly coupling docs to the release keeps them from diverging from the code.

**Delete decision**: Karthik has audio and video tutorials. Video gets huge traffic; audio gets few views, out-of-date samples, and many filed issues. Even though audio is still supported, he *deletes* the heavy audio tutorial and points users to a shorter, easier-to-maintain doc — using analytics (Ch 9) + feedback (Ch 8) to justify it.

## Anti-patterns
- **Write-once docs** that drift from code → frustration and lost trust.
- **Hiding deprecated features** instead of announcing them → users break unexpectedly.
- **No owner** → docs go stale.
- **Automating before understanding the steps** → compounds toil.
- **Deleting without notice/redirects** → strands users.

## Key Takeaways
1. Plan code and docs together; run a user impact analysis per change.
2. Release docs with the feature so they stay in sync (Kubernetes model).
3. Assign explicit document owners.
4. Automate toil: freshness checks, link checkers, linters, ref generators — carefully.
5. Deprecate with callouts + migration guides, then delete with notice and redirects.

## Connects To
- **Ch 7**: maintenance extends the release process and publication cadence.
- **Ch 8 & 9**: feedback and analytics drive delete/keep decisions.
- **Ch 5**: sample testing is part of accuracy maintenance.
- **Ch 6**: visuals decay fastest — share source files.
