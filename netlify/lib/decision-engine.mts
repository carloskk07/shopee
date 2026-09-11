import { getStore, getDeployStore } from '@netlify/blobs';

const STORE='freedom-control-center-decisions';
const KEY='ledger.json';
const VERDICTS=new Set(['KEEP','ITERATE','REVERT','INCONCLUSIVE']);

function store(){
  const production=Netlify.context?.deploy?.context==='production';
  return production?getStore(STORE,{consistency:'strong'}):getDeployStore(STORE);
}
function isoDate(v:any){return String(v||'').slice(0,10)}
function utc(date:string){return new Date(`${date}T00:00:00Z`)}
function shift(date:string,days:number){const d=utc(date);d.setUTCDate(d.getUTCDate()+days);return d.toISOString().slice(0,10)}
function daysInclusive(a:string,b:string){if(!a||!b||b<a)return 0;return Math.floor((utc(b).getTime()-utc(a).getTime())/86400000)+1}
function normalize(v:any){return String(v||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim()}
function latestDate(rows:any[]=[]){return rows.map(r=>isoDate(r?.date)).filter(Boolean).sort().at(-1)||''}
function num(v:any){const n=Number(v||0);return Number.isFinite(n)?n:0}
function pctChange(current:number,base:number){return base?((current-base)/base)*100:null}
function fnv1a32(value:string){let h=0x811c9dc5;for(let i=0;i<value.length;i++){h^=value.charCodeAt(i);h=Math.imul(h,0x01000193)}return `fnv1a32-${(h>>>0).toString(16).padStart(8,'0')}`}

export function aggregateRows(rows:any[]=[]){
  const clicks=rows.reduce((a,r)=>a+num(r.clicks),0), impressions=rows.reduce((a,r)=>a+num(r.impressions),0);
  const position=impressions?rows.reduce((a,r)=>a+num(r.position)*num(r.impressions),0)/impressions:0;
  return {rows:rows.length,clicks,impressions,ctr:impressions?clicks/impressions*100:0,position};
}
function mergedRows(gsc:any){
  const map=new Map<string,any>();
  for(const r of [...(gsc?.baseline?.rows||[]),...(gsc?.current?.rows||[])]){
    const key=[isoDate(r?.date),String(r?.query||''),String(r?.page||''),String(r?.device||'')].join('|');
    if(key.startsWith('|'))continue;
    map.set(key,r);
  }
  return [...map.values()];
}
function matchesExperiment(exp:any,row:any){
  const page=String(row?.page||''), q=normalize(row?.query);
  if(page&&[exp?.targetHtml,exp?.targetPdf].filter(Boolean).includes(page))return true;
  return (exp?.queryContains||[]).some((x:any)=>q.includes(normalize(x)));
}
function targetMetrics(rows:any[],url:string){return aggregateRows(rows.filter(r=>String(r?.page||'')===String(url||'')))}
function targetPath(exp:any){
  try{const u=new URL(String(exp?.targetHtml||''));const p=u.pathname.replace(/^\/+|\/+$/g,'');return p?`${p}.html`:''}catch(_){return ''}
}

export function evaluateExperiment(exp:any,gsc:any,policy:any={}){
  const all=mergedRows(gsc), dataEnd=isoDate(gsc?.current?.endDate)||latestDate(gsc?.current?.rows||[]), startedAt=isoDate(exp?.startedAt), minimumDecisionDate=isoDate(exp?.minimumDecisionDate);
  const dataCoversStart=!!dataEnd&&!!startedAt&&dataEnd>=startedAt;
  const finalizedDecisionReached=!!dataEnd&&!!minimumDecisionDate&&dataEnd>=minimumDecisionDate;
  const clockDecisionReached=!!minimumDecisionDate&&new Date()>=new Date(`${minimumDecisionDate}T00:00:00Z`);
  const postEnd=dataCoversStart?dataEnd:'';
  const postDays=postEnd?daysInclusive(startedAt,postEnd):0;
  const preEnd=startedAt?shift(startedAt,-1):'';
  const preStart=preEnd&&postDays?shift(preEnd,-postDays+1):'';
  const matched=all.filter(r=>matchesExperiment(exp,r));
  const postRows=matched.filter(r=>{const d=isoDate(r?.date);return postDays&&d>=startedAt&&d<=postEnd});
  const preRows=matched.filter(r=>{const d=isoDate(r?.date);return postDays&&d>=preStart&&d<=preEnd});
  const post=aggregateRows(postRows), pre=aggregateRows(preRows), htmlPost=targetMetrics(postRows,exp?.targetHtml), pdfPost=targetMetrics(postRows,exp?.targetPdf), htmlPre=targetMetrics(preRows,exp?.targetHtml), pdfPre=targetMetrics(preRows,exp?.targetPdf);
  const criteria={
    minClusterImpressions:num(exp?.successCriteria?.minClusterImpressions||policy?.minimumClusterImpressions||10),
    htmlImpressionsMin:num(exp?.successCriteria?.htmlImpressionsMin||3),
    minTrafficRatio:num(exp?.successCriteria?.minTrafficRatio||0.65),
    hardTrafficRatio:num(exp?.successCriteria?.hardTrafficRatio||0.50),
    maxPositionRegression:num(exp?.successCriteria?.maxPositionRegression||2),
  };
  const decisionEligible=finalizedDecisionReached&&post.impressions>=criteria.minClusterImpressions&&postDays>0;
  const clusterRatio=pre.impressions?post.impressions/pre.impressions:null, positionDelta=pre.impressions?post.position-pre.position:null, htmlShare=post.impressions?htmlPost.impressions/post.impressions:0;
  let status='WAITING_DATA', recommendation='WAIT';
  if(dataCoversStart)status='OBSERVING';
  if(clockDecisionReached&&!finalizedDecisionReached)status='WAITING_FINALIZED_GSC';
  if(decisionEligible)status='DECISION_WINDOW';
  if(decisionEligible){
    if(!pre.impressions)recommendation='INCONCLUSIVE';
    else if(clusterRatio!==null&&clusterRatio<criteria.hardTrafficRatio&&positionDelta!==null&&positionDelta>criteria.maxPositionRegression)recommendation='REVERT';
    else if(htmlPost.impressions>=criteria.htmlImpressionsMin&&clusterRatio!==null&&clusterRatio>=criteria.minTrafficRatio&&(positionDelta===null||positionDelta<=criteria.maxPositionRegression))recommendation='KEEP';
    else if(clusterRatio!==null&&clusterRatio>=criteria.minTrafficRatio)recommendation='ITERATE';
    else recommendation='INCONCLUSIVE';
  }
  const evidence={dataEnd,startedAt,minimumDecisionDate,preStart,preEnd,postEnd,postDays,pre,post,htmlPre,htmlPost,pdfPre,pdfPost,clusterRatio,clusterImpressionsChangePct:pctChange(post.impressions,pre.impressions),positionDelta,htmlShare,criteria};
  const evidenceFingerprint=fnv1a32(JSON.stringify({experimentId:exp?.id,status,recommendation,evidence}));
  return {id:String(exp?.id||''),name:String(exp?.name||exp?.id||''),status,recommendation,decisionEligible,dataCoversStart,clockDecisionReached,finalizedDecisionReached,targetHtml:exp?.targetHtml||'',targetPdf:exp?.targetPdf||'',targetPath:targetPath(exp),decisionRule:exp?.decisionRule||'',objective:exp?.objective||'',evidence,evidenceFingerprint};
}

export function evaluateExperiments(experiments:any[]=[],gsc:any,policy:any={}){
  return experiments.map(exp=>evaluateExperiment(exp,gsc,policy));
}

export async function readDecisionLedger(){
  const value=await store().get(KEY,{type:'json'}).catch(()=>null);
  return Array.isArray(value)?value:[];
}
async function writeLedger(rows:any[]){await store().setJSON(KEY,rows.slice(0,100))}
function cleanNote(v:any){return String(v||'').trim().slice(0,500)}

export async function recordDecision(input:{experiment:any,evaluation:any,verdict:string,mode?:string,note?:string}){
  const verdict=String(input.verdict||'').toUpperCase();
  if(!VERDICTS.has(verdict))throw new Error('Decisão inválida');
  if(!input?.evaluation?.decisionEligible)throw new Error('Janela causal ainda não está elegível para decisão');
  const now=new Date().toISOString(), rows=await readDecisionLedger();
  const id=`dec-${now.slice(0,10).replace(/-/g,'')}-${crypto.randomUUID().slice(0,8)}`;
  const state=input.mode==='PREPARE'&&['ITERATE','REVERT'].includes(verdict)?'PREPARED':'DECIDED';
  const rec={id,experimentId:String(input.experiment?.id||''),experimentName:String(input.experiment?.name||input.experiment?.id||''),state,verdict,createdAt:now,updatedAt:now,note:cleanNote(input.note),evidenceFingerprint:input.evaluation.evidenceFingerprint,evidence:{status:input.evaluation.status,recommendation:input.evaluation.recommendation,...input.evaluation.evidence},targetPath:input.evaluation.targetPath||'',targetHtml:input.evaluation.targetHtml||'',pr:null,history:[{at:now,event:state,verdict}]};
  await writeLedger([rec,...rows]);
  return rec;
}

export async function linkDecisionPr(context:any,pr:any){
  const id=String(context?.decisionId||'');if(!id)return null;
  const rows=await readDecisionLedger(), idx=rows.findIndex((r:any)=>r.id===id);if(idx<0)return null;
  const now=new Date().toISOString(), rec={...rows[idx]};
  rec.state='PR_OPEN';rec.updatedAt=now;rec.pr={number:num(pr?.number),url:String(pr?.html_url||''),branch:String(pr?.branch||''),baseSha:String(pr?.baseSha||''),createdAt:now};rec.history=[{at:now,event:'PR_OPEN',number:rec.pr.number},...(rec.history||[])].slice(0,30);
  rows[idx]=rec;await writeLedger(rows);return rec;
}

export function decisionContext(rec:any){return rec?{decisionId:rec.id,experimentId:rec.experimentId,verdict:rec.verdict,evidenceFingerprint:rec.evidenceFingerprint,targetPath:rec.targetPath||''}:null}
