#!/usr/bin/env python3
"""Extrai a carteira de um XLSX de posição da B3 (ou similar) usando apenas a
biblioteca padrão (sem openpyxl). Lê todas as abas, identifica a linha de
cabeçalho e devolve, em JSON, os ativos de cada aba com ticker, quantidade,
preço e valor atual.

Uso:
    python3 extract_carteira.py CAMINHO.xlsx

Saída (stdout): JSON
    {
      "arquivo": "...",
      "abas": [
        {
          "aba": "Acoes",
          "tipo": "acao",            # acao | fii | desconhecido (heurística)
          "ativos": [
            {"ticker": "BBAS3", "produto": "...", "quantidade": 100,
             "preco_fechamento": 27.5, "valor_atualizado": 2750.0}
          ]
        }
      ],
      "total_atualizado": 12345.67
    }
"""
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def col_to_idx(ref):
    """A1 -> 0, B2 -> 1 ..."""
    letters = re.match(r"[A-Z]+", ref).group(0)
    idx = 0
    for ch in letters:
        idx = idx * 26 + (ord(ch) - ord("A") + 1)
    return idx - 1


def load_shared_strings(z):
    try:
        xml = z.read("xl/sharedStrings.xml")
    except KeyError:
        return []
    root = ET.fromstring(xml)
    out = []
    for si in root.findall(f"{NS}si"):
        out.append("".join(t.text or "" for t in si.iter(f"{NS}t")))
    return out


def sheet_files(z):
    """Mapeia nome da aba -> caminho do XML, preservando a ordem do workbook."""
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels_xml = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rns = "{http://schemas.openxmlformats.org/package/2006/relationships}"
    rid_to_target = {
        r.get("Id"): r.get("Target") for r in rels_xml.findall(f"{rns}Relationship")
    }
    rel_attr = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
    out = []
    for s in wb.iter(f"{NS}sheet"):
        rid = s.get(rel_attr)
        target = rid_to_target.get(rid, "")
        if not target.startswith("/"):
            target = "xl/" + target.lstrip("/")
        else:
            target = target.lstrip("/")
        out.append((s.get("name"), target))
    return out


def read_rows(z, path, strings):
    root = ET.fromstring(z.read(path))
    rows = []
    for row in root.iter(f"{NS}row"):
        cells = {}
        maxc = -1
        for c in row.findall(f"{NS}c"):
            ref = c.get("r")
            idx = col_to_idx(ref)
            t = c.get("t")
            v = c.find(f"{NS}v")
            if t == "s":
                val = strings[int(v.text)] if v is not None else ""
            elif t == "inlineStr":
                isn = c.find(f"{NS}is")
                val = "".join(x.text or "" for x in isn.iter(f"{NS}t")) if isn is not None else ""
            elif v is not None:
                val = v.text
            else:
                val = None
            cells[idx] = val
            maxc = max(maxc, idx)
        rows.append([cells.get(i) for i in range(maxc + 1)])
    return rows


def norm(s):
    return (s or "").strip().lower()


def find_header(rows):
    """Acha a linha de cabeçalho procurando 'código de negociação'."""
    for i, row in enumerate(rows):
        joined = norm(" | ".join(str(c) for c in row if c is not None))
        if "código de negociação" in joined or "codigo de negociacao" in joined:
            return i
    return 0


def num(v):
    if v is None:
        return None
    try:
        return float(str(v).replace(".", "").replace(",", ".")) if re.search(r",\d", str(v)) else float(v)
    except ValueError:
        return None


def classify(aba_nome, tickers):
    n = norm(aba_nome)
    if "fundo" in n or "imobili" in n or "fii" in n:
        return "fii"
    if "ação" in n or "acoes" in n or "ações" in n or "acao" in n:
        return "acao"
    return "desconhecido"


def main():
    if len(sys.argv) < 2:
        print("uso: extract_carteira.py CAMINHO.xlsx", file=sys.stderr)
        sys.exit(2)
    path = sys.argv[1]
    z = zipfile.ZipFile(path)
    strings = load_shared_strings(z)
    abas = []
    total = 0.0
    for nome, sheet_path in sheet_files(z):
        rows = read_rows(z, sheet_path, strings)
        if not rows:
            continue
        h = find_header(rows)
        header = [norm(c) for c in rows[h]]

        def col(*names):
            for nm in names:
                for j, hc in enumerate(header):
                    if nm in hc:
                        return j
            return None

        ci_tic = col("código de negociação", "codigo de negociacao")
        ci_prod = col("produto")
        ci_qtd = col("quantidade disponível", "quantidade")
        ci_preco = col("preço de fechamento", "preco de fechamento")
        ci_val = col("valor atualizado", "valor")
        ativos = []
        tickers = []
        for row in rows[h + 1:]:
            if ci_tic is None or ci_tic >= len(row):
                continue
            tic = (row[ci_tic] or "").strip() if row[ci_tic] else ""
            if not tic:
                continue
            valor = num(row[ci_val]) if ci_val is not None and ci_val < len(row) else None
            ativos.append({
                "ticker": tic,
                "produto": (row[ci_prod] or "").strip() if ci_prod is not None and ci_prod < len(row) and row[ci_prod] else "",
                "quantidade": num(row[ci_qtd]) if ci_qtd is not None and ci_qtd < len(row) else None,
                "preco_fechamento": num(row[ci_preco]) if ci_preco is not None and ci_preco < len(row) else None,
                "valor_atualizado": valor,
            })
            tickers.append(tic)
            if valor:
                total += valor
        if ativos:
            abas.append({"aba": nome, "tipo": classify(nome, tickers), "ativos": ativos})
    print(json.dumps({"arquivo": path, "abas": abas, "total_atualizado": round(total, 2)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
