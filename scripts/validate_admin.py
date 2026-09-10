#!/usr/bin/env python3
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
ADMIN=ROOT/'admin'
def fail(msg): raise SystemExit(msg)
for rel in ('admin/index.html','admin/style.css','admin/app.js','admin/release.json'):
    p=ROOT/rel
    minimum=100 if rel.endswith('release.json') else 500
    if not p.is_file() or p.stat().st_size<minimum: fail(f'missing/undersized admin asset: {rel}')
html=(ADMIN/'index.html').read_text(encoding='utf-8')
js=(ADMIN/'app.js').read_text(encoding='utf-8')
css=(ADMIN/'style.css').read_text(encoding='utf-8')
for marker in ('noindex,nofollow,noarchive,nosnippet','Content-Security-Policy','/admin/app.js','/admin/style.css','Freedom Control Center'):
    if marker not in html: fail(f'admin HTML contract missing: {marker}')
for banned in ('googletagmanager.com','analytics.tiktok.com','<script src="http','localStorage.setItem','document.cookie'):
    if banned in html+js: fail(f'admin unsafe/persistence token: {banned}')
for marker in ("state={token:null","state.token=token","state.token=null","/git/refs","/git/trees","/git/commits","/pulls","release.json","crypto.subtle.digest","sessionStorage.getItem('freedom-gsc-v1')"):
    if marker not in js: fail(f'admin runtime contract missing: {marker}')
if '.github/workflows/' not in js or "path.startsWith('.github/')" not in js: fail('admin workflow editing guard missing')
if 'Authorization' not in js or 'Bearer ${state.token}' not in js: fail('admin GitHub auth contract missing')
if 'tokenInput' not in html or 'autocomplete="off"' not in html: fail('admin token UX contract missing')
if '@media(max-width:760px)' not in css: fail('admin mobile contract missing')
release=json.loads((ADMIN/'release.json').read_text(encoding='utf-8'))
if release.get('schema')!='freedom-admin-release-v1': fail('bad admin release schema')
art=release.get('artifacts',{})
import hashlib
for rel in ('index.html','style.css','app.js'):
    p=ADMIN/rel
    if rel not in art: fail(f'admin asset not release-managed: {rel}')
    actual=hashlib.sha256(p.read_bytes()).hexdigest()
    if actual!=art[rel]: fail(f'admin release hash mismatch: {rel}')
sitemap=(ROOT/'sitemap.xml').read_text(encoding='utf-8')
if '/admin' in sitemap: fail('admin must not enter sitemap')
print('PASS: Freedom Control Center is noindex, mobile-first, release-managed, PR-only and does not persist GitHub credentials')
