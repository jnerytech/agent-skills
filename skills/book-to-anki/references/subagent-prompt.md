# Per-chapter subagent prompt (Step 3)

Copy this template verbatim, substituting the `<...>` placeholders. The
subagent starts with **zero context** — every fact it needs must be in the
prompt. Do not summarize or paraphrase this template into something shorter:
the batch-mode override, the budget, and the curation rules below are exactly
the parts that fail silently when dropped. Two of them are load-bearing and
were added after a real run shipped 533 unusable cards — the **camada/budget**
from Step 2b, and the **atomicity limits**. A subagent that doesn't see them
writes ~20 sprawling cards for every chapter, appendix and epilogue alike.

```
Curate a Pareto (80/20) study kit for one chapter of a book.

Book: "<Book Title>"
Chapter: "<NN - Chapter Title>"
Chapter file: <absolute path to the chapter .pdf or .md>
Partials directory: <absolute path to the partials dir>
Camada deste capítulo: <nucleo | complementar | periferico>
Budget de flashcards: <14-20 | 8-12 | 4-6> — este é um TETO, não uma meta.
Questões do quiz: cerca de metade dos flashcards.

The camada was decided by the orchestrator from this chapter's role in the
book, not from its length. Respect the budget: land under it when the chapter
yielded less, never over it because the chapter felt rich. If you believe the
camada is wrong, say so in your SUMMARY and still respect the budget — the
orchestrator can re-run one chapter, but cannot un-inflate a merged book.

Load the `pareto-study-kit` skill and follow its rubric to identify the vital
20% (its Step 2), size the kit within the budget above (Step 3), and write
the flashcards (Step 4), the multiple-choice questions (Step 5), and the
Anki-importable version of the quiz (Step 5b) — including:
  - its pt-BR language rule (technical terms stay in whatever language
    practitioners in this field actually use them in);
  - its self-containment rule (every card/question must name its real
    subject, never rely on "o capítulo" alone);
  - its "The subject is the material, never the book" rule (never test
    chapter numbers, reading order, what a chapter covers, or the book's
    structure — if the book vanished, the answer must still be true and
    usable);
  - its "One card, one fact" hard limits: resposta <= 200 chars e no máximo
    2 frases, média do lote <= 150 chars, nada de ';' juntando fatos
    independentes, nenhuma pergunta enumerativa ("quais são as três...") e
    nenhuma pergunta dupla ("o que é X e como se usa Y?"). Conteúdo que só
    funciona como lista vira questão de múltipla escolha, nunca flashcard.

You are running in BATCH MODE — read that skill's `references/batch-mode.md`
and use its **partials on disk** variant: write three partial files into the
partials directory above, named after this chapter exactly as given, and
return only a short summary. Skip its Step 6 and Step 8 as that file says;
the orchestrator writes the final files and reports.

Write exactly these three files, with NO header lines, NO deck column and NO
tags column — the orchestrator's merge script appends deck and tags itself,
so adding them here produces malformed 6-column rows:

1. `<NN - Chapter Title>.flashcards.tsv`
   One card per line, exactly 2 tab-separated fields: Front<TAB>Back.

2. `<NN - Chapter Title>.questions.txt`
   The plain-text quiz for this chapter only, numbered from 1 (the merge
   script renumbers continuously across the book). Each question: the
   `N) pergunta` line, then `A)` `B)` `C)` `D)` lines, then a
   `Resposta: <letra> — <justificativa de uma linha>` line.

3. `<NN - Chapter Title>.questions-anki.tsv`
   One question per line, exactly 11 tab-separated fields in this order:
   Question, Title, QType, Q_1, Q_2, Q_3, Q_4, Q_5, Answers, Sources,
   Extra 1. QType is always `2`. Q_5 is always empty (its tab still has to
   be there). Answers is four space-separated 0/1 flags with exactly one
   `1`. Sources is `<Book Title> — <Chapter Title>`. Extra 1 is the same
   one-line justification used after "Resposta:".

No field may contain a literal tab or newline. The same questions must
appear in files 2 and 3, in the same order and same count.

Before returning, run the quality gate on your own flashcards partial and
rewrite anything it marks REPROVADO, until it passes:

  python3 <caminho das skills>/anki-deck-audit/scripts/deck-audit.py \
    --flashcards "<partials dir>/<NN - Chapter Title>.flashcards.tsv"

Then return ONLY this, as your final message:

SUMMARY:
<2-4 sentences in pt-BR: what was cut and what was kept for THIS chapter
specifically, naming real concepts from it — not generic labels. If you
disagree with the camada assigned above, say why in one sentence.>
COUNTS: <N> flashcards (budget <teto>), <M> questões
AUDIT: <a linha de veredito final do deck-audit.py>
```
