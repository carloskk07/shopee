from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'admin'/'knowledge.json'
J=ROOT/'admin'/'knowledge-layer.js'
I=ROOT/'admin'/'index.html'

def fail(msg):
    print('FAIL:',msg)
    raise SystemExit(1)

if not P.exists() or not J.exists(): fail('knowledge artifacts missing')
data=json.loads(P.read_text(encoding='utf-8'))
if data.get('schema')!='freedom-knowledge-layer-v1': fail('knowledge schema')
if data.get('classification')!='PUBLIC_OPERATIONAL': fail('knowledge classification')
if data.get('adminVersion')!='2.2.0': fail('admin version mismatch')
if data.get('version')!='1.1.0': fail('knowledge version mismatch')
pe=data.get('privateEvidence',{}).get('searchConsole',{})
if pe.get('classification')!='PRIVATE_NETLIFY_BLOBS': fail('GSC private classification')
if pe.get('repositoryPersistence') is not False: fail('GSC repository persistence must be false')
if pe.get('browserPersistence')!='sessionStorage hydration only': fail('GSC browser hydration contract')
if 'Netlify Blobs' not in pe.get('privateServerPersistence',''): fail('GSC private server persistence contract')
ledger=data.get('privateEvidence',{}).get('decisionLedger',{})
if ledger.get('classification')!='PRIVATE_NETLIFY_BLOBS': fail('decision ledger private classification')
if ledger.get('repositoryPersistence') is not False: fail('decision ledger repository persistence must be false')

# Public operational knowledge may describe policy, but never carry raw private metrics or OAuth material.
forbidden_keys={'clicks','impressions','ctr','position','topQueries','topPages','queryPageRelationships','risingKeywords','fallingKeywords','refreshToken','accessToken','clientSecret'}
def walk(v,path='root'):
    if isinstance(v,dict):
        for k,x in v.items():
            if k in forbidden_keys: fail(f'private evidence key leaked: {path}.{k}')
            walk(x,f'{path}.{k}')
    elif isinstance(v,list):
        for i,x in enumerate(v): walk(x,f'{path}[{i}]')
walk(data)

text=P.read_text(encoding='utf-8')+J.read_text(encoding='utf-8')
for marker in ('github_pat_','ghp_','ya29.','AIza','client_secret','GOCSPX-','1//'):
    if marker in text: fail(f'secret-like marker leaked: {marker}')

js=J.read_text(encoding='utf-8')
for marker in ('freedom-knowledge-layer-v1','__FCC_KNOWLEDGE_LAYER__','Decision Ledger','Persistência privada','knowledgeNav'):
    if marker not in js: fail(f'knowledge runtime marker missing: {marker}')

html=I.read_text(encoding='utf-8')
if '/admin/knowledge-layer.js' not in html: fail('knowledge layer script not loaded by admin index')
print('PASS: Freedom Knowledge Layer public/private boundary matches private Netlify GSC snapshots and decision ledger without leaking metrics or secrets')
