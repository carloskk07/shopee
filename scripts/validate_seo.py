#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CANON = 'https://achadostube.com.br'

def fail(message: str) -> None:
    raise SystemExit(message)

def jsonld(path: Path) -> dict:
    text = path.read_text(encoding='utf-8')
    m = re.search(r'<script\s+type="application/ld\+json">(.*?)</script>', text, re.S | re.I)
    if not m:
        fail(f'{path.name}: JSON-LD missing')
    try:
        return json.loads(m.group(1))
    except Exception as exc:
        fail(f'{path.name}: invalid JSON-LD: {exc}')


data = json.loads((ROOT / 'site-data.generated.json').read_text(encoding='utf-8'))
modified = data.get('site', {}).get('modified')
if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(modified)):
    fail(f'invalid site modified date: {modified!r}')
available = [b for b in data.get('books', []) if b.get('available')]
if len(available) != 10:
    fail(f'expected 10 available books, got {len(available)}')

# Home entity consistency.
home = (ROOT / 'index.html').read_text(encoding='utf-8')
if data['site']['logo'] not in home:
    fail('home Organization logo is not the optimized canonical asset')
if CANON + '/imagens/logo-freedom-book-redonda.png' in home:
    fail('home still exposes stale PNG logo in structured data')
if f'"dateModified":"{modified}"' not in home:
    fail('home dateModified drift')

# Author page is a genuine ProfilePage, not a synthetic biography.
author_path = ROOT / 'autor-arthur-magnus.html'
author_text = author_path.read_text(encoding='utf-8')
author_ld = jsonld(author_path)
graph = author_ld.get('@graph', []) if isinstance(author_ld, dict) else []
by_type: dict[str, list[dict]] = {}
for node in graph:
    types = node.get('@type', [])
    if isinstance(types, str):
        types = [types]
    for t in types:
        by_type.setdefault(t, []).append(node)
profile = (by_type.get('ProfilePage') or [None])[0]
person = (by_type.get('Person') or [None])[0]
breadcrumb = (by_type.get('BreadcrumbList') or [None])[0]
org = (by_type.get('Organization') or [None])[0]
if not all((profile, person, breadcrumb, org)):
    fail('author graph must include ProfilePage, Person, BreadcrumbList and Organization')
if profile.get('mainEntity', {}).get('@id') != CANON + '/autor-arthur-magnus#person':
    fail('author ProfilePage mainEntity mismatch')
if profile.get('dateModified') != modified:
    fail('author ProfilePage dateModified mismatch')
if person.get('name') != 'Arthur Magnus' or person.get('url') != CANON + '/autor-arthur-magnus':
    fail('author Person identity drift')
if 'image' in person:
    fail('author Person must not use a logo/placeholder as a synthetic portrait')
if org.get('logo', {}).get('url') != data['site']['logo']:
    fail('author Organization logo drift')
has_part = profile.get('hasPart', [])
if len(has_part) != len(available):
    fail(f'author ProfilePage hasPart count mismatch: {len(has_part)}')
expected_urls = {b['pageUrl'] for b in available}
if {x.get('url') for x in has_part} != expected_urls:
    fail('author ProfilePage published-book URL set mismatch')
for b in available:
    href = f'href="/{b["slug"]}"'
    cover = f'src="/assets/covers/capa-{b["slug"]}.webp"'
    if href not in author_text or cover not in author_text or b['title'] not in author_text:
        fail(f'author visible library missing {b["slug"]}')

# Book page authority: canonical landing page, optimized cover, author/publisher graph and truthful modified date.
for b in available:
    slug = b['slug']
    page = ROOT / f'{slug}.html'
    text = page.read_text(encoding='utf-8')
    if f'<link href="{b["pageUrl"]}" rel="canonical"' not in text and f'<link rel="canonical" href="{b["pageUrl"]}"' not in text:
        fail(f'{slug}: canonical drift')
    if b['cover'] not in text:
        fail(f'{slug}: optimized cover URL absent from metadata/markup')
    if CANON + f'/imagens/capa-{slug}.png' in text:
        fail(f'{slug}: stale PNG cover URL remains in SEO metadata')
    if f'"dateModified":"{modified}"' not in text:
        fail(f'{slug}: dateModified drift')
    ld = jsonld(page)
    nodes = ld.get('@graph', []) if isinstance(ld, dict) else []
    book = next((n for n in nodes if n.get('@type') == 'Book'), None)
    web_page = next((n for n in nodes if n.get('@type') == 'WebPage'), None)
    crumbs = next((n for n in nodes if n.get('@type') == 'BreadcrumbList'), None)
    if not all((book, web_page, crumbs)):
        fail(f'{slug}: expected Book + WebPage + BreadcrumbList graph')
    if book.get('url') != b['pageUrl'] or book.get('image') != b['cover']:
        fail(f'{slug}: Book entity URL/image drift')
    if book.get('author', {}).get('@id') != CANON + '/autor-arthur-magnus#person':
        fail(f'{slug}: Book author identity drift')
    if book.get('publisher', {}).get('@id') != CANON + '/#organization':
        fail(f'{slug}: Book publisher identity drift')
    if web_page.get('dateModified') != modified:
        fail(f'{slug}: WebPage dateModified mismatch')

# Sitemap must contain only indexable canonical editorial pages and accurate lastmod values.
ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9', 'i': 'http://www.google.com/schemas/sitemap-image/1.1'}
root = ET.parse(ROOT / 'sitemap.xml').getroot()
nodes = root.findall('s:url', ns)
expected = {CANON + '/', CANON + '/autor-arthur-magnus'} | {b['pageUrl'] for b in available}
seen: set[str] = set()
for node in nodes:
    loc = node.find('s:loc', ns)
    lastmod = node.find('s:lastmod', ns)
    if loc is None or lastmod is None:
        fail('sitemap loc/lastmod missing')
    url = loc.text.strip()
    seen.add(url)
    if lastmod.text.strip() != modified:
        fail(f'sitemap lastmod drift: {url} -> {lastmod.text!r}')
    parsed = urlparse(url)
    if parsed.scheme != 'https' or parsed.netloc != 'achadostube.com.br':
        fail(f'sitemap non-canonical origin: {url}')
    if url not in {CANON + '/', CANON + '/autor-arthur-magnus'}:
        image = node.find('i:image/i:loc', ns)
        if image is None or not image.text.endswith('.webp'):
            fail(f'sitemap optimized cover missing: {url}')
if seen != expected:
    fail(f'sitemap indexable URL set mismatch: {sorted(seen ^ expected)}')
if CANON + '/codigo-da-vida-inabalavel' in seen:
    fail('noindex upcoming page must not enter sitemap')

# Legacy commerce remains outside the editorial sitemap. Its indexability is not changed without traffic evidence.
for name in ('kit-3-pares.html', 'kit-sandalias-infantil.html'):
    text = (ROOT / name).read_text(encoding='utf-8')
    if 'name="robots" content="index,follow' not in text:
        fail(f'{name}: legacy indexability changed without Search Console evidence')
    if name[:-5] in ''.join(sorted(seen)):
        fail(f'{name}: legacy offer leaked into editorial sitemap')

print(f'PASS: SEO/indexation contract coherent for {len(expected)} canonical indexable pages and {len(available)} published books')
