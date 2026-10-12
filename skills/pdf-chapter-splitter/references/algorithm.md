# How the splitter derives chapters from the outline

Read this when a split comes out wrong, or before changing
`scripts/split_pdf_by_chapters.py`. In a normal run you don't need it — run
`--inspect` and read what it prints.

1. **Parse the whole nested outline tree**, not just depth-0, into
   `{title, page, children}` nodes via `reader.outline` and
   `reader.get_destination_page_number`.

2. **Detect Part wrappers per top-level node, independently.** For each
   depth-0 node, if at least half of its direct children have a title
   matching a chapter-numbering pattern (`1 …`, `Chapter 1…`, `Capítulo 1…`),
   that node is a Part wrapper: its *children* become the split units, tagged
   with the Part's label for the filename. A depth-0 node whose children
   don't match — or that has no children, like `Preface` or `Index` — stays a
   single unit. A book that mixes both shapes still splits correctly, section
   by section.

3. **Drop bookmarks whose page doesn't advance**, reported as `NOTA` lines,
   never silently:
   - *backwards* — stray bookmarks (often pointing at an embedded image)
     appended after the real outline; keeping them corrupts every page range
     that follows;
   - *repeated* — a bookmark on the same page as the previous one, which
     yields an `end < start` range and therefore a **0-page PDF**: a chapter
     that appears to exist but has no content, and that `pdftotext` reads as
     empty further down the pipeline.

4. **Compute `[start, end]` ranges** over the surviving units: each runs from
   its own start page to one page before the next unit's start; the last runs
   to the end of the document. If the first unit doesn't start at page 0,
   everything before it (cover, title page) becomes a `Front Matter` unit so
   no page is silently dropped.

5. **Check coverage** — the ranges must tile the document exactly. Gaps,
   overlaps, empty ranges and a page total that doesn't match are reported as
   `PROBLEMA` and make the script exit non-zero.

6. **Write one PDF per range** and name it `NN - Title.pdf`, or
   `NN - Part X - ChY - Title.pdf` for a unit from an expanded Part wrapper.
   The index is zero-padded and follows book order; every text piece is
   sanitized (`\xa0` → space, whitespace collapsed, `:` → ` -`, and the
   filesystem-illegal `\/*?"<>|` stripped) so ordering and readability
   survive in any file manager.

## Known limitation: unnumbered chapters under a Part

Part-vs-chapter detection relies on a leading number in the children's
titles. A book that wraps purely *named* sections under a Part (no "1", no
"Chapter 1") is not detected as Part-wrapped and falls back to one file per
Part.

The symptom is a suspiciously coarse split — one huge file covering what
should obviously be several chapters. Confirm with `--inspect`, then widen
`CHAPTER_NUM_RE` in the script rather than reverting to manual page ranges.
