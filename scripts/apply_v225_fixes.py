#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
OLD_RELEASE = '2026.09.08-v2.2.4'
NEW_RELEASE = '2026.09.08-v2.2.5'
OLD_CSS = '/assets/style.v2.2.4.css'
NEW_CSS = '/assets/style.v2.2.5.css'
OLD_JS = '/assets/app.v2.2.4.js'
NEW_JS = '/assets/app.v2.2.5.js'
CANON = 'https://achadostube.com.br'

HTMLS = [
    'index.html', '404.html', 'autor-arthur-magnus.html', 'privacidade.html', 'termos.html',
    'codigo-da-vida-inabalavel.html', 'proposito-maior.html', 'recomecos-sao-escolhas.html',
    'foco-que-gera-resultados.html', 'mente-forte-vida-leve.html', 'disciplina-e-liberdade.html',
    'o-metodo-da-vida-mais-leve.html', 'o-cansaco-invisivel.html',
    'quando-sua-vida-virou-sobrevivencia.html', 'a-vida-que-voce-adiou.html',
    'o-peso-de-ser-forte-o-tempo-todo.html',
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding='utf-8')


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


# 1) Versioned active assets.
shutil.copyfile(ROOT / 'assets/style.v2.2.4.css', ROOT / 'assets/style.v2.2.5.css')
with (ROOT / 'assets/style.v2.2.5.css').open('a', encoding='utf-8') as f:
    f.write('\n/* Freedom Book V2.2.5 — error-correction hardening */\n')
    f.write('body::before{-webkit-mask-image:radial-gradient(circle at 50% 12%,#000,transparent 72%)}\n')
shutil.copyfile(ROOT / 'assets/app.v2.2.4.js', ROOT / 'assets/app.v2.2.5.js')

# 2) Coherent release/assets/theme across all active editorial HTML.
for name in HTMLS:
    text = read(name)
    text = text.replace(OLD_RELEASE, NEW_RELEASE).replace(OLD_CSS, NEW_CSS).replace(OLD_JS, NEW_JS)
    text = text.replace('#050609', '#050505')
    write(name, text)

# 3) Visible taxonomy duplication and page-type telemetry.
write('index.html', read('index.html').replace('Códigos de Vida · Códigos de Vida', 'Códigos de Vida · Próximo lançamento'))
for name, page_type in {
    '404.html': '404',
    'privacidade.html': 'legal',
    'termos.html': 'legal',
    'codigo-da-vida-inabalavel.html': 'coming_soon',
}.items():
    text = read(name)
    if '<body>' in text:
        text = text.replace('<body>', f'<body data-page-type="{page_type}">', 1)
    write(name, text)

# 4) Author page parity: typography/PWA/social metadata, self-contained entity, footer and consent.
author = read('autor-arthur-magnus.html')
canonical = '<link rel="canonical" href="https://achadostube.com.br/autor-arthur-magnus"/>'
script_marker = '<script type="application/ld+json">'
require(canonical in author and script_marker in author, 'author head anchors missing')
ci = author.index(canonical) + len(canonical)
si = author.index(script_marker, ci)
head_extra = ''.join([
    '<link href="https://fonts.googleapis.com" rel="preconnect"/>',
    '<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>',
    '<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&amp;family=Inter:wght@400;600;700;800;900&amp;display=swap" rel="stylesheet"/>',
    '<link rel="stylesheet" href="/assets/style.v2.2.5.css"/>',
    '<link href="/assets/favicon.ico" rel="icon" sizes="any"/>',
    '<link href="/assets/icons/apple-touch-icon.png" rel="apple-touch-icon"/>',
    '<link rel="manifest" href="/manifest.webmanifest"/>',
    '<link rel="alternate" type="application/atom+xml" title="Freedom Book — novos e-books" href="/feed.xml"/>',
    '<meta content="pt_BR" property="og:locale"/>',
    '<meta content="profile" property="og:type"/>',
    '<meta content="Arthur Magnus — autor da Freedom Book" property="og:title"/>',
    '<meta content="Conheça Arthur Magnus, autor dos e-books publicados pela Freedom Book sobre propósito, foco, disciplina, recomeços, clareza mental e vida prática." property="og:description"/>',
    '<meta content="https://achadostube.com.br/autor-arthur-magnus" property="og:url"/>',
    '<meta content="Freedom Book" property="og:site_name"/>',
    '<meta content="https://achadostube.com.br/og/freedom-book-home.png" property="og:image"/>',
    '<meta content="Arthur Magnus — Freedom Book" property="og:image:alt"/>',
    '<meta content="summary_large_image" name="twitter:card"/>',
    '<meta content="Arthur Magnus — autor da Freedom Book" name="twitter:title"/>',
    '<meta content="Conheça Arthur Magnus, autor dos e-books publicados pela Freedom Book." name="twitter:description"/>',
    '<meta content="https://achadostube.com.br/og/freedom-book-home.png" name="twitter:image"/>',
])
author = author[:ci] + head_extra + author[si:]

m = re.search(r'<script type="application/ld\+json">(.*?)</script>', author, re.S)
require(m is not None, 'author JSON-LD missing')
structured = json.loads(m.group(1))
graph = structured.get('@graph', [])
if not any(isinstance(x, dict) and x.get('@id') == CANON + '/#organization' for x in graph):
    graph.insert(0, {'@type': 'Organization', '@id': CANON + '/#organization', 'name': 'Freedom Book', 'url': CANON + '/'})
structured['@graph'] = graph
author = author[:m.start(1)] + json.dumps(structured, ensure_ascii=False, separators=(',', ':')) + author[m.end(1):]

privacy = read('privacidade.html')
fs = privacy.index('<footer class="footer">')
fe = privacy.index('</footer>', fs) + len('</footer>')
footer = privacy[fs:fe]
afs = author.index('<footer class="footer">')
afe = author.index('</footer>', afs) + len('</footer>')
author = author[:afs] + footer + author[afe:]
cs = privacy.index('<div aria-label="Preferências de privacidade"')
ce = privacy.index('<div aria-live="polite"', cs)
consent_markup = privacy[cs:ce]
if 'id="consentBanner"' not in author:
    toast_i = author.index('<div id="toast"')
    author = author[:toast_i] + consent_markup + author[toast_i:]
write('autor-arthur-magnus.html', author)

# 5) Canonical data model uses optimized assets and non-duplicated badge metadata.
data_path = ROOT / 'site-data.generated.json'
data = json.loads(data_path.read_text(encoding='utf-8'))
data['site']['release'] = NEW_RELEASE
data['site']['logo'] = CANON + '/assets/covers/logo-freedom-book-redonda.webp'
for book in data.get('books', []):
    if book.get('slug') == 'codigo-da-vida-inabalavel':
        book['badge'] = 'Próximo lançamento'
    if book.get('available'):
        book['cover'] = CANON + f"/assets/covers/capa-{book['slug']}.webp"
data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# 6) PWA browser chrome matches the active premium palette.
manifest_path = ROOT / 'manifest.webmanifest'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['background_color'] = '#050505'
manifest['theme_color'] = '#050505'
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# 7) Runtime data-quality and consent-revocation fixes.
js_path = ROOT / 'assets/app.v2.2.5.js'
js = js_path.read_text(encoding='utf-8').replace(OLD_RELEASE, NEW_RELEASE)
duplicate = '    search?.addEventListener("change",()=>{const q=norm(search.value||"");if(q)track("catalog_search",{query_length:q.length,release:CONFIG.release})});\n'
require(duplicate in js, 'expected duplicate catalog search listener not found')
js = js.replace(duplicate, '')
anchor = '  let gaLoaded=false,tiktokLoaded=false,perfStarted=false;\n'
cleanup = '''  let gaLoaded=false,tiktokLoaded=false,perfStarted=false;\n  const OPTIONAL_COOKIE_PREFIXES=["_ga","_gcl_","_ttp","_tt_enable_cookie"];\n  const clearOptionalCookies=()=>{\n    const expired="Thu, 01 Jan 1970 00:00:00 GMT";\n    document.cookie.split(";").forEach(part=>{\n      const name=(part.split("=")[0]||"").trim();\n      if(!name||!OPTIONAL_COOKIE_PREFIXES.some(prefix=>name===prefix||name.startsWith(prefix)))return;\n      ["",location.hostname,`.`+location.hostname].forEach(domain=>{\n        document.cookie=`${name}=; expires=${expired}; Max-Age=0; path=/${domain?`; domain=${domain}`:""}`;\n      });\n    });\n  };\n'''
require(anchor in js, 'consent runtime anchor missing')
js = js.replace(anchor, cleanup, 1)
old_save = '''  function saveConsent(next){\n    const requiresReload=(gaLoaded&&!next.analytics)||(tiktokLoaded&&!next.marketing);\n    consent={analytics:!!next.analytics,marketing:!!next.marketing};storage.set(CONSENT_KEY,JSON.stringify(consent));\n'''
new_save = '''  function saveConsent(next){\n    const previous={...consent};\n    const requiresReload=(gaLoaded&&!next.analytics)||(tiktokLoaded&&!next.marketing);\n    consent={analytics:!!next.analytics,marketing:!!next.marketing};\n    if((previous.analytics&&!consent.analytics)||(previous.marketing&&!consent.marketing))clearOptionalCookies();\n    storage.set(CONSENT_KEY,JSON.stringify(consent));\n'''
require(old_save in js, 'saveConsent contract anchor missing')
js = js.replace(old_save, new_save, 1)
js_path.write_text(js, encoding='utf-8')

# 8) README release label where present.
write('README.md', read('README.md').replace(OLD_RELEASE, NEW_RELEASE))

# 9) Strengthen validator without weakening existing checks.
vp = ROOT / 'scripts/validate_site.py'
v = vp.read_text(encoding='utf-8')
v = v.replace("RELEASE='2026.09.08-v2.2.4'", "RELEASE='2026.09.08-v2.2.5'")
v = v.replace("CSS='/assets/style.v2.2.4.css'", "CSS='/assets/style.v2.2.5.css'")
v = v.replace("JS='/assets/app.v2.2.4.js'", "JS='/assets/app.v2.2.5.js'")
v = v.replace('not using V2.2.4 versioned assets', 'not using V2.2.5 versioned assets')
old_stale = "if '/assets/style.v2.2.3.css' in text or '/assets/app.v2.2.3.js' in text or '/assets/style.v2.2.css' in text or '/assets/app.v2.2.js' in text:\n        fail(f'{name}: stale active asset reference')"
new_stale = "if '/assets/style.v2.2.4.css' in text or '/assets/app.v2.2.4.js' in text or '/assets/style.v2.2.3.css' in text or '/assets/app.v2.2.3.js' in text or '/assets/style.v2.2.css' in text or '/assets/app.v2.2.js' in text:\n        fail(f'{name}: stale active asset reference')"
require(old_stale in v, 'validator stale-asset anchor missing')
v = v.replace(old_stale, new_stale, 1)
old_markers = "for marker in ('V2.2.2 mobile performance hardening','content-visibility:auto','prefers-reduced-motion:reduce','V2.2.3 discovery/cache hardening','Freedom Book V2.2.4 — contextual premium editorial system'):"
new_markers = "for marker in ('V2.2.2 mobile performance hardening','content-visibility:auto','prefers-reduced-motion:reduce','V2.2.3 discovery/cache hardening','Freedom Book V2.2.4 — contextual premium editorial system','Freedom Book V2.2.5 — error-correction hardening'):"
require(old_markers in v, 'validator CSS marker anchor missing')
v = v.replace(old_markers, new_markers, 1)
v = v.replace(
    "for required in ('index.html','autor-arthur-magnus.html','feed.xml','sitemap.xml','assets/style.v2.2.4.css','assets/app.v2.2.4.js','deploy-marker.json'):",
    "for required in ('index.html','autor-arthur-magnus.html','feed.xml','sitemap.xml','assets/style.v2.2.5.css','assets/app.v2.2.5.js','deploy-marker.json'):",
)
v = v.replace(
    "if 'assets/style.v2.2.3.css' in art or 'assets/app.v2.2.3.js' in art:fail('release surface still contains prior active version assets')",
    "if any(x in art for x in ('assets/style.v2.2.4.css','assets/app.v2.2.4.js','assets/style.v2.2.3.css','assets/app.v2.2.3.js')):fail('release surface still contains prior active version assets')",
)
page_anchor = "    if p.release!=[RELEASE]:fail(f'{name}: release mismatch {p.release}')\n"
page_guard = (
    "    if '#050505' not in text:fail(f'{name}: theme-color drift from active visual palette')\n"
    "    if '/assets/favicon.ico' not in text or '/manifest.webmanifest' not in text:fail(f'{name}: browser/PWA identity assets missing')\n"
    "    if 'fonts.googleapis.com' not in text:fail(f'{name}: typography contract missing')\n"
    "    if 'id=\"consentBanner\"' not in text or 'id=\"cookiePrefs\"' not in text:fail(f'{name}: consent controls missing')\n"
)
require(page_anchor in v, 'validator page-contract anchor missing')
v = v.replace(page_anchor, page_anchor + page_guard, 1)
home_anchor = "if 'autor-arthur-magnus#person' not in home:fail('home author entity missing')\n"
require(home_anchor in v, 'validator home anchor missing')
v = v.replace(home_anchor, home_anchor + "if 'Códigos de Vida · Códigos de Vida' in home:fail('duplicated upcoming taxonomy label')\n", 1)
site_data_anchor = "if data.get('site',{}).get('release')!=RELEASE:fail('site-data release mismatch')\n"
require(site_data_anchor in v, 'validator site-data anchor missing')
v = v.replace(site_data_anchor, site_data_anchor + "if data.get('site',{}).get('logo')!=CANON+'/assets/covers/logo-freedom-book-redonda.webp':fail('site-data optimized logo drift')\n", 1)
pdf_anchor = "        pdf=b.get('pdfUrl','')\n"
require(pdf_anchor in v, 'validator PDF anchor missing')
v = v.replace(pdf_anchor, "        expected_cover=CANON+f'/assets/covers/capa-{slug}.webp'\n        if b.get('cover')!=expected_cover:fail(f'{slug}: site-data optimized cover drift')\n" + pdf_anchor, 1)
utm_anchor = "if 'utm_source' in js or 'utm_medium' in js or 'utm_campaign' in js:fail('raw UTM capture is forbidden')\n"
require(utm_anchor in v, 'validator JS guard anchor missing')
v = v.replace(utm_anchor, utm_anchor + "if 'search?.addEventListener(\"change\"' in js:fail('duplicate catalog search analytics listener reintroduced')\nif 'clearOptionalCookies' not in js:fail('optional-cookie revocation cleanup missing')\n", 1)
manifest_anchor = "manifest=json.loads((ROOT/'manifest.webmanifest').read_text('utf-8'))\n"
require(manifest_anchor in v, 'validator manifest anchor missing')
v = v.replace(manifest_anchor, manifest_anchor + "if manifest.get('background_color')!='#050505' or manifest.get('theme_color')!='#050505':fail('manifest theme palette drift')\n", 1)
vp.write_text(v, encoding='utf-8')

# 10) CI and post-deploy smoke point to the new active assets and verify author parity.
si_path = ROOT / '.github/workflows/site-integrity.yml'
si = si_path.read_text(encoding='utf-8')
si = si.replace('assets/style.v2.2.4.css', 'assets/style.v2.2.5.css').replace('assets/app.v2.2.4.js', 'assets/app.v2.2.5.js')
old_tuple = "old=('/assets/style.v2.2.css','/assets/app.v2.2.js','/assets/style.v2.2.3.css','/assets/app.v2.2.3.js')"
new_tuple = "old=('/assets/style.v2.2.css','/assets/app.v2.2.js','/assets/style.v2.2.3.css','/assets/app.v2.2.3.js','/assets/style.v2.2.4.css','/assets/app.v2.2.4.js')"
require(old_tuple in si, 'site-integrity stale tuple anchor missing')
si = si.replace(old_tuple, new_tuple, 1)
si = si.replace('missing V2.2.4 asset reference', 'missing V2.2.5 asset reference').replace('V2.2.4 versioned asset references', 'V2.2.5 versioned asset references')
si_path.write_text(si, encoding='utf-8')

ps_path = ROOT / '.github/workflows/production-smoke.yml'
ps = ps_path.read_text(encoding='utf-8').replace('FreedomBook-Production-Smoke/2.2.4', 'FreedomBook-Production-Smoke/2.2.5')
ps = ps.replace('/assets/style.v2.2.4.css', '/assets/style.v2.2.5.css').replace('/assets/app.v2.2.4.js', '/assets/app.v2.2.5.js')
marker = "          ! grep -q '/assets/style.v2.2.3.css' /tmp/home.html\n"
require(marker in ps, 'production-smoke stale marker missing')
ps = ps.replace(marker, "          ! grep -q '/assets/style.v2.2.4.css' /tmp/home.html\n          ! grep -q '/assets/app.v2.2.4.js' /tmp/home.html\n" + marker, 1)
author_marker = "          grep -q '/assets/covers/logo-freedom-book-redonda.webp' /tmp/author.html\n"
require(author_marker in ps, 'production-smoke author marker missing')
ps = ps.replace(author_marker, author_marker + "          grep -q 'fonts.googleapis.com' /tmp/author.html\n          grep -q 'id=\"consentBanner\"' /tmp/author.html\n          grep -q 'id=\"cookiePrefs\"' /tmp/author.html\n          grep -q 'property=\"og:title\"' /tmp/author.html\n", 1)
ps_path.write_text(ps, encoding='utf-8')

# 11) Release authority: rotate active asset names and hash exact candidate bytes.
rp = ROOT / 'release.json'
release = json.loads(rp.read_text(encoding='utf-8'))
release['release'] = NEW_RELEASE
art = release.get('artifacts', {})
art.pop('assets/style.v2.2.4.css', None)
art.pop('assets/app.v2.2.4.js', None)
art['assets/style.v2.2.5.css'] = ''
art['assets/app.v2.2.5.js'] = ''
for rel in list(art):
    f = ROOT / rel
    require(f.is_file(), f'missing release artifact: {rel}')
    art[rel] = hashlib.sha256(f.read_bytes()).hexdigest()
release['artifacts'] = dict(sorted(art.items()))
rp.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

print('V2.2.5 correction candidate built successfully')
