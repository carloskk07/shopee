#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CANON = "https://achadostube.com.br"

STOPWORDS = {
    "a","ao","aos","as","o","os","um","uma","uns","umas","de","da","das","do","dos","e","em","no","nos","na","nas",
    "para","por","com","sem","que","como","qual","quais","porque","porquê","pra","mais","menos","muito","muita","muitos","muitas",
    "meu","minha","meus","minhas","seu","sua","seus","suas","eu","voce","voces","ser","ter","ficar","quando","onde","hoje"
}

ALIASES = {
    "query": {"query","consulta","consultas","principais consultas","top queries"},
    "page": {"page","pagina","paginas","página","páginas","pages"},
    "clicks": {"clicks","cliques"},
    "impressions": {"impressions","impressoes","impressões"},
    "ctr": {"ctr"},
    "position": {"position","posicao","posição"},
}

INTENT_CANON = {
    "concentracao":"foco", "concentrar":"foco", "concentrado":"foco", "concentrada":"foco", "distraido":"foco", "distraida":"foco",
    "distracao":"foco", "distracoes":"foco", "atencao":"foco",
    "constancia":"disciplina", "habito":"disciplina", "habitos":"disciplina", "motivacao":"disciplina",
    "sentido":"proposito", "direcao":"proposito", "valores":"proposito",
    "recomecar":"recomeco", "recomecando":"recomeco", "retomar":"recomeco", "retomada":"recomeco",
    "sobrecarregado":"rotina", "sobrecarregada":"rotina", "pesada":"rotina", "cansaco":"rotina",
    "estimulo":"mente", "estimulos":"mente", "pendencia":"mente", "pendencias":"mente", "mental":"mente",
}


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch)).lower().strip()
    value = re.sub(r"\s+", " ", value)
    return value


def tokens(value: str) -> set[str]:
    out = set()
    for token in re.findall(r"[a-z0-9]+", norm(value)):
        if len(token) < 3 or token in STOPWORDS:
            continue
        out.add(INTENT_CANON.get(token, token))
    return out


def number(value: str, percent: bool = False) -> float:
    raw = (value or "0").strip().replace("\u00a0", " ").replace(" ", "")
    is_pct = raw.endswith("%") or percent
    raw = raw.rstrip("%")
    if "," in raw and "." in raw:
        if raw.rfind(",") > raw.rfind("."):
            raw = raw.replace(".", "").replace(",", ".")
        else:
            raw = raw.replace(",", "")
    elif "," in raw:
        raw = raw.replace(",", ".")
    try:
        value_num = float(raw)
    except ValueError:
        return 0.0
    if is_pct and value_num > 1:
        value_num /= 100.0
    return value_num


def resolve_columns(fieldnames: list[str]) -> dict[str, str]:
    lookup = {norm(name): name for name in fieldnames}
    result = {}
    for canonical, aliases in ALIASES.items():
        for alias in aliases:
            if norm(alias) in lookup:
                result[canonical] = lookup[norm(alias)]
                break
    required = {"query", "clicks", "impressions", "ctr", "position"}
    missing = required - result.keys()
    if missing:
        raise SystemExit(f"CSV missing required Search Console columns: {', '.join(sorted(missing))}; got {fieldnames}")
    return result


def canonical_page(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    if value.startswith("http://") or value.startswith("https://"):
        parsed = urlparse(value)
        return parsed.path.rstrip("/") or "/"
    return "/" + value.strip("/")


def extract_guide_profiles() -> list[dict]:
    profiles = []
    for path in sorted((ROOT / "guias").glob("*.html")):
        text = path.read_text(encoding="utf-8")
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', text)
        h1 = re.search(r"<h1>(.*?)</h1>", text, re.S | re.I)
        desc = re.search(r'<meta name="description" content="([^"]+)"', text, re.I)
        keyword_values = []
        for script in re.findall(r'<script\s+type="application/ld\+json">(.*?)</script>', text, re.S | re.I):
            try:
                data = json.loads(script)
            except Exception:
                continue
            nodes = data.get("@graph", []) if isinstance(data, dict) else []
            for node in nodes:
                if isinstance(node, dict) and node.get("@type") == "Article" and node.get("keywords"):
                    keyword_values.append(str(node["keywords"]))
        page = canonical_page(canonical.group(1)) if canonical else f"/guias/{path.stem}"
        corpus = " ".join([h1.group(1) if h1 else "", desc.group(1) if desc else "", *keyword_values, path.stem.replace("-", " ")])
        profiles.append({"page": page, "title": re.sub(r"<[^>]+>", "", h1.group(1)).strip() if h1 else path.stem, "tokens": tokens(corpus)})
    if not profiles:
        raise SystemExit("No guide profiles found under guias/*.html")
    return profiles


def similarity(query_tokens: set[str], profile_tokens: set[str]) -> float:
    if not query_tokens or not profile_tokens:
        return 0.0
    overlap = query_tokens & profile_tokens
    return len(overlap) / max(1, min(len(query_tokens), 4))


def intent_key(query: str) -> str:
    ts = sorted(tokens(query))
    return "|".join(ts[:4]) if ts else norm(query)


@dataclass
class Row:
    query: str
    page: str
    clicks: float
    impressions: float
    ctr: float
    position: float
    best_guide: str
    best_similarity: float
    action: str
    priority: float


def choose_action(impressions: float, ctr: float, position: float, similarity_score: float, page: str) -> str:
    is_guide = page.startswith("/guias/")
    if impressions >= 30 and position <= 10 and ctr < 0.02:
        return "CTR_OPPORTUNITY"
    if impressions >= 20 and 8 <= position <= 20:
        return "STRIKING_DISTANCE"
    if similarity_score >= 0.34 and (is_guide or position <= 30):
        return "EXPAND_EXISTING_PAGE"
    if impressions >= 50 and similarity_score < 0.25:
        return "NEW_INTENT_REVIEW"
    return "OBSERVE"


def priority_score(impressions: float, ctr: float, position: float, action: str) -> float:
    position_factor = 1.0
    if 4 <= position <= 20:
        position_factor = 2.2
    elif position <= 40:
        position_factor = 1.4
    ctr_factor = 1.5 if ctr < 0.02 and position <= 10 else 1.0
    action_factor = {"STRIKING_DISTANCE": 1.5, "CTR_OPPORTUNITY": 1.5, "EXPAND_EXISTING_PAGE": 1.25, "NEW_INTENT_REVIEW": 1.2}.get(action, 0.7)
    return round(math.log1p(max(0.0, impressions)) * position_factor * ctr_factor * action_factor, 4)


def analyze(csv_path: Path) -> dict:
    profiles = extract_guide_profiles()
    rows: list[Row] = []
    by_query_pages: dict[str, list[Row]] = defaultdict(list)
    by_intent: dict[str, list[Row]] = defaultdict(list)

    with csv_path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames:
            raise SystemExit("CSV has no header")
        cols = resolve_columns(reader.fieldnames)
        for raw in reader:
            query = (raw.get(cols["query"]) or "").strip()
            if not query:
                continue
            page = canonical_page(raw.get(cols.get("page", ""), "")) if cols.get("page") else ""
            clicks = number(raw.get(cols["clicks"], ""))
            impressions = number(raw.get(cols["impressions"], ""))
            ctr = number(raw.get(cols["ctr"], ""), percent=True)
            position = number(raw.get(cols["position"], ""))
            qtokens = tokens(query)
            best = max(profiles, key=lambda p: similarity(qtokens, p["tokens"]))
            sim = similarity(qtokens, best["tokens"])
            action = choose_action(impressions, ctr, position, sim, page)
            row = Row(query, page, clicks, impressions, ctr, position, best["page"], round(sim, 4), action, priority_score(impressions, ctr, position, action))
            rows.append(row)
            by_query_pages[norm(query)].append(row)
            by_intent[intent_key(query)].append(row)

    cannibalization = []
    for query, group in by_query_pages.items():
        pages = defaultdict(float)
        total = sum(r.impressions for r in group)
        for r in group:
            if r.page:
                pages[r.page] += r.impressions
        ranked = sorted(pages.items(), key=lambda x: x[1], reverse=True)
        if total >= 20 and len(ranked) >= 2 and ranked[1][1] / max(total, 1) >= 0.20:
            cannibalization.append({"query": query, "total_impressions": total, "pages": ranked})

    new_intent_candidates = []
    for key, group in by_intent.items():
        total_imp = sum(r.impressions for r in group)
        distinct_queries = len({norm(r.query) for r in group})
        avg_similarity = sum(r.best_similarity * r.impressions for r in group) / max(total_imp, 1)
        page_impressions = defaultdict(float)
        for r in group:
            if r.page:
                page_impressions[r.page] += r.impressions
        dominant_share = max(page_impressions.values(), default=0) / max(total_imp, 1)
        if total_imp >= 100 and distinct_queries >= 3 and avg_similarity < 0.25 and dominant_share < 0.55:
            new_intent_candidates.append({
                "intent": key,
                "queries": sorted({r.query for r in group}),
                "impressions": round(total_imp, 2),
                "avg_existing_similarity": round(avg_similarity, 4),
                "dominant_page_share": round(dominant_share, 4),
                "decision": "REVIEW_FOR_NEW_URL",
            })

    rows_sorted = sorted(rows, key=lambda r: (-r.priority, -r.impressions, r.position))
    return {
        "schema": "freedom-search-intelligence-v1",
        "source": str(csv_path),
        "guardrail": "recommend_only_no_auto_publish",
        "summary": {
            "rows": len(rows),
            "queries": len(by_query_pages),
            "striking_distance": sum(r.action == "STRIKING_DISTANCE" for r in rows),
            "ctr_opportunities": sum(r.action == "CTR_OPPORTUNITY" for r in rows),
            "expand_existing": sum(r.action == "EXPAND_EXISTING_PAGE" for r in rows),
            "new_intent_reviews": sum(r.action == "NEW_INTENT_REVIEW" for r in rows),
            "cannibalization_queries": len(cannibalization),
            "new_url_candidates": len(new_intent_candidates),
        },
        "opportunities": [asdict(r) for r in rows_sorted],
        "cannibalization": cannibalization,
        "new_intent_candidates": sorted(new_intent_candidates, key=lambda x: -x["impressions"]),
    }


def markdown(report: dict) -> str:
    s = report["summary"]
    lines = [
        "# Freedom Search Intelligence",
        "",
        "> Recomendações baseadas em dados exportados do Google Search Console. Nenhuma URL é publicada automaticamente.",
        "",
        "## Resumo",
        "",
        f"- Consultas analisadas: **{s['queries']}**",
        f"- Oportunidades em distância de ataque: **{s['striking_distance']}**",
        f"- Oportunidades de CTR: **{s['ctr_opportunities']}**",
        f"- Expansões de páginas existentes: **{s['expand_existing']}**",
        f"- Alertas de canibalização: **{s['cannibalization_queries']}**",
        f"- Candidatas a nova URL após gates: **{s['new_url_candidates']}**",
        "",
        "## Prioridades",
        "",
        "| Ação | Consulta | Página observada | Melhor guia | Impressões | CTR | Posição | Score |",
        "|---|---|---|---|---:|---:|---:|---:|",
    ]
    for row in report["opportunities"][:30]:
        q = row["query"].replace("|", "\\|")
        lines.append(f"| {row['action']} | {q} | {row['page'] or '-'} | {row['best_guide']} | {row['impressions']:.0f} | {row['ctr']:.2%} | {row['position']:.1f} | {row['priority']:.2f} |")
    if report["new_intent_candidates"]:
        lines += ["", "## Novas intenções que passaram os gates mínimos", ""]
        for item in report["new_intent_candidates"]:
            lines.append(f"- `{item['intent']}` — {item['impressions']:.0f} impressões; {len(item['queries'])} consultas distintas; similaridade existente {item['avg_existing_similarity']:.2f}.")
    if report["cannibalization"]:
        lines += ["", "## Canibalização potencial", ""]
        for item in report["cannibalization"][:20]:
            lines.append(f"- **{item['query']}** → " + ", ".join(f"{p} ({imp:.0f})" for p, imp in item["pages"]))
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Freedom Book Search Console opportunity analyzer (stdlib only).")
    parser.add_argument("input", type=Path, help="CSV exported from Google Search Console Performance report.")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    report = analyze(args.input)
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
