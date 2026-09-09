#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
CANON = "https://achadostube.com.br"


def write(path: str, content: str) -> None:
    (ROOT / path).write_text(content, encoding="utf-8")


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def redirect_page(title: str, canonical: str, target: str, follow: bool = True) -> str:
    robots = "noindex,follow" if follow else "noindex,nofollow,noarchive"
    return f'''<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="robots" content="{robots}">
  <link rel="canonical" href="{canonical}">
  <meta http-equiv="refresh" content="0;url={target}">
  <title>{title}</title>
</head>
<body>
  <main>
    <p>Redirecionando. <a href="{target}">Continuar</a>.</p>
  </main>
</body>
</html>
'''


LEGACY_CSS = r'''/* AchadosTube legacy offer surface v1 — lightweight, truthful and mobile-first */
:root{--bg:#f6f8fb;--panel:#fff;--ink:#172033;--muted:#667085;--line:#e5e9f0;--accent:#0f9f95;--accent2:#087b73;--soft:#e9fbf8;--radius:22px;--shadow:0 20px 55px rgba(25,35,55,.09);color-scheme:light}
*{box-sizing:border-box}html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}body{margin:0;background:linear-gradient(180deg,#fbfcfe,var(--bg));color:var(--ink);font:400 16px/1.58 Inter,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}body.theme-sandals{--accent:#7c3aed;--accent2:#5b21b6;--soft:#f3efff}a{color:inherit}.wrap{width:min(calc(100% - 28px),1080px);margin-inline:auto}.top{border-bottom:1px solid var(--line);background:rgba(255,255,255,.94);position:sticky;top:0;z-index:20;backdrop-filter:blur(14px)}.topin{min-height:66px;display:flex;align-items:center;justify-content:space-between;gap:14px}.brand{font-weight:900;letter-spacing:-.03em}.brand span{color:var(--accent)}.top a{font-weight:800;text-decoration:none}.hero{padding:46px 0 30px}.grid{display:grid;grid-template-columns:.92fr 1.08fr;gap:34px;align-items:center}.card{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow)}.media{padding:18px;display:grid;place-items:center}.media img{width:min(100%,440px);aspect-ratio:1/1;object-fit:cover;border-radius:17px;background:#eef2f6}.copy{padding:clamp(22px,4vw,40px)}.eyebrow{display:inline-flex;padding:7px 11px;border-radius:999px;background:var(--soft);color:var(--accent2);font-size:.78rem;font-weight:900;text-transform:uppercase;letter-spacing:.08em}.copy h1{font-size:clamp(2rem,5vw,3.7rem);line-height:1.02;letter-spacing:-.055em;margin:15px 0}.lead{font-size:1.06rem;color:var(--muted);margin:0}.notice{margin:20px 0;padding:14px 15px;border:1px solid var(--line);border-radius:15px;background:#fafbfd;color:#4f5b6d;font-size:.91rem}.actions{display:flex;gap:10px;flex-wrap:wrap}.btn{display:inline-flex;align-items:center;justify-content:center;min-height:52px;padding:0 19px;border-radius:14px;background:linear-gradient(180deg,var(--accent),var(--accent2));color:#fff;text-decoration:none;font-weight:900;border:0;cursor:pointer}.btn.secondary{background:#fff;color:var(--ink);border:1px solid var(--line)}.section{padding:36px 0}.section h2{font-size:clamp(1.55rem,3vw,2.2rem);letter-spacing:-.04em;margin:0 0 16px}.checks{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.check{padding:18px}.check strong{display:block;margin-bottom:6px}.check p{margin:0;color:var(--muted);font-size:.92rem}.disclosure{padding:18px 20px;background:#fff9e8;border-color:#f3dd9c}.disclosure strong{display:block;margin-bottom:5px}.disclosure p{margin:0;color:#6f5b24;font-size:.9rem}.footer{margin-top:36px;border-top:1px solid var(--line);padding:26px 0 96px;color:var(--muted);font-size:.88rem}.footerin{display:flex;justify-content:space-between;gap:18px;flex-wrap:wrap}.footer a{font-weight:800}.cookie-reopen{position:fixed;right:12px;bottom:12px;z-index:999;border:1px solid #d8dee8;background:#fff;color:#344054;border-radius:999px;padding:9px 12px;font:700 12px/1 system-ui;box-shadow:0 8px 25px rgba(0,0,0,.12);cursor:pointer}.consent-layer{position:fixed;inset:auto 10px 10px;z-index:1000}.consent-box{width:min(100%,720px);margin:auto;background:#101828;color:#fff;border-radius:18px;padding:17px;border:1px solid rgba(255,255,255,.14);box-shadow:0 24px 70px rgba(0,0,0,.35)}.consent-box strong{display:block;font-size:1rem;margin-bottom:5px}.consent-box p{margin:0;color:#d0d5dd;font-size:.86rem}.consent-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}.consent-actions button{min-height:42px;border:0;border-radius:11px;padding:0 14px;font-weight:850;cursor:pointer}.consent-yes{background:#fff;color:#101828}.consent-no{background:#344054;color:#fff}.consent-link{color:#d0d5dd;font-size:.8rem;margin-left:auto;align-self:center}@media(max-width:820px){.grid{grid-template-columns:1fr}.media{order:2}.checks{grid-template-columns:1fr 1fr}.hero{padding-top:20px}.copy{padding:22px}.actions{display:grid}.btn{width:100%}}@media(max-width:480px){.checks{grid-template-columns:1fr}.topin{min-height:60px}.topin .back{font-size:.86rem}}
'''

LEGACY_JS = r'''(() => {
  "use strict";
  const GA="G-DK72PVREEJ",TIKTOK="D78O6VJC77U8CCU0EA0G",KEY="freedom_book_consent_v2";
  const storage={get:k=>{try{return localStorage.getItem(k)}catch(_){return null}},set:(k,v)=>{try{localStorage.setItem(k,v)}catch(_){}}};
  const parse=()=>{const raw=storage.get(KEY);if(!raw)return null;try{const x=JSON.parse(raw);return {analytics:x.analytics===true,marketing:x.marketing===true}}catch(_){return null}};
  let consent=parse()||{analytics:false,marketing:false},gaLoaded=false,ttLoaded=false;
  const clearOptionalCookies=()=>{const expired="Thu, 01 Jan 1970 00:00:00 GMT";document.cookie.split(";").forEach(part=>{const name=(part.split("=")[0]||"").trim();if(!name||!["_ga","_gcl_","_ttp","_tt_enable_cookie"].some(p=>name===p||name.startsWith(p)))return;["",location.hostname,`.`+location.hostname].forEach(domain=>{document.cookie=`${name}=; expires=${expired}; Max-Age=0; path=/${domain?`; domain=${domain}`:""}`})})};
  function loadGA(){if(gaLoaded||!consent.analytics)return;gaLoaded=true;window.dataLayer=window.dataLayer||[];window.gtag=window.gtag||function(){window.dataLayer.push(arguments)};const s=document.createElement("script");s.async=true;s.src=`https://www.googletagmanager.com/gtag/js?id=${GA}`;s.onerror=()=>{gaLoaded=false};document.head.appendChild(s);window.gtag("js",new Date());window.gtag("config",GA,{anonymize_ip:true,send_page_view:true})}
  function loadTikTok(){if(ttLoaded||!consent.marketing)return;ttLoaded=true;!function(w,d,t){w.TiktokAnalyticsObject=t;var q=w[t]=w[t]||[];q.methods=["page","track","identify","instances","debug","on","off","once","ready","alias","group","enableCookie","disableCookie"];q.setAndDefer=function(x,e){x[e]=function(){x.push([e].concat([].slice.call(arguments,0)))}};for(var i=0;i<q.methods.length;i++)q.setAndDefer(q,q.methods[i]);q._i=q._i||{};q._t=q._t||{};q._o=q._o||{};q.load=function(id,opts){var u="https://analytics.tiktok.com/i18n/pixel/events.js",o=d.createElement("script");q._i[id]=[];q._i[id]._u=u;q._t[id]=+new Date;q._o[id]=opts||{};o.async=true;o.src=u+"?sdkid="+id+"&lib="+t;o.onerror=function(){ttLoaded=false};var a=d.getElementsByTagName("script")[0];a.parentNode.insertBefore(o,a)};q.load(TIKTOK);q.page()}(window,document,"ttq")}
  const apply=()=>{loadGA();loadTikTok()};
  const layer=()=>document.getElementById("legacyConsentLayer");
  function renderConsent(){if(layer())return;const el=document.createElement("div");el.id="legacyConsentLayer";el.className="consent-layer";el.innerHTML='<div class="consent-box" role="region" aria-label="Preferências de privacidade"><strong>Privacidade e métricas</strong><p>A página funciona sem cookies opcionais. Você pode permitir métricas de audiência e marketing ou continuar somente com o necessário.</p><div class="consent-actions"><button class="consent-yes" type="button">Aceitar opcionais</button><button class="consent-no" type="button">Somente necessários</button><a class="consent-link" href="/privacidade">Política de privacidade</a></div></div>';document.body.appendChild(el);el.querySelector(".consent-yes").addEventListener("click",()=>save({analytics:true,marketing:true}));el.querySelector(".consent-no").addEventListener("click",()=>save({analytics:false,marketing:false}))}
  function save(next){const prev={...consent};consent={analytics:!!next.analytics,marketing:!!next.marketing};if((prev.analytics&&!consent.analytics)||(prev.marketing&&!consent.marketing))clearOptionalCookies();storage.set(KEY,JSON.stringify(consent));layer()?.remove();apply();if((gaLoaded&&!consent.analytics)||(ttLoaded&&!consent.marketing))location.reload()}
  function addReopen(){if(document.querySelector(".cookie-reopen"))return;const b=document.createElement("button");b.className="cookie-reopen";b.type="button";b.textContent="Cookies";b.addEventListener("click",renderConsent);document.body.appendChild(b)}
  document.addEventListener("click",e=>{const a=e.target.closest('a[href*="s.shopee.com.br"]');if(!a)return;const placement=a.dataset.location||"offer";if(consent.analytics&&typeof window.gtag==="function")window.gtag("event","affiliate_click",{placement,destination:"shopee",page_type:"legacy_affiliate"});if(consent.marketing&&window.ttq?.track)try{window.ttq.track("ClickButton",{content_type:"product",content_name:document.body?.dataset?.offerSlug||"legacy_offer",placement})}catch(_){}});
  if(parse())apply();else renderConsent();addReopen();
})();
'''


def offer_page(slug: str, title: str, description: str, image: str, affiliate: str, theme_class: str = "") -> str:
    canonical = f"{CANON}/{slug}"
    body_class = f' class="{theme_class}"' if theme_class else ""
    theme_color = "#7c3aed" if theme_class else "#0f9f95"
    data_title = title.replace('"', '&quot;')
    schema = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "url": canonical,
        "description": description,
        "inLanguage": "pt-BR",
        "isPartOf": {"@type": "WebSite", "name": "AchadosTube", "url": f"{CANON}/"},
    }
    return f'''<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <title>{title} | AchadosTube</title>
  <meta name="description" content="{description}">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <meta name="theme-color" content="{theme_color}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:locale" content="pt_BR">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title} | AchadosTube">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{image}">
  <meta property="og:image:alt" content="{data_title}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title} | AchadosTube">
  <meta name="twitter:description" content="{description}">
  <meta name="twitter:image" content="{image}">
  <link rel="preconnect" href="https://down-br.img.susercontent.com" crossorigin>
  <link rel="preload" href="{image}" as="image" fetchpriority="high">
  <link rel="stylesheet" href="/assets/legacy-offer.v1.css">
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(',', ':'))}</script>
  <script defer src="/assets/legacy-consent.v1.js"></script>
</head>
<body{body_class} data-page-type="legacy_affiliate" data-offer-slug="{slug}">
  <header class="top"><div class="wrap topin"><div class="brand">Achados<span>Tube</span></div><a class="back" href="/">Freedom Book</a></div></header>
  <main>
    <section class="hero"><div class="wrap grid">
      <div class="card media"><img src="{image}" alt="{data_title}" width="450" height="450" decoding="async" fetchpriority="high"></div>
      <article class="card copy">
        <span class="eyebrow">Oferta em loja parceira</span>
        <h1>{title}</h1>
        <p class="lead">{description}</p>
        <div class="notice"><strong>Condições atualizadas na Shopee.</strong> Preço, estoque, frete, parcelamento, prazo e políticas de compra podem mudar. Confira essas informações diretamente no anúncio antes de finalizar.</div>
        <div class="actions">
          <a class="btn" href="{affiliate}" target="_blank" rel="sponsored noopener noreferrer" data-location="hero">Ver oferta atual na Shopee</a>
          <a class="btn secondary" href="#antes-de-comprar">O que conferir antes</a>
        </div>
      </article>
    </div></section>
    <section class="section" id="antes-de-comprar"><div class="wrap">
      <h2>Antes de comprar</h2>
      <div class="checks">
        <div class="card check"><strong>Variação e tamanho</strong><p>Confirme numeração, modelo, cor e itens incluídos no anúncio selecionado.</p></div>
        <div class="card check"><strong>Avaliações do anúncio</strong><p>Consulte avaliações e fotos publicadas na própria Shopee para a oferta atual.</p></div>
        <div class="card check"><strong>Frete e prazo</strong><p>Verifique o cálculo para seu CEP, pois condições de entrega variam por região e vendedor.</p></div>
        <div class="card check"><strong>Políticas da compra</strong><p>Confira devolução, garantia e suporte aplicáveis diretamente na plataforma e no anúncio.</p></div>
      </div>
    </div></section>
    <section class="section"><div class="wrap card disclosure"><strong>Transparência de afiliado</strong><p>Esta é uma página legada de indicação do AchadosTube. O link pode gerar comissão de afiliado sem custo adicional para você. O AchadosTube não é o vendedor e não controla preço, estoque, frete, prazo, garantia ou condições do anúncio.</p></div></section>
    <section class="section"><div class="wrap actions"><a class="btn" href="{affiliate}" target="_blank" rel="sponsored noopener noreferrer" data-location="final">Conferir oferta na Shopee</a></div></section>
  </main>
  <footer class="footer"><div class="wrap footerin"><span>AchadosTube · página legada de indicação</span><span><a href="/privacidade">Privacidade</a> · <a href="/">Freedom Book</a></span></div></footer>
</body>
</html>
'''


write("assets/legacy-offer.v1.css", LEGACY_CSS)
write("assets/legacy-consent.v1.js", LEGACY_JS)

write(
    "kit-3-pares.html",
    offer_page(
        "kit-3-pares",
        "Kit 3 Pares Tênis Infantil + Sandália",
        "Acesso rápido ao anúncio do kit infantil na Shopee, com conferência das condições atuais diretamente na plataforma.",
        "https://down-br.img.susercontent.com/file/br-11134207-7r98o-m8yy2m40hoop76@resize_w450_nl.webp",
        "https://s.shopee.com.br/1qY8M5JuwS",
    ),
)
write(
    "kit-sandalias-infantil.html",
    offer_page(
        "kit-sandalias-infantil",
        "Kit 2 Pares Sandálias Infantil Stitch e Minnie Mouse",
        "Acesso rápido ao anúncio do kit de sandálias infantis na Shopee, com preço, frete, estoque e demais condições conferidos na plataforma.",
        "https://down-br.img.susercontent.com/file/br-11134207-7r98o-m954tenhlqnt3f@resize_w450_nl.webp",
        "https://s.shopee.com.br/7Kt6RkhRF1",
        "theme-sandals",
    ),
)

write(
    "kit-tenis-sandalia.html",
    redirect_page(
        "Kit infantil — endereço atualizado | AchadosTube",
        f"{CANON}/kit-3-pares",
        "/kit-3-pares",
        True,
    ),
)
write(
    "leitor.html",
    redirect_page(
        "O Cansaço Invisível — página atualizada | Freedom Book",
        f"{CANON}/o-cansaco-invisivel",
        "/o-cansaco-invisivel",
        True,
    ),
)
write(
    "locked/the_select.html",
    redirect_page(
        "Conteúdo descontinuado | AchadosTube",
        f"{CANON}/",
        "/",
        False,
    ),
)

# Keep host-portability redirects aligned with the HTML fallbacks.
redirects = read("_redirects")
for rule in (
    "/leitor /o-cansaco-invisivel 301",
    "/leitor.html /o-cansaco-invisivel 301",
    "/kit-tenis-sandalia /kit-3-pares 301",
    "/kit-tenis-sandalia.html /kit-3-pares 301",
    "/locked/the_select / 301",
    "/locked/the_select.html / 301",
):
    if rule not in redirects:
        redirects += ("\n" if not redirects.endswith("\n") else "") + rule + "\n"
write("_redirects", redirects)

# Documentation truth: remove stale V2.2.3-as-current statements without changing historical assets.
readme = read("README.md")
readme = readme.replace("Freedom Book V2.2.3", "Freedom Book V2.2.5")
readme = readme.replace("assets/style.v2.2.3.css` — CSS ativo", "assets/style.v2.2.5.css` — CSS ativo")
readme = readme.replace("assets/app.v2.2.3.js` — runtime ativo", "assets/app.v2.2.5.js` — runtime ativo")
readme = readme.replace("(`style.v2.2.3.css` / `app.v2.2.3.js`)", "(`style.v2.2.5.css` / `app.v2.2.5.js`)")
readme = readme.replace("A V2.2.3 acrescenta metadados", "A V2.2.5 mantém metadados")
legacy_note = "- `assets/legacy-offer.v1.css` + `assets/legacy-consent.v1.js` — superfície leve das páginas legadas de afiliado, com consentimento antes de métricas e sem urgência/estoque/preço simulados.\n"
anchor = "- `product/`, `locked/` e páginas `kit-*` — legado AchadosTube/Shopee preservado para compatibilidade e tráfego existente.\n"
if legacy_note not in readme:
    readme = readme.replace(anchor, anchor + legacy_note)
write("README.md", readme)

marker = {
    "schema": "achadostube-maintenance-marker-v1",
    "campaign": "legacy-surface-integrity",
    "version": 1,
    "source": "main",
    "origin": f"{CANON}/",
}
write("maintenance-marker.json", json.dumps(marker, ensure_ascii=False, indent=2) + "\n")

# Expand the permanent validator to cover the public legacy surface that used to escape the release gate.
vp = ROOT / "scripts/validate_site.py"
v = vp.read_text(encoding="utf-8")
insert = r'''

# Public legacy surface integrity: preserve traffic without stale prices, fabricated urgency or pre-consent tracking.
LEGACY_OFFERS={
    'kit-3-pares.html':CANON+'/kit-3-pares',
    'kit-sandalias-infantil.html':CANON+'/kit-sandalias-infantil',
}
for name,canonical in LEGACY_OFFERS.items():
    text=(ROOT/name).read_text('utf-8'); p=Parser(); p.feed(text)
    if p.h1!=1:fail(f'{name}: legacy offer must have exactly one h1')
    if p.canon!=[canonical]:fail(f'{name}: legacy canonical mismatch {p.canon}')
    if '/assets/legacy-offer.v1.css' not in text or '/assets/legacy-consent.v1.js' not in text:fail(f'{name}: legacy shared assets missing')
    if 'googletagmanager.com/gtag/js' in text or 'analytics.tiktok.com' in text:fail(f'{name}: static tracker before consent')
    if 'R$' in text:fail(f'{name}: stale static price reintroduced')
    for bad in ('vendidos hoje','unidades restantes','estoque quase zerado','estão vendo esta oferta agora','mães reais','oferta relâmpago','últimas unidades','garantia 30 dias'):
        if bad in text.lower():fail(f'{name}: unsupported urgency/social-proof claim reintroduced: {bad}')
    if re.search(r"ttq\.track\(['\"]Purchase",text,re.I) or re.search(r"gtag\(['\"]event['\"],\s*['\"]purchase",text,re.I):fail(f'{name}: click-to-purchase telemetry reintroduced')
    links=re.findall(r'<a\b[^>]*href="https://s\.shopee\.com\.br/[^"]+"[^>]*>',text,re.I)
    if not links:fail(f'{name}: affiliate destination missing')
    for tag in links:
        m=re.search(r'rel="([^"]+)"',tag,re.I)
        rel=set((m.group(1) if m else '').lower().split())
        if not {'sponsored','noopener','noreferrer'}<=rel:fail(f'{name}: affiliate rel contract missing {tag}')

legacy_js=(ROOT/'assets/legacy-consent.v1.js').read_text('utf-8')
for marker in ('freedom_book_consent_v2','affiliate_click','ClickButton','clearOptionalCookies'):
    if marker not in legacy_js:fail(f'legacy consent contract missing: {marker}')
if 'Purchase' in legacy_js:fail('legacy consent runtime must never synthesize purchase events')

# Duplicate/obsolete routes are kept as safe noindex redirects, never as parallel indexable surfaces.
redirect_contracts={
    'kit-tenis-sandalia.html':(CANON+'/kit-3-pares','/kit-3-pares'),
    'leitor.html':(CANON+'/o-cansaco-invisivel','/o-cansaco-invisivel'),
    'locked/the_select.html':(CANON+'/','/'),
}
for name,(canonical,target) in redirect_contracts.items():
    text=(ROOT/name).read_text('utf-8').lower()
    if 'noindex' not in text:fail(f'{name}: obsolete route must be noindex')
    if canonical.lower() not in text or f'url={target}'.lower() not in text:fail(f'{name}: redirect target mismatch')
    if 'googletagmanager.com' in text or 'analytics.tiktok.com' in text:fail(f'{name}: tracker must not load on redirect')
if 'o_cansaco_invisivel.pdf' in (ROOT/'leitor.html').read_text('utf-8'):fail('broken legacy reader PDF path reintroduced')
if 'theselect.com.br' in (ROOT/'locked/the_select.html').read_text('utf-8') or 'example.com' in (ROOT/'locked/the_select.html').read_text('utf-8'):fail('locked placeholder identity/data reintroduced')

# Documentation and maintenance deploy marker must describe the actual production state.
readme=(ROOT/'README.md').read_text('utf-8')
for required in ('Freedom Book V2.2.5','assets/style.v2.2.5.css','assets/app.v2.2.5.js','assets/legacy-consent.v1.js'):
    if required not in readme:fail(f'README production truth missing: {required}')
for stale in ('Freedom Book V2.2.3','assets/style.v2.2.3.css` — CSS ativo','assets/app.v2.2.3.js` — runtime ativo'):
    if stale in readme:fail(f'README stale current-version statement: {stale}')
maintenance=json.loads((ROOT/'maintenance-marker.json').read_text('utf-8'))
expected_maintenance={'schema':'achadostube-maintenance-marker-v1','campaign':'legacy-surface-integrity','version':1,'source':'main','origin':CANON+'/'}
if maintenance!=expected_maintenance:fail(f'maintenance marker mismatch: {maintenance}')
'''
final_print="print(f'PASS: Freedom Book {RELEASE}; {len(EXPECTED_HTML)} editorial HTML; {len(available)} available books; {len(urls)} sitemap routes; {len(entries)} feed entries; {len(art)} release artifacts')\n"
if "LEGACY_OFFERS={" not in v:
    if final_print not in v:
        raise SystemExit("validator final print anchor missing")
    v = v.replace(final_print, insert + "\n" + final_print)
vp.write_text(v, encoding="utf-8")

print("Legacy surface integrity candidate built successfully")
