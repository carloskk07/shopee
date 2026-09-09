#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import seo_intelligence


def pct_change(current: float, previous: float) -> float | None:
    if previous <= 0:
        return None
    return (current - previous) / previous


def evidence_level(current_imp: float, previous_imp: float) -> str:
    total = current_imp + previous_imp
    if total >= 200:
        return "STRONG"
    if total >= 80:
        return "MODERATE"
    return "WEAK"


def classify_pair(cur: dict, prev: dict) -> tuple[str, str]:
    ci = float(cur["impressions"])
    pi = float(prev["impressions"])
    cp = float(cur["position"])
    pp = float(prev["position"])
    growth = pct_change(ci, pi)
    position_gain = pp - cp  # positive = improvement

    if pi >= 50 and ci >= 30 and cp <= 10 and position_gain <= -2:
        return "DEFEND_RANKING", "Review intent alignment, freshness and internal authority before the loss compounds."
    if pi >= 50 and growth is not None and growth <= -0.40 and position_gain <= -1:
        return "DECAYING", "Diagnose query/page fit, SERP change and internal authority before editing or splitting content."
    if ci >= 30 and growth is not None and growth >= 0.40 and position_gain >= 2:
        return "BREAKOUT", "Reinforce the winning page and adjacent internal links; do not fragment the intent."
    if ci >= 20 and 8 <= cp <= 20 and position_gain >= 1:
        return "ACCELERATING_STRIKING_DISTANCE", "Expand the existing answer and route more relevant internal authority to it."
    if ci >= 30 and growth is not None and growth >= 0.50:
        return "EMERGING", "Observe one more comparable window while strengthening the existing topical path."
    return "STABLE", "Keep observing; no material temporal intervention is justified yet."


def keyed(report: dict) -> dict[tuple[str, str], dict]:
    return {(seo_intelligence.norm(r["query"]), r.get("page") or ""): r for r in report["opportunities"]}


def compare(current_csv: Path, previous_csv: Path) -> dict:
    current = seo_intelligence.analyze(current_csv)
    previous = seo_intelligence.analyze(previous_csv)
    cur = keyed(current)
    prev = keyed(previous)

    comparisons = []
    for key in sorted(set(cur) | set(prev)):
        c = cur.get(key)
        p = prev.get(key)
        if c is None:
            comparisons.append({
                "query": p["query"], "page": p.get("page") or "", "state": "NOT_IN_CURRENT_EXPORT",
                "evidence": "UNRESOLVED", "reason": "Absence from a Search Console export is not proof of zero traffic because exports/API may return only top rows.",
            })
            continue
        if p is None:
            comparisons.append({
                "query": c["query"], "page": c.get("page") or "", "state": "NEW_OBSERVED",
                "evidence": evidence_level(float(c["impressions"]), 0.0), "current": c,
                "reason": "Newly observed in the current export; no trend is inferred without a comparable previous row.",
            })
            continue

        state, recommendation = classify_pair(c, p)
        ci, pi = float(c["impressions"]), float(p["impressions"])
        cc, pc = float(c["clicks"]), float(p["clicks"])
        comparisons.append({
            "query": c["query"],
            "page": c.get("page") or "",
            "state": state,
            "evidence": evidence_level(ci, pi),
            "current": c,
            "previous": p,
            "deltas": {
                "impressions_pct": None if pct_change(ci, pi) is None else round(pct_change(ci, pi), 4),
                "clicks_pct": None if pct_change(cc, pc) is None else round(pct_change(cc, pc), 4),
                "ctr_points": round(float(c["ctr"]) - float(p["ctr"]), 4),
                "position_gain": round(float(p["position"]) - float(c["position"]), 2),
            },
            "recommendation": recommendation,
        })

    priority = {"DEFEND_RANKING": 0, "DECAYING": 1, "BREAKOUT": 2, "ACCELERATING_STRIKING_DISTANCE": 3, "EMERGING": 4, "NEW_OBSERVED": 5, "STABLE": 6, "NOT_IN_CURRENT_EXPORT": 7}
    comparisons.sort(key=lambda x: (priority.get(x["state"], 99), -float((x.get("current") or {}).get("impressions", 0))))
    counts: dict[str, int] = {}
    for item in comparisons:
        counts[item["state"]] = counts.get(item["state"], 0) + 1

    return {
        "schema": "freedom-search-temporal-v1",
        "guardrails": [
            "comparable_windows_required_for_trend",
            "missing_export_row_is_not_zero",
            "recommend_only_no_auto_publish",
            "prefer_existing_winner_before_new_url",
        ],
        "current_source": str(current_csv),
        "previous_source": str(previous_csv),
        "summary": {"comparisons": len(comparisons), "states": counts},
        "comparisons": comparisons,
    }


def markdown(report: dict) -> str:
    lines = [
        "# Freedom Search Temporal Intelligence",
        "",
        "> Comparação entre duas janelas equivalentes. Linha ausente no export atual nunca é tratada automaticamente como tráfego zero.",
        "",
        "## Estados",
        "",
    ]
    for state, count in sorted(report["summary"]["states"].items()):
        lines.append(f"- {state}: **{count}**")
    lines += ["", "## Prioridades", "", "| Estado | Evidência | Consulta | Página | Δ impressões | Ganho posição |", "|---|---|---|---|---:|---:|"]
    for item in report["comparisons"][:40]:
        d = item.get("deltas", {})
        imp = d.get("impressions_pct")
        pos = d.get("position_gain")
        imp_text = "-" if imp is None else f"{imp:+.1%}"
        pos_text = "-" if pos is None else f"{pos:+.1f}"
        q = item["query"].replace("|", "\\|")
        lines.append(f"| {item['state']} | {item.get('evidence','-')} | {q} | {item.get('page') or '-'} | {imp_text} | {pos_text} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two comparable Search Console exports without treating missing rows as zero.")
    parser.add_argument("current_csv", type=Path)
    parser.add_argument("previous_csv", type=Path)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()
    report = compare(args.current_csv, args.previous_csv)
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
