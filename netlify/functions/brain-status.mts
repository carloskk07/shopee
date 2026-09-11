import { readAudit } from '../lib/audit.mts';
import { gscConfig, readGsc } from '../lib/gsc.mts';
import { readDecisionLedger } from '../lib/decision-engine.mts';

function dayDiff(a:string,b:string){if(!a||!b)return null;return Math.floor((new Date(`${b}T00:00:00Z`).getTime()-new Date(`${a}T00:00:00Z`).getTime())/86400000)}
function hoursSince(v:any){const t=new Date(String(v||'')).getTime();return Number.isFinite(t)?Math.max(0,(Date.now()-t)/3600000):null}

export default async (req:Request)=>{
  if(req.method!=='GET')return new Response('Method not allowed',{status:405});
  const githubReady=!!Netlify.env.get('FCC_GITHUB_TOKEN');
  const gsc=gscConfig();
  const [latest,audit,decisions]=await Promise.all([readGsc(),readAudit(8),readDecisionLedger()]);
  const currentEnd=String(latest?.current?.endDate||'').slice(0,10), today=new Date().toISOString().slice(0,10), dataLagDays=currentEnd?dayDiff(currentEnd,today):null;
  const gscHealth=!gsc.ready?'SETUP':!latest?'NO_SNAPSHOT':dataLagDays!==null&&dataLagDays>6?'STALE':'READY';
  return Response.json({
    schema:'freedom-operational-brain-status-v2',
    version:'2.0.0',
    generatedAt:new Date().toISOString(),
    runtime:{hosting:'netlify-private',access:'team-sso'},
    connectors:{
      github:{ready:githubReady,mode:githubReady?'SERVER_SIDE':'MANUAL_SESSION_FALLBACK'},
      gsc:{ready:gsc.ready,mode:gsc.ready?'AUTO_PRIVATE':'NEEDS_CREDENTIAL',missing:gsc.missing,lastSync:latest?.syncedAt||null,health:gscHealth,currentEnd,dataLagDays,syncAgeHours:hoursSince(latest?.syncedAt),currentRows:latest?.current?.rows?.length||0,baselineRows:latest?.baseline?.rows?.length||0},
    },
    decisionLoop:{records:decisions.length,prepared:decisions.filter((x:any)=>x.state==='PREPARED').length,openPr:decisions.filter((x:any)=>x.state==='PR_OPEN').length},
    audit,
  });
};

export const config={path:'/api/brain/status'};
