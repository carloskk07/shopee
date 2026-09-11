import { readAudit } from '../lib/audit.mts';

export default async (req:Request)=>{
  if(req.method!=='GET')return new Response('Method not allowed',{status:405});
  const url=new URL(req.url), limit=Math.max(1,Math.min(Number(url.searchParams.get('limit')||30),100));
  return Response.json({schema:'freedom-audit-v1',events:await readAudit(limit)});
};

export const config={path:'/api/audit'};
