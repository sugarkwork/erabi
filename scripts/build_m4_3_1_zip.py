"""Package M4.3.1 Semantic Repair review bundle zip excluding weights, virtualenvs, and secrets."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "runs/m4_3_1_phrasing_fix"
ZIP_PATH = OUT_DIR / "review_bundle.zip"

EXCLUDED_EXTENSIONS = {".safetensors", ".bin", ".pt", ".pth", ".onnx", ".pyc", ".zip"}
EXCLUDED_DIRS = {".venv", ".git", "__pycache__", ".pytest_cache", ".idea", ".vscode"}


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def should_include(rel_path: Path) -> bool:
    parts = rel_path.parts
    for part in parts:
        if part in EXCLUDED_DIRS:
            return False
    if rel_path.suffix in EXCLUDED_EXTENSIONS:
        return False
    if "checkpoint" in parts and rel_path.suffix in {".safetensors", ".bin", ".pt", ".pth"}:
        return False
    if rel_path.name == "tokenizer.json" and "checkpoint" in parts:
        return False
    if "api_key" in rel_path.name.lower() or "secret" in rel_path.name.lower():
        return False
    return True


def main():
    print("Creating review_bundle.zip for M4.3.1 Phrasing Semantic Repair...")
    files_to_add = []

    # 1. runs/m4_3_1_phrasing_fix/ artifacts
    for p in OUT_DIR.rglob("*"):
        if p.is_file() and p.name != "review_bundle.zip" and should_include(p.relative_to(ROOT)):
            files_to_add.append(p)

    # 2. data/m4_3_1_phrasing_fix/
    for p in (ROOT / "data/m4_3_1_phrasing_fix").rglob("*"):
        if p.is_file() and should_include(p.relative_to(ROOT)):
            files_to_add.append(p)

    # 3. Source code in src/erabi/
    for p in (ROOT / "src/erabi").rglob("*"):
        if p.is_file() and should_include(p.relative_to(ROOT)):
            files_to_add.append(p)

    # 4. Relevant scripts
    script_names = [
        "scripts/build_m4_3_1_repaired_data.py",
        "scripts/train_m4_3_1_phrasing.py",
        "scripts/run_m4_3_1_comparisons.py",
        "scripts/make_m4_3_1_summary.py",
        "scripts/build_m4_3_1_zip.py",
        "scripts/build_m4_3_data.py",
        "scripts/train_m4_3_phrasing.py",
        "scripts/run_m4_3_comparisons.py",
    ]
    for sname in script_names:
        sp = ROOT / sname
        if sp.is_file():
            files_to_add.append(sp)

    # 5. Relevant tests
    for p in (ROOT / "tests").rglob("*"):
        if p.is_file() and should_include(p.relative_to(ROOT)):
            files_to_add.append(p)

    # 6. Smoke cases
    smoke_path = ROOT / "examples/smoke_cases.jsonl"
    if smoke_path.is_file():
        files_to_add.append(smoke_path)

    # 7. Documentation and instructions
    doc_files = [
        "STATUS.md",
        "pyproject.toml",
        "AGENTS.md",
        "docs/ERABI_DESIGN.md",
        "ERABI_M4_3_1_SEMANTIC_REPAIR_NEXT.md",
        "ERABI_M4_3_ZIP_AUDIT.md",
    ]
    for fname in doc_files:
        fp = ROOT / fname
        if fp.is_file():
            files_to_add.append(fp)

    # De-duplicate while preserving order
    unique_files = []
    seen = set()
    for f in files_to_add:
        rpath = f.relative_to(ROOT)
        if rpath not in seen:
            seen.add(rpath)
            unique_files.append(f)

    print(f"Total files to package: {len(unique_files)}")

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in unique_files:
            rel = f.relative_to(ROOT)
            zf.write(f, arcname=str(rel).replace("\\", "/"))

    zip_size = ZIP_PATH.stat().st_size
    zip_sha = compute_sha256(ZIP_PATH)

    print(f"review_bundle.zip successfully created!")
    print(f"Path: {ZIP_PATH}")
    print(f"Size: {zip_size:,} bytes ({zip_size / (1024*1024):.2f} MB)")
    print(f"SHA-256: {zip_sha}")

    # Write manifest
    manifest_data = {
        "zip_file": "runs/m4_3_1_phrasing_fix/review_bundle.zip",
        "size_bytes": zip_size,
        "sha256": zip_sha,
        "file_count": len(unique_files),
        "files": [str(f.relative_to(ROOT)).replace("\\", "/") for f in unique_files],
    }
    with open(OUT_DIR / "review_bundle_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
