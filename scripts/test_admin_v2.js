'use strict';
global.__FCC_TEST_MODE__=true;
require('../admin/app.js');
const t=global.__FCC_TEST__;
if(!t)throw new Error('FCC test hook unavailable');

const fs=require('fs');
function assert(condition,message){if(!condition)throw new Error(message)}

const css=fs.readFileSync(require('path').join(__dirname,'../admin/style.css'),'utf8');
assert(css.includes('[hidden]{display:none!important}'),'hidden attribute must override component display');

const localized=[
  'Consulta;Página;Cliques;Impressões;CTR;Posição;Data;Dispositivo',
  '"o peso de ser tudo o tempo todo";https://achadostube.com.br/ebook/o-peso-de-ser-forte-o-tempo-todo.pdf;0;40;0,00%;9,5;2026-09-10;MOBILE',
  '"foco no resultado";https://achadostube.com.br/foco-que-gera-resultados;1;50;2,00%;15,2;2026-09-10;MOBILE',
].join('\n');
const current=t.parseGsc(localized,'atual.csv');
assert(current.rows.length===2,'localized CSV row count');
assert(current.rows[0].position===9.5,'decimal comma position');
assert(current.rows[0].impressions===40,'localized impressions');
assert(current.endDate==='2026-09-10','date boundary');

t.state.gsc.current=current;
t.state.gsc.baseline={rows:[{query:'foco no resultado',page:'https://achadostube.com.br/foco-que-gera-resultados',clicks:0,impressions:20,ctr:0,position:18,date:'2026-09-01',device:'MOBILE'}]};
const opportunities=t.opportunityEngine();
assert(opportunities.some(x=>x.type==='CTR_OPPORTUNITY'),'CTR opportunity missing');
assert(opportunities.some(x=>x.type==='STRIKING_DISTANCE'),'striking distance missing');

const conflict=[
  'Consulta;Página;Cliques;Impressões;CTR;Posição',
  'q;https://achadostube.com.br/a;1;20;5%;8',
  'q;https://achadostube.com.br/b;0;10;0%;12',
  'q;https://achadostube.com.br/a.pdf;0;5;0%;9',
].join('\n');
t.state.gsc.current=t.parseGsc(conflict,'conflict.csv');
assert(t.cannibalization().length===1,'cannibalization detector');
assert(t.pdfHtmlConflicts().length===1,'PDF/HTML detector');

const release='{"artifacts":{"index.html":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}}';
const patched=t.patchReleaseHash(release,'index.html','bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb');
assert(patched.includes('bbbbbbbbbbbbbbbb'),'release hash patch');

const robots=t.validateContent('robots.txt','User-agent: *\nDisallow: /\n');
assert(robots.warnings.length>0,'dangerous robots warning');
const broken=t.validateContent('config.json','{"x":');
assert(broken.errors.length>0,'invalid JSON blocker');

const requiredQualityRuns=['Site integrity','Admin integrity','Route integrity','Production smoke','Admin production smoke','Route production smoke','pages build and deployment'];
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

console.log('PASS: Freedom Control Center V2.1.1 quality semantics regression suite');


global.__FCC_TEST_MODE__=true;
require('../admin/book-publisher.js');
const bp=global.__FCC_BOOK_TEST__;
assert(bp,'Book Publisher test hook unavailable');
assert(bp.slugify('Propósito & Direção!')==='proposito-direcao','book slug normalization');
const plan=bp.bookPathPlan('novo-livro');
assert(Object.keys(plan).length===10,'book bundle must plan 10 files');
assert(plan.cover==='assets/covers/capa-novo-livro.webp','cover path contract');
assert(plan.pdf==='ebook/novo-livro.pdf','PDF path contract');
const book=bp.buildBookRecord({slug:'novo-livro',title:'Novo Livro',badge:'Novo',featured:false,description:'Descrição editorial suficientemente clara.',tags:['a','b','c'],line:'reflexiva',intent:'Para leitores que precisam de direção.',path:'direcao'});
assert(book.pageUrl==='https://achadostube.com.br/novo-livro','canonical book URL');
assert(book.pdfUrl.endsWith('/ebook/novo-livro.pdf'),'PDF URL');
assert(bp.buildShim('novo-livro').includes('static-route-shim-v1 /novo-livro/ -> /novo-livro'),'route shim marker');
assert(bp.sitemapNode(book,'2026-09-09').includes('<image:image>'),'sitemap image entry');
assert(bp.feedEntry(book,'2026-09-09').includes('<id>https://achadostube.com.br/novo-livro</id>'),'Atom entry');
assert(t.binaryPathAllowed('assets/covers/capa-novo-livro.webp'),'cover binary allowlist');
assert(t.binaryPathAllowed('ebook/novo-livro.pdf'),'PDF binary allowlist');
assert(!t.binaryPathAllowed('assets/app.js'),'binary allowlist blocks arbitrary path');
console.log('PASS: Book Publisher V2.1 bundle contracts');

assert(require('fs').readFileSync(require('path').join(__dirname,'../admin/app.js'),'utf8').includes('BOOK_BUNDLE_ATOMIC'),'atomic Book Publisher preflight missing');
assert(require('fs').readFileSync(require('path').join(__dirname,'../admin/book-publisher.js'),'utf8').includes('bundleId:`book:${b.slug}`'),'Book Publisher bundle identity missing');
console.log('PASS: Book Publisher V2.1 atomic bundle guard');
