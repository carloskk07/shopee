import { syncGsc } from '../lib/gsc.mts';

export default async ()=>{
  try{await syncGsc()}catch(e){console.error('GSC scheduled sync failed',e)}
};

export const config={schedule:'0 10 * * *'};
