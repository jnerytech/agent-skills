# Batch mode — the contract with an orchestrator

You are in batch mode when the calling prompt says so explicitly (typically
launched by `book-to-anki` as one chapter of a whole-book run). The caller is
a subagent orchestrator, not the end user.

**What does not change:** Steps 1-5 and 5b in full — extract, curate the
vital 20%, size the kit, write the actual cards, the questions, and the
AllInOne rows. Batch mode changes what happens to the *output*, never the
curation rigor. Every rule in SKILL.md still binds: pt-BR with field-native
technical terms, self-containment, "the subject is the material, never the
book", and the hard limits in "One card, one fact".

**What changes:**

- **Step 3's tier is not yours to pick.** The caller states this chapter's
  tier (`núcleo` / `complementar` / `periférico`) and its flashcard budget.
  Honor the budget as a ceiling: land under it when the chapter yielded less,
  never over it because the chapter felt rich. A periférico chapter that
  reads like core material is a triage disagreement — say so in your SUMMARY
  and still respect the budget. The orchestrator can re-run one chapter for
  the price of one subagent; it cannot un-inflate a merged book.
- **Skip Step 6** — no `study/` folder, no book-wide files. The orchestrator
  owns where things land.
- **Keep Step 7's checks**, applied to what you are about to hand back. Run
  the quality script on your own partial before returning — it takes a
  2-column file directly:

  ```
  python3 ${CLAUDE_SKILL_DIR}/../anki-deck-audit/scripts/deck-audit.py \
    --flashcards "<partials dir>/<NN - Chapter Title>.flashcards.tsv"
  ```

  Rewrite anything it marks `REPROVADO` and re-run until it passes; a
  chapter-sized batch is small enough that this is a handful of edits. Then
  confirm by hand what the script does not see: no stray tab or newline
  inside a field, no duplicate cards, no question with two defensible correct
  answers, exactly one `1` in each `Answers` row.
- **Skip Step 8** — do not print a user-facing curation report. Return
  whatever the calling prompt asks for; the orchestrator folds your summary
  into one consolidated report.

## Two output variants — the caller picks one

**Inline** — return the rows in the caller's labeled blocks (typically
FLASHCARDS / QUESTIONS / QUESTIONS_ANKI / SUMMARY). Fine for a handful of
chapters; a whole book's worth of TSV in one context is not.

**Partials on disk** (what `book-to-anki` uses) — write three files into the
partials directory the caller names, called after the chapter exactly as the
caller spells it, and return only a short SUMMARY plus counts:

| File | Fields per line |
| --- | --- |
| `<NN - Chapter Title>.flashcards.tsv` | 2 — Front, Back |
| `<NN - Chapter Title>.questions.txt` | plain quiz, numbered from 1 |
| `<NN - Chapter Title>.questions-anki.tsv` | 11 — Question … Extra 1 |

In this variant, and only this one, **omit the header directives, the Deck
column and the Tags column** — including the tier tag, even though the caller
told you the tier. The orchestrator's merge script appends deck and both tags
itself, from the tier map it wrote, so the deck value is constant by
construction and every tag runs through one slugify function; emitting them
here produces malformed rows with too many columns. The question numbering
restarts at 1 per chapter — the merge script renumbers continuously across
the book.

If the calling prompt does not say which variant it wants, return inline.
