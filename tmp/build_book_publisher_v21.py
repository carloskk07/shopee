from pathlib import Path
import hashlib, json

# control plane
cp_path=Path('admin/control-plane.json')
cp=json.loads(cp_path.read_text(encoding='utf-8'))
cp['version']='2.1.0'
cp['bookPublishing']={
    'enabled': True,
    'templateSlug': 'proposito-maior',
    'author': 'Arthur Magnus',
    'requiredTags': 3,
    'maxTags': 8,
    'cover': {'maxInputBytes': 8388608, 'maxOutputWidth': 1200, 'minWidth': 600, 'minHeight': 800, 'webpQuality': 0.9},
    'pdf': {'maxBytes': 26214400},
    'paths': {'coverPrefix':'assets/covers/capa-','pdfPrefix':'ebook/'},
    'bundleFiles': 10,
    'binaryPersistence': 'memory-only'
}
cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# admin HTML
p=Path('admin/index.html'); html=p.read_text(encoding='utf-8')
if 'id="bookPublisherDialog"' not in html:
    dialog='''
  <dialog id="bookPublisherDialog" class="dialog">
    <div class="dialog-card book-publisher-card">
      <div class="dialog-head"><div><span class="kicker">Book Publisher · lançamento seguro</span><h2>Novo livro</h2><p class="publisher-sub">Dados → arquivos → SEO → revisão → Change Set</p></div><button data-close="bookPublisherDialog" class="icon-btn" aria-label="Fechar">×</button></div>
      <div class="publisher-steps" aria-label="Etapas"><button class="active" data-book-step-jump="0"><b>1</b><span>Dados</span></button><button data-book-step-jump="1"><b>2</b><span>Capa & PDF</span></button><button data-book-step-jump="2"><b>3</b><span>SEO</span></button><button data-book-step-jump="3"><b>4</b><span>Revisão</span></button></div>
      <div class="book-step active" data-book-step="0">
        <div class="form-grid two"><label>Título do livro<input id="bookTitle" maxlength="100" autocomplete="off" placeholder="Título completo"></label><label>Slug<input id="bookSlug" maxlength="80" autocomplete="off" spellcheck="false" placeholder="titulo-do-livro"></label></div>
        <label>Descrição editorial<textarea id="bookDescription" rows="4" maxlength="420" placeholder="Explique claramente o que o leitor encontrará neste livro."></textarea></label>
        <label>Momento / intenção do leitor<textarea id="bookIntent" rows="3" maxlength="300" placeholder="Para quem esta leitura é uma boa escolha?"></textarea></label>
        <div class="form-grid three"><label>Linha editorial<select id="bookLine"><option value="reflexiva">Reflexiva</option><option value="pratica">Prática</option><option value="codigos">Códigos de Vida</option></select></label><label>Jornada na home<select id="bookPath"><option value="">Somente catálogo</option><option value="direcao">Sem direção</option><option value="foco">Voltar ao foco</option><option value="mente">Mente não desliga</option><option value="recomeco">Recomeçar</option><option value="peso">Rotina pesada</option></select></label><label>Badge<input id="bookBadge" maxlength="40" value="Novo lançamento"></label></div>
        <label>Temas / palavras-chave<input id="bookTags" maxlength="220" placeholder="ex.: clareza, escolhas, direção"></label>
        <label class="check-row"><input id="bookFeatured" type="checkbox"> <span>Marcar como destaque editorial</span></label>
      </div>
      <div class="book-step" data-book-step="1">
        <div class="upload-grid"><label class="upload-card"><span class="upload-icon">▧</span><strong>Capa</strong><span>JPG, PNG ou WebP · será normalizada para WebP</span><input id="bookCover" type="file" accept="image/jpeg,image/png,image/webp" hidden><button type="button" class="btn ghost" data-pick-cover>Selecionar capa</button><small id="bookCoverStatus">Nenhum arquivo</small><img id="bookCoverPreview" class="publisher-cover" alt="Prévia da capa" hidden></label><label class="upload-card"><span class="upload-icon">PDF</span><strong>Livro em PDF</strong><span>Validação de assinatura %PDF- · até 25 MB</span><input id="bookPdf" type="file" accept="application/pdf,.pdf" hidden><button type="button" class="btn ghost" data-pick-pdf>Selecionar PDF</button><small id="bookPdfStatus">Nenhum arquivo</small></label></div>
        <div class="callout warn"><strong>Arquivos sensíveis</strong><span>Capa e PDF ficam somente na memória desta aba até o Pull Request ser criado. Recarregar a página descarta o bundle inteiro e evita staging incompleto.</span></div>
      </div>
      <div class="book-step" data-book-step="2">
        <label>SEO title<input id="bookSeoTitle" maxlength="72" placeholder="Gerado automaticamente a partir do título"></label>
        <label>Meta description<textarea id="bookMeta" rows="3" maxlength="180" placeholder="Descrição para resultados de busca"></textarea></label>
        <div class="publisher-seo-preview"><span>Prévia editorial</span><strong id="bookSeoPreviewTitle">Título do livro | Freedom Book</strong><small id="bookSeoPreviewUrl">achadostube.com.br/slug</small><p id="bookSeoPreviewMeta">Descrição da página.</p></div>
        <div class="callout"><strong>Schema automático</strong><span>O publicador gera canonical, BreadcrumbList, WebPage, Book, autor Arthur Magnus, publisher Freedom Book, imagem WebP e MediaObject do PDF.</span></div>
      </div>
      <div class="book-step" data-book-step="3"><div id="bookReview"></div></div>
      <div id="bookPublisherError" class="error"></div>
      <div class="publisher-actions"><button type="button" class="btn ghost" data-book-prev>Voltar</button><div class="publisher-actions-right"><button type="button" class="btn ghost" data-close="bookPublisherDialog">Cancelar</button><button type="button" class="btn primary" data-book-next>Continuar</button><button type="button" class="btn primary" data-stage-book hidden>Adicionar ao Change Set</button></div></div>
    </div>
  </dialog>
'''
    anchor='  <dialog id="commandDialog" class="dialog command-dialog">'
    assert anchor in html
    html=html.replace(anchor,dialog+'\n'+anchor,1)
if '/admin/book-publisher.js' not in html:
    html=html.replace('  <script src="/admin/app.js" defer></script>','  <script src="/admin/app.js" defer></script>\n  <script src="/admin/book-publisher.js" defer></script>',1)
p.write_text(html,encoding='utf-8')

# admin app core staging
p=Path('admin/app.js'); js=p.read_text(encoding='utf-8')
old="staged:new Map(),gsc:{current:null,baseline:null},selectedFile:null"
assert old in js
js=js.replace(old,"staged:new Map(),binaryStaged:new Map(),gsc:{current:null,baseline:null},selectedFile:null",1)
old="  async function sha256(text){const b=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(text));return [...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,'0')).join('')}\n"
assert old in js
js=js.replace(old,old+"  function b64Bytes(s){return Uint8Array.from(atob(String(s||'').replace(/\\s/g,'')),c=>c.charCodeAt(0))}\n  async function sha256Base64(s){const b=await crypto.subtle.digest('SHA-256',b64Bytes(s));return [...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,'0')).join('')}\n  function allStaged(){return [...state.staged.values(),...state.binaryStaged.values()]}\n  function stagedCount(){return state.staged.size+state.binaryStaged.size}\n  function binaryPathAllowed(path){return /^assets\\/covers\\/capa-[a-z0-9-]+\\.webp$/.test(path)||/^ebook\\/[a-z0-9-]+\\.pdf$/.test(path)}\n",1)
js=js.replace("sessionStorage.setItem(SESSION_KEYS.changes,JSON.stringify([...state.staged.values()]))","sessionStorage.setItem(SESSION_KEYS.changes,JSON.stringify([...state.staged.values()].filter(x=>!x.volatile)))",1)
js=js.replace("function updateStagedUi(){const n=state.staged.size;","function updateStagedUi(){const n=stagedCount();",1)
js=js.replace("function unstage(path){state.staged.delete(path);persistStaged();render()}","function unstage(path){state.staged.delete(path);state.binaryStaged.delete(path);persistStaged();render()}",1)
js=js.replace("function clearStaged(){state.staged.clear();persistStaged();render()}","function clearStaged(){state.staged.clear();state.binaryStaged.clear();persistStaged();render()}",1)
needle="<div class=\"toolbar-right\">${pill('fonte: site-data.generated.json')}</div>"
assert needle in js
js=js.replace(needle,"<div class=\"toolbar-right\"><button class=\"btn primary\" data-new-book>+ Novo livro</button>${pill('fonte: site-data.generated.json')}</div>",1)
pre_old="function preflight(){const c=config(),max=c.publishing?.maxFilesPerChangeSet||12,items=[...state.staged.values()],checks=[];"
assert pre_old in js
js=js.replace(pre_old,"function preflight(){const c=config(),max=c.publishing?.maxFilesPerChangeSet||12,items=allStaged(),checks=[];",1)
validate_old="for(const x of items){const v=validateContent(x.path,x.content);checks.push({ok:!v.errors.length,level:v.errors.length?'bad':v.warnings.length?'warn':'good',name:x.path,detail:v.errors[0]||v.warnings[0]||'conteúdo passa nas validações locais'})}"
assert validate_old in js
js=js.replace(validate_old,"for(const x of items){if(x.encoding==='base64'){const ok=binaryPathAllowed(x.path)&&x.bytes>0;checks.push({ok,level:ok?'good':'bad',name:x.path,detail:ok?`${fmt(x.bytes)} bytes · binário validado pelo Book Publisher`:'binário fora da política'});continue}const v=validateContent(x.path,x.content);checks.push({ok:!v.errors.length,level:v.errors.length?'bad':v.warnings.length?'warn':'good',name:x.path,detail:v.errors[0]||v.warnings[0]||'conteúdo passa nas validações locais'})}",1)
js=js.replace("function changeRisk(){const items=[...state.staged.values()];","function changeRisk(){const items=allStaged();",1)
changes_old="function changesView(){const items=[...state.staged.values()],checks=preflight(),body=items.map(x=>`<div class=\"change-file\"><div><strong>${esc(x.path)}</strong><span>${fmt(new TextEncoder().encode(x.content).length)} bytes · atualizado ${when(x.updatedAt)}</span></div><div class=\"small-actions\"><span class=\"risk ${fileRisk(x.path)}\">${fileRisk(x.path)}</span><button class=\"mini-btn\" data-open-diff=\"${esc(x.path)}\">Diff</button><button class=\"mini-btn\" data-unstage=\"${esc(x.path)}\">Remover</button></div></div>`).join('');"
assert changes_old in js
changes_new="function changesView(){const items=allStaged(),checks=preflight(),body=items.map(x=>`<div class=\"change-file\"><div><strong>${esc(x.path)}</strong><span>${fmt(x.encoding==='base64'?x.bytes:new TextEncoder().encode(x.content).length)} bytes · ${x.encoding==='base64'?'binário · memória da aba':'texto'} · atualizado ${when(x.updatedAt)}</span></div><div class=\"small-actions\"><span class=\"risk ${fileRisk(x.path)}\">${fileRisk(x.path)}</span><button class=\"mini-btn\" data-open-diff=\"${esc(x.path)}\" ${x.encoding==='base64'?'disabled':''}>Diff</button><button class=\"mini-btn\" data-unstage=\"${esc(x.path)}\">Remover</button></div></div>`).join('');"
js=js.replace(changes_old,changes_new,1)
js=js.replace("function diffView(path){const x=state.staged.get(path);if(!x)return;","function diffView(path){const x=state.staged.get(path)||state.binaryStaged.get(path);if(!x)return;if(x.encoding==='base64')return toast('Diff binário é revisado por nome, tamanho e hash no PR','warn');",1)
js=js.replace("changeSet:{files:[...state.staged.keys()],risk:changeRisk()}","changeSet:{files:allStaged().map(x=>x.path),binaryFiles:[...state.binaryStaged.values()].map(x=>({path:x.path,bytes:x.bytes,mime:x.mime})),risk:changeRisk()}",1)
old="files:[...state.staged.values()].map(x=>({path:x.path,content:x.content,baseContent:x.baseContent,updatedAt:x.updatedAt}))"
assert old in js
js=js.replace(old,"files:allStaged().map(x=>x.encoding==='base64'?{path:x.path,encoding:'base64',bytes:x.bytes,mime:x.mime,content:'[memory-only binary omitted]'}:{path:x.path,content:x.content,baseContent:x.baseContent,updatedAt:x.updatedAt})",1)
prep_old="  async function preparedFiles(){const files=new Map([...state.staged].map(([k,v])=>[k,{...v}]));let rel=state.releaseText||'',changed=false;for(const [path,x] of files){if(state.release?.artifacts?.[path]){const h=await sha256(x.content);const next=patchReleaseHash(rel,path,h);if(next!==rel){rel=next;changed=true}}}if(changed)files.set('release.json',{path:'release.json',content:rel,label:'release hashes automáticos',baseContent:state.releaseText||''});return files}\n"
assert prep_old in js
prep_new="  async function preparedFiles(){const files=new Map();for(const x of allStaged())files.set(x.path,{...x});const relObj=JSON.parse(state.releaseText||'{\"artifacts\":{}}');relObj.artifacts=relObj.artifacts||{};let changed=false;for(const [path,x] of files){const bind=x.releaseBound===true||Object.prototype.hasOwnProperty.call(relObj.artifacts,path);if(!bind||x.releaseBound===false)continue;const h=x.encoding==='base64'?await sha256Base64(x.content):await sha256(x.content);if(relObj.artifacts[path]!==h){relObj.artifacts[path]=h;changed=true}}if(changed){const rel=JSON.stringify(relObj,null,2)+'\\n';files.set('release.json',{path:'release.json',content:rel,encoding:'utf-8',label:'release hashes automáticos',baseContent:state.releaseText||''})}return files}\n"
js=js.replace(prep_old,prep_new,1)
js=js.replace("body:JSON.stringify({content:x.content,encoding:'utf-8'})","body:JSON.stringify({content:x.content,encoding:x.encoding||'utf-8'})",1)
js=js.replace("state.staged.size===files.size?'sem release adicional':'+ release.json automático'","stagedCount()===files.size?'sem release adicional':'+ release.json automático'",1)
api_anchor="  const commands=[\n"
assert api_anchor in js
api_code="""  globalThis.__FCC_PUBLISHER_API__={
    snapshot:()=>({siteData:clone(state.siteData),tree:clone(state.tree),release:clone(state.release),main:currentBranch(),config:clone(config())}),
    readFile:async(path)=>(await ghFile(path)).text,
    sha256Text:sha256,
    stageBundle:({texts=[],binaries=[]})=>{
      const now=new Date().toISOString(),nextText=[],nextBin=[];
      for(const x of texts){if(!x?.path||typeof x.content!=='string'||!isEditable(x.path)||x.path==='release.json')throw new Error(`Texto gerado fora da política: ${x?.path||'?'}`);nextText.push({...x,encoding:'utf-8',volatile:true,updatedAt:now})}
      for(const x of binaries){if(!x?.path||x.encoding!=='base64'||!binaryPathAllowed(x.path)||!x.content||!x.bytes)throw new Error(`Binário fora da política: ${x?.path||'?'}`);nextBin.push({...x,volatile:true,updatedAt:now})}
      for(const x of nextText)state.staged.set(x.path,x);for(const x of nextBin)state.binaryStaged.set(x.path,x);persistStaged();render();toast(`Bundle editorial: ${texts.length+binaries.length} arquivos no Change Set`);return stagedCount();
    },
    hasPath:(path)=>state.staged.has(path)||state.binaryStaged.has(path),
    openChanges:()=>setView('changes')
  };

"""
js=js.replace(api_anchor,api_code+api_anchor,1)
cmd_anchor="    {name:'Atualizar estado',desc:'Recarregar GitHub, produção e contratos',icon:'↻',run:()=>loadAll()},\n"
assert cmd_anchor in js
js=js.replace(cmd_anchor,cmd_anchor+"    {name:'Publicar novo livro',desc:'Abrir Book Publisher: capa, PDF, landing, SEO e PR',icon:'＋',run:()=>document.dispatchEvent(new CustomEvent('fcc:new-book'))},\n",1)
test_old="if(globalThis.__FCC_TEST_MODE__){globalThis.__FCC_TEST__={parseGsc,opportunityEngine,cannibalization,pdfHtmlConflicts,experimentModel,validateContent,patchReleaseHash,state,config,gscStats};return}"
assert test_old in js
js=js.replace(test_old,"if(globalThis.__FCC_TEST_MODE__){globalThis.__FCC_TEST__={parseGsc,opportunityEngine,cannibalization,pdfHtmlConflicts,experimentModel,validateContent,patchReleaseHash,state,config,gscStats,binaryPathAllowed,allStaged};return}",1)
p.write_text(js,encoding='utf-8')

# publisher module
Path('admin/book-publisher.js').write_text(Path('tmp/book-publisher.v21.js').read_text(encoding='utf-8'),encoding='utf-8')

# styles
p=Path('admin/style.css'); css=p.read_text(encoding='utf-8')
if '/* Book Publisher V2.1 */' not in css:
    css += '''
/* Book Publisher V2.1 */
.book-publisher-card{width:min(1060px,calc(100vw - 28px))}.publisher-sub{margin:4px 0 0;color:var(--muted);font-size:10px}.publisher-steps{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;margin:12px 0 18px}.publisher-steps button{border:1px solid var(--line);background:#0d1218;color:var(--muted);border-radius:11px;padding:9px;display:flex;align-items:center;gap:8px;text-align:left}.publisher-steps button b{display:grid;place-items:center;width:24px;height:24px;border-radius:8px;background:#1c2531;color:#93a1b5;font-size:9px}.publisher-steps button span{font-size:9px;font-weight:800}.publisher-steps button.active{border-color:#6b3340;background:rgba(238,51,68,.08);color:#fff}.publisher-steps button.active b{background:var(--red);color:#fff}.book-step{display:none;min-height:330px}.book-step.active{display:block}.form-grid.two{grid-template-columns:1fr 1fr;gap:10px}.form-grid.three{grid-template-columns:repeat(3,1fr);gap:10px}.check-row{display:flex!important;grid-template-columns:none!important;align-items:center;gap:8px}.check-row input{width:16px;height:16px}.upload-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}.upload-card{margin:0!important;min-height:280px;border:1px dashed #3b4656;border-radius:15px;background:#0d1219;padding:18px;display:flex!important;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:8px}.upload-card strong{font-size:14px;color:#fff}.upload-card>span:not(.upload-icon){font-size:9px;color:var(--muted)}.upload-card small{color:#7f8b9d;max-width:330px}.upload-icon{width:48px;height:48px;display:grid;place-items:center;border-radius:13px;background:#19212c;color:var(--red2);font-weight:900}.publisher-cover{width:90px;max-height:135px;object-fit:contain;border-radius:8px;border:1px solid var(--line)}.publisher-seo-preview{border:1px solid #26303d;background:#0d1219;border-radius:14px;padding:16px;margin:14px 0}.publisher-seo-preview>span{display:block;color:#5f8dff;font-size:9px}.publisher-seo-preview strong{display:block;font-size:16px;margin:8px 0 2px}.publisher-seo-preview small{color:#5bb27f}.publisher-seo-preview p{font-size:11px;color:#a0aab8;line-height:1.45;margin:7px 0 0}.publisher-actions{display:flex;justify-content:space-between;gap:10px;margin-top:16px;padding-top:14px;border-top:1px solid var(--line)}.publisher-actions-right{display:flex;gap:8px}.publisher-review{display:grid;grid-template-columns:170px 1fr;gap:20px}.publisher-review-cover{width:160px;max-height:240px;object-fit:contain;border-radius:12px;background:#0c1117;border:1px solid var(--line)}.publisher-review h3{font-size:24px;margin:8px 0}.publisher-review p{font-size:11px;color:var(--muted);line-height:1.5}.publisher-file-plan{display:flex;flex-wrap:wrap;gap:6px;margin:14px 0}.publisher-file-plan code{font-size:8px;padding:5px 7px;border-radius:7px;background:#171f29;color:#9eabbc}@media(max-width:760px){.publisher-steps span{display:none}.publisher-steps button{justify-content:center}.form-grid.two,.form-grid.three,.upload-grid,.publisher-review{grid-template-columns:1fr}.book-step{min-height:0}.publisher-review-cover{width:110px;max-height:165px}.publisher-actions{align-items:stretch}.publisher-actions-right{flex:1;justify-content:flex-end;flex-wrap:wrap}}
'''
    p.write_text(css,encoding='utf-8')

# future-proof site validator
p=Path('scripts/validate_site.py'); s=p.read_text(encoding='utf-8')
anchor="}\n\nclass Parser(HTMLParser):"
if 'CATALOG_DATA_EARLY' not in s:
    insert="}\n\nCATALOG_DATA_EARLY=json.loads((ROOT/'site-data.generated.json').read_text('utf-8'))\nEXPECTED_HTML |= {f\"{b['slug']}.html\" for b in CATALOG_DATA_EARLY.get('books',[]) if b.get('slug')}\n\nclass Parser(HTMLParser):"
    assert anchor in s; s=s.replace(anchor,insert,1)
s=s.replace("if home.count('data-book-card')!=11:fail('home must contain 11 catalog cards')","if home.count('data-book-card')!=len(CATALOG_DATA_EARLY.get('books',[])):fail('home catalog card count must match site-data')")
s=s.replace("data=json.loads((ROOT/'site-data.generated.json').read_text('utf-8'))","data=CATALOG_DATA_EARLY",1)
s=s.replace("if len(books)!=11:fail(f'expected 11 books, got {len(books)}')","if len(books)<11:fail(f'catalog shrank below protected baseline: {len(books)} books')")
s=s.replace("if len(available)!=10:fail(f'expected 10 available books, got {len(available)}')","if len(available)<10:fail(f'published catalog shrank below protected baseline: {len(available)} books')")
p.write_text(s,encoding='utf-8')

p=Path('scripts/validate_seo.py'); s=p.read_text(encoding='utf-8')
s=s.replace("if len(available) != 10:\n    fail(f'expected 10 available books, got {len(available)}')","if len(available) < 10:\n    fail(f'published catalog shrank below protected baseline: {len(available)} books')")
p.write_text(s,encoding='utf-8')

p=Path('scripts/generate-route-shims.py'); s=p.read_text(encoding='utf-8')
old="    for path in CANONICAL_PATHS:\n        file_path = f\"{path.lstrip('/')}/index.html\"\n        routes[file_path] = (path + '/', path)\n"
new="    canonical_paths = set(CANONICAL_PATHS)\n    data = json.loads((ROOT / 'site-data.generated.json').read_text(encoding='utf-8'))\n    canonical_paths.update('/' + b['slug'] for b in data.get('books', []) if b.get('slug'))\n    for path in sorted(canonical_paths):\n        file_path = f\"{path.lstrip('/')}/index.html\"\n        routes[file_path] = (path + '/', path)\n"
assert old in s;s=s.replace(old,new,1);p.write_text(s,encoding='utf-8')

# admin validator
p=Path('scripts/validate_admin.py'); s=p.read_text(encoding='utf-8')
s=s.replace("'admin/app.js':15000,","'admin/app.js':15000,\n    'admin/book-publisher.js':12000,")
s=s.replace("html=read('admin/index.html'); js=read('admin/app.js'); css=read('admin/style.css')","html=read('admin/index.html'); js=read('admin/app.js'); publisher=read('admin/book-publisher.js'); css=read('admin/style.css')")
s=s.replace("combined=html+js+css","combined=html+js+publisher+css")
s=s.replace("'/admin/app.js','/admin/style.css','commandDialog','diffDialog'","'/admin/app.js','/admin/book-publisher.js','/admin/style.css','commandDialog','diffDialog','bookPublisherDialog'")
s=s.replace("if cp.get('version')!='2.0.0': fail('unexpected control plane version')","if cp.get('version')!='2.1.0': fail('unexpected control plane version')")
s=s.replace("for rel in ('index.html','style.css','app.js','control-plane.json'):","for rel in ('index.html','style.css','app.js','book-publisher.js','control-plane.json'):")
extra="""
book=cp.get('bookPublishing',{})
if book.get('enabled') is not True: fail('Book Publisher must be enabled')
if book.get('binaryPersistence')!='memory-only': fail('binary uploads must remain memory-only')
if int(book.get('bundleFiles',0))>int(pub.get('maxFilesPerChangeSet',0)): fail('Book Publisher bundle exceeds change-set budget')
for marker in ('Book Publisher','stageBook','buildBookRecord','buildShim','routeManifestWithBook','landingFromTemplate','homeWithBook','authorWithBook','%PDF-','image/webp'):
    if marker not in publisher: fail(f'Book Publisher contract missing: {marker}')
for marker in ('binaryStaged','binaryPathAllowed',"encoding:x.encoding||'utf-8'",'__FCC_PUBLISHER_API__'):
    if marker not in js: fail(f'binary publishing runtime missing: {marker}')
if '[hidden]{display:none!important}' not in css: fail('hidden contract regression')
"""
insert_before="if release.get('schema')!='freedom-admin-release-v1': fail('bad admin release schema')"
assert insert_before in s;s=s.replace(insert_before,extra+'\n'+insert_before,1)
s=s.replace("print('PASS: Freedom Control Center V2 is policy-driven, noindex, mobile-first, session-only for credentials, evidence-first, experiment-aware, release-managed and PR-only')","print('PASS: Freedom Control Center V2.1 adds a memory-only Book Publisher with binary-safe PR staging while preserving policy, SEO and release contracts')")
p.write_text(s,encoding='utf-8')

# tests
p=Path('scripts/test_admin_v2.js'); t=p.read_text(encoding='utf-8')
if "__FCC_BOOK_TEST__" not in t:
    t += '''\n\nglobal.__FCC_TEST_MODE__=true;\nrequire('../admin/book-publisher.js');\nconst bp=global.__FCC_BOOK_TEST__;\nassert(bp,'Book Publisher test hook unavailable');\nassert(bp.slugify('Propósito & Direção!')==='proposito-direcao','book slug normalization');\nconst plan=bp.bookPathPlan('novo-livro');\nassert(Object.keys(plan).length===10,'book bundle must plan 10 files');\nassert(plan.cover==='assets/covers/capa-novo-livro.webp','cover path contract');\nassert(plan.pdf==='ebook/novo-livro.pdf','PDF path contract');\nconst book=bp.buildBookRecord({slug:'novo-livro',title:'Novo Livro',badge:'Novo',featured:false,description:'Descrição editorial suficientemente clara.',tags:['a','b','c'],line:'reflexiva',intent:'Para leitores que precisam de direção.',path:'direcao'});\nassert(book.pageUrl==='https://achadostube.com.br/novo-livro','canonical book URL');\nassert(book.pdfUrl.endsWith('/ebook/novo-livro.pdf'),'PDF URL');\nassert(bp.buildShim('novo-livro').includes('static-route-shim-v1 /novo-livro/ -> /novo-livro'),'route shim marker');\nassert(bp.sitemapNode(book,'2026-09-09').includes('<image:image>'),'sitemap image entry');\nassert(bp.feedEntry(book,'2026-09-09').includes('<id>https://achadostube.com.br/novo-livro</id>'),'Atom entry');\nassert(t.binaryPathAllowed('assets/covers/capa-novo-livro.webp'),'cover binary allowlist');\nassert(t.binaryPathAllowed('ebook/novo-livro.pdf'),'PDF binary allowlist');\nassert(!t.binaryPathAllowed('assets/app.js'),'binary allowlist blocks arbitrary path');\nconsole.log('PASS: Book Publisher V2.1 bundle contracts');\n'''
    p.write_text(t,encoding='utf-8')

# admin release
rp=Path('admin/release.json'); rel=json.loads(rp.read_text(encoding='utf-8'));rel['version']='2.1.0';rel['artifacts']['book-publisher.js']=''
for name in ('index.html','style.css','app.js','book-publisher.js','control-plane.json'):
    rel['artifacts'][name]=hashlib.sha256((Path('admin')/name).read_bytes()).hexdigest()
rp.write_text(json.dumps(rel,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
