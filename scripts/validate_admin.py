#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re

ROOT=Path(__file__).resolve().parents[1]
ADMIN=ROOT/'admin'

def fail(msg): raise SystemExit(msg)

def read(path): return (ROOT/path).read_text(encoding='utf-8')

required={
    'admin/index.html':1000,
    'admin/style.css':5000,
    'admin/app.js':15000,
    'admin/book-publisher.js':12000,
    'admin/control-plane.json':500,
    'admin/release.json':100,
    'admin/README.md':500,
    'scripts/test_admin_v2.js':500,
}
for rel,minimum in required.items():
    p=ROOT/rel
    if not p.is_file() or p.stat().st_size<minimum: fail(f'missing/undersized admin asset: {rel}')

html=read('admin/index.html'); js=read('admin/app.js'); publisher=read('admin/book-publisher.js'); css=read('admin/style.css')
cp=json.loads(read('admin/control-plane.json'))
release=json.loads(read('admin/release.json'))

for marker in ('Freedom Control Center · V2','noindex,nofollow,noarchive,nosnippet','Content-Security-Policy','/admin/app.js','/admin/book-publisher.js','/admin/style.css','commandDialog','diffDialog','bookPublisherDialog'):
    if marker not in html: fail(f'admin HTML contract missing: {marker}')

combined=html+js+publisher+css
for banned in ('googletagmanager.com','analytics.tiktok.com','document.cookie','localStorage','github_pat_'):
    if banned in combined: fail(f'admin unsafe/persistence token: {banned}')

for marker in (
    "token:null", "state.token=token", "state.token=null", "sessionStorage",
    "/git/refs", "/git/trees", "/git/commits", "/pulls",
    "crypto.subtle.digest", "preparedFiles", "patchReleaseHash", "preflight",
    "freedom-gsc-current-v2", "freedom-gsc-baseline-v2", "cannibalization",
    "pdfHtmlConflicts", "experimentModel", "opportunityEngine", "qualityModel",
    "freedom-change-set-v2", "ctrlKey", "commandDialog", "__FCC_TEST_MODE__"
):
    if marker not in js: fail(f'admin V2 runtime contract missing: {marker}')

if "base:'main'" not in js or "head:branch" not in js: fail('PR-only publication contract missing')
if "/git/ref/heads/main" not in js: fail('main reference read contract missing')
if "method:'PATCH'" not in js: fail('branch ref update contract missing')
if "path==='release.json'" not in js: fail('manual release editing guard missing')
if "blockedPrefixes" not in js or "editableExtensions" not in js: fail('policy-driven editor guard missing')
if "Authorization" not in js or "Bearer ${state.token}" not in js: fail('GitHub auth contract missing')
if 'autocomplete="off"' not in html or 'tokenInput' not in html: fail('credential UX contract missing')
if '@media(max-width:760px)' not in css: fail('mobile contract missing')
if '--sidebar' not in css or '.command-dialog' not in css or '.seo-opportunity' not in css: fail('V2 UI contracts missing')

if cp.get('schema')!='freedom-control-plane-v2': fail('bad control plane schema')
if cp.get('version')!='2.1.0': fail('unexpected control plane version')
if cp.get('repository')!='carloskk07/shopee' or cp.get('ownerLogin')!='carloskk07': fail('control plane repository authority drift')
pub=cp.get('publishing',{})
if pub.get('directMainWrites') is not False: fail('direct main writes must remain false')
if not pub.get('branchPrefix','').startswith('control-center/'): fail('unsafe branch prefix')
if not (1 <= int(pub.get('maxFilesPerChangeSet',0)) <= 20): fail('change set budget outside safe range')
sec=cp.get('security',{})
for prefix in ('.github/','admin/','.git/'):
    if prefix not in sec.get('blockedPrefixes',[]): fail(f'missing blocked prefix: {prefix}')
if 'release.json' not in sec.get('blockedFiles',[]): fail('release.json must be generated, not manually edited')
if '.html' not in sec.get('editableExtensions',[]) or '.json' not in sec.get('editableExtensions',[]): fail('safe text extensions missing')
seo=cp.get('seo',{})
if seo.get('ctrOpportunity',{}).get('minImpressions') != 30: fail('CTR evidence threshold drift')
if seo.get('strikingDistance',{}).get('minImpressions') != 20: fail('striking-distance evidence threshold drift')
experiments=cp.get('experiments',[])
if not experiments: fail('V2 must carry at least the currently active causal experiment')
for exp in experiments:
    for k in ('id','name','startedAt','minimumDecisionDate','targetHtml','targetPdf','decisionRule'):
        if not exp.get(k): fail(f'experiment missing {k}')
    if exp['minimumDecisionDate'] < exp['startedAt']: fail('experiment decision date precedes start')


book=cp.get('bookPublishing',{})
if book.get('enabled') is not True: fail('Book Publisher must be enabled')
if book.get('binaryPersistence')!='memory-only': fail('binary uploads must remain memory-only')
if int(book.get('bundleFiles',0))>int(pub.get('maxFilesPerChangeSet',0)): fail('Book Publisher bundle exceeds change-set budget')
for marker in ('Book Publisher','stageBook','buildBookRecord','buildShim','routeManifestWithBook','landingFromTemplate','homeWithBook','authorWithBook','%PDF-','image/webp'):
    if marker not in publisher: fail(f'Book Publisher contract missing: {marker}')
for marker in ('binaryStaged','binaryPathAllowed',"encoding:x.encoding||'utf-8'",'__FCC_PUBLISHER_API__'):
    if marker not in js: fail(f'binary publishing runtime missing: {marker}')
if '[hidden]{display:none!important}' not in css: fail('hidden contract regression')

if release.get('schema')!='freedom-admin-release-v1': fail('bad admin release schema')
art=release.get('artifacts',{})
for rel in ('index.html','style.css','app.js','book-publisher.js','control-plane.json'):
    p=ADMIN/rel
    if rel not in art: fail(f'admin asset not release-managed: {rel}')
    actual=hashlib.sha256(p.read_bytes()).hexdigest()
    if actual!=art[rel]: fail(f'admin release hash mismatch: {rel}')

sitemap=read('sitemap.xml')
if '/admin' in sitemap: fail('admin must not enter sitemap')
robots=read('robots.txt')
if not robots.strip(): fail('robots.txt unexpectedly empty')

print('PASS: Freedom Control Center V2.1 adds a memory-only Book Publisher with binary-safe PR staging while preserving policy, SEO and release contracts')
