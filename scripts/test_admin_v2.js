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
