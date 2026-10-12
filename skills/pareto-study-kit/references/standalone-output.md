# Standalone output — where files go and what to report

Applies to Step 6 and Step 8 in standalone mode only. In batch mode both
steps are skipped — see [batch-mode.md](batch-mode.md).

## Step 6 — Where to save

- Default output directory: a `study/` subfolder next to the source file
  (create it if missing).
- Filenames reuse the chapter's own basename so they stay traceable to the
  source (keep a `NN - Chapter Title` prefix if `pdf-chapter-splitter`
  produced it):
  `<basename> - Study.txt`, `<basename> - Questions.txt`,
  `<basename> - Questions-Anki.txt` — the same three suffixes the deck names
  use.
- An explicit output path from the user overrides this.

Note the asymmetry, and don't "fix" it: the **filenames** are named after the
chapter, the **decks** after the book. That is what keeps every chapter of a
book landing in the same two decks while the files stay individually
identifiable on disk.

## Step 8 — Report the curation, not just the file paths

The deliverable of this skill is the *judgment call*, not the export. A user
cannot audit "12 flashcards" on their own, but they can audit *what got cut
and why*. Never end the turn with file paths and an item count. Report, in
pt-BR:

1. **"De onde veio o 20%"** — one line naming the chapter's raw size/scope
   (pages, how many tools/topics/sections it covered) and what was discarded
   as low-retention, naming the categories cut (e.g. "listas exaustivas de
   vendors", "GUIDs e números de versão", "digressões históricas") — not
   just "filtrei algumas coisas".
2. **What was kept, bucketed** — group the kept items back into the Step 2
   buckets that produced them (regras explícitas do autor, modelos mentais
   reaproveitados adiante, trade-offs acionáveis com fórmula ou limiar,
   heurísticas de escolha de ferramenta), with a short real example from
   each bucket, not a raw count.
3. **The add-on requirement** — `Questions-Anki.txt` needs the "Multiple
   Choice" add-on (zjosua, AnkiWeb code
   [1566095810](https://ankiweb.net/shared/info/1566095810)) installed in
   Anki 2.1.55+ *before* import; a missing note type fails the whole import
   rather than degrading.

No closing question, no "quer que eu faça os outros capítulos?" line — if
the user wants that, they will ask.

The report is content-driven, not a template to fill in. What matters is
that it lets the user audit the call without reading every card: it names
real concepts from *this* chapter (never generic labels like "conceitos
importantes"), it is honest about volume ("mantive 12 do que daria uns 40
flashcards"), and it names what was cut with actual examples. A report that
could be pasted unchanged onto a different chapter has failed at the one job
this step exists for.
