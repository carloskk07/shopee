#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, pathlib

ROOT=pathlib.Path(__file__).resolve().parents[1]
vp=ROOT/'scripts/validate_site.py'
v=vp.read_text('utf-8')
old="for marker in ('Freedom Book cover integrity v1','.book-cover img','.featured-cover img','.book-hero-cover img','object-fit:contain','aspect-ratio:auto'):"
new="for marker in ('Freedom Book cover integrity v1','.book-cover img','.featured-cover img','.book-hero-cover img','.related-card img','object-fit:contain','aspect-ratio:auto'):"
if old in v:
    v=v.replace(old,new,1)
elif new not in v:
    raise SystemExit('cover marker tuple not found')
vp.write_text(v,encoding='utf-8')

relp=ROOT/'release.json'
rel=json.loads(relp.read_text('utf-8'))
art=rel.get('artifacts',{})
if 'assets/cover-integrity.v1.css' not in art:
    raise SystemExit('cover-integrity asset missing from release surface')
for path in sorted(art):
    p=ROOT/path
    if not p.is_file(): raise SystemExit(f'missing release artifact {path}')
    art[path]=hashlib.sha256(p.read_bytes()).hexdigest()
relp.write_text(json.dumps(rel,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
print('Cover contract refreshed:',len(art),'artifacts')
