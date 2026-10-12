#!/usr/bin/env python3
"""Merge per-chapter study partials into book-wide Anki files, and validate them.

Used by the `book-to-anki` skill. Two subcommands:

  merge    --partials DIR --book "Title" --out DIR
  validate --book "Title" (--dir DIR | --files F Q QA) [--expect-chapters N]

Partial files are written one set per chapter by the per-chapter subagents,
named after the chapter file they came from, e.g.

  07 - Basic Concepts.flashcards.tsv     Front <TAB> Back
  07 - Basic Concepts.questions.txt      plain quiz, numbered from 1
  07 - Basic Concepts.questions-anki.tsv 11 AllInOne fields, Question..Extra 1

Deck and tag columns are appended here, never by the subagents, so the deck
value is constant by construction and every tag is slugified the same way.
"""

import argparse
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

FLASH_HEADER = ["#separator:tab", "#html:false", "#notetype:Basic",
                "#deck column:3", "#tags column:4"]
QUIZ_HEADER = ["#separator:tab", "#html:false", "#notetype:AllInOne (kprim, mc, sc)",
               "#deck column:12", "#tags column:13"]

STRUCTURE_WORDS = ["capítulo", "capitulo", "seção", "secao", "parte ",
                   "até agora", "ate agora", "mais adiante", "neste livro",
                   "deste livro"]

SLUG_RE = re.compile(r"^[a-z0-9]+(?:[-:][a-z0-9]+)*$")
ANSWERS_RE = re.compile(r"^[01](?: [01]){3}$")

# Filenames mirror the deck names on purpose: "<Book> - Study" holds the
# flashcards, "<Book> - Questions" the quiz, so a file on disk and a deck in
# Anki are never two different names for the same thing.
SUFFIX_FLASH = " - Study.txt"
SUFFIX_QUIZ = " - Questions.txt"
SUFFIX_QUIZ_ANKI = " - Questions-Anki.txt"

TIERS = ("nucleo", "complementar", "periferico")
TIER_BUDGET = {"nucleo": 20, "complementar": 12, "periferico": 6}  # tetos de flashcards
TIERS_FILE = "tiers.tsv"


def check_tags(value):
    """Tag field = space-separated slugs: '<capitulo-slug> <camada>'.

    Anki splits on whitespace, so several tags in one field is intended; each
    of them still has to be a slug, and exactly one has to be a tier.
    """
    tags = value.split(" ")
    if value != " ".join(tags) or not all(SLUG_RE.match(t) for t in tags):
        return f"tag {value!r} não é uma lista de slugs separados por um espaço"
    found = [t for t in tags if t in TIERS]
    if len(found) != 1:
        return (f"tag {value!r} deveria ter exatamente uma camada "
                f"({'/'.join(TIERS)}), tem {len(found)}")
    return None


def chapter_tag_of(value):
    return next((t for t in value.split(" ") if t not in TIERS), value)


def tier_tag_of(value):
    return next((t for t in value.split(" ") if t in TIERS), "sem-camada")


def read_tiers(partials, errors):
    """chapter basename -> tier, from tiers.tsv written by the orchestrator."""
    path = os.path.join(partials, TIERS_FILE)
    if not os.path.exists(path):
        sys.exit(f"ERRO: {path} não existe. O orquestrador (book-to-anki Step 2) "
                 f"deve escrever um {TIERS_FILE} com '<base do capítulo>\\t<camada>' "
                 f"por linha, camada em {'/'.join(TIERS)}.")
    tiers = {}
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.rstrip("\n")
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) != 2 or parts[1].strip() not in TIERS:
                errors.append(f"{TIERS_FILE}:{lineno}: esperado "
                              f"'<capítulo><TAB><{'/'.join(TIERS)}>', veio {line!r}")
                continue
            tiers[parts[0].strip()] = parts[1].strip()
    return tiers


def slugify(text):
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return text


def chapter_sort_key(base):
    m = re.match(r"\s*(\d+)", base)
    return (0, int(m.group(1)), base) if m else (1, 0, base)


def discover(partials):
    """Group partial files by chapter basename."""
    suffixes = {".flashcards.tsv": "flash",
                ".questions.txt": "quiz",
                ".questions-anki.tsv": "quiz_anki"}
    chapters = defaultdict(dict)
    for name in os.listdir(partials):
        for suf, key in suffixes.items():
            if name.endswith(suf):
                chapters[name[: -len(suf)]][key] = os.path.join(partials, name)
                break
    return dict(sorted(chapters.items(), key=lambda kv: chapter_sort_key(kv[0])))


def read_rows(path, expected_fields, errors):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.rstrip("\n").rstrip("\r")
            if not line.strip() or line.startswith("#"):
                continue
            fields = line.split("\t")
            if len(fields) != expected_fields:
                errors.append(f"{os.path.basename(path)}:{lineno}: "
                              f"{len(fields)} campos, esperado {expected_fields}")
                continue
            if any(f.strip() == "" for f in fields[:2]):
                errors.append(f"{os.path.basename(path)}:{lineno}: campo vazio no início da linha")
                continue
            rows.append(fields)
    return rows


def parse_quiz_text(path, errors):
    """Split a plain quiz partial into blocks, one per question."""
    blocks, current = [], []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if re.match(r"^\s*\d+\)\s", line):
                if current:
                    blocks.append(current)
                current = [re.sub(r"^\s*\d+\)\s*", "", line)]
            elif current is not None and current:
                current.append(line)
    if current:
        blocks.append(current)
    for block in blocks:
        text = "\n".join(block)
        for letter in "ABCD":
            if not re.search(rf"^\s*{letter}\)\s", text, re.M):
                errors.append(f"{os.path.basename(path)}: questão sem alternativa {letter}): "
                              f"{block[0][:60]}")
        if not re.search(r"^\s*Resposta:", text, re.M):
            errors.append(f"{os.path.basename(path)}: questão sem linha 'Resposta:': "
                          f"{block[0][:60]}")
    return [[b[0]] + [l for l in b[1:]] for b in blocks]


def cmd_merge(args):
    errors, warnings = [], []
    chapters = discover(args.partials)
    if not chapters:
        sys.exit(f"ERRO: nenhum arquivo parcial encontrado em {args.partials}")
    tiers = read_tiers(args.partials, errors)

    study_deck = f"{args.book} - Study"
    quiz_deck = f"{args.book} - Questions"
    flash_lines, quiz_lines, quiz_anki_lines = [], [], []
    quiz_lines.append(f"Quiz — {args.book}")
    quiz_lines.append("Baseado nos 20% de conceitos com maior valor de aprendizado "
                      "de cada capítulo.")
    qnum = 0
    stats = []

    for base, files in chapters.items():
        chapter_tag = "capitulo-" + slugify(base) \
            if not base.lower().startswith("capitulo") else slugify(base)
        tier = tiers.get(base)
        if tier is None:
            errors.append(f"{base}: sem camada em {TIERS_FILE} — todo capítulo "
                          f"precisa de uma ({'/'.join(TIERS)})")
            continue
        tag = f"{chapter_tag} {tier}"
        missing = [k for k in ("flash", "quiz", "quiz_anki") if k not in files]
        if missing:
            errors.append(f"{base}: parcial faltando ({', '.join(missing)}) — "
                          f"subagente pode ter falhado")
            continue

        flash = read_rows(files["flash"], 2, errors)
        for front, back in flash:
            flash_lines.append("\t".join([front, back, study_deck, tag]))

        anki = read_rows(files["quiz_anki"], 11, errors)
        for fields in anki:
            if fields[2] != "2":
                errors.append(f"{base}: QType={fields[2]!r}, esperado '2' — {fields[0][:50]}")
            if fields[7].strip():
                errors.append(f"{base}: Q_5 deveria ser vazio — {fields[0][:50]}")
            if not ANSWERS_RE.match(fields[8]) or fields[8].split().count("1") != 1:
                errors.append(f"{base}: Answers inválido {fields[8]!r} "
                              f"(4 flags, exatamente um '1') — {fields[0][:50]}")
            quiz_anki_lines.append("\t".join(fields + [quiz_deck, tag]))

        blocks = parse_quiz_text(files["quiz"], errors)
        num = re.match(r"\s*(\d+)", base)
        title = re.sub(r"^\s*\d+\s*[-–.]\s*", "", base)
        heading = f"Capítulo {num.group(1)}: {title}" if num else base
        quiz_lines += ["", f"== {heading} ==", ""]
        for block in blocks:
            qnum += 1
            quiz_lines.append(f"{qnum}) {block[0]}")
            quiz_lines.extend(block[1:])
            quiz_lines.append("")

        if len(blocks) != len(anki):
            warnings.append(f"{base}: {len(blocks)} questões no texto vs "
                            f"{len(anki)} no Anki — devem ser as mesmas")
        ceiling = TIER_BUDGET[tier]
        if len(flash) > ceiling:
            warnings.append(f"{base}: {len(flash)} flashcards para um capítulo "
                            f"{tier} (teto {ceiling}) — o subagente estourou o budget")
        stats.append((base, title, tag, tier, len(flash), len(anki)))

    os.makedirs(args.out, exist_ok=True)
    paths = {
        "flash": os.path.join(args.out, args.book + SUFFIX_FLASH),
        "quiz": os.path.join(args.out, args.book + SUFFIX_QUIZ),
        "quiz_anki": os.path.join(args.out, args.book + SUFFIX_QUIZ_ANKI),
    }
    with open(paths["flash"], "w", encoding="utf-8") as fh:
        fh.write("\n".join(FLASH_HEADER + flash_lines) + "\n")
    collapsed = []
    for line in quiz_lines:
        if not line.strip() and collapsed and not collapsed[-1].strip():
            continue
        collapsed.append(line)
    with open(paths["quiz"], "w", encoding="utf-8") as fh:
        fh.write("\n".join(collapsed).rstrip() + "\n")
    with open(paths["quiz_anki"], "w", encoding="utf-8") as fh:
        fh.write("\n".join(QUIZ_HEADER + quiz_anki_lines) + "\n")

    print(f"Capítulos mesclados: {len(stats)}")
    for base, _title, tag, _tier, nf, nq in stats:
        print(f"  {base}: {nf} flashcards, {nq} questões  [tags: {tag}]")
    print(f"TOTAL: {len(flash_lines)} flashcards, {qnum} questões")
    per_tier = defaultdict(lambda: [0, 0])
    for _base, _title, _tag, tier, nf, _nq in stats:
        per_tier[tier][0] += 1
        per_tier[tier][1] += nf
    total_cards = len(flash_lines) or 1
    for tier in TIERS:
        chaps, cards = per_tier.get(tier, (0, 0))
        print(f"  camada {tier:<13} {chaps:>2} capítulos, {cards:>3} flashcards "
              f"({cards / total_cards:.0%})")
    for p in paths.values():
        print(f"  -> {p}")
    for w in warnings:
        print(f"AVISO: {w}")
    for e in errors:
        print(f"ERRO: {e}")
    return 1 if errors else 0


def check_header(lines, expected, label, errors):
    header = [l for l in lines if l.startswith("#")]
    for directive in expected:
        if directive not in header:
            errors.append(f"{label}: falta a diretiva de cabeçalho '{directive}'")


def scan_structure(text, label, where, warnings):
    low = text.lower()
    for word in STRUCTURE_WORDS:
        if word in low:
            warnings.append(f"{label}: possível pergunta sobre o livro, não sobre o "
                            f"assunto ('{word.strip()}') — {where[:70]}")
            break


def cmd_validate(args):
    errors, warnings = [], []
    study_deck = f"{args.book} - Study"
    quiz_deck = f"{args.book} - Questions"
    if args.files:
        flash_path, quiz_path, anki_path = args.files
    else:
        flash_path = os.path.join(args.dir, args.book + SUFFIX_FLASH)
        quiz_path = os.path.join(args.dir, args.book + SUFFIX_QUIZ)
        anki_path = os.path.join(args.dir, args.book + SUFFIX_QUIZ_ANKI)
    for p in (flash_path, quiz_path, anki_path):
        if not os.path.exists(p):
            sys.exit(f"ERRO: arquivo não encontrado: {p}")

    flash_lines = open(flash_path, encoding="utf-8").read().splitlines()
    check_header(flash_lines, FLASH_HEADER, "Study", errors)
    fronts, flash_tags, flash_tiers = {}, set(), Counter()
    for i, line in enumerate(flash_lines, 1):
        if not line.strip() or line.startswith("#"):
            continue
        f = line.split("\t")
        if len(f) != 4:
            errors.append(f"Study:{i}: {len(f)} colunas, esperado 4")
            continue
        if f[2] != study_deck:
            errors.append(f"Study:{i}: deck {f[2]!r}, esperado {study_deck!r}")
        problem = check_tags(f[3])
        if problem:
            errors.append(f"Study:{i}: {problem}")
        flash_tags.add(chapter_tag_of(f[3]))
        flash_tiers[tier_tag_of(f[3])] += 1
        if f[0] in fronts:
            warnings.append(f"Study:{i}: front duplicado da linha {fronts[f[0]]}: {f[0][:60]}")
        fronts[f[0]] = i
        scan_structure(f[0], "Study", f[0], warnings)

    anki_lines = open(anki_path, encoding="utf-8").read().splitlines()
    check_header(anki_lines, QUIZ_HEADER, "Questions-Anki", errors)
    anki_tags, anki_count = set(), 0
    for i, line in enumerate(anki_lines, 1):
        if not line.strip() or line.startswith("#"):
            continue
        f = line.split("\t")
        if len(f) != 13:
            errors.append(f"Questions-Anki:{i}: {len(f)} colunas, esperado 13")
            continue
        anki_count += 1
        if f[2] != "2":
            errors.append(f"Questions-Anki:{i}: QType {f[2]!r}, esperado '2'")
        if f[7].strip():
            errors.append(f"Questions-Anki:{i}: Q_5 deveria ser vazio")
        if not ANSWERS_RE.match(f[8]) or f[8].split().count("1") != 1:
            errors.append(f"Questions-Anki:{i}: Answers {f[8]!r} inválido "
                          f"(4 flags, exatamente um '1')")
        if f[11] != quiz_deck:
            errors.append(f"Questions-Anki:{i}: deck {f[11]!r}, esperado {quiz_deck!r}")
        problem = check_tags(f[12])
        if problem:
            errors.append(f"Questions-Anki:{i}: {problem}")
        anki_tags.add(chapter_tag_of(f[12]))
        scan_structure(f[0], "Questions-Anki", f[0], warnings)

    quiz_text = open(quiz_path, encoding="utf-8").read()
    numbers = [int(n) for n in re.findall(r"^\s*(\d+)\)\s", quiz_text, re.M)]
    if numbers != list(range(1, len(numbers) + 1)):
        errors.append("Questions: numeração não é contínua/única a partir de 1 "
                      f"(vistos: {numbers[:12]}{'...' if len(numbers) > 12 else ''})")
    if len(numbers) != anki_count:
        errors.append(f"Questions: {len(numbers)} questões no texto vs {anki_count} no Anki")

    if flash_tags != anki_tags:
        only_f = sorted(flash_tags - anki_tags)
        only_a = sorted(anki_tags - flash_tags)
        warnings.append(f"capítulos presentes só nos flashcards: {only_f or '—'}; "
                        f"só no quiz: {only_a or '—'}")
    if args.expect_chapters and len(flash_tags) != args.expect_chapters:
        errors.append(f"{len(flash_tags)} capítulos nos flashcards, "
                      f"esperado {args.expect_chapters} — subagente falhou em silêncio?")

    total = sum(flash_tiers.values()) or 1
    tier_summary = "  ".join(f"{t}={flash_tiers.get(t, 0)} ({flash_tiers.get(t, 0) / total:.0%})"
                             for t in TIERS)
    print(f"Flashcards: {len(fronts)} | Questões: {len(numbers)} | "
          f"Capítulos: {len(flash_tags)}")
    print(f"Camadas: {tier_summary}")
    if flash_tiers.get("nucleo", 0) / total > 0.45:
        warnings.append(f"{flash_tiers['nucleo'] / total:.0%} do deck está marcado como "
                        f"núcleo — se quase tudo é núcleo, a camada não filtra nada")
    for w in warnings:
        print(f"AVISO: {w}")
    for e in errors:
        print(f"ERRO: {e}")
    print("OK — nenhum erro estrutural." if not errors
          else f"{len(errors)} erro(s) estrutural(is): corrija antes de entregar.")
    return 1 if errors else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("merge", help="mescla parciais por capítulo nos 3 arquivos do livro")
    m.add_argument("--partials", required=True)
    m.add_argument("--book", required=True)
    m.add_argument("--out", required=True)
    m.set_defaults(func=cmd_merge)

    v = sub.add_parser("validate", help="valida os 3 arquivos finais")
    src = v.add_mutually_exclusive_group(required=True)
    src.add_argument("--dir", help="pasta com os 3 arquivos nomeados a partir de --book")
    src.add_argument("--files", nargs=3,
                     metavar=("STUDY", "QUESTIONS", "QUESTIONS_ANKI"),
                     help="caminhos explícitos — use no modo standalone de um capítulo só")
    v.add_argument("--book", required=True)
    v.add_argument("--expect-chapters", type=int, default=0)
    v.set_defaults(func=cmd_validate)

    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
