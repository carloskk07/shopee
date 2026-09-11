import { getDeployStore, getStore } from '@netlify/blobs';

export type MonetizationChannel='SUPPORT'|'AFFILIATE'|'KDP'|'PREMIUM'|'ADS'|'OTHER';
export type MonetizationRecord={
  id:string;
  date:string;
  channel:MonetizationChannel;
  amount:number;
  currency:string;
  source:string;
  pagePath:string|null;
  note:string;
  createdAt:string;
  voidedAt:string|null;
  voidReason:string|null;
};

function store(){
  const production=Netlify.context?.deploy?.context==='production';
  return production
    ? getStore('freedom-monetization-ledger',{consistency:'strong'})
    : getDeployStore('freedom-monetization-ledger');
}

function cleanRecord(x:any):MonetizationRecord|null{
  if(!x||typeof x!=='object')return null;
  const channel=String(x.channel||'').toUpperCase() as MonetizationChannel;
  if(!['SUPPORT','AFFILIATE','KDP','PREMIUM','ADS','OTHER'].includes(channel))return null;
  const amount=Number(x.amount);
  if(!Number.isFinite(amount)||amount<=0)return null;
  const date=/^\d{4}-\d{2}-\d{2}$/.test(String(x.date||''))?String(x.date):'';
  if(!date)return null;
  const currency=String(x.currency||'BRL').toUpperCase().replace(/[^A-Z]/g,'').slice(0,3);
  if(currency.length!==3)return null;
  return {
    id:String(x.id||'').slice(0,96),
    date,
    channel,
    amount:Math.round(amount*100)/100,
    currency,
    source:String(x.source||'manual').trim().slice(0,80)||'manual',
    pagePath:x.pagePath?String(x.pagePath).trim().slice(0,240):null,
    note:String(x.note||'').trim().slice(0,320),
    createdAt:String(x.createdAt||''),
    voidedAt:x.voidedAt?String(x.voidedAt):null,
    voidReason:x.voidReason?String(x.voidReason).slice(0,240):null,
  };
}

export async function readMonetizationLedger():Promise<MonetizationRecord[]>{
  const raw=await store().get('ledger-v1',{type:'json'}).catch(()=>null) as any;
  const rows=Array.isArray(raw?.records)?raw.records:[];
  return rows.map(cleanRecord).filter(Boolean).slice(-500) as MonetizationRecord[];
}

export async function writeMonetizationLedger(records:MonetizationRecord[]):Promise<void>{
  const safe=records.map(cleanRecord).filter(Boolean).slice(-500) as MonetizationRecord[];
  await store().setJSON('ledger-v1',{schema:'freedom-monetization-ledger-v1',updatedAt:new Date().toISOString(),records:safe});
}

export function summarizeMonetization(records:MonetizationRecord[]){
  const active=records.filter(x=>!x.voidedAt);
  const byCurrency:Record<string,number>={};
  const byChannel:Record<string,Record<string,number>>={};
  for(const r of active){
    byCurrency[r.currency]=(byCurrency[r.currency]||0)+r.amount;
    byChannel[r.channel]=byChannel[r.channel]||{};
    byChannel[r.channel][r.currency]=(byChannel[r.channel][r.currency]||0)+r.amount;
  }
  for(const k of Object.keys(byCurrency))byCurrency[k]=Math.round(byCurrency[k]*100)/100;
  for(const c of Object.keys(byChannel))for(const k of Object.keys(byChannel[c]))byChannel[c][k]=Math.round(byChannel[c][k]*100)/100;
  return {records:active.length,voided:records.length-active.length,byCurrency,byChannel};
}
