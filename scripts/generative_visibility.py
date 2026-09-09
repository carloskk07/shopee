#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import unicodedata
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

ALIASES = {
    "page": {"page", "pages", "pagina", "paginas", "página", "páginas"},
    "impressions": {"impressions", "impressoes", "impressões"},
}


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    return "".join(ch for ch in value if not unicodedata.combining(ch)).lower().strip()


def number(value: str) -> float:
    raw = (value or "0").strip().replace("\u00a0", " ").replace(" ", "")
    if raw in {"", "-", "~"}:
        return 0.0
    if "," in raw and "." in raw:
        if raw.rfind(",") > raw.rfind("."):
            raw = raw.replace(".", "").replace(",", ".")
        else:
            raw = raw.replace(",", "")
    elif "," in raw:
        raw = raw.replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return 0.0


def canonical_page(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    if value.startswith("http://") or value.startswith("https://"):
        value = urlparse(value).path
    value = value.split("?", 1)[0].split("#", 1)[0]
    if value.endswith(".html"):
        value = value[:-5]
    if not value.startswith("/"):
        value = "/" + value
    return value.rstrip("/") or "/"


def resolve(fieldnames: list[str]) -> dict[str, str]:
    lookup = {norm(x): x for x in fieldnames}
    out = {}
    for key, aliases in ALIASES.items():
        for alias in aliases:
            if norm(alias) in lookup:
                out[key] = lookup[norm(alias)]
                break
    missing = {"page", "impressions"} - out.keys()
    if missing:
        raise SystemExit(f"CSV missing required page/impressions columns: {sorted(missing)}; got {fieldnames}")
    return out


def load_page_impressions(path: Path) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames:
            raise SystemExit(f"CSV has no header: {path}")
        cols = resolve(reader.fieldnames)
        for row in reader:
            page = canonical_page(row.get(cols["page"], ""))
            if page:
                totals[page] += number(row.get(cols["impressions"], ""))
    return dict(totals)


def analyze(ai_csv: Path, web_csv: Path | None = None) -> dict:
    ai = load_page_impressions(ai_csv)
    web = load_page_impressions(web_csv) if web_csv else {}
    pages = sorted(set(ai) | set(web))
    rows = []

    for page in pages:
        ai_imp = ai.get(page)
        web_imp = web.get(page)
        if ai_imp is None:
            state = "NOT_IN_AI_EXPORT"
            confidence = "UNRESOLVED"
            reason = "The page is absent from the AI export; export row limits mean absence cannot prove zero generative visibility."
        elif ai_imp <= 0:
            state = "AI_ZERO_OR_UNAVAILABLE"
            confidence = "UNRESOLVED"
            reason = "Search Console exports ~ or unavailable values as zero, so zero is not treated as proof of no generative visibility."
        elif ai_imp >= 50:
            state = "STRONG_AI_VISIBILITY"
            confidence = "STRONG"
            reason = "Material positive generative-AI impressions are directly observed in Search Console."
        elif ai_imp >= 10:
            state = "AI_VISIBLE"
            confidence = "MODERATE"
            reason = "Positive generative-AI impressions are directly observed in Search Console."
        else:
            state = "EARLY_AI_SIGNAL"
            confidence = "WEAK"
            reason = "Positive generative-AI impressions exist but the sample is still small."

        ratio = None
        if ai_imp is not None and ai_imp > 0 and web_imp is not None and web_imp > 0:
            ratio = round(ai_imp / web_imp, 4)
        rows.append({
            "page": page,
            "ai_impressions": ai_imp,
            "web_impressions": web_imp,
            "ai_to_web_ratio": ratio,
            "state": state,
            "confidence": confidence,
            "reason": reason,
        })

    priority = {"STRONG_AI_VISIBILITY": 0, "AI_VISIBLE": 1, "EARLY_AI_SIGNAL": 2, "AI_ZERO_OR_UNAVAILABLE": 3, "NOT_IN_AI_EXPORT": 4}
    rows.sort(key=lambda x: (priority.get(x["state"], 99), -(x.get("ai_impressions") or 0), -(x.get("web_impressions") or 0)))
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["state"]] = counts.get(row["state"], 0) + 1

    return {
        "schema": "freedom-generative-visibility-v1",
        "source": str(ai_csv),
        "web_comparison_source": str(web_csv) if web_csv else None,
        "guardrails": [
            "positive_impressions_are_evidence",
            "zero_export_value_is_ambiguous",
            "missing_export_row_is_not_zero",
            "no_third_party_internal_google_metrics_claims",
            "recommend_only_no_auto_publish",
        ],
        "summary": {"pages": len(rows), "states": counts},
        "pages": rows,
    }


def markdown(report: dict) -> str:
    lines = [
        "# Freedom Generative Visibility",
        "",
        "> Leitura de Search Console para AI Overviews / AI Mode. Zero e linha ausente nunca são tratados como prova de ausência de visibilidade.",
        "",
        "| Estado | Página | Impressões IA | Impressões Web | Razão IA/Web | Confiança |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in report["pages"]:
        ai = "-" if row["ai_impressions"] is None else f"{row['ai_impressions']:.0f}"
        web = "-" if row["web_impressions"] is None else f"{row['web_impressions']:.0f}"
        ratio = "-" if row["ai_to_web_ratio"] is None else f"{row['ai_to_web_ratio']:.2%}"
        lines.append(f"| {row['state']} | {row['page']} | {ai} | {web} | {ratio} | {row['confidence']} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze official Search Console generative-AI page impressions without over-interpreting zeros or missing rows.")
    parser.add_argument("ai_csv", type=Path)
    parser.add_argument("--web-csv", type=Path)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()
    report = analyze(args.ai_csv, args.web_csv)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(text + "\n", encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown(report), encoding="utf-8")
    if not args.json_output and not args.markdown_output:
        print(text)


if __name__ == "__main__":
    main()
