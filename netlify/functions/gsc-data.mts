import { gscConfig, readGsc } from '../lib/gsc.mts';

export default async (req:Request)=>{
  if(req.method!=='GET')return new Response('Method not allowed',{status:405});
  const cfg=gscConfig(), payload=await readGsc();
  return Response.json({schema:'freedom-gsc-private-v1',available:!!payload,configured:cfg.ready,missing:cfg.missing,syncedAt:payload?.syncedAt||null,current:payload?.current||null,baseline:payload?.baseline||null});
};

export const config={path:'/api/gsc/data'};
