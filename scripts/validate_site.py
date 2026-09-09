#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os, pathlib, re
from html.parser import HTMLParser
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

ROOT=pathlib.Path(__file__).resolve().parents[1]
RELEASE='2026.09.08-v2.2.5'
CANON='https://achadostube.com.br'
CSS='/assets/style.v2.2.5.css'
JS='/assets/app.v2.2.5.js'
COVER_CSS='/assets/cover-integrity.v1.css'
EXPECTED_HTML={
 'index.html','404.html','autor-arthur-magnus.html','a-vida-que-voce-adiou.html','codigo-da-vida-inabalavel.html',
 'disciplina-e-liberdade.html','foco-que-gera-resultados.html','mente-forte-vida-leve.html','o-cansaco-invisivel.html',
 'o-metodo-da-vida-mais-leve.html','o-peso-de-ser-forte-o-tempo-todo.html','privacidade.html','proposito-maior.html',
 'quando-sua-vida-virou-sobrevivencia.html','recomecos-sao-escolhas.html','termos.html'
}

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.ids=[]; self.h1=0; self.canon=[]; self.scripts=[]; self.release=[]; self.handlers=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='h1':self.h1+=1
        if tag=='link' and a.get('rel')=='canonical':self.canon.append(a.get('href',''))
        if tag=='script':self.scripts.append(a)
        if tag=='meta' and a.get('name')=='freedom-book-release':self.release.append(a.get('content',''))
        for k in a:
            if k.lower().startswith('on'):self.handlers.append(k)

def fail(msg): raise SystemExit(msg)
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def target_for(path):
    p=path.rstrip('/')
    if not p:return ROOT/'index.html'
    q=ROOT/(p.lstrip('/')+'.html')
    return q if q.exists() else ROOT/p.lstrip('/')

for name in sorted(EXPECTED_HTML):
    p=ROOT/name
    if not p.is_file() or p.stat().st_size==0:fail(f'missing editorial HTML: {name}')

seen={}
for name in sorted(EXPECTED_HTML):
    text=(ROOT/name).read_text('utf-8'); p=Parser(); p.feed(text)
    if 'https://www.achadostube.com.br' in text:fail(f'obsolete www canonical: {name}')
    if '/_vercel/image' in text:fail(f'Vercel-only endpoint: {name}')
    if len(p.ids)!=len(set(p.ids)):fail(f'duplicate id: {name}')
    if p.h1!=1:fail(f'{name}: expected one h1, got {p.h1}')
    if p.handlers:fail(f'{name}: inline handlers forbidden')
    if p.release!=[RELEASE]:fail(f'{name}: release mismatch {p.release}')
    if '#050505' not in text:fail(f'{name}: theme-color drift from active visual palette')
    if '/assets/favicon.ico' not in text or '/manifest.webmanifest' not in text:fail(f'{name}: browser/PWA identity assets missing')
    if 'fonts.googleapis.com' not in text:fail(f'{name}: typography contract missing')
    if 'id="consentBanner"' not in text or 'id="cookiePrefs"' not in text:fail(f'{name}: consent controls missing')
    if name!='404.html':
        if len(p.canon)!=1 or not p.canon[0].startswith(CANON):fail(f'{name}: canonical invalid {p.canon}')
        c=p.canon[0]
        if c in seen:fail(f'duplicate canonical: {c}')
        seen[c]=name
    if CSS not in text or JS not in text or COVER_CSS not in text:fail(f'{name}: active stylesheet/runtime contract missing')
    if '/assets/style.v2.2.4.css' in text or '/assets/app.v2.2.4.js' in text or '/assets/style.v2.2.3.css' in text or '/assets/app.v2.2.3.js' in text or '/assets/style.v2.2.css' in text or '/assets/app.v2.2.js' in text:
        fail(f'{name}: stale active asset reference')
    if 'gtag/js?id=' in text or 'analytics.tiktok.com' in text:fail(f'{name}: static tracker before consent')
    for s in p.scripts:
        src=s.get('src','')
        if 'googletagmanager.com' in src or 'analytics.tiktok.com' in src:fail(f'{name}: tracker embedded')
    for m in re.finditer(r'<script\s+type="application/ld\+json">(.*?)</script>',text,re.S|re.I):
        try:json.loads(m.group(1))
        except Exception as e:fail(f'{name}: invalid JSON-LD: {e}')
    for src in re.findall(r'<img\b[^>]*\bsrc="(/[^"]+)"',text,re.I):
        q=ROOT/urlparse(src).path.lstrip('/')
        if not q.is_file() or q.stat().st_size==0:fail(f'{name}: missing image {src}')

home=(ROOT/'index.html').read_text('utf-8')
if home.count('data-book-card')!=11:fail('home must contain 11 catalog cards')
if 'href="/autor-arthur-magnus"' not in home:fail('author internal discovery link missing')
if 'autor-arthur-magnus#person' not in home:fail('home author entity missing')
if 'Códigos de Vida · Códigos de Vida' in home:fail('duplicated upcoming taxonomy label')

css=(ROOT/CSS.lstrip('/')).read_text('utf-8')
for marker in ('V2.2.2 mobile performance hardening','content-visibility:auto','prefers-reduced-motion:reduce','V2.2.3 discovery/cache hardening','Freedom Book V2.2.4 — contextual premium editorial system','Freedom Book V2.2.5 — error-correction hardening'):
    if marker not in css:fail(f'CSS contract missing: {marker}')
if 'book-card:first-child' in css:fail('positional featured styling reintroduced')

cover_css=(ROOT/COVER_CSS.lstrip('/')).read_text('utf-8')
for marker in ('Freedom Book cover integrity v1','.book-cover img','.featured-cover img','.book-hero-cover img','object-fit:contain','aspect-ratio:auto'):
    if marker not in cover_css:fail(f'cover-integrity CSS contract missing: {marker}')
for name in sorted(EXPECTED_HTML):
    text=(ROOT/name).read_text('utf-8')
    for tag in re.findall(r'<img\b[^>]*>',text,re.I):
        if '/assets/covers/capa-' in tag and re.search(r'\s(?:width|height)=',tag,re.I):
            fail(f'{name}: hard-coded cover dimensions can reintroduce aspect-ratio cropping')


js=(ROOT/JS.lstrip('/')).read_text('utf-8')
for marker in (f'release:"{RELEASE}"','coarseTrafficSource','traffic_source','catalog_search','query_length','result_count'):
    if marker not in js:fail(f'JS funnel contract missing: {marker}')
if 'utm_source' in js or 'utm_medium' in js or 'utm_campaign' in js:fail('raw UTM capture is forbidden')
if 'search?.addEventListener("change"' in js:fail('duplicate catalog search analytics listener reintroduced')
if 'clearOptionalCookies' not in js:fail('optional-cookie revocation cleanup missing')

# Catalog and PDF truth.
data=json.loads((ROOT/'site-data.generated.json').read_text('utf-8'))
if data.get('site',{}).get('release')!=RELEASE:fail('site-data release mismatch')
if data.get('site',{}).get('logo')!=CANON+'/assets/covers/logo-freedom-book-redonda.webp':fail('site-data optimized logo drift')
books=data.get('books',[])
if len(books)!=11:fail(f'expected 11 books, got {len(books)}')
slugs=[b['slug'] for b in books]
if len(slugs)!=len(set(slugs)):fail('duplicate book slug')
available=[b for b in books if b.get('available')]
if len(available)!=10:fail(f'expected 10 available books, got {len(available)}')
for b in books:
    slug=b['slug']; page=ROOT/f'{slug}.html'
    if not page.is_file():fail(f'missing book page {slug}')
    title=b.get('title','').strip()
    if title and title not in home:fail(f'home catalog missing real title: {title}')
    if b.get('available'):
        expected_cover=CANON+f'/assets/covers/capa-{slug}.webp'
        if b.get('cover')!=expected_cover:fail(f'{slug}: site-data optimized cover drift')
        pdf=b.get('pdfUrl','')
        if not pdf.startswith(CANON+'/ebook/') or not pdf.endswith('.pdf'):fail(f'{slug}: bad PDF URL')
        local=ROOT/'ebook'/pathlib.PurePosixPath(urlparse(pdf).path).name
        if not local.is_file():
            if not (os.environ.get('ALLOW_MISSING_EBOOK_DIR')=='1' and not (ROOT/'ebook').exists()):fail(f'{slug}: PDF missing')
        elif local.stat().st_size<1024 or local.open('rb').read(5)!=b'%PDF-':fail(f'{slug}: invalid PDF')
        text=page.read_text('utf-8')
        preload=f'<link href="/assets/covers/capa-{slug}.webp" rel="preload" as="image" type="image/webp" fetchpriority="high"/>'
        if preload not in text:fail(f'{slug}: LCP preload missing')
        if 'autor-arthur-magnus#person' not in text:fail(f'{slug}: author entity link missing')
    elif b.get('pdfUrl'):fail(f'{slug}: unavailable book advertises PDF')

# Author page must remain contextual: identity mark, not a synthetic portrait or invented social proof.
author=(ROOT/'autor-arthur-magnus.html').read_text('utf-8')
if '/assets/covers/logo-freedom-book-redonda.webp' not in author:fail('author identity mark missing')
for invented in ('Avaliação dos leitores','depoimentos de leitores','newsletter exclusiva'):
    if invented.lower() in author.lower() or invented.lower() in home.lower():fail(f'invented editorial claim detected: {invented}')

# Sitemap + image discovery truth.
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9','i':'http://www.google.com/schemas/sitemap-image/1.1'}
root=ET.parse(ROOT/'sitemap.xml').getroot(); nodes=root.findall('s:url',ns)
urls=[n.find('s:loc',ns).text.strip() for n in nodes]
expected={CANON+'/',CANON+'/autor-arthur-magnus'}|{b['pageUrl'] for b in available}
if set(urls)!=expected or len(urls)!=len(expected):fail(f'sitemap routes mismatch: {urls}')
for n in nodes:
    loc=n.find('s:loc',ns).text.strip(); u=urlparse(loc)
    if u.scheme!='https' or u.netloc!='achadostube.com.br':fail(f'bad sitemap URL {loc}')
    t=target_for(u.path)
    if not t.is_file() or t.stat().st_size==0:fail(f'sitemap target missing {loc}')
    if loc not in {CANON+'/',CANON+'/autor-arthur-magnus'}:
        im=n.find('i:image',ns)
        if im is None or not im.find('i:loc',ns).text.endswith('.webp'):fail(f'image sitemap missing for {loc}')
if CANON+'/codigo-da-vida-inabalavel' in urls:fail('upcoming noindex route in sitemap')

# Atom discovery feed must represent the available catalog, no phantom entries.
atom={'a':'http://www.w3.org/2005/Atom'}
feed=ET.parse(ROOT/'feed.xml').getroot(); entries=feed.findall('a:entry',atom)
if len(entries)!=len(available):fail(f'feed entry count mismatch: {len(entries)}')
feed_ids={e.find('a:id',atom).text.strip() for e in entries}
if feed_ids!={b['pageUrl'] for b in available}:fail('feed/catalog URL mismatch')

# Static media/PWA truth.
cover_dir=ROOT/'assets/covers'
for cover in {f'capa-{b["slug"]}.webp' for b in available}|{'logo-freedom-book-redonda.webp'}:
    p=cover_dir/cover
    if not p.is_file() or p.stat().st_size<1024:fail(f'invalid optimized cover {cover}')
manifest=json.loads((ROOT/'manifest.webmanifest').read_text('utf-8'))
if manifest.get('background_color')!='#050505' or manifest.get('theme_color')!='#050505':fail('manifest theme palette drift')
expected_icons={'/assets/icons/icon-192.png':('192x192','any'),'/assets/icons/icon-512.png':('512x512','any'),'/assets/icons/maskable-512.png':('512x512','maskable')}
actual={i.get('src'):(i.get('sizes'),i.get('purpose')) for i in manifest.get('icons',[])}
if actual!=expected_icons:fail(f'manifest icons mismatch {actual}')
for src in expected_icons:
    p=ROOT/src.lstrip('/')
    if not p.is_file() or p.stat().st_size<1024:fail(f'invalid PWA icon {src}')
if not (ROOT/'assets/icons/apple-touch-icon.png').is_file():fail('missing apple-touch-icon')

# Cryptographic release surface must include active versioned assets and match bytes exactly.
release=json.loads((ROOT/'release.json').read_text('utf-8'))
if release.get('release')!=RELEASE:fail('release.json release mismatch')
art=release.get('artifacts',{})
for required in ('index.html','autor-arthur-magnus.html','feed.xml','sitemap.xml','assets/style.v2.2.5.css','assets/cover-integrity.v1.css','assets/app.v2.2.5.js','deploy-marker.json'):
    if required not in art:fail(f'release surface missing {required}')
if any(x in art for x in ('assets/style.v2.2.4.css','assets/app.v2.2.4.js','assets/style.v2.2.3.css','assets/app.v2.2.3.js')):fail('release surface still contains prior active version assets')
if len(art)<38:fail(f'release surface unexpectedly small: {len(art)}')
for rel,expected_hash in art.items():
    p=ROOT/rel
    if not p.is_file():fail(f'release artifact missing {rel}')
    actual_hash=sha(p)
    if actual_hash!=expected_hash:fail(f'release hash mismatch {rel}: {actual_hash} != {expected_hash}')



# Public legacy surface integrity: preserve traffic without stale prices, fabricated urgency or pre-consent tracking.
LEGACY_OFFERS={
    'kit-3-pares.html':CANON+'/kit-3-pares',
    'kit-sandalias-infantil.html':CANON+'/kit-sandalias-infantil',
}
for name,canonical in LEGACY_OFFERS.items():
    text=(ROOT/name).read_text('utf-8'); p=Parser(); p.feed(text)
    if p.h1!=1:fail(f'{name}: legacy offer must have exactly one h1')
    if p.canon!=[canonical]:fail(f'{name}: legacy canonical mismatch {p.canon}')
    if '/assets/legacy-offer.v1.css' not in text or '/assets/legacy-consent.v1.js' not in text:fail(f'{name}: legacy shared assets missing')
    if 'googletagmanager.com/gtag/js' in text or 'analytics.tiktok.com' in text:fail(f'{name}: static tracker before consent')
    if 'R$' in text:fail(f'{name}: stale static price reintroduced')
    for bad in ('vendidos hoje','unidades restantes','estoque quase zerado','estão vendo esta oferta agora','mães reais','oferta relâmpago','últimas unidades','garantia 30 dias'):
        if bad in text.lower():fail(f'{name}: unsupported urgency/social-proof claim reintroduced: {bad}')
    if re.search(r"ttq\.track\(['\"]Purchase",text,re.I) or re.search(r"gtag\(['\"]event['\"],\s*['\"]purchase",text,re.I):fail(f'{name}: click-to-purchase telemetry reintroduced')
    links=re.findall(r'<a\b[^>]*href="https://s\.shopee\.com\.br/[^"]+"[^>]*>',text,re.I)
    if not links:fail(f'{name}: affiliate destination missing')
    for tag in links:
        m=re.search(r'rel="([^"]+)"',tag,re.I)
        rel=set((m.group(1) if m else '').lower().split())
        if not {'sponsored','noopener','noreferrer'}<=rel:fail(f'{name}: affiliate rel contract missing {tag}')

legacy_js=(ROOT/'assets/legacy-consent.v1.js').read_text('utf-8')
for marker in ('freedom_book_consent_v2','affiliate_click','ClickButton','clearOptionalCookies'):
    if marker not in legacy_js:fail(f'legacy consent contract missing: {marker}')
if 'Purchase' in legacy_js:fail('legacy consent runtime must never synthesize purchase events')

# Duplicate/obsolete routes are kept as safe noindex redirects, never as parallel indexable surfaces.
redirect_contracts={
    'kit-tenis-sandalia.html':(CANON+'/kit-3-pares','/kit-3-pares'),
    'leitor.html':(CANON+'/o-cansaco-invisivel','/o-cansaco-invisivel'),
    'locked/the_select.html':(CANON+'/','/'),
}
for name,(canonical,target) in redirect_contracts.items():
    text=(ROOT/name).read_text('utf-8').lower()
    if 'noindex' not in text:fail(f'{name}: obsolete route must be noindex')
    if canonical.lower() not in text or f'url={target}'.lower() not in text:fail(f'{name}: redirect target mismatch')
    if 'googletagmanager.com' in text or 'analytics.tiktok.com' in text:fail(f'{name}: tracker must not load on redirect')
if 'o_cansaco_invisivel.pdf' in (ROOT/'leitor.html').read_text('utf-8'):fail('broken legacy reader PDF path reintroduced')
if 'theselect.com.br' in (ROOT/'locked/the_select.html').read_text('utf-8') or 'example.com' in (ROOT/'locked/the_select.html').read_text('utf-8'):fail('locked placeholder identity/data reintroduced')

# Documentation and maintenance deploy marker must describe the actual production state.
readme=(ROOT/'README.md').read_text('utf-8')
for required in ('Freedom Book V2.2.5','assets/style.v2.2.5.css','assets/app.v2.2.5.js','assets/legacy-consent.v1.js'):
    if required not in readme:fail(f'README production truth missing: {required}')
for stale in ('Freedom Book V2.2.3','assets/style.v2.2.3.css` — CSS ativo','assets/app.v2.2.3.js` — runtime ativo'):
    if stale in readme:fail(f'README stale current-version statement: {stale}')
maintenance=json.loads((ROOT/'maintenance-marker.json').read_text('utf-8'))
expected_maintenance={'schema':'achadostube-maintenance-marker-v1','campaign':'cover-integrity-v1','version':2,'source':'main','origin':CANON+'/'}
if maintenance!=expected_maintenance:fail(f'maintenance marker mismatch: {maintenance}')

print(f'PASS: Freedom Book {RELEASE}; {len(EXPECTED_HTML)} editorial HTML; {len(available)} available books; {len(urls)} sitemap routes; {len(entries)} feed entries; {len(art)} release artifacts')
