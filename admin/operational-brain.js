(() => {
  'use strict';
  const CURRENT='freedom-gsc-current-v2', BASE='freedom-gsc-baseline-v2', AUTO='freedom-gsc-auto-applied-v1', DECISION_CTX='freedom-decision-context-v1';
  const state={status:null,evaluation:null,audit:[],loading:false,decisionLoading:false};
  const $=(s,r=document)=>r.querySelector(s);
  const esc=v=>String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const when=v=>v?new Intl.DateTimeFormat('pt-BR',{day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit'}).format(new Date(v)):'—';
  const num=(v,d=0)=>Number(v||0).toLocaleString('pt-BR',{minimumFractionDigits:d,maximumFractionDigits:d});
  const pct=v=>v===null||v===undefined?'—':`${num(v,1)}%`;
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
  function decisionKind(v){return v==='KEEP'?'good':v==='REVERT'?'bad':v==='ITERATE'?'warn':v==='INCONCLUSIVE'?'blue':''}
  function healthKind(v){return v==='READY'?'good':v==='STALE'||v==='NO_SNAPSHOT'?'warn':v==='SETUP'?'warn':'bad'}
  function connector(name,x){const ready=!!x?.ready;return `<div class="gate"><div><strong>${esc(name)}</strong><span>${esc(x?.mode||'')}</span></div>${pill(ready?'READY':'NEEDS CREDENTIAL',ready?'good':'warn')}</div>`}
  function actionRows(actions=[]){return actions.map((a,i)=>`<div class="queue-item"><div class="queue-rank">${esc(a.priority||`#${i+1}`)}</div><div><strong>${esc(a.title)}</strong><span>${esc(a.detail)}<br><b>${esc(a.action)}</b></span></div><div class="queue-score ${priorityKind(a.priority)}">${Number(a.score||0)}</div></div>`).join('')||'<div class="callout"><strong>Sem ação prioritária</strong><span>Nenhuma regra ultrapassou os thresholds atuais.</span></div>'}
  function auditRows(events=[]){return events.slice(0,12).map(e=>`<div class="timeline-item"><strong>${esc(e.type)}</strong><span>${esc(when(e.at))}${e.detail?.mainSha?` · ${esc(String(e.detail.mainSha).slice(0,8))}`:''}${e.detail?.decisionId?` · ${esc(e.detail.decisionId)}`:''}</span></div>`).join('')||'<p class="muted">Ainda não há eventos persistidos.</p>'}

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
    try{state.evaluation=await json('/api/brain/evaluate',{method:'POST',body:'{}'});const a=await json('/api/audit?limit=30');state.audit=a.events||[]}catch(e){state.evaluation={error:e.message,topActions:[]}}finally{state.loading=false;renderBrain()}
  }
  async function syncGsc(){
    const btn=$('[data-brain-sync]');if(btn)btn.disabled=true;
    try{await json('/api/gsc/sync',{method:'POST',body:'{}'});await refreshStatus();await hydrateGsc();await evaluate()}catch(e){alert(`GSC: ${e.message}`)}finally{if(btn)btn.disabled=false}
  }
  function openPreparedEditor(context){
    if(!context?.targetPath)return;
    sessionStorage.setItem(DECISION_CTX,JSON.stringify(context));
    const nav=document.querySelector('#nav [data-view="editor"]');if(nav)nav.click();
    setTimeout(()=>{const q=$('#fileSearch');if(q){q.value=context.targetPath;q.dispatchEvent(new Event('input',{bubbles:true}));q.focus()}},80);
  }
  async function decide(experimentId,verdict,mode){
    if(state.decisionLoading)return;state.decisionLoading=true;renderBrain();
    try{
      const out=await json('/api/decision/ledger',{method:'POST',body:JSON.stringify({action:mode,experimentId,verdict})});
      if(mode==='PREPARE'&&out.context){openPreparedEditor(out.context);return}
      await evaluate();
    }catch(e){alert(`Decisão: ${e.message}`)}finally{state.decisionLoading=false;renderBrain()}
  }

  function experimentCard(x){
    const e=x.evidence||{}, ratio=e.clusterRatio===null||e.clusterRatio===undefined?'—':`${num(e.clusterRatio*100,0)}%`, pos=e.positionDelta===null||e.positionDelta===undefined?'—':`${e.positionDelta>0?'+':''}${num(e.positionDelta,1)}`;
    const waiting=x.status==='WAITING_FINALIZED_GSC'?`Calendário atingido, mas GSC finalizado ainda termina em ${e.dataEnd||'—'}; exige cobertura até ${e.minimumDecisionDate}.`:x.status==='OBSERVING'?`Observando dados finalizados desde ${e.startedAt}; decisão mínima em ${e.minimumDecisionDate}.`:x.status==='WAITING_DATA'?'O GSC finalizado ainda não alcançou o início do experimento.':'';
    const buttons=x.decisionEligible?`<div class="dialog-actions" style="justify-content:flex-start;margin-top:14px"><button class="btn ghost" data-decision="KEEP" data-experiment="${esc(x.id)}">KEEP</button><button class="btn ghost" data-decision="ITERATE" data-mode="PREPARE" data-experiment="${esc(x.id)}">Preparar ITERATE</button><button class="btn ghost" data-decision="REVERT" data-mode="PREPARE" data-experiment="${esc(x.id)}">Preparar REVERT</button><button class="btn ghost" data-decision="INCONCLUSIVE" data-experiment="${esc(x.id)}">INCONCLUSIVE</button></div>`:`<div class="callout ${x.status==='WAITING_FINALIZED_GSC'?'warn':''}" style="margin-top:12px"><strong>Sem decisão ainda</strong><span>${esc(waiting||'A janela causal ainda não satisfaz os gates.')}</span></div>`;
    return `<section class="card pad"><div class="card-head"><div><span class="kicker">${esc(x.id)}</span><h3>${esc(x.name)}</h3><p>${esc(x.decisionRule||'')}</p></div><div class="status-row">${pill(x.status,x.status==='DECISION_WINDOW'?'good':x.status==='WAITING_FINALIZED_GSC'?'warn':'blue')}${x.recommendation!=='WAIT'?pill(`REC ${x.recommendation}`,decisionKind(x.recommendation)):''}</div></div><div class="metric-grid"><section class="metric"><span>Pré · impressões</span><strong>${num(e.pre?.impressions)}</strong><small>${esc(e.preStart||'—')} → ${esc(e.preEnd||'—')}</small></section><section class="metric"><span>Pós · impressões</span><strong>${num(e.post?.impressions)}</strong><small>${esc(e.startedAt||'—')} → ${esc(e.postEnd||'—')}</small></section><section class="metric"><span>Tráfego pós/pré</span><strong>${ratio}</strong><small>janelas de ${num(e.postDays)} dia(s)</small></section><section class="metric"><span>Δ posição</span><strong>${pos}</strong><small>positivo = piora</small></section></div><div class="grid-2" style="margin-top:12px"><div class="callout"><strong>HTML</strong><span>${num(e.htmlPost?.impressions)} impressões pós · share ${pct((e.htmlShare||0)*100)}</span></div><div class="callout"><strong>PDF</strong><span>${num(e.pdfPost?.impressions)} impressões pós · ${num(e.pdfPost?.clicks)} clique(s)</span></div></div>${buttons}</section>`;
  }
  function decisionRows(records=[]){return records.slice(0,8).map(r=>`<div class="gate"><div><strong>${esc(r.experimentName||r.experimentId)}</strong><span>${esc(r.id)} · ${esc(when(r.updatedAt))}${r.githubPr?.number?` · PR #${r.githubPr.number}`:''}</span></div>${pill(`${r.effectiveState||r.state} · ${r.verdict}`,decisionKind(r.verdict))}</div>`).join('')||'<div class="callout"><strong>Nenhuma decisão registrada</strong><span>O ledger começa somente quando uma janela causal fica elegível e uma decisão humana é registrada.</span></div>'}
  function inventoryRows(inv){const items=inv?.items||[];return items.slice(0,10).map(x=>`<div class="gate"><div><strong>${esc(x.title)}</strong><span>${num(x.impressions)} imp · ${num(x.clicks)} clique(s)${x.experimentId?` · ${esc(x.experimentId)}`:''}</span></div>${pill(x.lifecycle,x.lifecycle==='PUBLISHED'?'good':x.lifecycle==='OPTIMIZING'?'warn':x.lifecycle==='DECISION_READY'?'blue':'')}</div>`).join('')||'<p class="muted">Inventário indisponível.</p>'}
  function policyView(policy={}){const objectives=(policy.objectives||[]).map(x=>`<div class="gate"><div><strong>${esc(x.label||x.id)}</strong><span>${num(x.weight)}% de peso</span></div>${pill(x.id||'objective')}</div>`).join('');return `${objectives}<div class="preflight" style="margin-top:10px"><div class="preflight-row good"><i></i><div><strong>Human-approved</strong><span>Sem auto-merge e sem mutação direta de produção.</span></div></div><div class="preflight-row good"><i></i><div><strong>Uma hipótese primária</strong><span>Change Sets experimentais preservam atribuição causal.</span></div></div><div class="preflight-row good"><i></i><div><strong>GSC finalizado obrigatório</strong><span>A decisão só abre quando os dados alcançam a data mínima configurada.</span></div></div></div>`}

  function renderBrain(){
    const main=$('#main');if(!main)return;
    clearActive();const title=$('#viewTitle');if(title)title.textContent='Cérebro operacional';const eye=$('#eyebrow');if(eye)eye.textContent='Freedom Book · closed-loop decision engine';
    const s=state.status||{}, e=state.evaluation||{}, gh=s.connectors?.github||{}, gsc=s.connectors?.gsc||{}, technical=e.technical||{}, dl=e.decisionLoop||{}, obs=e.observability||{}, experiments=dl.experiments||[];
    main.innerHTML=`<div class="stack">
      <section class="card hero"><div><span class="kicker">Operational Brain V2 · Closed Loop</span><h2>Evidência → decisão → Change Set → PR → observação</h2><p>O motor agora separa calendário de evidência finalizada, compara janelas pré/pós equivalentes e mantém decisões ligadas ao PR sem auto-merge ou escrita direta em produção.</p></div><div class="status-row">${pill(technical.releaseExact===false?'RELEASE DRIFT':'RELEASE OK',technical.releaseExact===false?'bad':'good')}${pill(technical.failedRuns?`${technical.failedRuns} CI FAIL`:'CI OK',technical.failedRuns?'bad':'good')}${pill(`GSC ${obs.gsc?.health||'—'}`,healthKind(obs.gsc?.health))}${pill(`${dl.readyCount||0} DECISION READY`,dl.readyCount?'warn':'good')}</div></section>
      <div class="metric-grid"><section class="card metric"><span>GitHub backend</span><strong>${gh.ready?'READY':'SETUP'}</strong><small>${gh.ready?'PR textual server-side':'credencial ausente'}</small></section><section class="card metric"><span>GSC automático</span><strong>${gsc.ready?'READY':'SETUP'}</strong><small>${gsc.lastSync?`sync ${when(gsc.lastSync)}`:'aguardando sync'}</small></section><section class="card metric"><span>Freshness GSC</span><strong>${obs.gsc?.dataLagDays??'—'}d</strong><small>${obs.gsc?.currentEnd?`finalizado até ${esc(obs.gsc.currentEnd)}`:'sem snapshot'}</small></section><section class="card metric"><span>Decision ledger</span><strong>${(dl.records||[]).length}</strong><small>${dl.preparedCount||0} preparado(s) · ${dl.openPrCount||0} PR ligado(s)</small></section></div>
      <div class="grid-2"><section class="card pad"><div class="card-head"><div><span class="kicker">prioridade causal</span><h3>Fila recomendada</h3></div><button class="btn ghost" data-brain-refresh>${state.loading?'Analisando…':'Recalcular'}</button></div><div class="queue">${state.loading?'<div class="callout"><strong>Analisando fontes</strong><span>GitHub, produção, GSC privado, experimentos, inventário e ledger.</span></div>':actionRows(e.topActions)}</div></section><section class="card pad"><div class="card-head"><div><span class="kicker">observabilidade</span><h3>Conectores e freshness</h3></div></div><div class="gate-list">${connector('GitHub server-side',gh)}${connector('Search Console automático',gsc)}<div class="gate"><div><strong>GSC snapshot</strong><span>${num(obs.gsc?.currentRows)} linhas atual · ${num(obs.gsc?.baselineRows)} baseline · sync ${obs.gsc?.syncAgeHours===null||obs.gsc?.syncAgeHours===undefined?'—':`${num(obs.gsc.syncAgeHours,1)}h atrás`}</span></div>${pill(obs.gsc?.health||'—',healthKind(obs.gsc?.health))}</div></div><div class="dialog-actions"><button class="btn ghost" data-brain-sync ${gsc.ready?'':'disabled'}>Sincronizar GSC agora</button></div></section></div>
      <section><div class="card-head" style="margin:4px 0 10px"><div><span class="kicker">experimentos causais</span><h3>Decision windows</h3></div></div><div class="stack">${experiments.map(experimentCard).join('')||'<section class="card pad"><div class="empty">Sem experimento ativo.</div></section>'}</div></section>
      <div class="grid-2"><section class="card pad"><div class="card-head"><div><span class="kicker">decision ledger</span><h3>Histórico e vínculo com PR</h3></div></div><div class="gate-list">${decisionRows(dl.records)}</div></section><section class="card pad"><div class="card-head"><div><span class="kicker">política de decisão</span><h3>Objetivos e guardrails</h3></div></div>${policyView(dl.policy||{})}</section></div>
      <div class="grid-2"><section class="card pad"><div class="card-head"><div><span class="kicker">lifecycle editorial</span><h3>Inventário por estado</h3></div><div class="status-row">${Object.entries(e.inventory?.counts||{}).map(([k,v])=>pill(`${k} ${v}`)).join('')}</div></div><div class="gate-list">${inventoryRows(e.inventory)}</div></section><section class="card pad"><div class="card-head"><div><span class="kicker">audit trail</span><h3>Histórico persistente</h3></div></div><div class="timeline">${auditRows(state.audit.length?state.audit:e.audit)}</div></section></div>
    </div>`;
    $('[data-brain-refresh]')?.addEventListener('click',evaluate);$('[data-brain-sync]')?.addEventListener('click',syncGsc);
    main.querySelectorAll('[data-decision]').forEach(b=>b.addEventListener('click',()=>decide(b.dataset.experiment,b.dataset.decision,b.dataset.mode||'DECIDE')));
  }
  async function openBrain(){await refreshStatus();renderBrain();await evaluate()}

  document.addEventListener('click',e=>{const b=e.target.closest?.('#nav button[data-view]');if(b)$('#brainNav')?.classList.remove('active')},true);
  const start=async()=>{injectNav();await refreshStatus();await hydrateGsc();new MutationObserver(injectNav).observe(document.body,{childList:true,subtree:true})};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
  globalThis.__FCC_OPERATIONAL_BRAIN__={open:openBrain,refresh:evaluate,status:()=>state.status,evaluation:()=>state.evaluation};
})();
