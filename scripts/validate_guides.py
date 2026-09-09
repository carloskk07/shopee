#!/usr/bin/env python3
from __future__ import annotations
import json,re
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CANON='https://achadostube.com.br'
class Text(HTMLParser):
    def __init__(self):super().__init__();self.parts=[]
    def handle_data(self,d):self.parts.append(d)
def fail(m):raise SystemExit(m)
data=json.loads((ROOT/'site-data.generated.json').read_text('utf-8'));guides=data.get('guides',[])
if len(guides)!=6:fail(f'guide count {len(guides)} != 6')
for g in guides:
    p=ROOT/'guias'/f"{g['slug']}.html"; t=p.read_text('utf-8'); x=Text();x.feed(t); words=re.findall(r"[A-Za-zÀ-ÿ0-9]+",' '.join(x.parts))
    if len(words)<430:fail(f"{g['slug']}: thin guide ({len(words)} visible words)")
    if t.count('<h1')!=1:fail(f"{g['slug']}: h1 contract")
    if t.count('<h2')<5:fail(f"{g['slug']}: insufficient section depth")
    if 'Guia editorial da Freedom Book' not in t:fail(f"{g['slug']}: editorial provenance missing")
    for bad in ('garantia de resultado','ranking garantido','cura garantida','segredo que ninguém conta'):
        if bad in t.lower():fail(f"{g['slug']}: manipulative/unsafe claim: {bad}")
    for b in g.get('relatedBooks',[]):
        bt=(ROOT/f'{b}.html').read_text('utf-8')
        if f'href="/guias/{g["slug"]}"' not in bt:fail(f"{b}: reciprocal topical link missing")
hub=(ROOT/'guias.html').read_text('utf-8')
if hub.count('class="card guide-card"')!=6:fail('hub guide count')
if '/assets/editorial-guides.v1.css' not in hub:fail('hub guide stylesheet missing')
print('PASS: six substantial people-first guide pages, reciprocal book links and topical hub are coherent')
