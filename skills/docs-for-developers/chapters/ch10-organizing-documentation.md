# Chapter 10: Organizing Documentation

## Core Idea
As docs grow, organization becomes the bottleneck — "we documented it" isn't enough if users can't find it. **Information architecture (IA)** is the structure you apply so readers build a **mental model** of your content and you know where new pages go.

## Frameworks Introduced
- **Information architecture (IA)**: the organizational structure of your docs; helps content scale without confusing readers.
- **Three ways to organize content**:
  - **Sequences** — one page after another (chronological steps, alphabetical index/glossary). Writer chooses the order.
  - **Hierarchies** — parent/child tree; broad → specific. One topic, many subtopics.
  - **Webs** — interconnected non-hierarchical pages, each linking to others (Wikipedia). Reader chooses the path.
  - Real sites **combine** all three.
- **Three navigation elements**: site navigation/organization, **landing pages**, **navigation cues**.
- **Users expect content to be**: **Consistent** (familiar patterns, always know where you are), **Relevant** (most-common needs easiest to find), **Findable** (reachable from home/landing pages and search).

## Key Concepts
- **Landing page**: a signpost that routes users to the right content with minimal reading — short, scannable, jargon-free, fewest clicks to a doc. Don't nest landing pages under landing pages.
- **Navigation cues**: breadcrumbs, side navigation, labels/metadata, prerequisites/next-steps sections, **escape hatches** (callouts pointing to a better page). Use *economically* — too many pointers cause decision fatigue; negative space helps.
- **Content gap**: information users request that doesn't exist yet — surfaced during assessment.
- **Card sorting**: write each page on a card, rearrange to experiment with structures and get user feedback.
- **Content reuse caution**: a doc fitting multiple locations → keep it in one best location and link to it; automated reuse hurts search and maintenance.

## Mental Models
- Users entering your docs are like travelers in an unfamiliar airport — scanning for signs of where they are and where to go next.
- Aim for an IA neither too deep nor too shallow (split deep sections; merge single-page sections).
- A consistent IA tells you exactly where new content belongs.

## Reference Tables
The organizing process:

| Step | Action |
|---|---|
| Assess existing content | List every page (title + URL); label Keep / Remove / Review / Merge / Split; find content gaps |
| Outline new IA | Map to users' mental model; ensure Consistent/Relevant/Findable; card-sort |
| Migrate | Audit via checklist; add redirects |

Migration validation checklist: landing pages sparse & guiding · content types consistent · page data (titles/headers/prereqs/next steps) descriptive · navigation cues present · labels/metadata for search · **redirects** from old URLs.

## Worked Example
**Corg.ly's video feature nobody could find.** After an alpha video release, Mei reports her team couldn't find how to send a video and get translation text. Karthik clicks through the site several times and admits "it's buried deep." Mei: "Without your direct link, I'd never have found it." The fix is IA: a Corg.ly **landing page** with three top sections (Getting Started, the two most-used how-tos), each a hierarchy of sequential how-to pages, plus breadcrumbs and escape hatches. They assess all pages, card-sort a new map, and migrate with redirects — then *document the IA itself* (site map + templates) for consistency.

## Anti-patterns
- **"We documented it" buried deep** — undiscoverable = nonexistent to the user.
- **Too many navigation cues / nested landing pages** — decision fatigue.
- **Automated content reuse** for org convenience over user benefit.
- **No redirects on migration** — strands users on dead URLs.

## Key Takeaways
1. IA is how readers build a mental model of your content.
2. Organize with sequences, hierarchies, and webs — usually combined.
3. Landing pages route fast; navigation cues orient — use both sparingly.
4. Assess (Keep/Remove/Review/Merge/Split) → find gaps → card-sort → migrate with redirects.
5. Document your IA so the team knows where new content goes.

## Connects To
- **Ch 9**: findability is the functional-quality lens on IA.
- **Ch 2**: clear content types make navigation predictable.
- **Ch 1**: users' mental model comes from research.
- **Ch 11**: a big release that moves many pages forces IA re-evaluation.
