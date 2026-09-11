#!/usr/bin/env python3
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
def fail(msg): raise SystemExit(msg)
cfg=json.loads((ROOT/'monetization.json').read_text(encoding='utf-8'))
if cfg.get('schema')!='freedom-book-monetization-v1': fail('bad monetization schema')
if cfg.get('enabled') is not True: fail('monetization control plane unexpectedly disabled')
intel=cfg.get('intelligence') or {}
if intel.get('version')!='2.0.0': fail('monetization intelligence version drift')
if intel.get('demandTruth')!='GSC_FINALIZED': fail('demand truth must remain finalized GSC')
if intel.get('interactionTruth')!='CONSENT_GATED_ANALYTICS': fail('interaction truth contract drift')
if intel.get('revenueTruth')!='PRIVATE_CONFIRMED_LEDGER_ONLY': fail('revenue truth contract drift')
if intel.get('missingRevenueSemantics')!='UNKNOWN_NOT_ZERO': fail('missing revenue cannot mean zero')
if intel.get('currencyPolicy')!='NO_IMPLICIT_FX_CONVERSION': fail('implicit FX conversion forbidden')
measurement=cfg.get('measurement') or {}
if measurement.get('privateRevenueLedger')!='netlify-blobs' or measurement.get('repositoryPersistence') is not False: fail('private revenue ledger boundary drift')
if set(measurement.get('trackedClicks') or [])!={'support_open','affiliate_open','premium_open'}: fail('public monetization click event contract drift')
support=cfg.get('support') or {}
if support.get('enabled') is not True: fail('support must be active')
if support.get('url')!='https://livepix.gg/editorafreedombook': fail('unapproved support URL')
if set(support.get('pageTypes') or [])!={'home','book','guide','guides','author'}: fail('support page type contract drift')
affiliates=cfg.get('affiliates') or {}; premium=cfg.get('premium') or {}; kdp=cfg.get('kdp') or {}; ads=cfg.get('ads') or {}
if affiliates.get('enabled') is not False or affiliates.get('offers')!=[]: fail('affiliate offers must remain dormant until real URLs exist')
if premium.get('enabled') is not False or premium.get('offers')!=[]: fail('premium offers must remain dormant until real products exist')
if kdp.get('enabled') is not False or kdp.get('offers')!=[]: fail('KDP must remain dormant until verified Amazon URLs exist')
if ads.get('enabled') is not False or ads.get('provider')!='': fail('ads must remain disabled until explicit evidence and provider approval')
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
if 'consent.analytics' not in app or 'consent.marketing' not in app: fail('monetization events must remain consent-gated')
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
print(f'PASS: Monetization Intelligence uses finalized demand, consented interactions and private confirmed revenue while commercial channels remain safely dormant on {editorial} editorial pages')
