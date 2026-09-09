#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE_PATH = ROOT / 'release.json'

release = json.loads(RELEASE_PATH.read_text(encoding='utf-8'))
artifacts = release.setdefault('artifacts', {})
artifacts.setdefault('assets/route-recovery.v1.js', '')
artifacts.setdefault('route-shims.generated.json', '')

for relative in sorted(artifacts):
    path = ROOT / relative
    if not path.is_file():
        raise SystemExit(f'missing release artifact: {relative}')
    artifacts[relative] = hashlib.sha256(path.read_bytes()).hexdigest()

RELEASE_PATH.write_text(
    json.dumps(release, ensure_ascii=False, indent=2, sort_keys=True) + '\n',
    encoding='utf-8',
)

print(f'Refreshed {len(artifacts)} release artifact hashes')
