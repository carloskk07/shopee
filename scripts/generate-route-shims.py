#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = 'https://achadostube.com.br'
MANIFEST = ROOT / 'route-shims.generated.json'

CANONICAL_PATHS = (
    '/autor-arthur-magnus',
    '/a-vida-que-voce-adiou',
    '/codigo-da-vida-inabalavel',
    '/disciplina-e-liberdade',
    '/foco-que-gera-resultados',
    '/mente-forte-vida-leve',
    '/o-cansaco-invisivel',
    '/o-metodo-da-vida-mais-leve',
    '/o-peso-de-ser-forte-o-tempo-todo',
    '/privacidade',
    '/proposito-maior',
    '/quando-sua-vida-virou-sobrevivencia',
    '/recomecos-sao-escolhas',
    '/termos',
    '/kit-3-pares',
    '/kit-sandalias-infantil',
)


def parse_redirects() -> dict[str, str]:
    redirects: dict[str, str] = {}
    for raw in (ROOT / '_redirects').read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        parts = re.split(r'\s+', line)
        if len(parts) < 3:
            raise SystemExit(f'invalid _redirects line: {line}')
        source, target, status = parts[:3]
        if status != '301':
            raise SystemExit(f'unsupported redirect status: {line}')
        if not source.startswith('/') or not target.startswith('/'):
            raise SystemExit(f'route must stay origin-relative: {line}')
        redirects[source] = target
    return redirects


def destination_for_alias(path: str, redirects: dict[str, str]) -> str | None:
    if path in redirects:
        return redirects[path]
    slash = path.rstrip('/') + '/'
    return redirects.get(slash)


def expected_routes() -> dict[str, tuple[str, str]]:
    redirects = parse_redirects()
    routes: dict[str, tuple[str, str]] = {}

    for path in CANONICAL_PATHS:
        file_path = f"{path.lstrip('/')}/index.html"
        routes[file_path] = (path + '/', path)

    alias_roots = {
        source.rstrip('/')
        for source in redirects
        if source.startswith('/') and source != '/' and not source.rstrip('/').endswith('.html')
    }
    for source in sorted(alias_roots):
        destination = destination_for_alias(source, redirects)
        if not destination:
            raise SystemExit(f'alias destination missing for {source}')
        file_path = f"{source.lstrip('/')}/index.html"
        routes[file_path] = (source + '/', destination)

    return routes


def shim_html(public_path: str, destination: str) -> str:
    canonical = CANON + ('/' if destination == '/' else destination)
    title = 'Freedom Book — endereço atualizado'
    dest_attr = html.escape(destination, quote=True)
    canon_attr = html.escape(canonical, quote=True)
    dest_js = json.dumps(destination, ensure_ascii=False)
    return (
        '<!doctype html>\n'
        '<html lang="pt-BR">\n'
        '<head>\n'
        '  <meta charset="utf-8">\n'
        '  <meta name="viewport" content="width=device-width,initial-scale=1">\n'
        '  <meta name="robots" content="noindex,follow">\n'
        f'  <link rel="canonical" href="{canon_attr}">\n'
        f'  <meta http-equiv="refresh" content="0;url={dest_attr}">\n'
        f'  <title>{title}</title>\n'
        '</head>\n'
        '<body>\n'
        f'  <p>Este endereço mudou. <a href="{dest_attr}">Continuar</a>.</p>\n'
        f'  <script>location.replace({dest_js}+location.search+location.hash);</script>\n'
        f'  <!-- static-route-shim-v1 {html.escape(public_path)} -> {dest_attr} -->\n'
        '</body>\n'
        '</html>\n'
    )


def manifest_bytes(entries: list[dict[str, str]]) -> bytes:
    data = {
        'schema': 'freedom-book-route-shims-v1',
        'origin': CANON,
        'entries': entries,
    }
    return (json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf-8')


def build_expected() -> tuple[dict[Path, bytes], bytes]:
    files: dict[Path, bytes] = {}
    entries: list[dict[str, str]] = []
    for relative, (public_path, destination) in sorted(expected_routes().items()):
        body = shim_html(public_path, destination).encode('utf-8')
        path = ROOT / relative
        files[path] = body
        entries.append({
            'publicPath': public_path,
            'file': relative,
            'destination': destination,
            'sha256': hashlib.sha256(body).hexdigest(),
        })
    return files, manifest_bytes(entries)


def check() -> None:
    files, manifest = build_expected()
    failures: list[str] = []
    for path, expected in files.items():
        if not path.is_file():
            failures.append(f'missing static route shim: {path.relative_to(ROOT)}')
        elif path.read_bytes() != expected:
            failures.append(f'static route shim drift: {path.relative_to(ROOT)}')
    if not MANIFEST.is_file():
        failures.append('missing route-shims.generated.json')
    elif MANIFEST.read_bytes() != manifest:
        failures.append('route-shims.generated.json drift')
    if failures:
        raise SystemExit('\n'.join(failures))
    print(f'PASS: {len(files)} static route shims are deterministic and complete')


def write() -> None:
    files, manifest = build_expected()
    for path, body in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
    MANIFEST.write_bytes(manifest)
    print(f'Generated {len(files)} static route shims + manifest')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    check() if args.check else write()


if __name__ == '__main__':
    main()
