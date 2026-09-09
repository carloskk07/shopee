#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import generative_visibility
import internal_link_intelligence as links
import seo_temporal


def write_csv(path: Path, rows: list[tuple[str, str, str, str, str, str]]) -> None:
    text = "Consulta,Página,Cliques,Impressões,CTR,Posição\n"
    for row in rows:
        text += ",".join(row) + "\n"
    path.write_text(text, encoding="utf-8")


def test_temporal() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        previous = root / "previous.csv"
        current = root / "current.csv"
        write_csv(previous, [
            ("como melhorar foco", "https://achadostube.com.br/guias/como-melhorar-o-foco-e-reduzir-distracoes", "2", "100", "2%", "15"),
            ("rotina pesada", "https://achadostube.com.br/guias/como-simplificar-uma-rotina-que-ficou-pesada", "1", "80", "1%", "18"),
        ])
        write_csv(current, [
            ("como melhorar foco", "https://achadostube.com.br/guias/como-melhorar-o-foco-e-reduzir-distracoes", "6", "170", "3.5%", "10"),
            ("clareza mental nova", "https://achadostube.com.br/guias/como-organizar-a-mente-quando-ha-excesso-de-estimulos", "1", "60", "1%", "22"),
        ])
        report = seo_temporal.compare(current, previous)
        states = {x["query"]: x["state"] for x in report["comparisons"]}
        assert states["como melhorar foco"] == "BREAKOUT", states
        assert states["rotina pesada"] == "NOT_IN_CURRENT_EXPORT", states
        assert states["clareza mental nova"] == "NEW_OBSERVED", states
        missing = next(x for x in report["comparisons"] if x["query"] == "rotina pesada")
        assert "not proof of zero traffic" in missing["reason"]
        assert report["guardrails"][1] == "missing_export_row_is_not_zero"


def test_generative_visibility() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        ai = root / "ai.csv"
        web = root / "web.csv"
        ai.write_text(
            "Páginas,Impressões\n"
            "https://achadostube.com.br/guias/como-melhorar-o-foco-e-reduzir-distracoes,40\n"
            "https://achadostube.com.br/guias/como-encontrar-proposito-na-vida,~\n",
            encoding="utf-8",
        )
        web.write_text(
            "Páginas,Impressões\n"
            "https://achadostube.com.br/guias/como-melhorar-o-foco-e-reduzir-distracoes,200\n"
            "https://achadostube.com.br/guias/como-encontrar-proposito-na-vida,300\n"
            "https://achadostube.com.br/guias/como-criar-disciplina-sem-depender-de-motivacao,180\n",
            encoding="utf-8",
        )
        report = generative_visibility.analyze(ai, web)
        states = {x["page"]: x["state"] for x in report["pages"]}
        assert states["/guias/como-melhorar-o-foco-e-reduzir-distracoes"] == "AI_VISIBLE", states
        assert states["/guias/como-encontrar-proposito-na-vida"] == "AI_ZERO_OR_UNAVAILABLE", states
        assert states["/guias/como-criar-disciplina-sem-depender-de-motivacao"] == "NOT_IN_AI_EXPORT", states
        focus = next(x for x in report["pages"] if x["page"].endswith("foco-e-reduzir-distracoes"))
        assert abs(focus["ai_to_web_ratio"] - 0.2) < 1e-9
        assert "zero_export_value_is_ambiguous" in report["guardrails"]


def html(title: str, h1: str, links_out: list[str]) -> str:
    anchors = "".join(f'<a href="{href}">{href}</a>' for href in links_out)
    return f'<!doctype html><html><head><title>{title}</title></head><body><h1>{h1}</h1>{anchors}</body></html>'


def test_internal_links() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "guias").mkdir()
        sitemap = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>https://achadostube.com.br/</loc></url>
<url><loc>https://achadostube.com.br/guias</loc></url>
<url><loc>https://achadostube.com.br/guias/foco</loc></url>
<url><loc>https://achadostube.com.br/foco-livro</loc></url>
</urlset>"""
        (root / "sitemap.xml").write_text(sitemap, encoding="utf-8")
        (root / "index.html").write_text(html("Freedom Book", "Freedom Book", ["/guias", "/foco-livro"]), encoding="utf-8")
        (root / "guias.html").write_text(html("Guias", "Guias", ["/guias/foco"]), encoding="utf-8")
        (root / "guias" / "foco.html").write_text(html("Como melhorar foco", "Como melhorar foco", ["/foco-livro"]), encoding="utf-8")
        (root / "foco-livro.html").write_text(html("Livro de foco", "Foco que gera resultados", ["/guias/foco"]), encoding="utf-8")
        report = links.analyze(root)
        assert report["schema"] == "freedom-internal-link-intelligence-v1"
        assert report["summary"]["indexable_urls"] == 4
        assert report["summary"]["orphan_pages"] == 0, report
        assert report["summary"]["dead_end_pages"] == 0, report
        assert report["guardrail"] == "recommend_only_no_auto_edit"
        assert abs(sum(n["authority"] for n in report["nodes"]) - 1.0) < 0.00001


def test_live_repository_graph_contract() -> None:
    report = links.analyze(Path(__file__).resolve().parents[1])
    assert report["summary"]["indexable_urls"] >= 19
    assert report["summary"]["missing_files"] == 0, report["missing_files"]
    assert report["summary"]["guide_to_guide_edges"] >= 1
    print("LIVE_GRAPH_SUMMARY", report["summary"])


if __name__ == "__main__":
    test_temporal()
    test_generative_visibility()
    test_internal_links()
    test_live_repository_graph_contract()
    print("PASS: temporal, generative-visibility and internal-link authority contracts are deterministic")
