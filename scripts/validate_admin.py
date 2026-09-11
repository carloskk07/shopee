#!/usr/bin/env python3
from pathlib import Path
import hashlib, json

ROOT=Path(__file__).resolve().parents[1]
ADMIN=ROOT/'admin'

def fail(msg): raise SystemExit(msg)
def read(path): return (ROOT/path).read_text(encoding='utf-8')

required={
    'admin/index.html':1000,
    'admin/style.css':5000,
    'admin/app.js':15000,
    'admin/book-publisher.js':12000,
    'admin/control-plane.json':1000,
    'admin/knowledge.json':1800,
    'admin/knowledge-layer.js':1800,
    'admin/operational-brain.js':6000,
    'admin/release.json':100,
    'admin/README.md':500,
    'scripts/test_admin_v2.js':500,
    'netlify/lib/decision-engine.mts':4000,
    'netlify/functions/decision-ledger.mts':1200,
    'netlify/functions/brain-evaluate.mts':5000,
    'netlify/functions/brain-status.mts':1200,
    'netlify/functions/github-publish.mts':3000,
    'scripts/build_private_admin.py':3000,
}
for rel,minimum in required.items():
    p=ROOT/rel
    if not p.is_file() or p.stat().st_size<minimum: fail(f'missing/undersized admin asset: {rel}')

html=read('admin/index.html'); js=read('admin/app.js'); publisher=read('admin/book-publisher.js'); knowledge_js=read('admin/knowledge-layer.js'); brain=read('admin/operational-brain.js'); css=read('admin/style.css')
engine=read('netlify/lib/decision-engine.mts'); ledger_fn=read('netlify/functions/decision-ledger.mts'); brain_fn=read('netlify/functions/brain-evaluate.mts'); status_fn=read('netlify/functions/brain-status.mts'); publish_fn=read('netlify/functions/github-publish.mts'); private_builder=read('scripts/build_private_admin.py')
cp=json.loads(read('admin/control-plane.json')); knowledge_json=json.loads(read('admin/knowledge.json')); release=json.loads(read('admin/release.json'))

for marker in ('Freedom Control Center · V2','noindex,nofollow,noarchive,nosnippet','Content-Security-Policy','/admin/app.js','/admin/book-publisher.js','/admin/knowledge-layer.js','/admin/style.css','commandDialog','diffDialog','bookPublisherDialog'):
    if marker not in html: fail(f'admin HTML contract missing: {marker}')

combined=html+js+publisher+knowledge_js+brain+css
for banned in ('googletagmanager.com','analytics.tiktok.com','document.cookie','localStorage','github_pat_'):
    if banned in combined: fail(f'admin unsafe/persistence token: {banned}')

for marker in (
    'token:null','state.token=token','state.token=null','sessionStorage',
    '/git/refs','/git/trees','/git/commits','/pulls',
    'crypto.subtle.digest','preparedFiles','patchReleaseHash','preflight',
    'freedom-gsc-current-v2','freedom-gsc-baseline-v2','cannibalization',
    'pdfHtmlConflicts','experimentModel','opportunityEngine','qualityModel',
    'freedom-change-set-v2','ctrlKey','commandDialog','__FCC_TEST_MODE__'
):
    if marker not in js: fail(f'admin V2 runtime contract missing: {marker}')
if "base:'main'" not in js or "head:branch" not in js: fail('PR-only publication contract missing')
if '/git/ref/heads/main' not in js: fail('main reference read contract missing')
if "method:'PATCH'" not in js: fail('branch ref update contract missing')
if "path==='release.json'" not in js: fail('manual release editing guard missing')
if 'blockedPrefixes' not in js or 'editableExtensions' not in js: fail('policy-driven editor guard missing')
if 'Authorization' not in js or 'Bearer ${state.token}' not in js: fail('GitHub auth contract missing')
if 'autocomplete="off"' not in html or 'tokenInput' not in html: fail('credential UX contract missing')
if '@media(max-width:760px)' not in css: fail('mobile contract missing')
if '--sidebar' not in css or '.command-dialog' not in css or '.seo-opportunity' not in css: fail('V2 UI contracts missing')

if cp.get('schema')!='freedom-control-plane-v2': fail('bad control plane schema')
if cp.get('version')!='2.2.0': fail('unexpected control plane version')
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

policy=cp.get('decisionPolicy',{})
if policy.get('schema')!='freedom-closed-loop-policy-v1': fail('closed-loop policy missing')
if policy.get('mode')!='human-approved': fail('decision loop must remain human-approved')
if policy.get('autoMerge') is not False or policy.get('directProductionMutation') is not False: fail('closed-loop cannot auto-merge or mutate production directly')
if policy.get('requireFinalizedDataThroughDecisionDate') is not True: fail('finalized GSC gate must remain mandatory')
if policy.get('requireEqualPrePostWindows') is not True: fail('equal pre/post causal windows must remain mandatory')
if policy.get('onePrimaryHypothesisPerChangeSet') is not True: fail('one-primary-hypothesis contract missing')
if int(policy.get('maxConcurrentSeoExperiments',0))!=1: fail('SEO experiment concurrency must remain one')
if sum(int(x.get('weight',0)) for x in policy.get('objectives',[]))!=100: fail('decision objective weights must total 100')
if set(policy.get('verdicts',[]))!={'KEEP','ITERATE','REVERT','INCONCLUSIVE'}: fail('decision verdict contract drift')

experiments=cp.get('experiments',[])
if not experiments: fail('must carry the currently active causal experiment')
if len([x for x in experiments if x.get('status') in ('OBSERVING','ACTIVE','DECISION_WINDOW')])>int(policy.get('maxConcurrentSeoExperiments',1)): fail('too many concurrent SEO experiments')
for exp in experiments:
    for k in ('id','name','startedAt','minimumDecisionDate','targetHtml','targetPdf','decisionRule','objective','successCriteria'):
        if not exp.get(k): fail(f'experiment missing {k}')
    if exp['minimumDecisionDate'] < exp['startedAt']: fail('experiment decision date precedes start')
    sc=exp.get('successCriteria',{})
    for k in ('minClusterImpressions','htmlImpressionsMin','minTrafficRatio','hardTrafficRatio','maxPositionRegression'):
        if k not in sc: fail(f'experiment success criterion missing: {k}')

knowledge=cp.get('knowledge',{})
if knowledge.get('enabled') is not True or knowledge.get('schema')!='freedom-knowledge-layer-v1': fail('knowledge layer policy drift')
if knowledge.get('privateSearchEvidence')!='netlify-private-blobs': fail('Search Console evidence must reflect private Netlify persistence')
if knowledge.get('browserHydration')!='session-only': fail('browser GSC hydration must remain session-only')
if knowledge.get('repositoryPersistence') is not False: fail('private Search Console evidence cannot persist in repository')
if knowledge_json.get('version')!='1.1.0': fail('knowledge layer version not advanced')
gsc_contract=knowledge_json.get('privateEvidence',{}).get('searchConsole',{})
ledger_contract=knowledge_json.get('privateEvidence',{}).get('decisionLedger',{})
if gsc_contract.get('classification')!='PRIVATE_NETLIFY_BLOBS' or gsc_contract.get('repositoryPersistence') is not False: fail('knowledge GSC privacy contract drift')
if ledger_contract.get('classification')!='PRIVATE_NETLIFY_BLOBS' or ledger_contract.get('repositoryPersistence') is not False: fail('knowledge decision ledger privacy contract drift')
for marker in ('freedom-knowledge-layer-v1','__FCC_KNOWLEDGE_LAYER__','PRIVATE','Decision Ledger','Persistência privada'):
    if marker not in knowledge_js: fail(f'knowledge runtime contract missing: {marker}')

quality=cp.get('quality',{}); required_runs=quality.get('requiredWorkflows',[]); optional_runs=quality.get('optionalWorkflows',[])
if quality.get('searchEvidenceScoring') is not False: fail('Search evidence must not reduce technical health score')
if quality.get('historicalRunsScoring') is not False: fail('Historical runs must not reduce current release health')
for name in ('Site integrity','Admin integrity','Production smoke','Admin production smoke','pages build and deployment'):
    if name not in required_runs: fail(f'quality required workflow missing: {name}')
for name in ('Route integrity','Route production smoke'):
    if name not in optional_runs or name in required_runs: fail(f'conditional workflow policy drift: {name}')
for marker in ('CI_CURRENT_RELEASE','NOT_LOADED','historicalFailed','operationalReadiness','technicalHealth'):
    if marker not in js: fail(f'quality semantics runtime missing: {marker}')

for marker in ('Operational Brain V2','Closed Loop','/api/decision/ledger','WAITING_FINALIZED_GSC','Decision ledger','lifecycle editorial','Preparar ITERATE','Preparar REVERT'):
    if marker not in brain: fail(f'Operational Brain V2 contract missing: {marker}')
for marker in ('evaluateExperiment','finalizedDecisionReached','preStart','postDays','fnv1a32','recordDecision','linkDecisionPr','PRIVATE'):
    if marker not in engine: fail(f'decision engine contract missing: {marker}')
for marker in ('/api/decision/ledger','DECIDE','PREPARE','Janela causal ainda não está elegível'):
    if marker not in ledger_fn and marker not in engine: fail(f'decision ledger function contract missing: {marker}')
for marker in ('freedom-operational-brain-v2','decisionLoop','observability','WAITING_FINALIZED_GSC','inventoryModel','readDecisionLedger'):
    if marker not in brain_fn: fail(f'brain backend V2 contract missing: {marker}')
for marker in ('freedom-operational-brain-status-v2','dataLagDays','decisionLoop'):
    if marker not in status_fn: fail(f'brain status V2 contract missing: {marker}')
for marker in ('FCC_DECISION_CONTEXT','decisionContext','linkDecisionPr','sem auto-merge'):
    if marker not in publish_fn: fail(f'GitHub decision linkage contract missing: {marker}')
for marker in ('freedom-decision-context-v1','WAITING_FINALIZED_GSC','closed-loop-decisions','causal-experiment-windows','decision-ledger'):
    if marker not in private_builder: fail(f'private build closed-loop contract missing: {marker}')

book=cp.get('bookPublishing',{})
if book.get('enabled') is not True: fail('Book Publisher must be enabled')
if book.get('binaryPersistence')!='memory-only': fail('binary uploads must remain memory-only')
if int(book.get('bundleFiles',0))>int(pub.get('maxFilesPerChangeSet',0)): fail('Book Publisher bundle exceeds change-set budget')
for marker in ('Book Publisher','stageBook','buildBookRecord','buildShim','routeManifestWithBook','landingFromTemplate','homeWithBook','authorWithBook','%PDF-','image/webp'):
    if marker not in publisher: fail(f'Book Publisher contract missing: {marker}')
for marker in ('binaryStaged','binaryPathAllowed',"encoding:x.encoding||'utf-8'",'__FCC_PUBLISHER_API__','BOOK_BUNDLE_ATOMIC','bundleId'):
    if marker not in js: fail(f'binary publishing runtime missing: {marker}')
if '[hidden]{display:none!important}' not in css: fail('hidden contract regression')

if release.get('schema')!='freedom-admin-release-v1': fail('bad admin release schema')
art=release.get('artifacts',{})
for rel in ('index.html','style.css','app.js','book-publisher.js','control-plane.json','knowledge.json','knowledge-layer.js'):
    p=ADMIN/rel
    if rel not in art: fail(f'admin asset not release-managed: {rel}')
    actual=hashlib.sha256(p.read_bytes()).hexdigest()
    if actual!=art[rel]: fail(f'admin release hash mismatch: {rel}')

sitemap=read('sitemap.xml')
if '/admin' in sitemap: fail('admin must not enter sitemap')
if not read('robots.txt').strip(): fail('robots.txt unexpectedly empty')

print('PASS: Freedom Control Center keeps PR-only publishing and technical health semantics while adding a private closed-loop causal decision engine, equal pre/post windows, finalized-GSC gates, decision ledger, PR linkage, observability and accurate private-evidence documentation')
