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


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST_ADMIN.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SRC_ADMIN, DIST_ADMIN)

    # Public release evidence is copied into the private runtime so the admin can
    # compare the repository authority without a cross-origin fetch.
    shutil.copy2(ROOT / "release.json", DIST / "release.json")

    index_path = DIST_ADMIN / "index.html"
    index = index_path.read_text(encoding="utf-8")

    # Historical duplicate script tags are normalized only in the private runtime.
    index = re.sub(r"\n\s*<script src=\"/admin/knowledge-layer\.js\" defer></script>", "", index)
    app_tag = '  <script src="/admin/app.js" defer></script>'
    if app_tag not in index:
        raise SystemExit("admin app script marker not found")
    index = index.replace(
        app_tag,
        '  <script src="/admin/runtime-adapter.js" defer></script>\n' + app_tag,
        1,
    )
    index = index.replace(
        "</body>",
        '  <script src="/admin/knowledge-layer.js" defer></script>\n</body>',
        1,
    )
    index_path.write_text(index, encoding="utf-8")

    (DIST_ADMIN / "runtime-adapter.js").write_text(PRIVATE_RUNTIME_ADAPTER, encoding="utf-8")

    # Generate a cryptographic runtime release from the exact bytes Netlify serves.
    source_release = json.loads((SRC_ADMIN / "release.json").read_text(encoding="utf-8"))
    artifact_names = [
        "index.html",
        "style.css",
        "app.js",
        "book-publisher.js",
        "control-plane.json",
        "knowledge.json",
        "knowledge-layer.js",
        "runtime-adapter.js",
    ]
    runtime_release = {
        "schema": source_release["schema"],
        "surface": "/admin/",
        "publishedFrom": "main",
        "version": source_release["version"],
        "hosting": "netlify-private",
        "access": "team-sso",
        "artifacts": {name: sha256(DIST_ADMIN / name) for name in artifact_names},
    }
    (DIST_ADMIN / "release.json").write_text(
        json.dumps(runtime_release, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    (DIST / "index.html").write_text(
        '<!doctype html><html lang="pt-BR"><meta charset="utf-8">'
        '<meta name="robots" content="noindex,nofollow,noarchive,nosnippet">'
        '<meta http-equiv="refresh" content="0;url=/admin/">'
        '<title>Freedom Admin</title><a href="/admin/">Abrir Control Center</a></html>\n',
        encoding="utf-8",
    )

    # Deterministic safety checks.
    built_index = index_path.read_text(encoding="utf-8")
    if built_index.count('/admin/knowledge-layer.js') != 1:
        raise SystemExit("knowledge layer script count must be exactly one")
    if built_index.count('/admin/runtime-adapter.js') != 1:
        raise SystemExit("runtime adapter script count must be exactly one")
    if built_index.index('/admin/runtime-adapter.js') > built_index.index('/admin/app.js'):
        raise SystemExit("runtime adapter must load before app.js")
    print(f"Private admin runtime built: {len(artifact_names)} artifacts")


if __name__ == "__main__":
    main()
