(() => {
  'use strict';
  const state={ledger:null,gsc:null,config:null,siteData:null,loading:false,error:null};
  const $=(s,r=document)=>r.querySelector(s);
  const esc=v=>String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const num=(v,d=0)=>Number(v||0).toLocaleString('pt-BR',{minimumFractionDigits:d,maximumFractionDigits:d});
  const money=(value,currency='BRL')=>new Intl.NumberFormat('pt-BR',{style:'currency',currency,maximumFractionDigits:2}).format(Number(value||0));
  const pill=(text,kind='')=>`<span class="pill ${kind}">${esc(text)}</span>`;
  async function json(url,opts={}){const r=await fetch(url,{...opts,headers:{'Content-Type':'application/json',...(opts.headers||{})},cache:'no-store'});const j=await r.json().catch(()=>({}));if(!r.ok)throw new Error(j.error||`${r.status} ${r.statusText}`);return j}
  function normalizePath(url){try{const u=new URL(url,location.origin);return (u.pathname.replace(/\/$/,'')||'/')}catch(_){return String(url||'').replace(/\/$/,'')||'/'}}
  function channelState(key,group={}){
    const offers=Array.isArray(group.offers)?group.offers:[];
    const validOffers=offers.filter(x=>x&&x.enabled!==false&&/^https:\/\//.test(String(x.url||'')));
    if(key==='support')return group.enabled&&/^https:\/\//.test(String(group.url||''))?{status:'ACTIVE',kind:'good',detail:'CTA público verificado'}:{status:'BLOCKED',kind:'bad',detail:'URL de apoio ausente'};
    if(key==='ads')return group.enabled?{status:'ACTIVE',kind:'warn',detail:'revisar impacto e consentimento'}:{status:'WAITING_EVIDENCE',kind:'blue',detail:'não ativar sem escala e decisão explícita'};
    if(group.enabled&&validOffers.length)return {status:'ACTIVE',kind:'good',detail:`${validOffers.length} oferta(s) ativa(s)`};
    if(validOffers.length)return {status:'READY',kind:'blue',detail:`${validOffers.length} oferta(s) pronta(s), módulo desligado`};
    return {status:'DORMANT',kind:'',detail:'sem oferta comercial real'};
  }
  function activeSpecificForPath(path){
    const cfg=state.config||{};
    for(const key of ['affiliates','premium','kdp']){
      const g=cfg[key]||{};if(g.enabled!==true)continue;
      for(const o of g.offers||[]){
        if(o?.enabled===false||!/^https:\/\//.test(String(o?.url||'')))continue;
        const paths=Array.isArray(o.paths)?o.paths.map(normalizePath):[];
        if(!paths.length||paths.includes(path))return key.toUpperCase();
      }
    }
    return null;
  }
  function aggregateGsc(){
    const rows=state.gsc?.current?.rows||[], map=new Map();
    const books=state.siteData?.books||[];
    const ownerByUrl=new Map();
    for(const b of books){if(b.pageUrl)ownerByUrl.set(String(b.pageUrl),String(b.pageUrl));if(b.pdfUrl)ownerByUrl.set(String(b.pdfUrl),String(b.pageUrl||b.pdfUrl))}
    for(const r of rows){
      const raw=String(r.page||'');if(!raw)continue;const page=ownerByUrl.get(raw)||raw;
      const x=map.get(page)||{page,clicks:0,impressions:0,posWeighted:0};
      const imp=Number(r.impressions||0);x.clicks+=Number(r.clicks||0);x.impressions+=imp;x.posWeighted+=Number(r.position||0)*imp;map.set(page,x);
    }
    return [...map.values()].map(x=>({...x,position:x.impressions?x.posWeighted/x.impressions:0,path:normalizePath(x.page)})).sort((a,b)=>b.clicks-a.clicks||b.impressions-a.impressions||a.position-b.position);
  }
  function opportunityRows(){
    return aggregateGsc().slice(0,10).map(x=>{
      const specific=activeSpecificForPath(x.path);let stateName='OBSERVE',kind='',action='Continuar coletando evidência.';
      if(x.clicks>0&&!specific){stateName='MONETIZATION_GAP';kind='warn';action='Há visita orgânica confirmada, mas nenhuma oferta específica ativa. Mapear somente uma oferta real e contextual.'}
      else if(x.clicks>0&&specific){stateName='MEASURE';kind='good';action=`Canal ${specific} ativo: medir clique, conversão e receita antes de expandir.`}
      else if(x.impressions>=5){stateName='ACQUISITION_FIRST';kind='blue';action='Existe descoberta, mas sem clique confirmado. Melhorar aquisição antes de acrescentar pressão comercial.'}
      return `<tr><td><strong>${esc(x.path)}</strong></td><td>${num(x.clicks)}</td><td>${num(x.impressions)}</td><td>${num(x.position,1)}</td><td>${pill(stateName,kind)}</td><td>${esc(action)}</td></tr>`;
    }).join('');
  }
  function revenueSummary(){
    const records=(state.ledger?.records||[]).filter(x=>!x.voidedAt), cutoff=Date.now()-30*86400000, last30=records.filter(x=>new Date(`${x.date}T00:00:00Z`).getTime()>=cutoff);
    const sum=rows=>rows.reduce((m,r)=>(m[r.currency]=(m[r.currency]||0)+Number(r.amount||0),m),{});
    return {records,last30,total:sum(records),recent:sum(last30)};
  }
  function moneyList(map){const xs=Object.entries(map||{});return xs.length?xs.map(([c,v])=>money(v,c)).join(' · '):'SEM REGISTROS'}
  function channelCard(key,label){const g=state.config?.[key]||{}, s=channelState(key,g);return `<section class="card pad"><div class="card-head"><div><span class="kicker">${esc(key.toUpperCase())}</span><h3>${esc(label)}</h3><p>${esc(s.detail)}</p></div>${pill(s.status,s.kind)}</div></section>`}
  function nextAction(){
    const top=aggregateGsc()[0], rev=revenueSummary();
    if(!rev.records.length)return {title:'Estabelecer verdade financeira',text:'O ledger ainda está vazio. Registre somente receitas confirmadas (LivePix, KDP, afiliados, premium ou ads); zero registro não será tratado como zero receita.'};
    if(top&&top.clicks>0&&!activeSpecificForPath(top.path))return {title:'Fechar lacuna de monetização',text:`${top.path} já recebeu clique orgânico no snapshot atual e não possui oferta específica ativa. A próxima ação é mapear uma oferta real, não inserir banner genérico.`};
    if(top&&top.clicks===0)return {title:'Aquisição antes de pressão comercial',text:'A maior oportunidade atual ainda não tem clique orgânico confirmado. Preserve o suporte discreto e concentre esforço em aquisição/CTR antes de adicionar novas ofertas.'};
    return {title:'Medir antes de expandir',text:'Já existe tráfego e monetização configurada. Use receita por canal e os eventos consentidos para decidir KEEP, ITERATE ou PAUSE.'};
  }
  function render(){
    const main=$('#main');if(!main)return;document.querySelectorAll('#nav button').forEach(x=>x.classList.remove('active'));$('#nav [data-view="money"]')?.classList.add('active');$('#viewTitle').textContent='Monetização';
    if(state.loading){main.innerHTML='<div class="stack"><section class="card pad"><span class="kicker">Monetization Intelligence V2</span><h2>Carregando verdade econômica…</h2><p>GSC privado, portfólio de canais e ledger financeiro.</p></section></div>';return}
    if(state.error){main.innerHTML=`<div class="stack"><section class="card pad"><span class="kicker">Monetization Intelligence V2</span><h2>Falha ao carregar</h2><p>${esc(state.error)}</p><button class="btn ghost" data-money-refresh>Tentar novamente</button></section></div>`;return}
    const rev=revenueSummary(), gscEnd=state.gsc?.current?.endDate||'—', currentRows=state.gsc?.current?.rows?.length||0, next=nextAction();
    const records=(state.ledger?.records||[]).slice(0,12).map(r=>`<tr><td>${esc(r.date)}</td><td>${pill(r.channel,r.voidedAt?'':'blue')}</td><td>${esc(money(r.amount,r.currency))}</td><td>${esc(r.source||'manual')}</td><td>${esc(r.pagePath||'—')}</td><td>${r.voidedAt?pill('ANULADO','warn'):`<button class="mini-btn" data-money-void="${esc(r.id)}">Anular</button>`}</td></tr>`).join('');
    main.innerHTML=`<div class="stack">
      <section class="card hero"><div><span class="kicker">Monetization Intelligence V2 · PRIVATE ECONOMIC LAYER</span><h2>Demanda → canal → clique → receita confirmada</h2><p>GSC mede descoberta; o ledger registra dinheiro realizado. O painel não converte impressões em receita fictícia e não ativa canais comerciais sem oferta real.</p></div><div class="status-row">${pill('SUPPORT ACTIVE','good')}${pill(`GSC ${gscEnd}`,'blue')}${pill(`${rev.records.length} REGISTRO(S)`)}</div></section>
      <div class="metric-grid"><section class="card metric"><span>Receita 30 dias</span><strong>${esc(moneyList(rev.recent))}</strong><small>somente registros confirmados</small></section><section class="card metric"><span>Receita registrada</span><strong>${esc(moneyList(rev.total))}</strong><small>sem conversão cambial artificial</small></section><section class="card metric"><span>GSC finalizado</span><strong>${esc(gscEnd)}</strong><small>${num(currentRows)} linhas privadas</small></section><section class="card metric"><span>Tracking público</span><strong>CONSENTED</strong><small>support_open · affiliate_open · premium_open</small></section></div>
      <section class="card pad"><div class="card-head"><div><span class="kicker">next best action</span><h3>${esc(next.title)}</h3><p>${esc(next.text)}</p></div><button class="btn ghost" data-money-refresh>Atualizar</button></div></section>
      <div class="grid-3">${channelCard('support','Apoio / LivePix')}${channelCard('affiliates','Afiliados')}${channelCard('kdp','KDP / venda de livros')}${channelCard('premium','Premium')}${channelCard('ads','Publicidade')}</div>
      <section class="card pad"><div class="card-head"><div><span class="kicker">organic × monetization</span><h3>Triagem por página</h3><p>Classificação operacional, não previsão de receita.</p></div></div><div class="table-wrap"><table><thead><tr><th>Página</th><th>Cliques</th><th>Imp.</th><th>Pos.</th><th>Estado</th><th>Próxima ação</th></tr></thead><tbody>${opportunityRows()||'<tr><td colspan="6">Sem páginas com evidência GSC no snapshot atual.</td></tr>'}</tbody></table></div></section>
      <div class="grid-2"><section class="card pad"><div class="card-head"><div><span class="kicker">private ledger</span><h3>Registrar receita confirmada</h3><p>Financeiro privado no Netlify Blobs. Nada é gravado no repositório público.</p></div></div><form id="monetizationRevenueForm" class="stack" style="gap:10px"><div class="grid-2"><label>Data<input name="date" type="date" required value="${new Date().toISOString().slice(0,10)}"></label><label>Canal<select name="channel"><option>SUPPORT</option><option>KDP</option><option>AFFILIATE</option><option>PREMIUM</option><option>ADS</option><option>OTHER</option></select></label></div><div class="grid-2"><label>Valor<input name="amount" type="number" min="0.01" step="0.01" required placeholder="0,00"></label><label>Moeda<input name="currency" maxlength="3" value="BRL" required></label></div><label>Origem<input name="source" maxlength="80" placeholder="LivePix, KDP, Amazon BR, etc."></label><label>Página relacionada<input name="pagePath" maxlength="240" placeholder="/o-peso-de-ser-forte-o-tempo-todo"></label><label>Nota<input name="note" maxlength="320" placeholder="Opcional"></label><div><button class="btn primary" type="submit">Registrar receita</button></div></form></section><section class="card pad"><div class="card-head"><div><span class="kicker">measurement contract</span><h3>O que o painel considera verdade</h3></div></div><div class="preflight"><div class="preflight-row good"><i></i><div><strong>Demanda</strong><span>Search Console finalizado: consultas, páginas, cliques, impressões e posição.</span></div></div><div class="preflight-row good"><i></i><div><strong>Interação</strong><span>Eventos GA/TikTok somente após consentimento; nenhum novo tracker foi instalado.</span></div></div><div class="preflight-row good"><i></i><div><strong>Receita</strong><span>Somente valor confirmado no ledger; sem estimar conversões ou RPM inexistentes.</span></div></div><div class="preflight-row warn"><i></i><div><strong>Conversão</strong><span>Até existir integração do provedor, venda/doação é registrada manualmente ou por importação futura.</span></div></div></div><div style="margin-top:12px"><button class="btn ghost" data-money-config>Abrir monetization.json</button></div></section></div>
      <section class="card pad"><div class="card-head"><div><span class="kicker">revenue history</span><h3>Ledger recente</h3></div></div><div class="table-wrap"><table><thead><tr><th>Data</th><th>Canal</th><th>Valor</th><th>Origem</th><th>Página</th><th></th></tr></thead><tbody>${records||'<tr><td colspan="6">Nenhuma receita registrada. Isso significa “sem dado”, não “receita zero”.</td></tr>'}</tbody></table></div></section>
    </div>`;
  }
  async function load(){state.loading=true;state.error=null;render();try{const [ledger,gsc,config,siteData]=await Promise.all([json('/api/monetization/ledger'),json('/api/gsc/data'),json(`/monetization.json?mi=${Date.now()}`),json(`/site-data.generated.json?mi=${Date.now()}`)]);Object.assign(state,{ledger,gsc,config,siteData})}catch(e){state.error=e.message}finally{state.loading=false;render()}}
  function openConfig(){const nav=$('#nav [data-view="editor"]');nav?.click();setTimeout(()=>{const q=$('#fileSearch');if(q){q.value='monetization.json';q.dispatchEvent(new Event('input',{bubbles:true}));q.focus()}},80)}
  async function record(form){const fd=new FormData(form), body={action:'RECORD',date:fd.get('date'),channel:fd.get('channel'),amount:Number(fd.get('amount')),currency:fd.get('currency'),source:fd.get('source'),pagePath:fd.get('pagePath'),note:fd.get('note')};await json('/api/monetization/ledger',{method:'POST',body:JSON.stringify(body)});await load()}
  async function voidRecord(id){if(!confirm('Anular este registro financeiro? O histórico será preservado.'))return;await json('/api/monetization/ledger',{method:'POST',body:JSON.stringify({action:'VOID',id,reason:'correção administrativa'})});await load()}
  function bind(){
    document.addEventListener('click',e=>{const money=e.target.closest?.('#nav [data-view="money"]');if(money){e.preventDefault();e.stopImmediatePropagation();load();return}const refresh=e.target.closest?.('[data-money-refresh]');if(refresh){e.preventDefault();load();return}const cfg=e.target.closest?.('[data-money-config]');if(cfg){e.preventDefault();openConfig();return}const v=e.target.closest?.('[data-money-void]');if(v){e.preventDefault();voidRecord(v.dataset.moneyVoid).catch(err=>alert(err.message))}},true);
    document.addEventListener('submit',e=>{if(e.target?.id!=='monetizationRevenueForm')return;e.preventDefault();record(e.target).catch(err=>alert(`Monetização: ${err.message}`))});
  }
  window.__FCC_MONETIZATION_INTELLIGENCE__={open:load,refresh:load,state};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bind,{once:true});else bind();
})();
