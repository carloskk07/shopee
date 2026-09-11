import { appendAudit, readAudit } from '../lib/audit.mts';
import { gscConfig, readGsc } from '../lib/gsc.mts';
import { aggregateRows, evaluateExperiments, readDecisionLedger } from '../lib/decision-engine.mts';

const REPO='carloskk07/shopee';
const GH='https://api.github.com/repos/'+REPO;
const SITE='https://achadostube.com.br';

function ghHeaders(){
  const token=Netlify.env.get('FCC_GITHUB_TOKEN');
  return {Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28',...(token?{Authorization:`Bearer ${token}`}:{})};
}
async function json(url:string,opts:any={}){
  const r=await fetch(url,{...opts,headers:{...(url.startsWith('https://api.github.com')?ghHeaders():{}),...(opts.headers||{})},cache:'no-store'});
  if(!r.ok)throw new Error(`${r.status} ${url}`);
  return r.json();
}
function add(actions:any[],priority:string,score:number,title:string,detail:string,source:string,action:string,meta:any={}){actions.push({priority,score,title,detail,source,action,...meta})}
function iso(v:any){return String(v||'').slice(0,10)}
function dayDiff(a:string,b:string){if(!a||!b)return null;return Math.floor((new Date(`${b}T00:00:00Z`).getTime()-new Date(`${a}T00:00:00Z`).getTime())/86400000)}
function hoursSince(v:any){const t=new Date(String(v||'')).getTime();return Number.isFinite(t)?Math.max(0,(Date.now()-t)/3600000):null}
function querySignals(ds:any){
  const map=new Map<string,any>();
  for(const r of ds?.rows||[]){
    const q=String(r.query||'').trim(); if(!q)continue;
    const x=map.get(q)||{query:q,clicks:0,impressions:0,posWeighted:0};
    x.clicks+=Number(r.clicks||0);x.impressions+=Number(r.impressions||0);x.posWeighted+=Number(r.position||0)*Number(r.impressions||0);map.set(q,x);
  }
  return [...map.values()].map(x=>({...x,ctr:x.impressions?x.clicks/x.impressions*100:0,position:x.impressions?x.posWeighted/x.impressions:0}));
}
function resolveRecordState(rec:any,pulls:any[],releaseExact:boolean,failedRuns:number){
  const pr=rec?.pr?.number?pulls.find((p:any)=>Number(p.number)===Number(rec.pr.number)):null;
  if(!pr)return {...rec,effectiveState:rec.state,githubPr:null};
  let effectiveState=rec.state;
  if(pr.state==='open')effectiveState='PR_OPEN';
  else if(pr.merged_at)effectiveState=releaseExact&&!failedRuns?'OBSERVING':'MERGED';
  else effectiveState='CLOSED';
  return {...rec,effectiveState,githubPr:{number:pr.number,state:pr.state,mergedAt:pr.merged_at||null,url:pr.html_url||rec?.pr?.url||'',headSha:pr.head?.sha||'',mergeCommitSha:pr.merge_commit_sha||''}};
}
function inventoryModel(siteData:any,gsc:any,experiments:any[],records:any[]){
  const rows=gsc?.current?.rows||[], exByUrl=new Map(experiments.filter((x:any)=>x.targetHtml).map((x:any)=>[x.targetHtml,x]));
  const recByPath=new Map(records.filter((x:any)=>x.targetPath).map((x:any)=>[x.targetPath,x]));
  const items=(siteData?.books||[]).map((b:any)=>{
    const html=String(b.pageUrl||`${SITE}/${b.slug||''}`), pdf=String(b.pdfUrl||''), path=b.slug?`${b.slug}.html`:'';
    const relevant=rows.filter((r:any)=>r.page===html||(pdf&&r.page===pdf)), stats=aggregateRows(relevant), exp=exByUrl.get(html), rec=recByPath.get(path);
    let lifecycle=b.available===false?'PLANNED':'PUBLISHED';
    if(exp)lifecycle=exp.status==='DECISION_WINDOW'?'DECISION_READY':'OBSERVING';
    if(rec&&['PREPARED','PR_OPEN','MERGED'].includes(rec.effectiveState||rec.state))lifecycle='OPTIMIZING';
    return {slug:b.slug||'',title:b.title||b.slug||'',html,pdf,lifecycle,impressions:stats.impressions,clicks:stats.clicks,experimentId:exp?.id||null,decisionId:rec?.id||null};
  });
  const counts=items.reduce((a:any,x:any)=>(a[x.lifecycle]=(a[x.lifecycle]||0)+1,a),{});
  return {counts,items:items.sort((a:any,b:any)=>b.impressions-a.impressions).slice(0,16)};
}

export default async (req:Request)=>{
  if(!['GET','POST'].includes(req.method))return new Response('Method not allowed',{status:405});
  const actions:any[]=[]; const failures:string[]=[];
  const safe=async<T>(name:string,fn:()=>Promise<T>,fallback:T)=>{try{return await fn()}catch(_){failures.push(name);return fallback}};
  const [commit,runsResp,pulls,cp,siteData,repoRelease,prodRelease,gsc,audit,ledger]=await Promise.all([
    safe('github_commit',()=>json(`${GH}/commits/main`),null),
    safe('github_runs',()=>json(`${GH}/actions/runs?branch=main&per_page=40`),{workflow_runs:[]}),
    safe('github_pulls',()=>json(`${GH}/pulls?state=all&sort=updated&direction=desc&per_page=30`),[]),
    safe('control_plane',()=>json(`https://raw.githubusercontent.com/${REPO}/main/admin/control-plane.json`),{}),
    safe('site_data',()=>json(`https://raw.githubusercontent.com/${REPO}/main/site-data.generated.json`),{}),
    safe('repo_release',()=>json(`https://raw.githubusercontent.com/${REPO}/main/release.json`),null),
    safe('prod_release',()=>json(`${SITE}/release.json?brain=${Date.now()}`),null),
    readGsc(),
    readAudit(16),
    readDecisionLedger(),
  ]);
  const mainSha=(commit as any)?.sha||'';
  const runs=((runsResp as any)?.workflow_runs||[]).filter((r:any)=>r.head_sha===mainSha);
  const failedRuns=runs.filter((r:any)=>r.status==='completed'&&r.conclusion&&!['success','skipped','neutral'].includes(r.conclusion));
  const pendingRuns=runs.filter((r:any)=>r.status!=='completed');
  const releaseExact=!!repoRelease&&!!prodRelease&&JSON.stringify(repoRelease)===JSON.stringify(prodRelease);
  const decisionPolicy=(cp as any)?.decisionPolicy||{};
  const experiments=evaluateExperiments((cp as any)?.experiments||[],gsc,decisionPolicy);
  const records=(ledger||[]).map((x:any)=>resolveRecordState(x,Array.isArray(pulls)?pulls:[],releaseExact,failedRuns.length));

  if(!releaseExact)add(actions,'P0',100,'Restabelecer paridade da produção','O release publicado não coincide com a autoridade do repositório.','release','Bloquear publicação e investigar o deploy atual.');
  if(failedRuns.length)add(actions,'P0',98,'Corrigir CI do release atual',`${failedRuns.length} workflow(s) do SHA atual falharam.`,'github-actions','Corrigir a causa antes de qualquer nova publicação.');
  else if(pendingRuns.length)add(actions,'P2',45,'Aguardar gates em execução',`${pendingRuns.length} workflow(s) do release atual ainda estão rodando.`,'github-actions','Não tomar decisão de release até os gates terminarem.');

  const githubReady=!!Netlify.env.get('FCC_GITHUB_TOKEN');
  if(!githubReady)add(actions,'P1',84,'Ativar publicação GitHub server-side','O backend está pronto, mas ainda falta o secret de escrita.','connector','Adicionar FCC_GITHUB_TOKEN ao ambiente privado do Netlify.');
  const gcfg=gscConfig();
  if(!gcfg.ready)add(actions,'P1',88,'Conectar Search Console automático','O motor SEO automático está instalado, mas faltam credenciais OAuth privadas.','connector','Adicionar GSC_CLIENT_ID, GSC_CLIENT_SECRET e GSC_REFRESH_TOKEN no Netlify.');
  else if(!gsc)add(actions,'P1',82,'Executar primeira sincronização GSC','As credenciais existem, mas ainda não há snapshot persistido.','gsc','Executar a sincronização manual uma vez; depois ela roda diariamente.');

  for(const exp of experiments){
    if(exp.status==='DECISION_WINDOW')add(actions,'P1',90,`Decidir experimento: ${exp.name}`,`GSC finalizado cobre ${exp.evidence.dataEnd}; janela pré/pós equivalente com ${exp.evidence.postDays} dia(s). Recomendação: ${exp.recommendation}.`,'experiment',exp.decisionRule||'Registrar uma decisão explícita.',{experimentId:exp.id,recommendation:exp.recommendation});
    else if(exp.status==='WAITING_FINALIZED_GSC')add(actions,'P2',52,`Aguardar GSC finalizado: ${exp.name}`,`A data mínima chegou no calendário, mas o GSC finalizado termina em ${exp.evidence.dataEnd||'—'} e ainda não cobre ${exp.evidence.minimumDecisionDate}.`,'experiment','Não alterar o experimento até a evidência finalizada alcançar a data mínima.',{experimentId:exp.id});
  }

  if(gsc?.current){
    const signals=querySignals(gsc.current);
    const ctr=signals.filter(x=>x.impressions>=30&&x.position<=10&&x.ctr<2).sort((a,b)=>b.impressions-a.impressions)[0];
    const strike=signals.filter(x=>x.impressions>=20&&x.position>=8&&x.position<=20).sort((a,b)=>b.impressions-a.impressions)[0];
    const hasDecisionWindow=experiments.some((x:any)=>x.status==='DECISION_WINDOW');
    if(ctr&&!hasDecisionWindow)add(actions,'P1',80,'Melhorar CTR de uma consulta já posicionada',`“${ctr.query}” tem ${Math.round(ctr.impressions)} impressões, posição média ${ctr.position.toFixed(1)} e CTR ${ctr.ctr.toFixed(2)}%.`,'gsc','Revisar title/description da página dominante sem criar uma URL nova.');
    if(strike&&!hasDecisionWindow)add(actions,'P1',76,'Empurrar consulta em striking distance',`“${strike.query}” está em posição média ${strike.position.toFixed(1)} com ${Math.round(strike.impressions)} impressões.`,'gsc','Fortalecer a página existente e preservar atribuição causal.');
  }
  const openPulls=Array.isArray(pulls)?pulls.filter((p:any)=>p.state==='open'):[];
  if(openPulls.length)add(actions,'P2',55,'Revisar Pull Requests abertos',`${openPulls.length} PR(s) permanecem abertos no repositório.`,'github','Fechar, integrar ou justificar os PRs para evitar estado operacional ambíguo.');
  if(!actions.some(a=>a.priority==='P0'||a.priority==='P1'))add(actions,'P3',30,'Manter observação controlada','Nenhum bloqueio ou oportunidade forte ultrapassou os thresholds atuais.','brain','Evitar mudanças cosméticas; aguardar evidência nova.');

  actions.sort((a,b)=>b.score-a.score);
  const currentEnd=iso(gsc?.current?.endDate), syncAgeHours=hoursSince(gsc?.syncedAt), dataLagDays=currentEnd?dayDiff(currentEnd,new Date().toISOString().slice(0,10)):null;
  const gscHealth=!gcfg.ready?'SETUP':!gsc?'NO_SNAPSHOT':dataLagDays!==null&&dataLagDays>6?'STALE':'READY';
  const observability={gsc:{health:gscHealth,lastSync:gsc?.syncedAt||null,syncAgeHours,currentEnd,dataLagDays,currentRows:gsc?.current?.rows?.length||0,baselineRows:gsc?.baseline?.rows?.length||0},github:{health:githubReady?'READY':'SETUP',mainSha,failedRuns:failedRuns.length,pendingRuns:pendingRuns.length,openPulls:openPulls.length,lastPr:pulls?.[0]?{number:pulls[0].number,state:pulls[0].state,updatedAt:pulls[0].updated_at}:null}};
  const inventory=inventoryModel(siteData,gsc,experiments,records);
  const result={schema:'freedom-operational-brain-v2',generatedAt:new Date().toISOString(),mainSha,technical:{releaseExact,failedRuns:failedRuns.length,pendingRuns:pendingRuns.length,openPulls:openPulls.length},connectors:{github:{ready:githubReady},gsc:{ready:gcfg.ready,lastSync:gsc?.syncedAt||null}},observability,gsc:{available:!!gsc,currentEnd},decisionLoop:{policy:decisionPolicy,experiments,records:records.slice(0,12),readyCount:experiments.filter((x:any)=>x.decisionEligible).length,preparedCount:records.filter((x:any)=>x.effectiveState==='PREPARED').length,openPrCount:records.filter((x:any)=>x.effectiveState==='PR_OPEN').length},inventory,topActions:actions.slice(0,8),audit,collectionFailures:failures};
  await appendAudit('brain_evaluated',{mainSha,releaseExact,failedRuns:failedRuns.length,actions:result.topActions.length,gscAvailable:!!gsc,decisionReady:result.decisionLoop.readyCount});
  return Response.json(result);
};

export const config={path:'/api/brain/evaluate'};
