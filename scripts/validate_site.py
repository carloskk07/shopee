#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os, pathlib, re, sys
from html.parser import HTMLParser
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
RELEASE = "2026.09.08-v2.2"
CANON = "https://achadostube.com.br"
EXPECTED_HTML = {
    "index.html", "404.html", "a-vida-que-voce-adiou.html", "codigo-da-vida-inabalavel.html",
    "disciplina-e-liberdade.html", "foco-que-gera-resultados.html", "mente-forte-vida-leve.html",
    "o-cansaco-invisivel.html", "o-metodo-da-vida-mais-leve.html", "o-peso-de-ser-forte-o-tempo-todo.html",
    "privacidade.html", "proposito-maior.html", "quando-sua-vida-virou-sobrevivencia.html",
    "recomecos-sao-escolhas.html", "termos.html"
}

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids=[]; self.h1=0; self.canon=[]; self.scripts=[]; self.links=[]; self.release=[]; self.inline_handlers=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag=='h1': self.h1 += 1
        if tag=='link' and a.get('rel')=='canonical': self.canon.append(a.get('href',''))
        if tag=='script': self.scripts.append(a)
        if tag in {'a','img','script','link'}:
            for key in ('href','src'):
                if a.get(key): self.links.append(a[key])
        if tag=='meta' and a.get('name')=='freedom-book-release': self.release.append(a.get('content',''))
        for k in a:
            if k.lower().startswith('on'): self.inline_handlers.append(k)


def fail(msg:str):
    raise SystemExit(msg)

def sha(path:pathlib.Path)->str:
    h=hashlib.sha256();
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20), b''): h.update(chunk)
    return h.hexdigest()

def route_target(path:str)->pathlib.Path:
    path=path.rstrip('/')
    if not path: return ROOT/'index.html'
    slug=path.lstrip('/')
    p=ROOT/f'{slug}.html'
    if p.exists(): return p
    p=ROOT/slug
    return p

# Expected editorial pages must exist. Legacy HTML may coexist outside this set.
for name in sorted(EXPECTED_HTML):
    p=ROOT/name
    if not p.is_file() or p.stat().st_size==0: fail(f'missing editorial HTML: {name}')

canon_seen={}
for name in sorted(EXPECTED_HTML):
    text=(ROOT/name).read_text('utf-8')
    if 'https://www.achadostube.com.br' in text: fail(f'obsolete www canonical in {name}')
    p=Parser(); p.feed(text)
    if len(p.ids)!=len(set(p.ids)): fail(f'duplicate id in {name}')
    if p.h1 != 1: fail(f'{name}: expected exactly one h1, got {p.h1}')
    if p.inline_handlers: fail(f'{name}: inline event handlers are forbidden: {p.inline_handlers}')
    if p.release != [RELEASE]: fail(f'{name}: invalid release meta {p.release}')
    if name not in {'404.html'}:
        if len(p.canon)!=1: fail(f'{name}: expected one canonical, got {p.canon}')
        c=p.canon[0]
        if not c.startswith(CANON): fail(f'{name}: non-canonical origin {c}')
        if name not in {'privacidade.html','termos.html','codigo-da-vida-inabalavel.html'}:
            if c in canon_seen: fail(f'duplicate canonical {c}: {canon_seen[c]} and {name}')
            canon_seen[c]=name
    # External tracking scripts must never be statically embedded.
    for s in p.scripts:
        src=s.get('src','')
        if 'googletagmanager.com' in src or 'analytics.tiktok.com' in src:
            fail(f'{name}: non-essential tracker embedded before consent: {src}')
    # JSON-LD must parse.
    for m in re.finditer(r'<script\s+type="application/ld\+json">(.*?)</script>', text, re.S|re.I):
        try: json.loads(m.group(1))
        except Exception as e: fail(f'{name}: invalid JSON-LD: {e}')

home=(ROOT/'index.html').read_text('utf-8')
if home.count('data-book-card') != 11: fail('home must contain exactly 11 catalog cards')
if 'book-card:first-child' in (ROOT/'assets/style.v2.2.css').read_text('utf-8'): fail('positional featured styling reintroduced')
if '/assets/style.v2.2.css' not in home or '/assets/app.v2.2.js' not in home: fail('home is not on v2.2 assets')
if 'gtag/js?id=' in home or 'analytics.tiktok.com' in home: fail('home embeds non-essential trackers')

# Catalog truth.
data=json.loads((ROOT/'site-data.generated.json').read_text('utf-8'))
if data.get('site',{}).get('release') != RELEASE: fail('site-data release mismatch')
books=data.get('books',[])
if len(books)!=11: fail(f'expected 11 books, got {len(books)}')
slugs=[b['slug'] for b in books]
if len(slugs)!=len(set(slugs)): fail('duplicate book slug')
for b in books:
    slug=b['slug']; page=ROOT/f'{slug}.html'
    if not page.is_file(): fail(f'missing book page: {slug}')
    if b.get('available'):
        pdf=b.get('pdfUrl','')
        if not pdf.startswith(CANON+'/ebook/') or not pdf.endswith('.pdf'): fail(f'{slug}: bad published PDF URL')
        local=ROOT/'ebook'/pathlib.PurePosixPath(urlparse(pdf).path).name
        if not local.is_file():
            if os.environ.get('ALLOW_MISSING_EBOOK_DIR') == '1' and not (ROOT/'ebook').exists():
                pass
            else:
                fail(f'{slug}: PDF missing in repository: {local}')
        elif local.stat().st_size<1024 or local.open('rb').read(5)!=b'%PDF-':
            fail(f'{slug}: invalid PDF')
    else:
        if b.get('pdfUrl'): fail(f'{slug}: unavailable book advertises a PDF')

# Sitemap truth.
root=ET.parse(ROOT/'sitemap.xml').getroot(); ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
urls=[e.text.strip() for e in root.findall('s:url/s:loc',ns) if e.text]
if len(urls)!=len(set(urls)): fail('duplicate sitemap URL')
if not urls: fail('empty sitemap')
for url in urls:
    u=urlparse(url)
    if u.scheme!='https' or u.netloc!='achadostube.com.br': fail(f'bad sitemap URL: {url}')
    target=route_target(u.path)
    if not target.is_file() or target.stat().st_size==0: fail(f'sitemap route missing: {url} -> {target.relative_to(ROOT)}')
if CANON+'/codigo-da-vida-inabalavel' in urls: fail('noindex upcoming release must not be in sitemap')

# Vercel image optimizer contract: every requested width and quality is allowlisted.
v=json.loads((ROOT/'vercel.json').read_text('utf-8'))
img=v.get('images',{}); sizes=set(img.get('sizes',[])); qualities=set(img.get('qualities',[]))
for name in EXPECTED_HTML:
    text=(ROOT/name).read_text('utf-8')
    for w in re.findall(r'/_vercel/image\?[^"\s]*?&amp;w=(\d+)&amp;q=(\d+)', text):
        wi,qi=map(int,w)
        if wi not in sizes: fail(f'{name}: image width {wi} not allowed by vercel.json')
        if qi not in qualities: fail(f'{name}: image quality {qi} not allowed by vercel.json')

# release.json must exactly describe critical bytes.
release=json.loads((ROOT/'release.json').read_text('utf-8'))
if release.get('release')!=RELEASE: fail('release.json release mismatch')
art=release.get('artifacts',{})
for rel, expected in art.items():
    p=ROOT/rel
    if not p.is_file(): fail(f'release artifact missing: {rel}')
    actual=sha(p)
    if actual!=expected: fail(f'release hash mismatch: {rel}: {actual} != {expected}')

print(f'PASS: Freedom Book {RELEASE}; {len(EXPECTED_HTML)} editorial HTML; {len(books)} books; {len(urls)} sitemap routes')
