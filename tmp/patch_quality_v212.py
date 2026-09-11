from pathlib import Path
import json, hashlib

app=Path('admin/app.js')
s=app.read_text(encoding='utf-8')
old="""    const required=qualityCfg.requiredWorkflows||['Site integrity','Admin integrity','Route integrity','Production smoke','Admin production smoke','Route production smoke','pages build and deployment'];
    const allRuns=state.runs||[], latestByName=new Map();
    for(const r of allRuns){if(r.head_branch==='main'&&r.head_sha===currentSha&&required.includes(r.name)&&!latestByName.has(r.name))latestByName.set(r.name,r)}
    const currentRuns=[...latestByName.values()], missingRuns=required.filter(name=>!latestByName.has(name));
    const failed=currentRuns.filter(r=>r.status==='completed'&&r.conclusion&&!['success','skipped','neutral'].includes(r.conclusion));
    const pending=currentRuns.filter(r=>r.status!=='completed');
    const historicalFailed=allRuns.filter(r=>r.head_sha!==currentSha&&r.status==='completed'&&r.conclusion&&!['success','skipped','neutral'].includes(r.conclusion));
    const ciStatus=failed.length?'FAIL':(pending.length||missingRuns.length)?'WARN':'PASS';
    const ciDetail=failed.length?`${failed.length} workflow(s) do release atual falharam`:pending.length?`${pending.length} workflow(s) do release atual em execução`:missingRuns.length?`${currentRuns.length}/${required.length} workflows do release atual observados`:`${currentRuns.length}/${required.length} workflows do release atual aprovados`;"""
new="""    const required=qualityCfg.requiredWorkflows||['Site integrity','Admin integrity','Production smoke','Admin production smoke','pages build and deployment'];
    const optional=qualityCfg.optionalWorkflows||['Route integrity','Route production smoke'], watched=[...new Set([...required,...optional])];
    const allRuns=state.runs||[], latestByName=new Map();
    for(const r of allRuns){if(r.head_branch==='main'&&r.head_sha===currentSha&&watched.includes(r.name)&&!latestByName.has(r.name))latestByName.set(r.name,r)}
    const currentRuns=[...latestByName.values()], missingRuns=required.filter(name=>!latestByName.has(name)), optionalRuns=currentRuns.filter(r=>optional.includes(r.name));
    const failed=currentRuns.filter(r=>r.status==='completed'&&r.conclusion&&!['success','skipped','neutral'].includes(r.conclusion));
    const pending=currentRuns.filter(r=>r.status!=='completed');
    const historicalFailed=allRuns.filter(r=>r.head_sha!==currentSha&&r.status==='completed'&&r.conclusion&&!['success','skipped','neutral'].includes(r.conclusion));
    const ciStatus=failed.length?'FAIL':(pending.length||missingRuns.length)?'WARN':'PASS';
    const ciDetail=failed.length?`${failed.length} workflow(s) do release atual falharam`:pending.length?`${pending.length} workflow(s) do release atual em execução`:missingRuns.length?`${required.length-missingRuns.length}/${required.length} workflows obrigatórios observados`:`${required.length}/${required.length} workflows obrigatórios aprovados${optionalRuns.length?` · ${optionalRuns.length} condicionais observados`:''}`;"""
if old not in s: raise SystemExit('quality workflow scope anchor missing')
s=s.replace(old,new,1)
oldret="return {score,gates,failed,pending,currentRuns,missingRuns,historicalFailed,ciStatus,exact,artifacts,books,guides,searchEvidence,operationalReadiness};"
newret="return {score,gates,failed,pending,currentRuns,optionalRuns,missingRuns,historicalFailed,ciStatus,exact,artifacts,books,guides,searchEvidence,operationalReadiness};"
if oldret not in s: raise SystemExit('quality return anchor missing')
s=s.replace(oldret,newret,1)
s=s.replace("currentReleaseRuns:q.currentRuns.length,missingCurrentRuns:q.missingRuns","currentReleaseRuns:q.currentRuns.length,conditionalCurrentRuns:q.optionalRuns.length,missingCurrentRuns:q.missingRuns",1)
app.write_text(s,encoding='utf-8')

cp_path=Path('admin/control-plane.json')
cp=json.loads(cp_path.read_text(encoding='utf-8'))
cp['version']='2.1.2'
q=cp.setdefault('quality',{})
q['requiredWorkflows']=['Site integrity','Admin integrity','Production smoke','Admin production smoke','pages build and deployment']
q['optionalWorkflows']=['Route integrity','Route production smoke']
cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

tp=Path('scripts/test_admin_v2.js')
t=tp.read_text(encoding='utf-8')
old_block="""const requiredQualityRuns=['Site integrity','Admin integrity','Route integrity','Production smoke','Admin production smoke','Route production smoke','pages build and deployment'];
t.state.cp={version:'2.1.1',quality:{requiredWorkflows:requiredQualityRuns,searchEvidenceScoring:false,historicalRunsScoring:false}};
t.state.release={artifacts:{'index.html':'x'}};t.state.prodRelease={artifacts:{'index.html':'x'}};
t.state.siteData={books:[{slug:'a',title:'A',available:true}],guides:Array.from({length:6},(_,i)=>({slug:`g${i}`,title:`G${i}`}))};
t.state.monetization={support:{url:'https://livepix.gg/editorafreedombook'},affiliates:{enabled:false,offers:[]},premium:{enabled:false,offers:[]}};
t.state.adminRelease={schema:'freedom-admin-release-v1',version:'2.1.1'};t.state.commits=[{sha:'current-sha'}];
t.state.runs=[{name:'obsolete builder',head_branch:'main',head_sha:'old-sha',status:'completed',conclusion:'failure'},...requiredQualityRuns.map(name=>({name,head_branch:'main',head_sha:'current-sha',status:'completed',conclusion:'success'}))];
t.state.gsc.current=null;t.state.gsc.baseline=null;
let qm=t.qualityModel();
assert(qm.score===100,'historical CI failures must not reduce current technical health');
assert(qm.failed.length===0,'historical failures must not appear as current release failures');
assert(qm.historicalFailed.length===1,'historical failure remains auditable');
assert(qm.gates.find(g=>g.name==='SEARCH_EVIDENCE').status==='NOT_LOADED','missing GSC must be NOT_LOADED');
assert(qm.gates.find(g=>g.name==='SEARCH_EVIDENCE').scorable===false,'missing GSC must not reduce technical score');
assert(qm.operationalReadiness==='READY','green current release should be READY without GSC import');
t.state.runs=t.state.runs.map(r=>r.name==='Site integrity'&&r.head_sha==='current-sha'?{...r,conclusion:'failure'}:r);qm=t.qualityModel();
assert(qm.score<100&&qm.failed.length===1,'current release CI failure must reduce technical health');
assert(qm.gates.find(g=>g.name==='CI_CURRENT_RELEASE').status==='FAIL','current release CI failure must fail CI gate');

console.log('PASS: Freedom Control Center V2.1.1 quality semantics regression suite');"""
new_block="""const requiredQualityRuns=['Site integrity','Admin integrity','Production smoke','Admin production smoke','pages build and deployment'];
const optionalQualityRuns=['Route integrity','Route production smoke'];
t.state.cp={version:'2.1.2',quality:{requiredWorkflows:requiredQualityRuns,optionalWorkflows:optionalQualityRuns,searchEvidenceScoring:false,historicalRunsScoring:false}};
t.state.release={artifacts:{'index.html':'x'}};t.state.prodRelease={artifacts:{'index.html':'x'}};
t.state.siteData={books:[{slug:'a',title:'A',available:true}],guides:Array.from({length:6},(_,i)=>({slug:`g${i}`,title:`G${i}`}))};
t.state.monetization={support:{url:'https://livepix.gg/editorafreedombook'},affiliates:{enabled:false,offers:[]},premium:{enabled:false,offers:[]}};
t.state.adminRelease={schema:'freedom-admin-release-v1',version:'2.1.2'};t.state.commits=[{sha:'current-sha'}];
t.state.runs=[{name:'obsolete builder',head_branch:'main',head_sha:'old-sha',status:'completed',conclusion:'failure'},...requiredQualityRuns.map(name=>({name,head_branch:'main',head_sha:'current-sha',status:'completed',conclusion:'success'}))];
t.state.gsc.current=null;t.state.gsc.baseline=null;
let qm=t.qualityModel();
assert(qm.score===100,'historical CI failures must not reduce current technical health');
assert(qm.failed.length===0,'historical failures must not appear as current release failures');
assert(qm.historicalFailed.length===1,'historical failure remains auditable');
assert(qm.missingRuns.length===0,'conditional route workflows must not be required on admin-only commits');
assert(qm.optionalRuns.length===0,'absent route workflows remain conditional');
assert(qm.gates.find(g=>g.name==='SEARCH_EVIDENCE').status==='NOT_LOADED','missing GSC must be NOT_LOADED');
assert(qm.gates.find(g=>g.name==='SEARCH_EVIDENCE').scorable===false,'missing GSC must not reduce technical score');
assert(qm.operationalReadiness==='READY','green current release should be READY without GSC import');
t.state.runs.push({name:'Route integrity',head_branch:'main',head_sha:'current-sha',status:'completed',conclusion:'failure'});qm=t.qualityModel();
assert(qm.failed.length===1&&qm.gates.find(g=>g.name==='CI_CURRENT_RELEASE').status==='FAIL','conditional workflow must fail CI gate if it runs and fails');
t.state.runs=t.state.runs.filter(r=>r.name!=='Route integrity');
t.state.runs=t.state.runs.map(r=>r.name==='Site integrity'&&r.head_sha==='current-sha'?{...r,conclusion:'failure'}:r);qm=t.qualityModel();
assert(qm.score<100&&qm.failed.length===1,'required current release CI failure must reduce technical health');
assert(qm.gates.find(g=>g.name==='CI_CURRENT_RELEASE').status==='FAIL','current release CI failure must fail CI gate');

console.log('PASS: Freedom Control Center V2.1.2 path-aware quality workflow regression suite');"""
if old_block not in t: raise SystemExit('quality test block anchor missing')
t=t.replace(old_block,new_block,1)
tp.write_text(t,encoding='utf-8')

vp=Path('scripts/validate_admin.py')
v=vp.read_text(encoding='utf-8')
v=v.replace("cp.get('version')!='2.1.1'","cp.get('version')!='2.1.2'",1)
old="""for name in ('Site integrity','Admin integrity','Route integrity','Production smoke','Admin production smoke'):
    if name not in required_runs: fail(f'quality current-release workflow missing: {name}')"""
new="""for name in ('Site integrity','Admin integrity','Production smoke','Admin production smoke','pages build and deployment'):
    if name not in required_runs: fail(f'quality required workflow missing: {name}')
optional_runs=quality.get('optionalWorkflows',[])
for name in ('Route integrity','Route production smoke'):
    if name not in optional_runs: fail(f'quality conditional workflow missing: {name}')
    if name in required_runs: fail(f'conditional workflow must not be globally required: {name}')"""
if old not in v: raise SystemExit('validator workflow quality anchor missing')
v=v.replace(old,new,1)
v=v.replace('V2.1.1 separates current technical health from historical CI and optional GSC evidence','V2.1.2 adds path-aware workflow semantics to current technical health while preserving historical CI and optional GSC evidence',1)
vp.write_text(v,encoding='utf-8')

rp=Path('admin/release.json')
r=json.loads(rp.read_text(encoding='utf-8'))
r['version']='2.1.2'
for name in r['artifacts']:
    r['artifacts'][name]=hashlib.sha256((Path('admin')/name).read_bytes()).hexdigest()
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
