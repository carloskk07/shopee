#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://achadostube.com.br"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self._capture_title = False
        self._capture_h1 = False
        self.title_parts: list[str] = []
        self.h1_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_d = dict(attrs)
        if tag == "a" and attrs_d.get("href"):
            self.links.append(attrs_d["href"] or "")
        elif tag == "title":
            self._capture_title = True
        elif tag == "h1":
            self._capture_h1 = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._capture_title = False
        elif tag == "h1":
            self._capture_h1 = False

    def handle_data(self, data: str) -> None:
        if self._capture_title:
            self.title_parts.append(data)
        if self._capture_h1:
            self.h1_parts.append(data)


def canonical_path(value: str) -> str | None:
    value = (value or "").strip()
    if not value or value.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
        return None
    if value.startswith("http://") or value.startswith("https://"):
        p = urlparse(value)
        if p.netloc not in {"achadostube.com.br", "www.achadostube.com.br"}:
            return None
        value = p.path
    value = value.split("?", 1)[0].split("#", 1)[0]
    if not value.startswith("/"):
        value = "/" + value
    if value.endswith(".html"):
        value = value[:-5]
    if value != "/":
        value = value.rstrip("/")
    return value or "/"


def html_for(root: Path, path: str) -> Path:
    if path == "/":
        return root / "index.html"
    rel = path.strip("/")
    direct = root / f"{rel}.html"
    if direct.exists():
        return direct
    index = root / rel / "index.html"
    if index.exists():
        return index
    return direct


def sitemap_paths(root: Path) -> list[str]:
    tree = ET.parse(root / "sitemap.xml")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    out = []
    for loc in tree.findall(".//s:loc", ns):
        path = canonical_path(loc.text or "")
        if path:
            out.append(path)
    return sorted(set(out))


def tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-zA-ZÀ-ÿ0-9]+", (text or "").lower())
    stop = {"como","para","uma","um","de","da","do","dos","das","e","o","a","os","as","em","na","no","nas","nos","que","sem","com","por","book","freedom"}
    return {w for w in words if len(w) >= 4 and w not in stop}


def page_profile(path: str, parser: PageParser) -> set[str]:
    title = " ".join(parser.title_parts)
    h1 = " ".join(parser.h1_parts)
    slug = path.replace("/", " ").replace("-", " ")
    return tokenize(f"{title} {h1} {slug}")


def similarity(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def pagerank(nodes: list[str], edges: dict[str, set[str]], rounds: int = 30, damping: float = 0.85) -> dict[str, float]:
    n = max(1, len(nodes))
    score = {node: 1.0 / n for node in nodes}
    for _ in range(rounds):
        new = {node: (1 - damping) / n for node in nodes}
        dangling = sum(score[node] for node in nodes if not edges[node])
        for node in nodes:
            new[node] += damping * dangling / n
        for src in nodes:
            if not edges[src]:
                continue
            share = damping * score[src] / len(edges[src])
            for dst in edges[src]:
                if dst in new:
                    new[dst] += share
        score = new
    total = sum(score.values()) or 1.0
    return {k: v / total for k, v in score.items()}


def analyze(root: Path = ROOT) -> dict:
    nodes = sitemap_paths(root)
    node_set = set(nodes)
    edges: dict[str, set[str]] = {n: set() for n in nodes}
    profiles: dict[str, set[str]] = {}
    missing_files = []

    for node in nodes:
        file = html_for(root, node)
        if not file.exists():
            missing_files.append({"path": node, "expected_file": str(file.relative_to(root))})
            profiles[node] = tokenize(node)
            continue
        parser = PageParser()
        parser.feed(file.read_text(encoding="utf-8"))
        profiles[node] = page_profile(node, parser)
        for href in parser.links:
            target = canonical_path(href)
            if target in node_set and target != node:
                edges[node].add(target)

    indegree = {n: 0 for n in nodes}
    for src in nodes:
        for dst in edges[src]:
            indegree[dst] += 1
    outdegree = {n: len(edges[n]) for n in nodes}
    ranks = pagerank(nodes, edges)

    orphans = [n for n in nodes if n != "/" and indegree[n] == 0]
    dead_ends = [n for n in nodes if outdegree[n] == 0]
    underlinked = [n for n in nodes if n != "/" and indegree[n] <= 1]

    suggestions = []
    for target in underlinked:
        candidates = []
        for src in nodes:
            if src == target or target in edges[src]:
                continue
            sim = similarity(profiles.get(src, set()), profiles.get(target, set()))
            if sim <= 0:
                continue
            candidates.append((sim, ranks.get(src, 0.0), src))
        for sim, authority, src in sorted(candidates, reverse=True)[:3]:
            suggestions.append({
                "source": src,
                "target": target,
                "topical_similarity": round(sim, 4),
                "source_authority": round(authority, 6),
                "decision": "REVIEW_INTERNAL_LINK",
            })

    guide_nodes = [n for n in nodes if n.startswith("/guias/")]
    guide_edges = sum(1 for g in guide_nodes for d in edges[g] if d.startswith("/guias/"))
    avg_indegree = (sum(indegree.values()) / len(nodes)) if nodes else 0.0
    health = 100.0
    health -= min(45, len(orphans) * 15)
    health -= min(25, len(dead_ends) * 10)
    health -= min(20, len(underlinked) * 2)
    health -= min(10, len(missing_files) * 5)

    node_rows = []
    for n in sorted(nodes, key=lambda x: (-ranks.get(x, 0.0), x)):
        node_rows.append({
            "path": n,
            "indegree": indegree[n],
            "outdegree": outdegree[n],
            "authority": round(ranks.get(n, 0.0), 6),
            "page_type": "guide" if n.startswith("/guias/") else ("guide_hub" if n == "/guias" else "editorial"),
        })

    return {
        "schema": "freedom-internal-link-intelligence-v1",
        "guardrail": "recommend_only_no_auto_edit",
        "summary": {
            "indexable_urls": len(nodes),
            "internal_edges": sum(len(v) for v in edges.values()),
            "average_indegree": round(avg_indegree, 2),
            "orphan_pages": len(orphans),
            "dead_end_pages": len(dead_ends),
            "underlinked_pages": len(underlinked),
            "guide_to_guide_edges": guide_edges,
            "health_score": round(max(0.0, health), 1),
            "missing_files": len(missing_files),
        },
        "orphans": orphans,
        "dead_ends": dead_ends,
        "underlinked": underlinked,
        "missing_files": missing_files,
        "nodes": node_rows,
        "suggested_links": suggestions,
    }


def markdown(report: dict) -> str:
    s = report["summary"]
    lines = [
        "# Freedom Internal Link Intelligence",
        "",
        "> Auditoria do grafo interno das URLs indexáveis. Sugestões nunca alteram HTML automaticamente.",
        "",
        f"- URLs indexáveis: **{s['indexable_urls']}**",
        f"- Arestas internas: **{s['internal_edges']}**",
        f"- Indegree médio: **{s['average_indegree']}**",
        f"- Órfãs: **{s['orphan_pages']}**",
        f"- Dead ends: **{s['dead_end_pages']}**",
        f"- Sub-linkadas: **{s['underlinked_pages']}**",
        f"- Links guia → guia: **{s['guide_to_guide_edges']}**",
        f"- Health score: **{s['health_score']}/100**",
        "",
        "## Autoridade interna",
        "",
        "| URL | Tipo | Entradas | Saídas | Autoridade |",
        "|---|---|---:|---:|---:|",
    ]
    for n in report["nodes"]:
        lines.append(f"| {n['path']} | {n['page_type']} | {n['indegree']} | {n['outdegree']} | {n['authority']:.6f} |")
    if report["suggested_links"]:
        lines += ["", "## Sugestões revisáveis", "", "| Origem | Destino | Similaridade | Autoridade origem |", "|---|---|---:|---:|"]
        for x in report["suggested_links"][:30]:
            lines.append(f"| {x['source']} | {x['target']} | {x['topical_similarity']:.2f} | {x['source_authority']:.6f} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit internal authority distribution across indexable Freedom Book URLs.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()
    report = analyze(args.root)
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
