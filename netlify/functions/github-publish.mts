import { appendAudit } from '../lib/audit.mts';
import { linkDecisionPr } from '../lib/decision-engine.mts';

const REPO='carloskk07/shopee';
const API='https://api.github.com/repos/'+REPO;
const blocked=['.github/','admin/','.git/'];
const allowed=['.html','.json','.xml','.txt','.css','.md'];

function token(){return Netlify.env.get('FCC_GITHUB_TOKEN')||''}
function pathAllowed(path:string){
  if(path==='release.json')return true;
  if(blocked.some(p=>path.startsWith(p)))return false;
  return allowed.some(ext=>path.endsWith(ext));
}
async function gh(path:string,opts:any={}){
  const r=await fetch(API+path,{...opts,headers:{Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28',Authorization:`Bearer ${token()}`,'Content-Type':'application/json',...(opts.headers||{})}});
  const j=await r.json().catch(()=>({}));
  if(!r.ok)throw new Error(j.message||`GitHub ${r.status}`);
  return j;
}
function slug(s:string){return s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,38)||'update'}
function cleanDecisionContext(value:any){
  if(!value||typeof value!=='object')return null;
  const out={decisionId:String(value.decisionId||'').slice(0,80),experimentId:String(value.experimentId||'').slice(0,120),verdict:String(value.verdict||'').slice(0,20),evidenceFingerprint:String(value.evidenceFingerprint||'').slice(0,80),targetPath:String(value.targetPath||'').slice(0,240)};
  return out.decisionId&&out.experimentId?out:null;
}

export default async (req:Request)=>{
  if(req.method!=='POST')return new Response('Method not allowed',{status:405});
  if(!token())return Response.json({error:'FCC_GITHUB_TOKEN não configurado'},{status:503});
  const origin=req.headers.get('origin');
  if(origin&&origin!==new URL(req.url).origin)return Response.json({error:'Origin rejeitada'},{status:403});
  try{
    const body=await req.json();
    const title=String(body.title||'').trim(), summary=String(body.summary||'').trim(), files=Array.isArray(body.files)?body.files:[], decision=cleanDecisionContext(body.decisionContext);
    if(title.length<4||title.length>90||summary.length<8||summary.length>1200)throw new Error('Título ou resumo inválido');
    if(!files.length||files.length>13)throw new Error('Change Set fora do limite server-side');
    let bytes=0;
    for(const f of files){
      f.path=String(f.path||'');f.content=String(f.content??'');f.encoding=String(f.encoding||'utf-8');
      if(f.encoding!=='utf-8')throw new Error('Backend server-side aceita apenas arquivos textuais');
      if(!pathAllowed(f.path))throw new Error(`Caminho bloqueado: ${f.path}`);
      bytes+=new TextEncoder().encode(f.content).length;
    }
    if(bytes>4_000_000)throw new Error('Payload textual excede 4 MB');
    const ref=await gh('/git/ref/heads/main'), baseSha=ref.object.sha, commit=await gh(`/git/commits/${baseSha}`), baseTree=commit.tree.sha;
    const prefix=String(body.branchPrefix||'control-center/');
    if(!prefix.startsWith('control-center/'))throw new Error('Prefixo de branch inválido');
    const branch=`${prefix}${new Date().toISOString().slice(0,10)}-${slug(title)}-${crypto.randomUUID().slice(0,4)}`;
    await gh('/git/refs',{method:'POST',body:JSON.stringify({ref:`refs/heads/${branch}`,sha:baseSha})});
    const tree=[];
    for(const f of files){const blob=await gh('/git/blobs',{method:'POST',body:JSON.stringify({content:f.content,encoding:'utf-8'})});tree.push({path:f.path,mode:'100644',type:'blob',sha:blob.sha})}
    const newTree=await gh('/git/trees',{method:'POST',body:JSON.stringify({base_tree:baseTree,tree})});
    const decisionBlock=decision?`\n\nDecision loop:\n- Decision ID: \`${decision.decisionId}\`\n- Experiment: \`${decision.experimentId}\`\n- Verdict: \`${decision.verdict||'—'}\`\n- Evidence: \`${decision.evidenceFingerprint||'—'}\`\n\n<!-- FCC_DECISION_CONTEXT ${JSON.stringify(decision)} -->`:'';
    const prBody=`${summary}\n\nChange Set criado pelo Freedom Control Center via backend privado Netlify.${decisionBlock}\n\nArquivos:\n${files.map((f:any)=>`- \`${f.path}\``).join('\n')}\n\nGuardrails: PR-only · main protegida · backend privado · sem auto-merge.`;
    const newCommit=await gh('/git/commits',{method:'POST',body:JSON.stringify({message:title,tree:newTree.sha,parents:[baseSha]})});
    await gh(`/git/refs/heads/${branch.split('/').map(encodeURIComponent).join('/')}`,{method:'PATCH',body:JSON.stringify({sha:newCommit.sha,force:false})});
    const pr=await gh('/pulls',{method:'POST',body:JSON.stringify({title,head:branch,base:'main',body:prBody})});
    if(decision)await linkDecisionPr(decision,{number:pr.number,html_url:pr.html_url,branch,baseSha}).catch(()=>null);
    await appendAudit('github_pr_created',{number:pr.number,branch,files:files.map((f:any)=>f.path),baseSha,decisionId:decision?.decisionId||null,experimentId:decision?.experimentId||null});
    return Response.json({ok:true,number:pr.number,html_url:pr.html_url,branch,baseSha,decisionId:decision?.decisionId||null});
  }catch(e:any){
    await appendAudit('github_publish_failed',{error:e?.message||String(e)}).catch(()=>{});
    return Response.json({error:e?.message||String(e)},{status:400});
  }
};

export const config={path:'/api/github/publish'};
