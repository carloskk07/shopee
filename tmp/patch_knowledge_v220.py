from pathlib import Path
import json,hashlib

ROOT=Path('.')

def replace(path,old,new):
    p=ROOT/path
    s=p.read_text(encoding='utf-8')
    if old not in s: raise SystemExit(f'anchor missing in {path}: {old[:80]}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

# Admin index loads the independent knowledge runtime.
replace('admin/index.html','  <script src="/admin/app.js" defer></script>\n  <script src="/admin/book-publisher.js" defer></script>', '  <script src="/admin/app.js" defer></script>\n  <script src="/admin/book-publisher.js" defer></script>\n  <script src="/admin/knowledge-layer.js" defer></script>')

# Control-plane policy advertises the public/private evidence boundary.
cp_path=ROOT/'admin/control-plane.json'
cp=json.loads(cp_path.read_text(encoding='utf-8'))
cp['version']='2.2.0'
cp['knowledge']={
  'enabled':True,
  'schema':'freedom-knowledge-layer-v1',
  'publicArtifact':'admin/knowledge.json',
  'runtime':'admin/knowledge-layer.js',
  'privateSearchEvidence':'session-only',
  'repositoryPersistence':False
}
cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Admin validator understands V2.2 and the two new release artifacts.
vp=ROOT/'scripts/validate_admin.py'
v=vp.read_text(encoding='utf-8')
v=v.replace("    'admin/control-plane.json':500,\n    'admin/release.json':100,", "    'admin/control-plane.json':500,\n    'admin/knowledge.json':1200,\n    'admin/knowledge-layer.js':1500,\n    'admin/release.json':100,",1)
v=v.replace("html=read('admin/index.html'); js=read('admin/app.js'); publisher=read('admin/book-publisher.js'); css=read('admin/style.css')", "html=read('admin/index.html'); js=read('admin/app.js'); publisher=read('admin/book-publisher.js'); knowledge_js=read('admin/knowledge-layer.js'); css=read('admin/style.css')",1)
v=v.replace("'/admin/book-publisher.js','/admin/style.css'", "'/admin/book-publisher.js','/admin/knowledge-layer.js','/admin/style.css'",1)
v=v.replace('combined=html+js+publisher+css','combined=html+js+publisher+knowledge_js+css',1)
v=v.replace("if cp.get('version')!='2.1.2'", "if cp.get('version')!='2.2.0'",1)
v=v.replace("for marker in ('index.html','style.css','app.js','book-publisher.js','control-plane.json'):", "for marker in ('index.html','style.css','app.js','book-publisher.js','control-plane.json','knowledge.json','knowledge-layer.js'):",1)
needle="seo=cp.get('seo',{})"
insert="""knowledge=cp.get('knowledge',{})
if knowledge.get('enabled') is not True: fail('knowledge layer must be enabled')
if knowledge.get('schema')!='freedom-knowledge-layer-v1': fail('knowledge schema policy drift')
if knowledge.get('privateSearchEvidence')!='session-only': fail('private Search Console evidence must remain session-only')
if knowledge.get('repositoryPersistence') is not False: fail('private Search Console evidence cannot persist in repository')
for marker in ('freedom-knowledge-layer-v1','__FCC_KNOWLEDGE_LAYER__','PRIVATE_SESSION_ONLY','knowledgeNav'):
    if marker not in knowledge_js: fail(f'knowledge runtime contract missing: {marker}')

seo=cp.get('seo',{})"""
if needle not in v: raise SystemExit('validate knowledge insertion anchor missing')
v=v.replace(needle,insert,1)
v=v.replace("print('PASS: Freedom Control Center V2.1.2 adds path-aware workflow semantics", "print('PASS: Freedom Control Center V2.2 adds curated Knowledge Layer with private Search Console boundary and path-aware workflow semantics",1)
vp.write_text(v,encoding='utf-8')

# Release authority now manages seven admin artifacts.
rp=ROOT/'admin/release.json'
r=json.loads(rp.read_text(encoding='utf-8'))
r['version']='2.2.0'
for name in ('index.html','style.css','app.js','book-publisher.js','control-plane.json','knowledge.json','knowledge-layer.js'):
    r.setdefault('artifacts',{})[name]=hashlib.sha256((ROOT/'admin'/name).read_bytes()).hexdigest()
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Permanent integrity workflow.
ip=ROOT/'.github/workflows/admin-integrity.yml'
s=ip.read_text(encoding='utf-8')
s=s.replace('Validate Freedom Control Center V2.1.2','Validate Freedom Control Center V2.2.0')
s=s.replace('scripts/validate_admin.py scripts/validate_site.py','scripts/validate_admin.py scripts/validate_knowledge.py scripts/validate_site.py')
s=s.replace('          python3 scripts/validate_admin.py\n          node --check admin/app.js', '          python3 scripts/validate_admin.py\n          python3 scripts/validate_knowledge.py\n          node --check admin/app.js\n          node --check admin/knowledge-layer.js')
s=s.replace('          test "$(stat -c%s admin/control-plane.json)" -lt 14000', '          test "$(stat -c%s admin/control-plane.json)" -lt 16000\n          test "$(stat -c%s admin/knowledge.json)" -lt 18000\n          test "$(stat -c%s admin/knowledge-layer.js)" -lt 18000')
s=s.replace("          grep -q '\"version\": \"2.1.2\"' admin/control-plane.json", "          grep -q '\"version\": \"2.2.0\"' admin/control-plane.json\n          grep -q 'freedom-knowledge-layer-v1' admin/knowledge.json\n          grep -q 'PRIVATE_SESSION_ONLY' admin/knowledge.json\n          grep -q '__FCC_KNOWLEDGE_LAYER__' admin/knowledge-layer.js\n          grep -q '/admin/knowledge-layer.js' admin/index.html")
s=s.replace('Verify scoped V2.1.2 mutation contract','Verify scoped V2.2.0 mutation contract')
s=s.replace('(validate_admin|test_admin_v2|validate_site|validate_seo|generate-route-shims)', '(validate_admin|validate_knowledge|test_admin_v2|validate_site|validate_seo|generate-route-shims)')
s=s.replace('Control Center V2.1.2 touched files outside','Control Center V2.2.0 touched files outside')
ip.write_text(s,encoding='utf-8')

# Production smoke verifies exact bytes and public/private separation.
sp=ROOT/'.github/workflows/admin-production-smoke.yml'
s=sp.read_text(encoding='utf-8')
s=s.replace('Verify admin V2.1.2 byte parity, path-aware quality and Book Publisher safety','Verify admin V2.2.0 byte parity, Knowledge Layer privacy and Book Publisher safety')
s=s.replace("assert release.get('version')=='2.1.2'", "assert release.get('version')=='2.2.0'")
s=s.replace("assert set(release['artifacts'])=={'index.html','style.css','app.js','book-publisher.js','control-plane.json'}", "assert set(release['artifacts'])=={'index.html','style.css','app.js','book-publisher.js','control-plane.json','knowledge.json','knowledge-layer.js'}")
s=s.replace("FreedomAdmin-Smoke/2.1.2", "FreedomAdmin-Smoke/2.2.0")
s=s.replace("          grep -q '/admin/book-publisher.js' /tmp/admin.html", "          grep -q '/admin/book-publisher.js' /tmp/admin.html\n          grep -q '/admin/knowledge-layer.js' /tmp/admin.html")
s=s.replace("          curl --fail --silent --show-error --location 'https://achadostube.com.br/admin/control-plane.json' -o /tmp/control-plane.json", "          curl --fail --silent --show-error --location 'https://achadostube.com.br/admin/knowledge.json' -o /tmp/knowledge.json\n          curl --fail --silent --show-error --location 'https://achadostube.com.br/admin/knowledge-layer.js' -o /tmp/knowledge-layer.js\n          grep -q 'freedom-knowledge-layer-v1' /tmp/knowledge.json\n          grep -q 'PRIVATE_SESSION_ONLY' /tmp/knowledge.json\n          grep -q '__FCC_KNOWLEDGE_LAYER__' /tmp/knowledge-layer.js\n          ! grep -Eq '\"(clicks|impressions|ctr|position|topQueries|topPages|queryPageRelationships)\"[[:space:]]*:' /tmp/knowledge.json\n          curl --fail --silent --show-error --location 'https://achadostube.com.br/admin/control-plane.json' -o /tmp/control-plane.json")
s=s.replace("assert cp['version']=='2.1.2'", "assert cp['version']=='2.2.0'")
s=s.replace("          book=cp['bookPublishing']", "          knowledge=cp['knowledge']\n          assert knowledge['enabled'] is True\n          assert knowledge['privateSearchEvidence']=='session-only'\n          assert knowledge['repositoryPersistence'] is False\n          book=cp['bookPublishing']")
s=s.replace("print('Control plane V2.1.2 path-aware quality + Book Publisher policy verified')", "print('Control plane V2.2 Knowledge Layer privacy + path-aware quality + Book Publisher policy verified')")
sp.write_text(s,encoding='utf-8')
