#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = 'https://achadostube.com.br'
MODIFIED = '2026-09-09'
DATA_PATH = ROOT / 'site-data.generated.json'


def compact_json(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(',', ':'))


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding='utf-8')


def replace_jsonld(text: str, payload: dict) -> str:
    pattern = r'<script type="application/ld\+json">.*?</script>'
    replacement = '<script type="application/ld+json">' + compact_json(payload) + '</script>'
    out, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit('expected exactly one JSON-LD block')
    return out


data = json.loads(DATA_PATH.read_text(encoding='utf-8'))
data['site']['modified'] = MODIFIED
books = data['books']
available = [b for b in books if b.get('available')]
if len(available) != 10:
    raise SystemExit(f'expected 10 available books, got {len(available)}')
write_text(DATA_PATH, json.dumps(data, ensure_ascii=False, indent=2) + '\n')

# Home: align entity logo with optimized canonical asset and truthful modification date.
home_path = ROOT / 'index.html'
home = home_path.read_text(encoding='utf-8')
home = home.replace(
    CANON + '/imagens/logo-freedom-book-redonda.png',
    data['site']['logo'],
)
home = re.sub(r'"dateModified":"[0-9]{4}-[0-9]{2}-[0-9]{2}"', f'"dateModified":"{MODIFIED}"', home, count=1)
write_text(home_path, home)

# Book landing pages: one image authority across social metadata, JSON-LD and sitemap.
for book in available:
    slug = book['slug']
    page_path = ROOT / f'{slug}.html'
    text = page_path.read_text(encoding='utf-8')
    old_image = CANON + f'/imagens/capa-{slug}.png'
    text = text.replace(old_image, book['cover'])
    text = re.sub(r'"dateModified":"[0-9]{4}-[0-9]{2}-[0-9]{2}"', f'"dateModified":"{MODIFIED}"', text, count=1)
    write_text(page_path, text)

# Author page: Google-supported ProfilePage + breadcrumb + explicit factual book graph and visible internal links.
author_path = ROOT / 'autor-arthur-magnus.html'
author = author_path.read_text(encoding='utf-8')
author_description = 'Arthur Magnus é o nome de autoria dos e-books publicados pela Freedom Book.'
person_id = CANON + '/autor-arthur-magnus#person'
org_id = CANON + '/#organization'
website_id = CANON + '/#website'
author_url = CANON + '/autor-arthur-magnus'

profile_graph = {
    '@context': 'https://schema.org',
    '@graph': [
        {
            '@type': 'Organization',
            '@id': org_id,
            'name': 'Freedom Book',
            'url': CANON + '/',
            'logo': {'@type': 'ImageObject', 'url': data['site']['logo']},
        },
        {
            '@type': 'WebSite',
            '@id': website_id,
            'name': 'Freedom Book',
            'url': CANON + '/',
            'publisher': {'@id': org_id},
            'inLanguage': 'pt-BR',
        },
        {
            '@type': 'Person',
            '@id': person_id,
            'name': 'Arthur Magnus',
            'url': author_url,
            'description': author_description,
            'worksFor': {'@id': org_id},
        },
        {
            '@type': 'BreadcrumbList',
            '@id': author_url + '#breadcrumb',
            'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Freedom Book', 'item': CANON + '/'},
                {'@type': 'ListItem', 'position': 2, 'name': 'Arthur Magnus', 'item': author_url},
            ],
        },
        {
            '@type': 'ProfilePage',
            '@id': author_url + '#webpage',
            'url': author_url,
            'name': 'Arthur Magnus — autor da Freedom Book',
            'description': 'Conheça Arthur Magnus, autor dos e-books publicados pela Freedom Book sobre propósito, foco, disciplina, recomeços, clareza mental e vida prática.',
            'inLanguage': 'pt-BR',
            'dateModified': MODIFIED,
            'isPartOf': {'@id': website_id},
            'breadcrumb': {'@id': author_url + '#breadcrumb'},
            'mainEntity': {'@id': person_id},
            'hasPart': [
                {
                    '@type': 'Book',
                    'name': b['title'],
                    'url': b['pageUrl'],
                    'author': {'@id': person_id},
                }
                for b in available
            ],
        },
    ],
}
author = replace_jsonld(author, profile_graph)

cards = []
for b in available:
    cards.append(
        '<a class="card related-card" href="/{slug}">'
        '<img alt="Capa de {title}" decoding="async" loading="lazy" src="/assets/covers/capa-{slug}.webp"/>'
        '<div><h3>{title}</h3><p>{description}</p></div></a>'.format(
            slug=b['slug'], title=b['title'], description=b['description']
        )
    )
new_author_section = (
    '<section class="section alt"><div class="container">'
    '<div class="section-head"><span class="kicker">Biblioteca</span><h2>Leituras publicadas</h2>'
    '<p>Os títulos abaixo são os e-books atualmente publicados pela Freedom Book e podem ser acessados diretamente.</p></div>'
    '<div class="grid related">' + ''.join(cards) + '</div>'
    '</div></section>'
)
section_pattern = (
    r'<section class="section alt"><div class="container"><div class="section-head">'
    r'<span class="kicker">Biblioteca</span>.*?</section>'
)
author, count = re.subn(section_pattern, new_author_section, author, count=1, flags=re.S)
if count != 1:
    raise SystemExit('author library section not found')
write_text(author_path, author)

# Sitemap: all canonical indexable pages changed in this campaign, so lastmod advances truthfully.
ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
ET.register_namespace('image', 'http://www.google.com/schemas/sitemap-image/1.1')
sitemap_path = ROOT / 'sitemap.xml'
tree = ET.parse(sitemap_path)
root = tree.getroot()
ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
for node in root.findall('s:url', ns):
    lastmod = node.find('s:lastmod', ns)
    if lastmod is None:
        lastmod = ET.SubElement(node, '{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
    lastmod.text = MODIFIED
tree.write(sitemap_path, encoding='utf-8', xml_declaration=True)

# Deliberately preserve maintenance-marker.json: the existing validator owns that contract.
print(f'Applied SEO hardening to home, author and {len(available)} book pages; lastmod={MODIFIED}')
