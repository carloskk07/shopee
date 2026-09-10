#!/usr/bin/env python3
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
def fail(msg): raise SystemExit(msg)
cfg=json.loads((ROOT/'monetization.json').read_text(encoding='utf-8'))
if cfg.get('schema')!='freedom-book-monetization-v1': fail('bad monetization schema')
if cfg.get('enabled') is not True: fail('monetization control plane unexpectedly disabled')
support=cfg.get('support') or {}
if support.get('enabled') is not True: fail('support must be active')
if support.get('url')!='https://livepix.gg/editorafreedombook': fail('unapproved support URL')
if set(support.get('pageTypes') or [])!={'home','book','guide','guides','author'}: fail('support page type contract drift')
affiliates=cfg.get('affiliates') or {}; premium=cfg.get('premium') or {}
if affiliates.get('enabled') is not False or affiliates.get('offers')!=[]: fail('affiliate offers must remain dormant until real URLs exist')
if premium.get('enabled') is not False or premium.get('offers')!=[]: fail('premium offers must remain dormant until real products exist')
if len(affiliates.get('disclosure',''))<80: fail('affiliate disclosure too weak')
guards=cfg.get('guardrails') or {}
required_true=('progressiveEnhancement','neverBeforeMainContent','neverNearPdfDownloadControls','noPopups','noInterstitials','noCountdowns','noAutoplay','noThirdPartyScripts','recommendOnlyWhenRelevant')
if any(guards.get(k) is not True for k in required_true): fail('monetization guardrail disabled')
if guards.get('affiliateRel')!='sponsored noopener noreferrer': fail('affiliate rel contract drift')
if int(guards.get('maxInjectedBlocksPerPage',99))>2: fail('too many commercial blocks allowed')
js=(ROOT/'assets/monetization.v1.js').read_text(encoding='utf-8')
if len(js.encode())>12*1024: fail('monetization JS exceeds 12 KiB budget')
for banned in ('innerHTML','document.write','eval(','localStorage','document.cookie','googletagmanager.com','analytics.tiktok.com'):
    if banned in js: fail(f'unsafe monetization JS token: {banned}')
for required in ('sponsored noopener noreferrer','dataset.monetizationSlot','fetch(CONFIG_URL','affiliate_open','premium_open','support_open'):
    if required not in js: fail(f'monetization JS contract missing: {required}')
app=(ROOT/'assets/app.v2.2.5.js').read_text(encoding='utf-8')
if 'e.target.closest("[data-track]")' not in app: fail('delegated analytics contract missing')
release=json.loads((ROOT/'release.json').read_text(encoding='utf-8')); artifacts=release.get('artifacts',{})
for public in ('assets/monetization.v1.js','monetization.json'):
    if public not in artifacts: fail(f'monetization public artifact missing from release: {public}')
editorial=0
for rel in artifacts:
    if not rel.endswith('.html'): continue
    html=(ROOT/rel).read_text(encoding='utf-8'); m=re.search(r'<body[^>]*data-page-type="([^"]+)"',html); ptype=m.group(1) if m else ''
    if ptype in {'home','book','guide','guides','author'}:
        editorial+=1
        if html.count('/assets/monetization.v1.js')!=1: fail(f'monetization loader count invalid: {rel}')
if editorial<10: fail(f'unexpectedly small monetizable editorial surface: {editorial}')
print(f'PASS: monetization control plane is support-first, progressive, policy-safe and loaded on {editorial} editorial pages')
