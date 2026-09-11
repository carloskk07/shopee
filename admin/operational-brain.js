(() => {
  'use strict';
  const CURRENT='freedom-gsc-current-v2', BASE='freedom-gsc-baseline-v2', AUTO='freedom-gsc-auto-applied-v1';
  const state={status:null,evaluation:null,audit:[],loading:false};
  const $=(s,r=document)=>r.querySelector(s);
  const esc=v=>String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const when=v=>v?new Intl.DateTimeFormat('pt-BR',{day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit'}).format(new Date(v)):'—';
  const pill=(text,kind='')=>`<span class="pill ${kind}">${esc(text)}</span>`;
  async function json(url,opts={}){const r=await fetch(url,{...opts,headers:{'Content-Type':'application/json',...(opts.headers||{})},cache:'no-store'});const j=await r.json().catch(()=>({}));if(!r.ok)throw new Error(j.error||`${r.status} ${r.statusText}`);return j}

  function injectNav(){
    if($('#brainNav'))return;
    const nav=$('#nav');if(!nav)return;
    const b=document.createElement('button');b.id='brainNav';b.type='button';b.innerHTML='<span>◆</span>Cérebro operacional';
    const quality=nav.querySelector('[data-view="quality"]');nav.insertBefore(b,quality||null);
    b.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();openBrain()});
  }
  function clearActive(){document.querySelectorAll('#nav button').forEach(x=>x.classList.remove('active'));$('#brainNav')?.classList.add('active')}
  function priorityKind(p){return p==='P0'?'bad':p==='P1'?'warn':p==='P2'?'blue':''}
  function connector(name,x){const ready=!!x?.ready;return `<div class="gate"><div><strong>${esc(name)}</strong><span>${esc(x?.mode||'')}</span></div>${pill(ready?'READY':'NEEDS CREDENTIAL',ready?'good':'warn')}</div>`}
  function actionRows(actions=[]){return actions.map((a,i)=>`<div class="queue-item"><div class="queue-rank">${esc(a.priority||`#${i+1}`)}</div><div><strong>${esc(a.title)}</strong><span>${esc(a.detail)}<br><b>${esc(a.action)}</b></span></div><div class="queue-score ${priorityKind(a.priority)}">${Number(a.score||0)}</div></div>`).join('')||'<div class="callout"><strong>Sem ação prioritária</strong><span>Nenhuma regra ultrapassou os thresholds atuais.</span></div>'}
  function auditRows(events=[]){return events.slice(0,10).map(e=>`<div class="timeline-item"><strong>${esc(e.type)}</strong><span>${esc(when(e.at))}${e.detail?.mainSha?` · ${esc(String(e.detail.mainSha).slice(0,8))}`:''}</span></div>`).join('')||'<p class="muted">Ainda não há eventos persistidos.</p>'}

  async function refreshStatus(){
    try{
      state.status=await json('/api/brain/status');
      window.__FCC_SERVER_GITHUB_READY__=!!state.status?.connectors?.github?.ready;
      const session=$('#sessionBtn');if(session&&window.__FCC_SERVER_GITHUB_READY__){session.textContent='GitHub servidor';session.title='Publicação textual usa o backend privado; sessão manual continua disponível para binários.'}
      const n=Number($('#navStaged')?.textContent||0), publish=$('#publishBtn');if(publish&&window.__FCC_SERVER_GITHUB_READY__&&n>0)publish.disabled=false;
    }catch(e){console.warn('Operational Brain status',e)}
  }
  async function hydrateGsc(){
    try{
      const g=await json('/api/gsc/data');
      if(!g.available||!g.current)return;
      const local=JSON.parse(sessionStorage.getItem(CURRENT)||'null');
      if((local?.endDate||'')<(g.current.endDate||'')){
        sessionStorage.setItem(CURRENT,JSON.stringify(g.current));
        if(g.baseline)sessionStorage.setItem(BASE,JSON.stringify(g.baseline));
        const marker=g.current.endDate||g.syncedAt||'ready';
        if(sessionStorage.getItem(AUTO)!==marker){sessionStorage.setItem(AUTO,marker);location.reload()}
      }
    }catch(e){console.warn('GSC private hydrate',e)}
  }
  async function evaluate(){
    if(state.loading)return;state.loading=true;renderBrain();
    try{state.evaluation=await json('/api/brain/evaluate',{method:'POST',body:'{}'});const a=await json('/api/audit?limit=20');state.audit=a.events||[]}catch(e){state.evaluation={error:e.message,topActions:[]}}finally{state.loading=false;renderBrain()}
  }
  async function syncGsc(){
    const btn=$('[data-brain-sync]');if(btn)btn.disabled=true;
    try{await json('/api/gsc/sync',{method:'POST',body:'{}'});await refreshStatus();await hydrateGsc();await evaluate()}catch(e){alert(`GSC: ${e.message}`)}finally{if(btn)btn.disabled=false}
  }
  function renderBrain(){
    const main=$('#main');if(!main)return;
    clearActive();const title=$('#viewTitle');if(title)title.textContent='Cérebro operacional';const eye=$('#eyebrow');if(eye)eye.textContent='Freedom Book · decisão assistida';
    const s=state.status||{}, e=state.evaluation||{}, gh=s.connectors?.github||{}, gsc=s.connectors?.gsc||{};
    const technical=e.technical||{};
    main.innerHTML=`<div class="stack">
      <section class="card hero"><div><span class="kicker">Operational Brain V1</span><h2>O que merece atenção agora</h2><p>Prioridades calculadas por evidência de release, CI, Search Console, experimentos e estado dos conectores. Nenhuma ação altera produção diretamente.</p></div><div class="status-row">${pill(technical.releaseExact===false?'RELEASE DRIFT':'RELEASE OK',technical.releaseExact===false?'bad':'good')}${pill(technical.failedRuns?`${technical.failedRuns} CI FAIL`:'CI OK',technical.failedRuns?'bad':'good')}${pill(e.gsc?.available?'GSC AUTO':'GSC PENDING',e.gsc?.available?'good':'warn')}</div></section>
      <div class="metric-grid"><section class="card metric"><span>GitHub backend</span><strong>${gh.ready?'READY':'SETUP'}</strong><small>${gh.ready?'PR textual sem PAT no navegador':'PAT manual continua como fallback'}</small></section><section class="card metric"><span>GSC automático</span><strong>${gsc.ready?'READY':'SETUP'}</strong><small>${gsc.lastSync?`último sync ${when(gsc.lastSync)}`:'aguardando credenciais/sync'}</small></section><section class="card metric"><span>PRs abertos</span><strong>${Number(technical.openPulls||0)}</strong><small>estado atual do repositório</small></section><section class="card metric"><span>SHA atual</span><strong class="mono">${esc(String(e.mainSha||'—').slice(0,8))}</strong><small>main observada pelo backend</small></section></div>
      <div class="grid-2"><section class="card pad"><div class="card-head"><div><span class="kicker">prioridade causal</span><h3>Fila recomendada</h3></div><button class="btn ghost" data-brain-refresh>${state.loading?'Analisando…':'Recalcular'}</button></div><div class="queue">${state.loading?'<div class="callout"><strong>Analisando fontes</strong><span>GitHub, produção, GSC privado, experimentos e audit trail.</span></div>':actionRows(e.topActions)}</div></section><section class="card pad"><div class="card-head"><div><span class="kicker">conectores privados</span><h3>Automação</h3></div></div><div class="gate-list">${connector('GitHub server-side',gh)}${connector('Search Console automático',gsc)}</div><div class="dialog-actions"><button class="btn ghost" data-brain-sync ${gsc.ready?'':'disabled'}>Sincronizar GSC agora</button></div></section></div>
      <div class="grid-2"><section class="card pad"><div class="card-head"><div><span class="kicker">audit trail</span><h3>Histórico persistente</h3></div></div><div class="timeline">${auditRows(state.audit.length?state.audit:e.audit)}</div></section><section class="card pad"><div class="card-head"><div><span class="kicker">limites conscientes</span><h3>O que ainda exige setup único</h3></div></div><div class="preflight"><div class="preflight-row ${gh.ready?'good':'warn'}"><i></i><div><strong>GitHub secret privado</strong><span>${gh.ready?'Conectado no Netlify.':'Adicionar FCC_GITHUB_TOKEN para eliminar PAT em mudanças textuais.'}</span></div></div><div class="preflight-row ${gsc.ready?'good':'warn'}"><i></i><div><strong>OAuth Search Console</strong><span>${gsc.ready?'Coleta automática habilitada.':`Faltam: ${(gsc.missing||[]).join(', ')||'credenciais OAuth'}.`}</span></div></div><div class="preflight-row good"><i></i><div><strong>Binários de livros</strong><span>Continuam no fluxo seguro atual; o backend textual rejeita base64 deliberadamente.</span></div></div></div></section></div>
    </div>`;
    $('[data-brain-refresh]')?.addEventListener('click',evaluate);$('[data-brain-sync]')?.addEventListener('click',syncGsc);
  }
  async function openBrain(){await refreshStatus();renderBrain();await evaluate()}

  document.addEventListener('click',e=>{const b=e.target.closest?.('#nav button[data-view]');if(b)$('#brainNav')?.classList.remove('active')},true);
  const start=async()=>{injectNav();await refreshStatus();await hydrateGsc();new MutationObserver(injectNav).observe(document.body,{childList:true,subtree:true})};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
  globalThis.__FCC_OPERATIONAL_BRAIN__={open:openBrain,refresh:evaluate,status:()=>state.status};
})();
