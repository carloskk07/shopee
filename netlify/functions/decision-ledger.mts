import { appendAudit } from '../lib/audit.mts';
import { readGsc } from '../lib/gsc.mts';
import { decisionContext, evaluateExperiment, readDecisionLedger, recordDecision } from '../lib/decision-engine.mts';

const CP='https://raw.githubusercontent.com/carloskk07/shopee/main/admin/control-plane.json';

async function controlPlane(){
  const r=await fetch(CP,{cache:'no-store'});if(!r.ok)throw new Error(`control-plane ${r.status}`);return r.json();
}
function sameOrigin(req:Request){const origin=req.headers.get('origin');return !origin||origin===new URL(req.url).origin}

export default async (req:Request)=>{
  if(req.method==='GET')return Response.json({schema:'freedom-decision-ledger-v1',records:await readDecisionLedger()});
  if(req.method!=='POST')return new Response('Method not allowed',{status:405});
  if(!sameOrigin(req))return Response.json({error:'Origin rejeitada'},{status:403});
  try{
    const body=await req.json(), action=String(body.action||'DECIDE').toUpperCase(), experimentId=String(body.experimentId||''), verdict=String(body.verdict||'').toUpperCase();
    if(!['DECIDE','PREPARE'].includes(action))throw new Error('Ação inválida');
    const [cp,gsc]=await Promise.all([controlPlane(),readGsc()]);
    const experiment=(cp.experiments||[]).find((x:any)=>String(x.id)===experimentId);if(!experiment)throw new Error('Experimento não encontrado');
    const evaluation=evaluateExperiment(experiment,gsc,cp.decisionPolicy||{});
    const rec=await recordDecision({experiment,evaluation,verdict,mode:action,note:body.note});
    await appendAudit('decision_recorded',{decisionId:rec.id,experimentId,verdict,state:rec.state,evidenceFingerprint:rec.evidenceFingerprint});
    return Response.json({ok:true,record:rec,context:decisionContext(rec),evaluation});
  }catch(e:any){
    await appendAudit('decision_failed',{error:e?.message||String(e)}).catch(()=>{});
    return Response.json({error:e?.message||String(e)},{status:400});
  }
};

export const config={path:'/api/decision/ledger'};
