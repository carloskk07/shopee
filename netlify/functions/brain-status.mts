import { readAudit } from '../lib/audit.mts';
import { gscConfig, readGsc } from '../lib/gsc.mts';

export default async (req:Request)=>{
  if(req.method!=='GET')return new Response('Method not allowed',{status:405});
  const githubReady=!!Netlify.env.get('FCC_GITHUB_TOKEN');
  const gsc=gscConfig();
  const latest=await readGsc();
  const audit=await readAudit(8);
  return Response.json({
    schema:'freedom-operational-brain-status-v1',
    version:'1.0.0',
    generatedAt:new Date().toISOString(),
    runtime:{hosting:'netlify-private',access:'team-sso'},
    connectors:{
      github:{ready:githubReady,mode:githubReady?'SERVER_SIDE':'MANUAL_SESSION_FALLBACK'},
      gsc:{ready:gsc.ready,mode:gsc.ready?'AUTO_PRIVATE':'NEEDS_CREDENTIAL',missing:gsc.missing,lastSync:latest?.syncedAt||null},
    },
    audit,
  });
};

export const config={path:'/api/brain/status'};
