(() => {
  "use strict";
  const CONFIG = {ga:"G-DK72PVREEJ",tiktok:"D78O6VJC77U8CCU0EA0G",release:"2026.09.08-v2.2.5"};
  const safeDestination=(href="")=>{try{const u=new URL(href,location.href);return u.origin===location.origin?u.pathname:u.hostname}catch(_){return ""}};
  const $=(s,root=document)=>root.querySelector(s);
  const $$=(s,root=document)=>[...root.querySelectorAll(s)];
  const toast=(msg)=>{const el=$("#toast");if(!el)return;el.textContent=msg;el.classList.add("show");clearTimeout(el._t);el._t=setTimeout(()=>el.classList.remove("show"),1800)};

  // Safe local storage: privacy controls must remain usable even when storage is unavailable.
  const storage={
    get:(k)=>{try{return localStorage.getItem(k)}catch(_){return null}},
    set:(k,v)=>{try{localStorage.setItem(k,v);return true}catch(_){return false}}
  };

  // Mobile navigation
  const nav=$("#mainNav"),menu=$("#menuBtn"),mobileMenu=$("#mobileMenu");
  if(nav&&menu){
    const setMenu=(open)=>{nav.classList.toggle("open",open);menu.setAttribute("aria-expanded",String(open));menu.setAttribute("aria-label",open?"Fechar menu":"Abrir menu");menu.textContent=open?"×":"☰"};
    menu.addEventListener("click",()=>setMenu(!nav.classList.contains("open")));
    $$("#mobileMenu a").forEach(a=>a.addEventListener("click",()=>setMenu(false)));
    document.addEventListener("keydown",e=>{if(e.key==="Escape")setMenu(false)});
    document.addEventListener("click",e=>{if(nav.classList.contains("open")&&!nav.contains(e.target))setMenu(false)});
    matchMedia("(min-width:761px)").addEventListener?.("change",e=>{if(e.matches)setMenu(false)});
  }

  // Catalog search/filter + editorial paths
  const grid=$("#catalogGrid");
  if(grid){
    const cards=$$("[data-book-card]",grid),search=$("#bookSearch"),count=$("#catalogCount"),empty=$("#catalogEmpty");
    let filter="all",forcedSlugs=null;
    const norm=(v="")=>v.normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase().trim();
    const apply=()=>{
      const q=norm(search?.value||"");let visible=0;
      cards.forEach(card=>{
        const text=norm(card.dataset.search||card.textContent),line=card.dataset.line,slug=card.dataset.slug;
        const show=(filter==="all"||line===filter)&&(!forcedSlugs||forcedSlugs.includes(slug))&&(!q||text.includes(q));
        card.hidden=!show;if(show)visible++;
      });
      if(count)count.textContent=`${visible} ${visible===1?"material":"materiais"} encontrados`;
      if(empty)empty.hidden=visible!==0;
    };
    let searchTimer=null;
    search?.addEventListener("input",()=>{
      forcedSlugs=null;apply();clearTimeout(searchTimer);
      searchTimer=setTimeout(()=>{const q=norm(search.value||"");if(q)track("catalog_search",{query_length:q.length,result_count:cards.filter(c=>!c.hidden).length})},450);
    });
    $$(".filter-btn").forEach(btn=>btn.addEventListener("click",()=>{
      $$(".filter-btn").forEach(b=>b.setAttribute("aria-pressed","false"));btn.setAttribute("aria-pressed","true");
      filter=btn.dataset.filter||"all";forcedSlugs=null;apply();track("catalog_filter",{filter,release:CONFIG.release});
    }));
    $$(".path-card").forEach(btn=>btn.addEventListener("click",()=>{
      forcedSlugs=(btn.dataset.slugs||"").split(",").filter(Boolean);filter="all";
      $$(".filter-btn").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.filter==="all")));
      if(search)search.value="";apply();$("#catalogo")?.scrollIntoView({behavior:"smooth"});
      track("editorial_path_select",{path_key:btn.dataset.path||"",books:forcedSlugs.join("|"),release:CONFIG.release});
    }));
    apply();
  }

  // Share/copy. Return the method actually used; don't report native share when fallback copied the link.
  const share=async(data)=>{
    if(navigator.share){
      try{await navigator.share(data);return "native"}
      catch(e){if(e?.name==="AbortError")return null}
    }
    try{await navigator.clipboard.writeText(data.url||location.href);toast("Link copiado");return "copy"}
    catch(_){return null}
  };
  document.addEventListener("click",async e=>{
    const dialogTrigger=e.target.closest("[data-open-dialog]");
    if(dialogTrigger){e.preventDefault();const d=document.getElementById(dialogTrigger.dataset.openDialog);if(d?.showModal)d.showModal()}
    const shareBtn=e.target.closest("[data-share]");
    if(shareBtn){e.preventDefault();const method=await share({title:shareBtn.dataset.title||document.title,text:shareBtn.dataset.text||"",url:shareBtn.dataset.url||location.href});if(method)track("share",{content_name:shareBtn.dataset.title||document.title,method,release:CONFIG.release})}
    const copyBtn=e.target.closest("[data-copy]");
    if(copyBtn){e.preventDefault();let method="clipboard";try{await navigator.clipboard.writeText(copyBtn.dataset.copy||"");toast("Link copiado")}catch(_){method="prompt";prompt("Copie o link:",copyBtn.dataset.copy||"")}track("copy_link",{method,placement:copyBtn.dataset.placement||"",release:CONFIG.release})}
    const tracked=e.target.closest("[data-track]");
    if(tracked)track(tracked.dataset.track,{content_name:tracked.dataset.book||"",destination:safeDestination(tracked.href||""),placement:tracked.dataset.placement||"",release:CONFIG.release});
  });

  // Consent management: non-essential scripts are not requested before consent.
  const CONSENT_KEY="freedom_book_consent_v2";
  const parseConsent=()=>{const raw=storage.get(CONSENT_KEY);if(!raw)return null;try{const x=JSON.parse(raw);return {analytics:x.analytics===true,marketing:x.marketing===true}}catch(_){return null}};
  let consent=parseConsent()||{analytics:false,marketing:false};
  let gaLoaded=false,tiktokLoaded=false,perfStarted=false;
  const OPTIONAL_COOKIE_PREFIXES=["_ga","_gcl_","_ttp","_tt_enable_cookie"];
  const clearOptionalCookies=()=>{
    const expired="Thu, 01 Jan 1970 00:00:00 GMT";
    document.cookie.split(";").forEach(part=>{
      const name=(part.split("=")[0]||"").trim();
      if(!name||!OPTIONAL_COOKIE_PREFIXES.some(prefix=>name===prefix||name.startsWith(prefix)))return;
      ["",location.hostname,`.`+location.hostname].forEach(domain=>{
        document.cookie=`${name}=; expires=${expired}; Max-Age=0; path=/${domain?`; domain=${domain}`:""}`;
      });
    });
  };
  window.dataLayer=window.dataLayer||[];
  window.gtag=window.gtag||function(){window.dataLayer.push(arguments)};

  function initPerformanceTelemetry(){
    if(perfStarted||!("PerformanceObserver" in window))return;perfStarted=true;
    let cls=0,lcp=0,inp=0,fcp=0,ttfb=0;
    try{const navEntry=performance.getEntriesByType("navigation")[0];if(navEntry)ttfb=Math.round(navEntry.responseStart||0)}catch(_){}
    try{new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput)cls+=e.value}).observe({type:"layout-shift",buffered:true})}catch(_){}
    try{new PerformanceObserver(list=>{const es=list.getEntries();const last=es[es.length-1];if(last)lcp=Math.round(last.startTime)}).observe({type:"largest-contentful-paint",buffered:true})}catch(_){}
    try{new PerformanceObserver(list=>{for(const e of list.getEntries())inp=Math.max(inp,Math.round(e.duration||0))}).observe({type:"event",buffered:true,durationThreshold:40})}catch(_){}
    try{new PerformanceObserver(list=>{for(const e of list.getEntries())if(e.name==="first-contentful-paint")fcp=Math.round(e.startTime)}).observe({type:"paint",buffered:true})}catch(_){}
    addEventListener("pagehide",()=>track("page_quality",{cls:Number(cls.toFixed(3)),lcp_ms:lcp||undefined,inp_ms:inp||undefined,fcp_ms:fcp||undefined,ttfb_ms:ttfb||undefined,release:CONFIG.release}),{once:true});
  }
  function loadGA(){
    if(gaLoaded||!consent.analytics)return;gaLoaded=true;
    const s=document.createElement("script");s.async=true;s.src=`https://www.googletagmanager.com/gtag/js?id=${CONFIG.ga}`;s.onerror=()=>{gaLoaded=false};document.head.appendChild(s);
    window.gtag("js",new Date());window.gtag("config",CONFIG.ga,{anonymize_ip:true,send_page_view:true});initPerformanceTelemetry();
  }
  function loadTikTok(){
    if(tiktokLoaded||!consent.marketing)return;tiktokLoaded=true;
    !function(w,d,t){w.TiktokAnalyticsObject=t;var ttq=w[t]=w[t]||[];ttq.methods=["page","track","identify","instances","debug","on","off","once","ready","alias","group","enableCookie","disableCookie"];ttq.setAndDefer=function(t,e){t[e]=function(){t.push([e].concat([].slice.call(arguments,0)))}};for(var i=0;i<ttq.methods.length;i++)ttq.setAndDefer(ttq,ttq.methods[i]);ttq.load=function(e){var i="https://analytics.tiktok.com/i18n/pixel/events.js",o=d.createElement("script");o.async=true;o.src=i+"?sdkid="+e+"&lib="+t;o.onerror=function(){tiktokLoaded=false};var a=d.getElementsByTagName("script")[0];a.parentNode.insertBefore(o,a)};ttq.load(CONFIG.tiktok);ttq.page()}(window,document,"ttq");
  }
  function applyConsent(){loadGA();loadTikTok()}
  function saveConsent(next){
    const previous={...consent};
    const requiresReload=(gaLoaded&&!next.analytics)||(tiktokLoaded&&!next.marketing);
    consent={analytics:!!next.analytics,marketing:!!next.marketing};
    if((previous.analytics&&!consent.analytics)||(previous.marketing&&!consent.marketing))clearOptionalCookies();
    storage.set(CONSENT_KEY,JSON.stringify(consent));
    $("#consentBanner")?.classList.remove("open");applyConsent();
    if(requiresReload)location.reload();
  }
  const banner=$("#consentBanner");if(!parseConsent())banner?.classList.add("open");else applyConsent();
  $("#consentAccept")?.addEventListener("click",()=>saveConsent({analytics:true,marketing:true}));
  $("#consentReject")?.addEventListener("click",()=>saveConsent({analytics:false,marketing:false}));
  const prefs=$("#cookiePrefs");
  function openPrefs(){if(!prefs)return;const a=$("#prefAnalytics"),m=$("#prefMarketing");if(a)a.checked=!!consent.analytics;if(m)m.checked=!!consent.marketing;prefs.showModal?.()}
  $("#consentCustomize")?.addEventListener("click",openPrefs);
  $$(".open-cookie-prefs").forEach(b=>b.addEventListener("click",e=>{e.preventDefault();openPrefs()}));
  $("#prefSave")?.addEventListener("click",()=>{saveConsent({analytics:!!$("#prefAnalytics")?.checked,marketing:!!$("#prefMarketing")?.checked});prefs?.close()});
  $$(".dialog-close").forEach(b=>b.addEventListener("click",()=>b.closest("dialog")?.close()));

  const coarseTrafficSource=()=>{
    try{
      if(!document.referrer)return "direct";
      const h=new URL(document.referrer).hostname.toLowerCase();
      if(h===location.hostname)return "internal";
      if(/google\.|bing\.|duckduckgo\.|yahoo\.|brave\./.test(h))return "search";
      if(/instagram\.|facebook\.|tiktok\.|youtube\.|x\.com$|twitter\.|whatsapp\./.test(h))return "social";
      return "referral";
    }catch(_){return "unknown"}
  };
  const funnelMeta=()=>({release:CONFIG.release,traffic_source:coarseTrafficSource(),page_type:document.body?.dataset?.pageType||"page"});
  function track(name,params={}){
    if(consent.analytics&&typeof window.gtag==="function")window.gtag("event",name,{...funnelMeta(),...params});
    if(consent.marketing&&window.ttq?.track)try{window.ttq.track(name,{...funnelMeta(),...params})}catch(_){}
  }
  window.freedomTrack=track;
})();
