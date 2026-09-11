#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_ADMIN = ROOT / "admin"
DIST = ROOT / "netlify-admin-dist"
DIST_ADMIN = DIST / "admin"

PRIVATE_RUNTIME_ADAPTER = r'''(() => {
  'use strict';
  const PUBLIC_SITE='https://achadostube.com.br';
  const nativeFetch=window.fetch.bind(window);
  const isPrivateNetlify=/^freedom-book-admin\.netlify\.app$/.test(location.hostname)||/--freedom-book-admin\.netlify\.app$/.test(location.hostname);
  if(!isPrivateNetlify)return;
  const rewrite=input=>{
    try{
      const u=new URL(typeof input==='string'?input:input.url,location.href);
      if(u.origin===PUBLIC_SITE&&u.pathname==='/release.json')return `${location.origin}/release.json${u.search}`;
      if(u.origin===PUBLIC_SITE&&u.pathname==='/admin/release.json')return `${location.origin}/admin/release.json${u.search}`;
    }catch(_){}
    return input;
  };
  window.fetch=(input,init)=>{
    const rewritten=rewrite(input);
    if(rewritten===input)return nativeFetch(input,init);
    if(typeof input==='string')return nativeFetch(rewritten,init);
    try{return nativeFetch(new Request(rewritten,input),init)}catch(_){return nativeFetch(rewritten,init)}
  };
  window.__FCC_ADMIN_RUNTIME__={hosting:'netlify-private',access:'team-sso',publicSite:PUBLIC_SITE};
})();
'''


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"private runtime patch marker missing: {label}")
    return text.replace(old, new, 1)


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST_ADMIN.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SRC_ADMIN, DIST_ADMIN)
    shutil.copy2(ROOT / "release.json", DIST / "release.json")

    index_path = DIST_ADMIN / "index.html"
    index = index_path.read_text(encoding="utf-8")
    index = re.sub(r"\n\s*<script src=\"/admin/knowledge-layer\.js\" defer></script>", "", index)
    app_tag = '  <script src="/admin/app.js" defer></script>'
    if app_tag not in index:
        raise SystemExit("admin app script marker not found")
    index = index.replace(app_tag, '  <script src="/admin/runtime-adapter.js" defer></script>\n' + app_tag + '\n  <script src="/admin/operational-brain.js" defer></script>', 1)
    index = index.replace("</body>", '  <script src="/admin/knowledge-layer.js" defer></script>\n</body>', 1)
    index_path.write_text(index, encoding="utf-8")
    (DIST_ADMIN / "runtime-adapter.js").write_text(PRIVATE_RUNTIME_ADAPTER, encoding="utf-8")

    # Private-only patch: prefer the server-side GitHub publisher for textual Change Sets.
    app_path = DIST_ADMIN / "app.js"
    app = app_path.read_text(encoding="utf-8")
    app = replace_once(app,
        "const p=$('#publishBtn');if(p)p.disabled=!state.token||!n",
        "const p=$('#publishBtn');if(p)p.disabled=!(state.token||window.__FCC_SERVER_GITHUB_READY__)||!n",
        "publish button server readiness")
    app = replace_once(app,
        "async function showPublish(){if(!state.token)return showSession();",
        "async function showPublish(){if(!state.token&&!window.__FCC_SERVER_GITHUB_READY__)return showSession();",
        "showPublish server readiness")
    app = replace_once(app,
        "if(!state.token)throw new Error('Sessão expirada');const files=await preparedFiles();if(files.size>",
        "const files=await preparedFiles();if(window.__FCC_SERVER_GITHUB_READY__&&!state.token){if([...files.values()].some(x=>x.encoding==='base64'))throw new Error('Publicação server-side ainda não aceita binários; conecte uma sessão GitHub para publicar livros.');const rsp=await fetch('/api/github/publish',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({title,summary,files:[...files.values()].map(x=>({path:x.path,content:x.content,encoding:x.encoding||'utf-8'})),branchPrefix:config().publishing?.branchPrefix||'control-center/'})});const out=await rsp.json().catch(()=>({}));if(!rsp.ok)throw new Error(out.error||`Backend GitHub ${rsp.status}`);clearStaged();$('#publishDialog').close();toast(`PR #${out.number} criado pelo backend privado`);openUrl(out.html_url);await sleep(900);await loadAll();setView('deploy');return;}if(!state.token)throw new Error('Sessão expirada');if(files.size>",
        "createPr server publisher")
    app_path.write_text(app, encoding="utf-8")

    source_release = json.loads((SRC_ADMIN / "release.json").read_text(encoding="utf-8"))
    artifact_names = [
        "index.html", "style.css", "app.js", "book-publisher.js", "control-plane.json",
        "knowledge.json", "knowledge-layer.js", "operational-brain.js", "runtime-adapter.js",
    ]
    runtime_release = {
        "schema": source_release["schema"],
        "surface": "/admin/",
        "publishedFrom": "main",
        "version": source_release["version"],
        "hosting": "netlify-private",
        "access": "team-sso",
        "capabilities": ["operational-brain", "audit-trail", "gsc-auto-ready", "github-server-publish-ready"],
        "artifacts": {name: sha256(DIST_ADMIN / name) for name in artifact_names},
    }
    (DIST_ADMIN / "release.json").write_text(json.dumps(runtime_release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    (DIST / "index.html").write_text(
        '<!doctype html><html lang="pt-BR"><meta charset="utf-8">'
        '<meta name="robots" content="noindex,nofollow,noarchive,nosnippet">'
        '<meta http-equiv="refresh" content="0;url=/admin/">'
        '<title>Freedom Admin</title><a href="/admin/">Abrir Control Center</a></html>\n',
        encoding="utf-8",
    )

    built_index = index_path.read_text(encoding="utf-8")
    if built_index.count('/admin/knowledge-layer.js') != 1:
        raise SystemExit("knowledge layer script count must be exactly one")
    if built_index.count('/admin/runtime-adapter.js') != 1 or built_index.count('/admin/operational-brain.js') != 1:
        raise SystemExit("private runtime scripts must be loaded exactly once")
    if built_index.index('/admin/runtime-adapter.js') > built_index.index('/admin/app.js'):
        raise SystemExit("runtime adapter must load before app.js")
    built_app = app_path.read_text(encoding="utf-8")
    for marker in ('__FCC_SERVER_GITHUB_READY__', '/api/github/publish', 'backend privado'):
        if marker not in built_app:
            raise SystemExit(f"private runtime app patch missing: {marker}")
    print(f"Private admin runtime built: {len(artifact_names)} artifacts")


if __name__ == "__main__":
    main()
