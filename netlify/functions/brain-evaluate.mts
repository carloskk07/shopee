import { appendAudit, readAudit } from '../lib/audit.mts';
import { gscConfig, readGsc } from '../lib/gsc.mts';

const REPO='carloskk07/shopee';
const GH='https://api.github.com/repos/'+REPO;
const SITE='https://achadostube.com.br';

function ghHeaders(){
  const token=Netlify.env.get('FCC_GITHUB_TOKEN');
  return {Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28',...(token?{Authorization:`Bearer ${token}`}:{})};
}
async function json(url:string,opts:any={}){
  const r=await fetch(url,{...opts,headers:{...(url.startsWith('https://api.github.com')?ghHeaders():{}),...(opts.headers||{})}});
  if(!r.ok)throw new Error(`${r.status} ${url}`);
  return r.json();
}
function add(actions:any[],priority:string,score:number,title:string,detail:string,source:string,action:string){actions.push({priority,score,title,detail,source,action})}
function querySignals(ds:any){
  const map=new Map<string,any>();
  for(const r of ds?.rows||[]){
    const q=String(r.query||'').trim(); if(!q)continue;
    const x=map.get(q)||{query:q,clicks:0,impressions:0,posWeighted:0};
    x.clicks+=Number(r.clicks||0);x.impressions+=Number(r.impressions||0);x.posWeighted+=Number(r.position||0)*Number(r.impressions||0);map.set(q,x);
  }
  return [...map.values()].map(x=>({...x,ctr:x.impressions?x.clicks/x.impressions*100:0,position:x.impressions?x.posWeighted/x.impressions:0}));
}

export default async (req:Request)=>{
  if(!['GET','POST'].includes(req.method))return new Response('Method not allowed',{status:405});
  const actions:any[]=[]; const failures:string[]=[];
  const safe=async<T>(name:string,fn:()=>Promise<T>,fallback:T)=>{try{return await fn()}catch(e){failures.push(name);return fallback}};
  const [commit,runsResp,pulls,cp,repoRelease,prodRelease,gsc,audit]=await Promise.all([
    safe('github_commit',()=>json(`${GH}/commits/main`),null),
    safe('github_runs',()=>json(`${GH}/actions/runs?branch=main&per_page=40`),{workflow_runs:[]}),
    safe('github_pulls',()=>json(`${GH}/pulls?state=open&per_page=20`),[]),
    safe('control_plane',()=>json(`https://raw.githubusercontent.com/${REPO}/main/admin/control-plane.json`),{}),
    safe('repo_release',()=>json(`https://raw.githubusercontent.com/${REPO}/main/release.json`),null),
    safe('prod_release',()=>json(`${SITE}/release.json?brain=${Date.now()}`),null),
    readGsc(),
    readAudit(12),
  ]);
  const mainSha=(commit as any)?.sha||'';
  const runs=((runsResp as any)?.workflow_runs||[]).filter((r:any)=>r.head_sha===mainSha);
  const failedRuns=runs.filter((r:any)=>r.status==='completed'&&r.conclusion&&!['success','skipped','neutral'].includes(r.conclusion));
  const pendingRuns=runs.filter((r:any)=>r.status!=='completed');
  const releaseExact=!!repoRelease&&!!prodRelease&&JSON.stringify(repoRelease)===JSON.stringify(prodRelease);

  if(!releaseExact)add(actions,'P0',100,'Restabelecer paridade da produção','O release publicado não coincide com a autoridade do repositório.','release','Bloquear publicação e investigar o deploy atual.');
  if(failedRuns.length)add(actions,'P0',98,'Corrigir CI do release atual',`${failedRuns.length} workflow(s) do SHA atual falharam.`, 'github-actions','Abrir o workflow que falhou e corrigir a causa antes de publicar novamente.');
  else if(pendingRuns.length)add(actions,'P2',45,'Aguardar gates em execução',`${pendingRuns.length} workflow(s) do release atual ainda estão rodando.`,'github-actions','Não tomar decisão de release até os gates terminarem.');

  const githubReady=!!Netlify.env.get('FCC_GITHUB_TOKEN');
  if(!githubReady)add(actions,'P1',84,'Ativar publicação GitHub server-side','O backend está pronto, mas ainda falta o secret de escrita. O PAT manual continua como fallback.','connector','Adicionar FCC_GITHUB_TOKEN ao ambiente privado do Netlify.');
  const gcfg=gscConfig();
  if(!gcfg.ready)add(actions,'P1',88,'Conectar Search Console automático','O motor SEO automático está instalado, mas faltam credenciais OAuth privadas.','connector','Adicionar GSC_CLIENT_ID, GSC_CLIENT_SECRET e GSC_REFRESH_TOKEN no Netlify.');
  else if(!gsc)add(actions,'P1',82,'Executar primeira sincronização GSC','As credenciais existem, mas ainda não há snapshot persistido.','gsc','Executar a sincronização manual uma vez; depois ela roda diariamente.');

  if(gsc?.current){
    const signals=querySignals(gsc.current);
    const ctr=signals.filter(x=>x.impressions>=30&&x.position<=10&&x.ctr<2).sort((a,b)=>b.impressions-a.impressions)[0];
    const strike=signals.filter(x=>x.impressions>=20&&x.position>=8&&x.position<=20).sort((a,b)=>b.impressions-a.impressions)[0];
    if(ctr)add(actions,'P1',80,'Melhorar CTR de uma consulta já posicionada',`“${ctr.query}” tem ${Math.round(ctr.impressions)} impressões, posição média ${ctr.position.toFixed(1)} e CTR ${ctr.ctr.toFixed(2)}%.`,'gsc','Revisar title/description da página dominante sem criar uma URL nova.');
    if(strike)add(actions,'P1',76,'Empurrar consulta em striking distance',`“${strike.query}” está em posição média ${strike.position.toFixed(1)} com ${Math.round(strike.impressions)} impressões.`,'gsc','Fortalecer a página existente e preservar atribuição causal.');
    for(const exp of (cp as any)?.experiments||[]){
      const today=new Date().toISOString().slice(0,10), end=gsc.current.endDate||'';
      if(today>=exp.minimumDecisionDate&&end>=exp.startedAt)add(actions,'P1',83,`Revisar experimento: ${exp.name}`,'A data mínima de decisão foi atingida e o dataset automático já cobre o início do experimento.','experiment',exp.decisionRule||'Revisar evidência antes de promover qualquer mudança.');
    }
  }
  if(Array.isArray(pulls)&&pulls.length)add(actions,'P2',55,'Revisar Pull Requests abertos',`${pulls.length} PR(s) permanecem abertos no repositório.`,'github','Fechar, integrar ou justificar os PRs para evitar estado operacional ambíguo.');
  if(!actions.some(a=>a.priority==='P0'||a.priority==='P1'))add(actions,'P3',30,'Manter observação controlada','Nenhum bloqueio ou oportunidade forte ultrapassou os thresholds atuais.','brain','Evitar mudanças cosméticas; aguardar evidência nova.');

  actions.sort((a,b)=>b.score-a.score);
  const result={schema:'freedom-operational-brain-v1',generatedAt:new Date().toISOString(),mainSha,technical:{releaseExact,failedRuns:failedRuns.length,pendingRuns:pendingRuns.length,openPulls:Array.isArray(pulls)?pulls.length:0},connectors:{github:{ready:githubReady},gsc:{ready:gcfg.ready,lastSync:gsc?.syncedAt||null}},gsc:{available:!!gsc,currentEnd:gsc?.current?.endDate||null},topActions:actions.slice(0,7),audit,collectionFailures:failures};
  await appendAudit('brain_evaluated',{mainSha,releaseExact,failedRuns:failedRuns.length,actions:result.topActions.length,gscAvailable:!!gsc});
  return Response.json(result);
};

export const config={path:'/api/brain/evaluate'};
