#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, pathlib, re

ROOT=pathlib.Path(__file__).resolve().parents[1]
MAIN_CSS='/assets/style.v2.2.5.css'
COVER_CSS='/assets/cover-integrity.v1.css'
EXPECTED_HTML={
 'index.html','404.html','autor-arthur-magnus.html','a-vida-que-voce-adiou.html','codigo-da-vida-inabalavel.html',
 'disciplina-e-liberdade.html','foco-que-gera-resultados.html','mente-forte-vida-leve.html','o-cansaco-invisivel.html',
 'o-metodo-da-vida-mais-leve.html','o-peso-de-ser-forte-o-tempo-todo.html','privacidade.html','proposito-maior.html',
 'quando-sua-vida-virou-sobrevivencia.html','recomecos-sao-escolhas.html','termos.html'
}

cover_css='''/* Freedom Book cover integrity v1 — preserve the complete original artwork. */
.book-cover{min-height:390px;align-items:center;justify-items:center}
.book-cover img{width:auto!important;max-width:min(100%,240px)!important;height:auto!important;max-height:360px;aspect-ratio:auto!important;object-fit:contain!important;object-position:center!important;background:#050505}
.featured-cover{min-height:430px;align-items:center;justify-items:center}
.featured-cover img{width:auto!important;max-width:min(100%,280px)!important;height:auto!important;max-height:420px;aspect-ratio:auto!important;object-fit:contain!important;object-position:center!important;background:#050505}
.book-hero-cover{align-self:stretch;min-height:500px;align-items:center;justify-items:center}
.book-hero-cover img{width:auto!important;max-width:min(100%,320px)!important;height:auto!important;max-height:560px;aspect-ratio:auto!important;object-fit:contain!important;object-position:center!important;background:#050505}
.status{z-index:2}
@media(max-width:760px){
  .book-cover{min-height:350px;padding:16px}
  .book-cover img{max-width:min(100%,220px)!important;max-height:330px}
  .featured-cover,.book-hero-cover{min-height:0}
  .featured-cover img{max-width:min(78vw,280px)!important;max-height:none}
  .book-hero-cover img{max-width:min(80vw,320px)!important;max-height:none}
}
@media(max-width:390px){
  .book-cover{min-height:320px}
  .book-cover img{max-width:min(100%,200px)!important;max-height:300px}
}
'''
(ROOT/COVER_CSS.lstrip('/')).write_text(cover_css,encoding='utf-8')

link=f'<link href="{COVER_CSS}" rel="stylesheet"/>'
style_re=re.compile(r'<link\b(?=[^>]*\bhref="/assets/style\.v2\.2\.5\.css")(?=[^>]*\brel="stylesheet")[^>]*/?>',re.I)
for name in sorted(EXPECTED_HTML):
    p=ROOT/name
    text=p.read_text('utf-8')
    if COVER_CSS not in text:
        m=style_re.search(text)
        if not m:
            raise SystemExit(f'{name}: main stylesheet link not found')
        text=text[:m.end()]+link+text[m.end():]
    def clean_cover_tag(m):
        tag=m.group(0)
        if '/assets/covers/capa-' not in tag:
            return tag
        tag=re.sub(r'\s+(?:width|height)="[0-9]+"','',tag,flags=re.I)
        return tag
    text=re.sub(r'<img\b[^>]*>',clean_cover_tag,text,flags=re.I)
    p.write_text(text,encoding='utf-8')

# Update permanent validator with a dedicated cover-integrity contract.
vp=ROOT/'scripts/validate_site.py'
v=vp.read_text('utf-8')
if "COVER_CSS='/assets/cover-integrity.v1.css'" not in v:
    v=v.replace("JS='/assets/app.v2.2.5.js'", "JS='/assets/app.v2.2.5.js'\nCOVER_CSS='/assets/cover-integrity.v1.css'",1)
    v=v.replace("if CSS not in text or JS not in text:fail(f'{name}: not using V2.2.5 versioned assets')",
                "if CSS not in text or JS not in text or COVER_CSS not in text:fail(f'{name}: active stylesheet/runtime contract missing')",1)
    anchor="if 'book-card:first-child' in css:fail('positional featured styling reintroduced')"
    extra="""if 'book-card:first-child' in css:fail('positional featured styling reintroduced')\n\ncover_css=(ROOT/COVER_CSS.lstrip('/')).read_text('utf-8')\nfor marker in ('Freedom Book cover integrity v1','.book-cover img','.featured-cover img','.book-hero-cover img','object-fit:contain','aspect-ratio:auto'):\n    if marker not in cover_css:fail(f'cover-integrity CSS contract missing: {marker}')\nfor name in sorted(EXPECTED_HTML):\n    text=(ROOT/name).read_text('utf-8')\n    for tag in re.findall(r'<img\\b[^>]*>',text,re.I):\n        if '/assets/covers/capa-' in tag and re.search(r'\\s(?:width|height)=',tag,re.I):\n            fail(f'{name}: hard-coded cover dimensions can reintroduce aspect-ratio cropping')\n"""
    if anchor not in v: raise SystemExit('validator CSS anchor not found')
    v=v.replace(anchor,extra,1)
    old="for required in ('index.html','autor-arthur-magnus.html','feed.xml','sitemap.xml','assets/style.v2.2.5.css','assets/app.v2.2.5.js','deploy-marker.json'):"
    new="for required in ('index.html','autor-arthur-magnus.html','feed.xml','sitemap.xml','assets/style.v2.2.5.css','assets/cover-integrity.v1.css','assets/app.v2.2.5.js','deploy-marker.json'):"
    if old not in v: raise SystemExit('validator release-surface anchor not found')
    v=v.replace(old,new,1)
vp.write_text(v,encoding='utf-8')

# Update maintenance provenance so post-deploy smoke waits for this campaign too.
marker={
 'schema':'achadostube-maintenance-marker-v1',
 'campaign':'cover-integrity-v1',
 'version':2,
 'source':'main',
 'origin':'https://achadostube.com.br/'
}
(ROOT/'maintenance-marker.json').write_text(json.dumps(marker,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Document the rendering contract.
rp=ROOT/'README.md'
r=rp.read_text('utf-8')
section='''\n## Integridade visual das capas\n\nAs capas editoriais nunca podem ser recortadas para preencher um quadro. `assets/cover-integrity.v1.css` preserva a proporção natural da arte com `object-fit: contain` e remove dependência de `aspect-ratio: 2/3` nas superfícies de catálogo, destaque e landing individual. Os HTMLs editoriais também não fixam `width`/`height` nas capas, evitando que metadados antigos imponham uma proporção incorreta.\n'''
if '## Integridade visual das capas' not in r:
    r=r.replace('\n## Estratégia de cache\n',section+'\n## Estratégia de cache\n',1)
rp.write_text(r,encoding='utf-8')

# Recompute the cryptographic release surface after the HTML changes and add the new CSS.
relp=ROOT/'release.json'
rel=json.loads(relp.read_text('utf-8'))
art=rel.setdefault('artifacts',{})
art['assets/cover-integrity.v1.css']=''
for path in sorted(art):
    p=ROOT/path
    if not p.is_file(): raise SystemExit(f'release artifact missing while hashing: {path}')
    art[path]=hashlib.sha256(p.read_bytes()).hexdigest()
relp.write_text(json.dumps(rel,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')

print('Cover integrity applied to',len(EXPECTED_HTML),'editorial HTML files')
print('Release artifacts:',len(art))
