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

console.log('PASS: Freedom Control Center V2 behavior regression suite');


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
