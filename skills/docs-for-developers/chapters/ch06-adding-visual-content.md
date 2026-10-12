# Chapter 6: Adding Visual Content

## Core Idea
Visuals convey information faster than text (the brain processes an image in ~13ms; illustrated instructions were 323% more effective) — but they're **high-risk/high-reward**. Judge every visual on three axes: **Comprehension, Accessibility, Performance**.

## Frameworks Introduced
- **The three failure modes of visual content** — ineffective visuals lack:
  - **Comprehension**: readers ignore images not relevant to them; overcrowded diagrams (crossing arrows, missing labels, mixed abstraction) hinder.
  - **Accessibility**: screen readers need descriptions; color-vision-deficient and dyslexic readers need contrast and not-color-alone meaning.
  - **Performance**: large images hurt load times on slow connections/low-spec machines.
- **Three process diagram types**:
  - **Boxes and arrows** — relationships/data flow between entities (`Database ➤ API ➤ Front-end ➤ User`); consistent shapes, no crossing lines, label/legend ambiguous links.
  - **Flowcharts** — start→finish processes; consistent shapes (rectangle = process, diamond = decision).
  - **Swimlanes** — multi-actor processes; each actor a lane, so responsibility per step is obvious at a glance.
- **"Simplify to amplify"** (Scott McCloud, *Understanding Comics*): removing unnecessary detail amplifies meaning. **One idea per diagram.**
- **Graphical excellence** (Edward Tufte): "the greatest number of ideas in the shortest time with the least ink in the smallest space"; "every single pixel should testify directly to content."

## Key Concepts
- **Alt text best practice**: better than alt text alone is describing the image *in the body text* as if the image weren't there ("there is a small cog at the top of the menu", not "an image of a small cog…"). Blank alt = tell screen readers to ignore.
- **C4 model** (Simon Brown): standardized way to diagram architecture at levels of abstraction.
- **WCAG**: accessibility guidelines, useful for diagrams too; color contrast ≥ **4.5:1**.
- **Visual content is a supplement, not a replacement** for written docs.

## Mental Models
- Start on paper/whiteboard/sticky notes; prototype and do rudimentary user testing before fiddly tooling.
- Find the reader's starting point (Western readers: top-left); guide the eye.
- Use multiple simple diagrams over one complex one — overview diagrams for conceptual docs, low-level data-flow diagrams for reference docs.
- "Learning styles" (visual vs verbal learners) is debunked — good visuals help almost everyone.

## Reference Tables
Screenshot rules:

| Do | Don't |
|---|---|
| Introduce/reference in text first | Leave it unreferenced |
| Place near related instructions | Make it the *sole* source of IP addresses/code |
| Keep clean, clutter-free, full context | Include non-UI clutter |
| Annotate (boxes/arrows/gray-out) to focus | Make it too big or too small |

## Worked Example
**Charlotte's architecture overview.** Karthik comments that her prose doesn't make the data flow (dog → translation service → user's web app) clear. Rereading with distance, she sees users are short on time and need to assess integration fast — words aren't enough, so she reaches for a **box-and-arrows diagram**. She'd start on paper, lay out entities and one-way vs two-way flows, label microservices with a legend, publish as **SVG** (scales/zooms at any screen size), and describe it in the body text for accessibility.

## Anti-patterns
- **Decorative images** with no relevant information — ignored by readers.
- **Video as a cure-all**: hard and expensive to create, costly to maintain, fast to go stale ("abandoned YouTube channels"); needs a professional, captions, and a timestamped transcript. Usually a well-written doc + images is cheaper.
- **Screenshotting copy-pastable content** (code, IPs).
- **Reviewing a visual in isolation** — check it with its surrounding text, on mobile and large screens.
- **Not sharing source files** — makes updates impossible; visuals go stale even faster than text (a UI change kills a screenshot).

## Key Takeaways
1. Visuals are faster than text but high-risk; supplement, never replace, prose.
2. Score every visual on Comprehension, Accessibility, Performance.
3. One idea per diagram; simplify to amplify; be consistent with shapes/colors/labels.
4. Make visuals accessible: describe in body text, 4.5:1 contrast, never color alone, SVG format.
5. Be very wary of video; it's expensive and decays fast.
6. Visuals are content — edit them (Ch 4) and maintain them (Ch 11).

## Connects To
- **Ch 3**: visuals break up walls of text.
- **Ch 4**: same editing process applies to visuals.
- **Ch 5**: keep code copy-pastable, never a screenshot.
- **Ch 1 & 11**: curse of knowledge clouds visual judgment; maintenance is the top failure cause.
