import { getStore, getDeployStore } from '@netlify/blobs';
import { appendAudit } from './audit.mts';

const STORE='freedom-control-center-gsc';

function store(){
  const production=Netlify.context?.deploy?.context==='production';
  return production?getStore(STORE,{consistency:'strong'}):getDeployStore(STORE);
}

function env(name:string){return Netlify.env.get(name)||''}

export function gscConfig(){
  const required=['GSC_CLIENT_ID','GSC_CLIENT_SECRET','GSC_REFRESH_TOKEN'];
  const missing=required.filter(k=>!env(k));
  return {ready:missing.length===0,missing,siteUrl:env('GSC_SITE_URL')||'sc-domain:achadostube.com.br'};
}

async function accessToken(){
  const c=gscConfig();
  if(!c.ready)throw new Error(`GSC credentials missing: ${c.missing.join(', ')}`);
  const body=new URLSearchParams({client_id:env('GSC_CLIENT_ID'),client_secret:env('GSC_CLIENT_SECRET'),refresh_token:env('GSC_REFRESH_TOKEN'),grant_type:'refresh_token'});
  const r=await fetch('https://oauth2.googleapis.com/token',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body});
  const j=await r.json();
  if(!r.ok||!j.access_token)throw new Error(j.error_description||j.error||`Google OAuth ${r.status}`);
  return j.access_token as string;
}

function iso(d:Date){return d.toISOString().slice(0,10)}
function shift(d:Date,days:number){const x=new Date(d);x.setUTCDate(x.getUTCDate()+days);return x}

async function query(token:string,siteUrl:string,startDate:string,endDate:string){
  const url=`https://searchconsole.googleapis.com/webmasters/v3/sites/${encodeURIComponent(siteUrl)}/searchAnalytics/query`;
  const r=await fetch(url,{method:'POST',headers:{Authorization:`Bearer ${token}`,'Content-Type':'application/json'},body:JSON.stringify({startDate,endDate,dimensions:['date','query','page'],rowLimit:25000,dataState:'final'})});
  const j=await r.json();
  if(!r.ok)throw new Error(j?.error?.message||`Search Console ${r.status}`);
  return (j.rows||[]).map((row:any)=>({date:row.keys?.[0]||'',query:row.keys?.[1]||'',page:row.keys?.[2]||'',clicks:Number(row.clicks||0),impressions:Number(row.impressions||0),ctr:Number(row.ctr||0)*100,position:Number(row.position||0)}));
}

export async function syncGsc(){
  const cfg=gscConfig();
  if(!cfg.ready)throw new Error(`GSC credentials missing: ${cfg.missing.join(', ')}`);
  const token=await accessToken();
  const today=new Date();
  const currentEnd=shift(today,-3), currentStart=shift(currentEnd,-27), baselineEnd=shift(currentStart,-1), baselineStart=shift(baselineEnd,-27);
  const [currentRows,baselineRows]=await Promise.all([
    query(token,cfg.siteUrl,iso(currentStart),iso(currentEnd)),
    query(token,cfg.siteUrl,iso(baselineStart),iso(baselineEnd)),
  ]);
  const current={source:'GSC_AUTO_PRIVATE',startDate:iso(currentStart),endDate:iso(currentEnd),rows:currentRows};
  const baseline={source:'GSC_AUTO_PRIVATE',startDate:iso(baselineStart),endDate:iso(baselineEnd),rows:baselineRows};
  const payload={syncedAt:new Date().toISOString(),siteUrl:cfg.siteUrl,current,baseline};
  await store().setJSON('latest.json',payload);
  await appendAudit('gsc_sync',{currentEnd:current.endDate,currentRows:currentRows.length,baselineRows:baselineRows.length});
  return payload;
}

export async function readGsc(){
  const payload=await store().get('latest.json',{type:'json'}).catch(()=>null);
  return payload||null;
}
