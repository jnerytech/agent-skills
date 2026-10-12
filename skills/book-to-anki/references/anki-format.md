# Output file formats and the Anki import mechanics behind them

`scripts/anki-kit.py merge` produces all three files, so in a normal run you
never type these bytes by hand. Read this when a validation error needs
interpreting, when patching a file manually, or when changing the script.

## Why deck/tags are appended by the script, not by the subagents

Two rules, both learned from real failed imports:

1. **Deck and tags are set by numbered header directives, never by naming a
   column "Deck"/"Tags" inside `#columns:`.** `#columns:` is cosmetic — it
   only labels columns in the import preview dialog and changes nothing
   about import behavior. Only `#deck column:N` and `#tags column:N`
   (`N` = 1-indexed position, counting every column) actually bind. Prefer
   `deck column` over a bare `#deck:<name>` header even when every row
   shares one deck: `deck column` is documented to create the deck if it is
   missing, while the bare header only "presets the deck, if it exists".
2. **A tag value must never contain a literal space.** Anki splits tags on
   whitespace, so `Enterprise Integration Patterns` in a tags column becomes
   three garbage one-word tags. Slugify: lowercase, accents stripped, every
   run of non-alphanumerics collapsed to a single `-`. `::` is allowed on
   purpose (hierarchical tags). The script derives the tag from the chapter
   filename — `07 - Análise de FIIs` → `capitulo-07-analise-de-fiis`.

Both are structural, mechanical, and easy to get subtly wrong when 15
subagents each emit their own deck column — hence the script owns them.

## Decks: exactly two per book

- Flashcards → `<Book Title> - Study`
- Quiz → `<Book Title> - Questions`

Never the bare book title (recall cards and quiz questions would share one
review queue) and never `Book::Chapter` subdecks. Chapter identity lives in
the **tag**, not the deck, however many chapters the book has. `Sources`
inside a quiz row keeps the bare `<Book Title> — <Chapter Title>` — it is a
citation, not a deck name.

## `<Book Title> - Study.txt`

```
#separator:tab
#html:false
#notetype:Basic
#deck column:3
#tags column:4
<Front>	<Back>	<Book Title> - Study	<capitulo-nn-slug>
```

4 columns / 3 tabs per row. With `#html:false`, every field is a single
plain line — no literal newline or tab anywhere in a field.

## `<Book Title> - Questions.txt`

Plain text, no Anki dependency, readable in any editor. Book header, then
one `== Capítulo NN: Título ==` section per chapter, questions renumbered
continuously across the whole book (not reset per chapter), answer key
inline right after each question:

```
Quiz — <Book Title>
Baseado nos 20% de conceitos com maior valor de aprendizado de cada capítulo.

== Capítulo 07: Análise de FIIs ==

1) <pergunta>
A) ... B) ... C) ... D) ...
Resposta: B — <justificativa de uma linha>
```

## `<Book Title> - Questions-Anki.txt`

Note type `AllInOne (kprim, mc, sc)`, from the community add-on **Multiple
Choice** (zjosua, AnkiWeb code
[1566095810](https://ankiweb.net/shared/info/1566095810)) — required in the
user's Anki *before* import, and required for Anki 2.1.55+. A missing note
type fails the whole import rather than degrading. Say so in the report.

Field order (the parenthetical in the QType field name is literal):

```
Question | Title | QType (0=kprim,1=mc,2=sc) | Q_1 | Q_2 | Q_3 | Q_4 | Q_5 | Answers | Sources | Extra 1
```

```
#separator:tab
#html:false
#notetype:AllInOne (kprim, mc, sc)
#deck column:12
#tags column:13
<question>	<chapter title>	2	<A>	<B>	<C>	<D>		<0 1 0 0>	<Book — Chapter>	<justificativa>	<Book Title> - Questions	<capitulo-nn-slug>
```

13 columns / 12 tabs per row. `QType` is always `2` (single choice) —
this pipeline only writes exactly-one-correct-answer questions. `Q_5` is
always empty but its tab must still be present. `Answers` is four
space-separated `0`/`1` flags with exactly one `1`, no fifth value for the
unused `Q_5`. `Title` gets the chapter title (the add-on renders it as a
heading — orientation, not a hint). `Extra 1` gets the same one-line
justification the plain quiz puts after "Resposta: X —".
