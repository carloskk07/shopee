import { syncGsc } from '../lib/gsc.mts';

export default async (req:Request)=>{
  if(req.method!=='POST')return new Response('Method not allowed',{status:405});
  try{
    const payload=await syncGsc();
    return Response.json({ok:true,syncedAt:payload.syncedAt,currentEnd:payload.current.endDate,currentRows:payload.current.rows.length,baselineRows:payload.baseline.rows.length});
  }catch(e:any){return Response.json({ok:false,error:e?.message||String(e)},{status:503})}
};

export const config={path:'/api/gsc/sync'};
