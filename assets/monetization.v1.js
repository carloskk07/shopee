(() => {
  "use strict";
  const CONFIG_URL="/monetization.json";
  const ELIGIBLE=new Set(["home","book","guide","guides","author"]);
  const q=(s,r=document)=>r.querySelector(s);
  const safeUrl=(value)=>{try{const u=new URL(value,location.origin);return u.protocol==="https:"?u:null}catch(_){return null}};
  const pagePath=()=>{const p=location.pathname.replace(/\/$/,"");return p||"/"};
  const pageType=()=>document.body?.dataset?.pageType||"";
  const matches=(offer,type,path)=>{const types=Array.isArray(offer.pageTypes)?offer.pageTypes:[];const paths=Array.isArray(offer.paths)?offer.paths:[];return (!types.length||types.includes(type))&&(!paths.length||paths.includes(path));};
  const text=(tag,value,cls)=>{const el=document.createElement(tag);if(cls)el.className=cls;el.textContent=value||"";return el};
  const link=(label,url,track,placement,rel)=>{const u=safeUrl(url);if(!u)return null;const a=document.createElement("a");a.className="btn secondary";a.href=u.href;a.textContent=label;a.target="_blank";a.rel=rel||"noopener noreferrer";a.dataset.track=track;a.dataset.placement=placement;return a;};
  const section=(kind,kicker,title,body,cta,note)=>{const s=document.createElement("section");s.className="section";s.dataset.monetizationSlot=kind;const c=document.createElement("div");c.className="container";const card=document.createElement("div");card.className="card channel";const copy=document.createElement("div");copy.append(text("span",kicker,"kicker"),text("h3",title),text("p",body));card.append(copy);if(cta)card.append(cta);if(note){const n=text("p",note,"support-note");n.dataset.monetizationNote=kind;card.append(n)}c.append(card);s.append(c);return s;};
  const append=(node)=>{const main=q("main");if(!main||!node)return false;main.append(node);return true};
  const existingSupport=()=>!!q('[data-monetization-slot="support"],a[href^="https://livepix.gg/"]');
  const activeOffers=(group,type,path)=>Array.isArray(group?.offers)?group.offers.filter(o=>o&&o.enabled===true&&matches(o,type,path)):[];
  async function boot(){
    const type=pageType();if(!ELIGIBLE.has(type))return;
    let cfg;try{const r=await fetch(CONFIG_URL,{credentials:"same-origin",cache:"no-cache"});if(!r.ok)return;cfg=await r.json()}catch(_){return}
    if(!cfg||cfg.schema!=="freedom-book-monetization-v1"||cfg.enabled!==true)return;
    const path=pagePath();let injected=0;const max=Math.max(0,Math.min(2,Number(cfg.guardrails?.maxInjectedBlocksPerPage)||2));
    const premium=activeOffers(cfg.premium,type,path)[0];
    if(cfg.premium?.enabled===true&&premium&&injected<max){const a=link(premium.cta||"Conhecer edição",premium.url,"premium_open","monetization_premium");if(a&&append(section("premium",premium.kicker||"Edição especial",premium.title,premium.text,a,premium.note||"O conteúdo gratuito continua disponível.")))injected++;}
    const affiliate=activeOffers(cfg.affiliates,type,path)[0];
    if(cfg.affiliates?.enabled===true&&affiliate&&injected<max){const a=link(affiliate.cta||"Ver recurso",affiliate.url,"affiliate_open","monetization_affiliate","sponsored noopener noreferrer");const disclosure=cfg.affiliates.disclosure||"Link de afiliado.";const body=[affiliate.text,affiliate.editorialReason].filter(Boolean).join(" ");if(a&&append(section("affiliate",affiliate.kicker||"Recomendação editorial",affiliate.title,body,a,disclosure)))injected++;}
    const s=cfg.support;const allowed=Array.isArray(s?.pageTypes)?s.pageTypes.includes(type):true;
    if(s?.enabled===true&&allowed&&!existingSupport()&&injected<max){const a=link(s.cta,s.url,s.track||"support_open","monetization_support");if(a&&append(section("support",s.kicker,s.title,s.text,a,s.note)))injected++;}
  }
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",boot,{once:true});else boot();
})();
