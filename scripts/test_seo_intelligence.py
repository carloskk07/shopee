#!/usr/bin/env python3
from __future__ import annotations

import csv
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from seo_intelligence import analyze, number, resolve_columns
from test_organic_control_plane import test_internal_links, test_live_repository_graph_contract, test_temporal


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fields = ["Principais consultas", "Páginas", "Cliques", "Impressões", "CTR", "Posição"]
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    cols = resolve_columns(["Principais consultas", "Páginas", "Cliques", "Impressões", "CTR", "Posição"])
    assert_true(cols["query"] == "Principais consultas", "Portuguese Search Console query header not recognized")
    assert_true(abs(number("1,5%", percent=True) - 0.015) < 1e-9, "localized percentage parsing failed")

    with tempfile.TemporaryDirectory() as tmp:
        fixture = Path(tmp) / "gsc.csv"
        write_csv(fixture, [
            {"Principais consultas":"como melhorar o foco", "Páginas":"https://achadostube.com.br/guias/como-melhorar-o-foco-e-reduzir-distracoes", "Cliques":"1", "Impressões":"120", "CTR":"0,8%", "Posição":"7,2"},
            {"Principais consultas":"como retomar disciplina", "Páginas":"https://achadostube.com.br/guias/como-criar-disciplina-sem-depender-de-motivacao", "Cliques":"2", "Impressões":"80", "CTR":"2,5%", "Posição":"12,4"},
            {"Principais consultas":"curso violao iniciante", "Páginas":"", "Cliques":"0", "Impressões":"40", "CTR":"0%", "Posição":"48"},
            {"Principais consultas":"aprender violao iniciante", "Páginas":"", "Cliques":"0", "Impressões":"35", "CTR":"0%", "Posição":"51"},
            {"Principais consultas":"violao para iniciantes", "Páginas":"", "Cliques":"0", "Impressões":"35", "CTR":"0%", "Posição":"55"},
            {"Principais consultas":"clareza mental", "Páginas":"https://achadostube.com.br/guias/como-organizar-a-mente-quando-ha-excesso-de-estimulos", "Cliques":"2", "Impressões":"60", "CTR":"3,3%", "Posição":"9"},
            {"Principais consultas":"clareza mental", "Páginas":"https://achadostube.com.br/mente-forte-vida-leve", "Cliques":"1", "Impressões":"40", "CTR":"2,5%", "Posição":"11"},
        ])
        report = analyze(fixture)

    actions = {row["query"]: row["action"] for row in report["opportunities"]}
    assert_true(actions["como melhorar o foco"] == "CTR_OPPORTUNITY", "CTR opportunity classifier regression")
    assert_true(actions["como retomar disciplina"] == "STRIKING_DISTANCE", "striking-distance classifier regression")
    assert_true(report["summary"]["cannibalization_queries"] == 1, "cannibalization detector regression")
    assert_true(report["summary"]["new_url_candidates"] >= 1, "new-intent evidence gates regression")
    assert_true(report["guardrail"] == "recommend_only_no_auto_publish", "automatic-publishing guardrail regression")

    # V4 control-plane contracts are deliberately executed by the existing
    # Site Integrity entrypoint, so the new intelligence cannot silently rot.
    test_temporal()
    test_internal_links()
    test_live_repository_graph_contract()

    print("PASS: Freedom Search Intelligence + temporal/link control-plane deterministic gates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
