#!/usr/bin/env python3
"""Audit an Anki flashcard deck for the quality problems that make a deck expensive to study.

Used by the `anki-deck-audit` skill, and as the final gate of `book-to-anki`.
Structural validity (columns, headers, deck names) is `anki-kit.py validate`'s
job; this script asks a different question: *is this deck worth the hours it
will cost?*

  deck-audit.py --flashcards "<Book> - Study.txt" [--questions ...] [--json]
  deck-audit.py --dir "<book>/study" --book "<Book Title>"

Works on a merged 4-column file (Front, Back, Deck, Tags) and on a raw
2-column subagent partial (Front, Back) — the column count is detected, and
per-chapter/tier analysis is simply skipped when there are no tags.

Exit code 1 means at least one HARD threshold was breached: the deck should be
regenerated or fixed, not shipped.
"""

import argparse
import json
import math
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

# --- Thresholds -------------------------------------------------------------
# Calibrated against a real failure: a 533-card Kubernetes deck where 43% of
# the answers bundled several facts and every chapter got a near-identical card
# count regardless of how much of it anyone would ever use.

MAX_BACK_CHARS = 200          # hard cap for a single answer
TARGET_AVG_BACK = 150         # average answer length a healthy deck sits under
MAX_COMPOUND_RATE = 0.20      # answers with >=3 sentences or a ';'
MAX_ENUM_RATE = 0.05          # "quais são as três..." fronts
MIN_CHAPTER_CV = 0.30         # below this, per-chapter counts are flat = unprioritized
NEAR_DUP_JACCARD = 0.80
BIG_DECK = 400                # cards above which the time cost needs stating

# Seconds to answer + verify one card: a fixed recall cost plus reading time.
SEC_FIXED = 6.0
CHARS_PER_SEC = 25.0
REPS_TO_MATURE = 9            # typical Anki repetitions before a card is mature

TIER_TAGS = ("nucleo", "complementar", "periferico")

STOPWORDS = set("""
para como qual quais quando onde porque por que sobre entre cada uma uns umas
esse essa este esta isso aquilo seus suas seu sua dos das nos nas pelo pela
mais menos muito pouco todo toda todos todas outro outra outros outras
ser estar tem ter tendo sendo faz fazer feito pode podem posso deve devem
que com sem mais nao não sim ele ela eles elas voce você seja sejam
quando entao então depois antes durante enquanto assim porem porém mas
qualquer algum alguma alguns algumas nenhum nenhuma cada mesmo mesma
usar usa usam usado usada dado dados caso casos vez vezes forma modo
serve servem existe existem chamado chamada chamados chamadas
precisa precisam quer queira valor valores parte partes tipo tipos
""".split())

SENT_END = re.compile(r"[.!?](?=\s|$)")
NUM_WORDS = r"(?:dois|duas|tr[eê]s|quatro|cinco|seis|sete|oito|nove|dez)"
ENUM_START = re.compile(rf"^\s*(quais|quantos|quantas|liste|cite|enumere)\b", re.I)
ENUM_COUNT = re.compile(rf"\b(?:as|os)\s+{NUM_WORDS}\b|\b{NUM_WORDS}\s+\w+", re.I)
DOUBLE_ASK = re.compile(
    r"\se\s+(o\s+que|como|por\s+que|porque|qual|quais|quando|quem|onde|para\s+que)\b",
    re.I)
WORD_RE = re.compile(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9_.-]{2,}")


def strip_accents(text):
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c))


def sentences(text):
    """Rough sentence count that does not trip on 2.1.55 or 'ex.'."""
    protected = re.sub(r"(?<=\d)\.(?=\d)", "\x00", text)
    protected = re.sub(r"\b(ex|etc|vs|p|Sr|Dra?)\.", lambda m: m.group(1) + "\x00",
                       protected)
    return max(1, len(SENT_END.findall(protected)) or 1)


def tokens(text):
    out = set()
    for w in WORD_RE.findall(strip_accents(text).lower()):
        w = w.rstrip("._-")  # keep spec.containers, drop the period ending a sentence
        if w not in STOPWORDS and len(w) > 3:
            out.add(w)
    return out


def load_cards(path):
    """Return (cards, n_cols). A card is a dict with front/back/deck/tags."""
    cards, widths = [], Counter()
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.rstrip("\n").rstrip("\r")
            if not line.strip() or line.startswith("#"):
                continue
            f = line.split("\t")
            widths[len(f)] += 1
            cards.append({
                "line": lineno,
                "front": f[0],
                "back": f[1] if len(f) > 1 else "",
                "deck": f[2] if len(f) > 2 else "",
                "tags": f[3].split() if len(f) > 3 else [],
            })
    return cards, (widths.most_common(1)[0][0] if widths else 0)


def study_seconds(card):
    return SEC_FIXED + (len(card["front"]) + len(card["back"])) / CHARS_PER_SEC


def fmt_hours(seconds):
    h, m = divmod(int(round(seconds / 60)), 60)
    return f"{h}h{m:02d}min" if h else f"{m}min"


def near_duplicates(cards, limit=15):
    """Fronts that ask the same thing in different words."""
    toks = [tokens(c["front"]) for c in cards]
    pairs = []
    for i in range(len(cards)):
        if not toks[i]:
            continue
        for j in range(i + 1, len(cards)):
            if not toks[j]:
                continue
            inter = len(toks[i] & toks[j])
            if not inter:
                continue
            jac = inter / len(toks[i] | toks[j])
            if jac >= NEAR_DUP_JACCARD:
                pairs.append((round(jac, 2), cards[i], cards[j]))
                if len(pairs) >= limit * 4:
                    return sorted(pairs, key=lambda p: -p[0])[:limit]
    return sorted(pairs, key=lambda p: -p[0])[:limit]


def chapter_of(card):
    for t in card["tags"]:
        if t not in TIER_TAGS:
            return t
    return None


def tier_of(card):
    for t in card["tags"]:
        if t in TIER_TAGS:
            return t
    return None


def audit(cards):
    n = len(cards)
    r = {"total": n}
    if not n:
        return r

    backs = [len(c["back"]) for c in cards]
    backs_sorted = sorted(backs)
    r["avg_back"] = sum(backs) / n
    r["median_back"] = backs_sorted[n // 2]
    r["max_back"] = max(backs)
    r["avg_front"] = sum(len(c["front"]) for c in cards) / n

    r["long"] = [c for c in cards if len(c["back"]) > MAX_BACK_CHARS]
    r["compound"] = [c for c in cards
                     if sentences(c["back"]) >= 3 or ";" in c["back"]]
    r["enum"] = [c for c in cards
                 if ENUM_START.match(c["front"]) or ENUM_COUNT.search(c["front"])]
    r["double"] = [c for c in cards
                   if c["front"].count("?") > 1 or DOUBLE_ASK.search(c["front"])]

    seen = {}
    r["dupes"] = []
    for c in cards:
        key = strip_accents(c["front"]).lower().strip()
        if key in seen:
            r["dupes"].append((seen[key], c))
        else:
            seen[key] = c
    r["near_dupes"] = near_duplicates(cards)

    total_sec = sum(study_seconds(c) for c in cards)
    r["pass_sec"] = total_sec
    r["mature_sec"] = total_sec * REPS_TO_MATURE
    r["sec_per_card"] = total_sec / n

    by_ch = Counter(filter(None, (chapter_of(c) for c in cards)))
    r["chapters"] = by_ch
    if len(by_ch) > 1:
        vals = list(by_ch.values())
        mean = sum(vals) / len(vals)
        sd = math.sqrt(sum((v - mean) ** 2 for v in vals) / len(vals))
        r["ch_mean"], r["ch_sd"] = mean, sd
        r["ch_cv"] = sd / mean if mean else 0.0

    r["tagged"] = any(c["tags"] for c in cards)
    r["tiers"] = Counter(filter(None, (tier_of(c) for c in cards)))

    df = Counter()
    for c in cards:
        for t in tokens(c["front"] + " " + c["back"]):
            df[t] += 1
    r["terms"] = df.most_common(20)
    return r


def verdict(r):
    """Return (hard, soft) — hard failures block shipping."""
    hard, soft, n = [], [], r["total"]
    if not n:
        return ["arquivo sem nenhum card"], []

    rate = lambda xs: len(xs) / n

    if rate(r["compound"]) > MAX_COMPOUND_RATE:
        hard.append(
            f"atomicidade: {len(r['compound'])} de {n} cards ({rate(r['compound']):.0%}) "
            f"têm resposta composta (>=3 frases ou ';') — limite {MAX_COMPOUND_RATE:.0%}. "
            f"Cada um desses é vários cards espremidos em um.")
    if rate(r["enum"]) > MAX_ENUM_RATE:
        hard.append(
            f"perguntas enumerativas: {len(r['enum'])} de {n} ({rate(r['enum']):.0%}) "
            f"pedem uma lista ('quais são as três...') — limite {MAX_ENUM_RATE:.0%}. "
            f"Em SRS elas falham repetidamente por um item esquecido.")
    if r["avg_back"] > TARGET_AVG_BACK:
        hard.append(
            f"resposta média de {r['avg_back']:.0f} chars (alvo <= {TARGET_AVG_BACK}) — "
            f"o deck está escrito como resumo, não como cards de recall.")
    if r["double"]:
        hard.append(
            f"{len(r['double'])} card(s) com pergunta dupla (dois '?' ou 'X e como Y') — "
            f"não têm resposta única.")
    if r["dupes"]:
        hard.append(f"{len(r['dupes'])} front(s) duplicado(s) exato(s).")

    if r["long"]:
        soft.append(f"{len(r['long'])} resposta(s) acima de {MAX_BACK_CHARS} chars "
                    f"(máx {r['max_back']}).")
    if r["near_dupes"]:
        soft.append(f"{len(r['near_dupes'])} par(es) de cards quase idênticos "
                    f"(Jaccard >= {NEAR_DUP_JACCARD}).")
    if "ch_cv" in r and r["ch_cv"] < MIN_CHAPTER_CV:
        soft.append(
            f"distribuição plana entre capítulos (CV {r['ch_cv']:.2f} < {MIN_CHAPTER_CV}): "
            f"{r['ch_mean']:.1f} cards por capítulo com desvio de só {r['ch_sd']:.1f}. "
            f"O 80/20 foi aplicado dentro de cada capítulo, nunca entre eles.")
    if r["tagged"] and not r["tiers"]:
        soft.append("nenhum card tem tag de camada (nucleo/complementar/periferico) — "
                    "não dá para estudar só o núcleo com 'tag:nucleo'.")
    elif r["tiers"].get("nucleo", 0) / n > 0.45:
        soft.append(f"{r['tiers']['nucleo'] / n:.0%} do deck está marcado como núcleo — "
                    f"se quase tudo é núcleo, a camada não filtra nada.")
    if r["total"] > BIG_DECK:
        soft.append(f"{r['total']} cards: {fmt_hours(r['pass_sec'])} por passada completa e "
                    f"~{fmt_hours(r['mature_sec'])} até maturar tudo.")
    return hard, soft


def sample(cards, k=5):
    return [f"    L{c['line']}: {c['front'][:88]}" for c in cards[:k]]


def report(r, path, questions_count=None):
    n = r["total"]
    out = [f"AUDITORIA — {os.path.basename(path)}", "=" * 72, "",
           "== INVENTÁRIO =="]
    out.append(f"  cards                {n}")
    if questions_count is not None:
        out.append(f"  questões             {questions_count}")
    if r["chapters"]:
        out.append(f"  capítulos            {len(r['chapters'])}")
    if r["tiers"]:
        tiers = "  ".join(f"{t}={r['tiers'][t]} ({r['tiers'][t] / n:.0%})"
                          for t in TIER_TAGS if r["tiers"].get(t))
        out.append(f"  camadas              {tiers}")
    out += ["", "== ATOMICIDADE =="]
    out.append(f"  pergunta média       {r['avg_front']:.0f} chars")
    out.append(f"  resposta média       {r['avg_back']:.0f} chars "
               f"(mediana {r['median_back']}, máx {r['max_back']}) "
               f"[alvo <= {TARGET_AVG_BACK}]")
    for label, key, limit in (("respostas compostas", "compound", MAX_COMPOUND_RATE),
                              ("perguntas enumerativas", "enum", MAX_ENUM_RATE)):
        xs = r[key]
        out.append(f"  {label:<20} {len(xs)} ({len(xs) / n:.0%}) "
                   f"[limite {limit:.0%}]")
        out += sample(xs, 3)
    out.append(f"  {'respostas > ' + str(MAX_BACK_CHARS) + ' chars':<20} {len(r['long'])}")
    out.append(f"  {'perguntas duplas':<20} {len(r['double'])}")
    out += sample(r["double"], 3)
    out.append(f"  {'duplicatas exatas':<20} {len(r['dupes'])}")
    out.append(f"  {'quase-duplicatas':<20} {len(r['near_dupes'])}")
    for jac, a, b in r["near_dupes"][:3]:
        out.append(f"    {jac} L{a['line']} ~ L{b['line']}: {a['front'][:60]}")

    if r["chapters"]:
        out += ["", "== DISTRIBUIÇÃO POR CAPÍTULO =="]
        if "ch_cv" in r:
            out.append(f"  média {r['ch_mean']:.1f} · desvio {r['ch_sd']:.1f} · "
                       f"CV {r['ch_cv']:.2f} [uniforme se < {MIN_CHAPTER_CV}]")
        width = max(len(c) for c in r["chapters"])
        for ch, cnt in sorted(r["chapters"].items()):
            bar = "#" * min(cnt, 40)
            out.append(f"  {ch:<{width}}  {cnt:>3}  {bar}")

    out += ["", "== CUSTO DE ESTUDO =="]
    out.append(f"  ~{r['sec_per_card']:.0f}s por card")
    out.append(f"  1 passada completa   {fmt_hours(r['pass_sec'])}")
    out.append(f"  até maturar (~{REPS_TO_MATURE}x)  {fmt_hours(r['mature_sec'])}")

    out += ["", "== CONCENTRAÇÃO TEMÁTICA (cards que citam o termo) =="]
    for term, cnt in r["terms"]:
        out.append(f"  {term:<24} {cnt:>4}  ({cnt / n:.0%})")

    hard, soft = verdict(r)
    out += ["", "== VEREDITO =="]
    for h in hard:
        out.append(f"REPROVADO: {h}")
    for s in soft:
        out.append(f"AVISO: {s}")
    if not hard and not soft:
        out.append("OK — nenhum problema de qualidade acima dos limites.")
    elif not hard:
        out.append("APROVADO com avisos — nada acima dos limites duros.")
    return "\n".join(out), hard, soft


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--flashcards", help="caminho do arquivo de flashcards (TSV)")
    src.add_argument("--dir", help="pasta de saída; usa --book para montar os nomes")
    ap.add_argument("--book", help="título do livro (com --dir)")
    ap.add_argument("--questions", help="arquivo de questões em texto (opcional)")
    ap.add_argument("--json", action="store_true", help="também imprime um resumo JSON")
    args = ap.parse_args()

    if args.dir:
        if not args.book:
            sys.exit("ERRO: --dir exige --book")
        flash = os.path.join(args.dir, f"{args.book} - Study.txt")
        quiz = os.path.join(args.dir, f"{args.book} - Questions.txt")
    else:
        flash, quiz = args.flashcards, args.questions
    if not os.path.exists(flash):
        sys.exit(f"ERRO: arquivo não encontrado: {flash}")

    cards, ncols = load_cards(flash)
    if ncols not in (2, 4):
        print(f"AVISO: {ncols} colunas detectadas (esperado 2 ou 4); "
              f"analisando só Front/Back.", file=sys.stderr)

    qcount = None
    if quiz and os.path.exists(quiz):
        qcount = len(re.findall(r"^\s*\d+\)\s", open(quiz, encoding="utf-8").read(), re.M))

    r = audit(cards)
    text, hard, soft = report(r, flash, qcount)
    print(text)

    if args.json:
        print("\n== JSON ==")
        print(json.dumps({
            "total": r["total"],
            "avg_back": round(r["avg_back"], 1),
            "compound_rate": round(len(r["compound"]) / r["total"], 3),
            "enum_rate": round(len(r["enum"]) / r["total"], 3),
            "long": len(r["long"]),
            "double": len(r["double"]),
            "dupes": len(r["dupes"]),
            "near_dupes": len(r["near_dupes"]),
            "chapter_cv": round(r.get("ch_cv", 0), 3),
            "tiers": dict(r["tiers"]),
            "pass_minutes": round(r["pass_sec"] / 60),
            "hard": hard, "soft": soft,
        }, ensure_ascii=False, indent=2))

    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
