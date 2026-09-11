(() => {
  'use strict';

  const $=(s,r=document)=>r.querySelector(s);
  const $$=(s,r=document)=>[...r.querySelectorAll(s)];
  const esc=v=>String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot',"'":'&#39;'}[m]));
  let data=null;

  function pill(text,kind=''){return `<span class="pill ${kind}">${esc(text)}</span>`}
  function card(title,body,subtitle='Knowledge Layer'){return `<section class="card pad"><div class="card-head"><div><span class="kicker">${esc(subtitle)}</span><h3>${esc(title)}</h3></div></div>${body}</section>`}
  function row(label,value,kind='good'){return `<div class="preflight-row ${kind}"><i></i><div><strong>${esc(label)}</strong><span>${esc(value)}</span></div></div>`}

  function render(){
    if(!data)return;
    const main=$('#main');if(!main)return;
    const priorities=(data.priorityPolicy||[]).map(x=>`<div class="preflight-row good"><i></i><div><strong>${esc(`${x.rank}. ${x.name}`)}</strong><span>${esc(x.rule)}</span></div></div>`).join('');
    const guards=(data.guardrails||[]).map(x=>`<div class="preflight-row warn"><i></i><div><strong>Guardrail</strong><span>${esc(x)}</span></div></div>`).join('');
    const caps=(data.capabilities||[]).map(x=>`<div class="preflight-row good"><i></i><div><strong>Disponível</strong><span>${esc(x)}</span></div></div>`).join('');
    const sources=(data.sourcePolicy||[]).map(x=>`<div class="preflight-row ${x.trust==='AUTHORITATIVE_PRIVATE'?'warn':'good'}"><i></i><div><strong>${esc(x.source)} · ${esc(x.trust)}</strong><span>${esc(`${x.use}${x.persistence?` · ${x.persistence}`:''}`)}</span></div></div>`).join('');
    const focus=data.currentFocus||{};
    const gsc=data.privateEvidence?.searchConsole||{};
    const ledger=data.privateEvidence?.decisionLedger||{};
    main.innerHTML=`
      <section class="card pad"><div class="card-head"><div><span class="kicker">Freedom operational knowledge</span><h2>Conhecimento operacional</h2><p>Camada versionada de regras, prioridades, capacidades e fontes confiáveis do projeto. Evidência privada fica fora do repositório público e somente a política operacional é versionada.</p></div>${pill(data.classification,'good')}</div></section>
      <div class="metric-grid">
        <section class="card metric"><span>Knowledge Layer</span><strong>${esc(data.version)}</strong><small>admin ${esc(data.adminVersion)}</small></section>
        <section class="card metric"><span>Produção</span><strong>${esc(data.identity?.hosting||'—')}</strong><small>${esc(data.identity?.productionBranch||'—')}</small></section>
        <section class="card metric"><span>Publicação</span><strong>PR ONLY</strong><small>main protegida · sem auto-merge</small></section>
        <section class="card metric"><span>GSC privado</span><strong>${esc(gsc.classification||'—')}</strong><small>nunca persistido no GitHub</small></section>
      </div>
      ${card('Foco atual',`<div class="preflight">${row(focus.name||'Sem experimento ativo',focus.rule||'—')}${row('Status',`${focus.status||'—'} · decisão mínima ${focus.minimumDecisionDate||'—'}`)}</div>`,'Experiment authority')}
      ${card('Prioridade de decisão',`<div class="preflight">${priorities}</div>`,'ROI por tempo')}
      ${card('Capacidades já operacionais',`<div class="preflight">${caps}</div>`,'Control Center')}
      ${card('Guardrails',`<div class="preflight">${guards}</div>`,'Anti-regressão')}
      ${card('Fontes e confiança',`<div class="preflight">${sources}</div>`,'Evidence provenance')}
      ${card('Privacidade do Search Console',`<div class="callout"><strong>${esc(gsc.classification||'PRIVATE')}</strong><span>${esc(gsc.rule||'')}</span></div><div class="preflight">${row('Persistência no repositório',String(gsc.repositoryPersistence))}${row('Persistência privada',gsc.privateServerPersistence||'—')}${row('Hidratação no navegador',gsc.browserPersistence||'—')}${row('Fonte esperada',gsc.expectedSource||'—')}</div>`,'Private evidence contract')}
      ${card('Decision Ledger',`<div class="callout"><strong>${esc(ledger.classification||'PRIVATE')}</strong><span>${esc(ledger.rule||'')}</span></div><div class="preflight">${row('Persistência no repositório',String(ledger.repositoryPersistence))}</div>`,'Closed-loop evidence')}
    `;
    $('#viewTitle').textContent='Conhecimento';
    $$('#nav button').forEach(b=>b.classList.remove('active'));
    $('#knowledgeNav')?.classList.add('active');
  }

  async function load(){
    const r=await fetch(`/admin/knowledge.json?fcc=${Date.now()}`,{cache:'no-store'});if(!r.ok)throw new Error(`knowledge ${r.status}`);
    const j=await r.json();if(j.schema!=='freedom-knowledge-layer-v1')throw new Error('knowledge schema inválido');
    data=j;
    const nav=$('#nav');
    if(nav&&!$('#knowledgeNav')){
      const b=document.createElement('button');b.id='knowledgeNav';b.type='button';b.innerHTML='<span>◆</span>Conhecimento';
      const settings=nav.querySelector('[data-view="settings"]');nav.insertBefore(b,settings||null);
      b.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();render()});
    }
    globalThis.__FCC_KNOWLEDGE_LAYER__={data,render,refresh:load};
  }

  window.addEventListener('DOMContentLoaded',()=>{load().catch(e=>console.warn('Knowledge Layer',e))});
})();
