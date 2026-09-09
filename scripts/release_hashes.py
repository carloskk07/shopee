#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE_PATH = ROOT / "release.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_release() -> dict:
    return json.loads(RELEASE_PATH.read_text(encoding="utf-8"))


def collect(release: dict) -> tuple[dict[str, str], list[str]]:
    actual: dict[str, str] = {}
    missing: list[str] = []
    for rel in release.get("artifacts", {}):
        path = ROOT / rel
        if not path.is_file():
            missing.append(rel)
            continue
        actual[rel] = sha256(path)
    return actual, missing


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit or regenerate release.json SHA-256 artifact hashes.")
    parser.add_argument("--write", action="store_true", help="Replace artifact hashes in release.json with current bytes.")
    parser.add_argument("--changed-only", action="store_true", help="Print only missing or mismatched artifacts.")
    args = parser.parse_args()

    release = load_release()
    expected = release.get("artifacts", {})
    actual, missing = collect(release)
    mismatches = [(rel, expected.get(rel), digest) for rel, digest in actual.items() if expected.get(rel) != digest]

    if args.write:
        if missing:
            for rel in missing:
                print(f"MISSING {rel}")
            return 2
        release["artifacts"] = {rel: actual[rel] for rel in expected}
        RELEASE_PATH.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"UPDATED release.json: {len(actual)} artifact hashes")
        return 0

    if not args.changed_only:
        for rel, digest in actual.items():
            print(f"SHA256 {rel} {digest}")
    for rel in missing:
        print(f"MISSING {rel}")
    for rel, old, new in mismatches:
        print(f"MISMATCH {rel} {new} expected={old}")

    if missing or mismatches:
        print(f"FAIL: {len(missing)} missing; {len(mismatches)} hash mismatch(es)")
        return 1
    print(f"PASS: {len(actual)} release artifact hashes match current bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
