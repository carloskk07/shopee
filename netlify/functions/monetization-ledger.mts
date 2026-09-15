import { appendAudit } from '../lib/audit.mts';
import { readMonetizationLedger, summarizeMonetization, writeMonetizationLedger, type MonetizationChannel } from '../lib/monetization-ledger.mts';

function sameOrigin(req:Request){
  const origin=req.headers.get('origin');
  return !origin||origin===new URL(req.url).origin;
}
function validDate(v:string){
  const m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(v);
  if(!m)return false;
  const year=Number(m[1]),month=Number(m[2]),day=Number(m[3]);
  const t=Date.UTC(year,month-1,day), d=new Date(t);
  if(d.getUTCFullYear()!==year||d.getUTCMonth()!==month-1||d.getUTCDate()!==day)return false;
  const floor=Date.UTC(2020,0,1);
  const now=new Date(), today=Date.UTC(now.getUTCFullYear(),now.getUTCMonth(),now.getUTCDate());
  return t>=floor&&t<=today+86400000;
}
function channel(v:any):MonetizationChannel|null{
  const x=String(v||'').toUpperCase() as MonetizationChannel;
  return ['SUPPORT','AFFILIATE','KDP','PREMIUM','ADS','OTHER'].includes(x)?x:null;
}
function currency(v:any){
  const x=String(v||'').trim().toUpperCase();
  return /^[A-Z]{3}$/.test(x)?x:null;
}

export default async (req:Request)=>{
  if(!sameOrigin(req))return Response.json({error:'Origin rejeitada'},{status:403});
  if(req.method==='GET'){
    const records=await readMonetizationLedger();
    return Response.json({schema:'freedom-monetization-ledger-api-v1',records:records.slice().reverse().slice(0,120),summary:summarizeMonetization(records)});
  }
  if(req.method!=='POST')return new Response('Method not allowed',{status:405});
  try{
    const body=await req.json();
    const action=String(body.action||'RECORD').toUpperCase();
    const records=await readMonetizationLedger();
    if(action==='RECORD'){
      const ch=channel(body.channel), amount=Number(body.amount), date=String(body.date||'');
      if(!ch)throw new Error('Canal inválido');
      if(!validDate(date))throw new Error('Data inválida');
      if(!Number.isFinite(amount)||amount<=0||amount>10_000_000)throw new Error('Valor inválido');
      const curr=currency(body.currency||'BRL');
      if(!curr)throw new Error('Moeda inválida');
      const pagePath=String(body.pagePath||'').trim();
      if(pagePath&&(!pagePath.startsWith('/')||pagePath.length>240))throw new Error('Caminho de página inválido');
      const record={
        id:`rev_${Date.now()}_${crypto.randomUUID().slice(0,8)}`,
        date,
        channel:ch,
        amount:Math.round(amount*100)/100,
        currency:curr,
        source:String(body.source||'manual').trim().slice(0,80)||'manual',
        pagePath:pagePath||null,
        note:String(body.note||'').trim().slice(0,320),
        createdAt:new Date().toISOString(),
        voidedAt:null,
        voidReason:null,
      };
      records.push(record);
      await writeMonetizationLedger(records);
      await appendAudit('monetization_revenue_recorded',{id:record.id,channel:record.channel,currency:record.currency,pagePath:record.pagePath});
      return Response.json({ok:true,record,summary:summarizeMonetization(records)});
    }
    if(action==='VOID'){
      const id=String(body.id||'');
      const record=records.find(x=>x.id===id);
      if(!record)throw new Error('Registro não encontrado');
      if(record.voidedAt)throw new Error('Registro já anulado');
      record.voidedAt=new Date().toISOString();
      record.voidReason=String(body.reason||'correção administrativa').trim().slice(0,240)||'correção administrativa';
      await writeMonetizationLedger(records);
      await appendAudit('monetization_revenue_voided',{id:record.id,channel:record.channel});
      return Response.json({ok:true,record,summary:summarizeMonetization(records)});
    }
    throw new Error('Ação inválida');
  }catch(e:any){
    await appendAudit('monetization_ledger_failed',{error:e?.message||String(e)}).catch(()=>{});
    return Response.json({error:e?.message||String(e)},{status:400});
  }
};

export const config={path:'/api/monetization/ledger'};
