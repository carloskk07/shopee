import { getStore, getDeployStore } from '@netlify/blobs';

const KEY='events.json';
const STORE='freedom-control-center-audit';

function store(){
  const production=Netlify.context?.deploy?.context==='production';
  return production?getStore(STORE,{consistency:'strong'}):getDeployStore(STORE);
}

function clean(value:any){
  if(value===null||value===undefined)return value;
  if(typeof value==='string')return value.slice(0,500);
  if(typeof value==='number'||typeof value==='boolean')return value;
  if(Array.isArray(value))return value.slice(0,20).map(clean);
  if(typeof value==='object'){
    const out:any={};
    for(const [k,v] of Object.entries(value).slice(0,30)){
      if(/token|secret|password|authorization/i.test(k))continue;
      out[k]=clean(v);
    }
    return out;
  }
  return String(value).slice(0,500);
}

export async function readAudit(limit=40){
  const current=await store().get(KEY,{type:'json'}).catch(()=>null);
  return Array.isArray(current)?current.slice(0,Math.max(1,Math.min(limit,100))):[];
}

export async function appendAudit(type:string,detail:any={}){
  const s=store();
  const current=await s.get(KEY,{type:'json'}).catch(()=>null);
  const events=Array.isArray(current)?current:[];
  const event={id:crypto.randomUUID(),at:new Date().toISOString(),type:String(type).slice(0,80),detail:clean(detail)};
  await s.setJSON(KEY,[event,...events].slice(0,200));
  return event;
}
