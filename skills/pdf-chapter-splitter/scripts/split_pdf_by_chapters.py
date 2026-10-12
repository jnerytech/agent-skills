"""Split a PDF book into one PDF per chapter, using its embedded outline.

  split_pdf_by_chapters.py <book.pdf> [output_dir]   split
  split_pdf_by_chapters.py --inspect <book.pdf>      dry run, writes nothing

`--inspect` prints the nested bookmark tree, the units the splitter would
derive from it, and the page coverage check — run it before splitting a book
you have not split before.
"""

import argparse
import re
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter

CHAPTER_NUM_RE = re.compile(
    r"^(?:chapter|cap[ií]tulo|ch)?\.?\s*(\d+)(?!\.\d)[\s.:)\-]+(.+)$", re.IGNORECASE
)
PART_LABEL_RE = re.compile(r"^(part|parte)\s+\d+", re.IGNORECASE)


def parse_outline_tree(reader, outline):
    """Turn pypdf's flat [item, [children], item, ...] outline into a tree
    of {title, page, children} nodes, one level of nesting at a time."""
    nodes = []
    for entry in outline:
        if isinstance(entry, list):
            if nodes:
                nodes[-1]["children"] = parse_outline_tree(reader, entry)
            continue
        try:
            page = reader.get_destination_page_number(entry)
        except Exception:
            continue
        nodes.append({"title": str(entry.title), "page": page, "children": []})
    return nodes


def looks_like_chapter_start(title):
    return CHAPTER_NUM_RE.match(title.strip()) is not None


def flatten_units(nodes):
    """Decide, per top-level node, whether it's already chapter-sized or
    whether it's a 'Part'-style wrapper whose children are the real
    chapters (detected by most children having numbered titles like
    '1 The basics...' or 'Chapter 1: ...'). Expand only the latter."""
    units = []
    for node in nodes:
        children = node["children"]
        numbered = [c for c in children if looks_like_chapter_start(c["title"])]
        is_part_wrapper = children and len(numbered) >= max(1, len(children) // 2)

        if is_part_wrapper:
            part_label_match = PART_LABEL_RE.match(node["title"].strip())
            part_label = part_label_match.group(0) if part_label_match else node["title"]
            for child in children:
                units.append({"title": child["title"], "page": child["page"],
                              "part_label": part_label})
        else:
            units.append({"title": node["title"], "page": node["page"], "part_label": None})
    return units


def clean_monotonic(units, warnings):
    """Drop bookmarks whose page does not advance.

    Two junk shapes, both fatal to the page ranges if kept:
      - a page that goes *backwards* (stray bookmarks pointing at an embedded
        image, usually appended after the real outline);
      - a page equal to the previous unit's, which yields an end < start range
        and therefore a 0-page PDF that silently swallows a chapter.
    Both are reported rather than dropped in silence — a dropped unit means a
    chapter file that will not exist.
    """
    clean = []
    for u in units:
        if clean and u["page"] <= clean[-1]["page"]:
            relation = "repete" if u["page"] == clean[-1]["page"] else "retrocede para"
            warnings.append(
                f"marcador descartado: {u['title']!r} {relation} a página "
                f"{u['page']} (anterior: {clean[-1]['title']!r} na página "
                f"{clean[-1]['page']})")
            continue
        clean.append(u)
    return clean


def build_ranges(units, n_pages):
    ranges = []
    if units and units[0]["page"] > 0:
        ranges.append(({"title": "Front Matter", "page": 0, "part_label": None},
                       0, units[0]["page"] - 1))
    for i, u in enumerate(units):
        end = units[i + 1]["page"] - 1 if i + 1 < len(units) else n_pages - 1
        ranges.append((u, u["page"], end))
    return ranges


def check_coverage(ranges, n_pages, problems):
    """Every page of the source must land in exactly one output file."""
    expected = 0
    for unit, start, end in ranges:
        if end < start:
            problems.append(f"intervalo vazio em {unit['title']!r} "
                            f"(páginas {start}-{end}) — não seria legível")
        if start != expected:
            problems.append(f"cobertura quebrada antes de {unit['title']!r}: "
                            f"esperava começar na página {expected}, começa em {start}")
        expected = end + 1
    if expected != n_pages:
        problems.append(f"cobertura incompleta: {expected} de {n_pages} páginas "
                        f"cobertas pelos arquivos de saída")
    return sum(end - start + 1 for _u, start, end in ranges)


def sanitize_piece(text):
    t = text.replace("\xa0", " ")
    t = re.sub(r"\s+", " ", t).strip()
    t = t.replace(":", " -")
    t = re.sub(r'[\\/*?"<>|]', "", t)
    return t


def format_filename(unit, index):
    title = unit["title"]
    part_label = unit.get("part_label")
    m = CHAPTER_NUM_RE.match(title.strip())
    if part_label and m:
        chapter_num, rest = m.group(1), m.group(2)
        label = f"{sanitize_piece(part_label)} - Ch{chapter_num} - {sanitize_piece(rest)}"
    else:
        label = sanitize_piece(title)
    return f"{index:02d} - {label}.pdf"


def print_tree(nodes, depth=0):
    for node in nodes:
        print(f"  {'  ' * depth}{node['title']!r} -> página {node['page']}")
        print_tree(node["children"], depth + 1)


def load(src):
    try:
        reader = PdfReader(str(src))
    except Exception as exc:
        sys.exit(f"ERRO: não foi possível abrir {src}: {exc}")
    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception:
            pass
        if reader.is_encrypted:
            sys.exit(f"ERRO: {src} está protegido por senha — remova a proteção antes de dividir.")
    if not reader.outline:
        sys.exit("ERRO: este PDF não tem bookmarks/outline — não dá para detectar capítulos.\n"
                 "Use intervalos de página manuais em vez deste script.")
    return reader


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("output_dir", nargs="?")
    ap.add_argument("--inspect", action="store_true",
                    help="mostra outline, unidades e cobertura sem escrever nada")
    args = ap.parse_args()

    src = Path(args.pdf)
    out_dir = Path(args.output_dir) if args.output_dir else src.with_suffix("")

    reader = load(src)
    n_pages = len(reader.pages)
    notes, problems = [], []

    tree = parse_outline_tree(reader, reader.outline)
    units = clean_monotonic(flatten_units(tree), notes)
    ranges = build_ranges(units, n_pages)
    covered = check_coverage(ranges, n_pages, problems)

    if args.inspect:
        print(f"{src.name}: {n_pages} páginas\n\nOutline aninhado:")
        print_tree(tree)
        print(f"\nUnidades derivadas ({len(ranges)} arquivos seriam escritos):")
        for idx, (unit, start, end) in enumerate(ranges):
            print(f"  {format_filename(unit, idx)}  (páginas {start}-{end}, "
                  f"{end - start + 1} pág.)")
    else:
        out_dir.mkdir(parents=True, exist_ok=True)
        for idx, (unit, start, end) in enumerate(ranges):
            name = format_filename(unit, idx)
            if end < start:
                problems.append(f"{name} não foi escrito (intervalo vazio)")
                continue
            writer = PdfWriter()
            for pg in range(start, end + 1):
                writer.add_page(reader.pages[pg])
            with open(out_dir / name, "wb") as f:
                writer.write(f)
            print(f"{name}  (páginas {start}-{end})")

    print(f"\nCobertura: {covered}/{n_pages} páginas em {len(ranges)} unidades.")
    for n in notes:
        print(f"NOTA: {n}")
    for p in problems:
        print(f"PROBLEMA: {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
