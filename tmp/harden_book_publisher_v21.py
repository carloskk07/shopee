from pathlib import Path
import hashlib,json

# Make each generated book bundle atomic in local preflight.
p=Path('admin/app.js'); s=p.read_text(encoding='utf-8')
old="checks.push({ok:items.length<=max,level:items.length<=max?'good':'bad',name:'SCOPE_BUDGET',detail:`${items.length}/${max} arquivos`});for(const x of items){"
new="checks.push({ok:items.length<=max,level:items.length<=max?'good':'bad',name:'SCOPE_BUDGET',detail:`${items.length}/${max} arquivos`});const bookGroups=new Map();for(const x of items){if(x.bundleId?.startsWith('book:')){if(!bookGroups.has(x.bundleId))bookGroups.set(x.bundleId,[]);bookGroups.get(x.bundleId).push(x)}}for(const [id,xs] of bookGroups){const expected=c.bookPublishing?.bundleFiles||10,ok=xs.length===expected;checks.push({ok,level:ok?'good':'bad',name:'BOOK_BUNDLE_ATOMIC',detail:`${id}: ${xs.length}/${expected} arquivos; capa, PDF e superfícies editoriais devem viajar juntos`})}for(const x of items){"
assert old in s, 'preflight anchor missing'
s=s.replace(old,new,1)
old="stageBundle:({texts=[],binaries=[]})=>{\n      const now=new Date().toISOString(),nextText=[],nextBin=[];"
new="stageBundle:({bundleId='',texts=[],binaries=[]})=>{\n      if(bundleId&&!/^book:[a-z0-9-]+$/.test(bundleId))throw new Error('bundleId editorial inválido');\n      const now=new Date().toISOString(),nextText=[],nextBin=[];"
assert old in s, 'stageBundle signature missing'
s=s.replace(old,new,1)
s=s.replace("nextText.push({...x,encoding:'utf-8',volatile:true,updatedAt:now})","nextText.push({...x,bundleId,encoding:'utf-8',volatile:true,updatedAt:now})",1)
s=s.replace("nextBin.push({...x,volatile:true,updatedAt:now})","nextBin.push({...x,bundleId,volatile:true,updatedAt:now})",1)
p.write_text(s,encoding='utf-8')

p=Path('admin/book-publisher.js'); s=p.read_text(encoding='utf-8')
old="API.stageBundle({texts:["
assert old in s, 'publisher bundle call missing'
s=s.replace(old,"API.stageBundle({bundleId:`book:${b.slug}`,texts:[",1)
p.write_text(s,encoding='utf-8')

# Browser DOM serialization legitimately emits <link ...> without XHTML '/>'; validate attributes semantically.
p=Path('scripts/validate_site.py'); s=p.read_text(encoding='utf-8')
old="        preload=f'<link href=\"/assets/covers/capa-{slug}.webp\" rel=\"preload\" as=\"image\" type=\"image/webp\" fetchpriority=\"high\"/>'\n        if preload not in text:fail(f'{slug}: LCP preload missing')"
new="        cover_path=f'/assets/covers/capa-{slug}.webp'\n        preload_tags=re.findall(r'<link\\b[^>]*>',text,re.I)\n        preload_ok=any(all(token in tag for token in (f'href=\"{cover_path}\"','rel=\"preload\"','as=\"image\"','type=\"image/webp\"','fetchpriority=\"high\"')) for tag in preload_tags)\n        if not preload_ok:fail(f'{slug}: LCP preload missing')"
assert old in s, 'preload validator anchor missing'
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

# Regression contracts.
p=Path('scripts/test_admin_v2.js'); s=p.read_text(encoding='utf-8')
if "bundleId editorial" not in s:
    s += "\nassert(require('fs').readFileSync(require('path').join(__dirname,'../admin/app.js'),'utf8').includes('BOOK_BUNDLE_ATOMIC'),'atomic Book Publisher preflight missing');\nassert(require('fs').readFileSync(require('path').join(__dirname,'../admin/book-publisher.js'),'utf8').includes('bundleId:`book:${b.slug}`'),'Book Publisher bundle identity missing');\nconsole.log('PASS: Book Publisher V2.1 atomic bundle guard');\n"
    p.write_text(s,encoding='utf-8')

p=Path('scripts/validate_admin.py'); s=p.read_text(encoding='utf-8')
old="for marker in ('binaryStaged','binaryPathAllowed',\"encoding:x.encoding||'utf-8'\",'__FCC_PUBLISHER_API__'):"
new="for marker in ('binaryStaged','binaryPathAllowed',\"encoding:x.encoding||'utf-8'\",'__FCC_PUBLISHER_API__','BOOK_BUNDLE_ATOMIC','bundleId'):"
assert old in s, 'admin validator binary marker anchor missing'
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

# Refresh admin release hashes for changed admin artifacts.
rp=Path('admin/release.json'); rel=json.loads(rp.read_text(encoding='utf-8'))
for name in ('app.js','book-publisher.js'):
    rel['artifacts'][name]=hashlib.sha256((Path('admin')/name).read_bytes()).hexdigest()
rp.write_text(json.dumps(rel,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
