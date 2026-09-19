"""Package M4.3-P Phrasing Diversification review bundle zip excluding weights, virtualenvs, and secrets."""

from __future__ import annotations

import hashlib
import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "runs/m4_3_phrasing"
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
    # Exclude model weights and huge files inside checkpoints
    if "checkpoint" in parts and rel_path.suffix in {".safetensors", ".bin", ".pt", ".pth"}:
        return False
    if rel_path.name == "tokenizer.json" and "checkpoint" in parts:
        return False
    if "api_key" in rel_path.name.lower() or "secret" in rel_path.name.lower():
        return False
    return True


def main():
    print("Creating review_bundle.zip for M4.3-P Phrasing Diversification...")
    files_to_add = []

    # 1. runs/m4_3_phrasing/ artifacts (excluding checkpoint weights and zip itself)
    for p in OUT_DIR.rglob("*"):
        if p.is_file() and p.name != "review_bundle.zip" and should_include(p.relative_to(ROOT)):
            files_to_add.append(p)

    # 2. data/m4_3_phrasing/
    for p in (ROOT / "data/m4_3_phrasing").rglob("*"):
        if p.is_file() and should_include(p.relative_to(ROOT)):
            files_to_add.append(p)

    # 3. Source code in src/erabi/
    for p in (ROOT / "src/erabi").rglob("*"):
        if p.is_file() and should_include(p.relative_to(ROOT)):
            files_to_add.append(p)

    # 4. Relevant scripts
    script_names = [
        "scripts/build_m4_3_data.py",
        "scripts/eval_m4_3_baselines.py",
        "scripts/train_m4_3_phrasing.py",
        "scripts/run_m4_3_comparisons.py",
        "scripts/make_m4_3_summary.py",
        "scripts/build_m4_3_zip.py",
        "scripts/build_m4_2_1_diagnostic_data.py",
        "scripts/run_m4_2_1_diagnostic_eval.py",
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
        "ERABI_M4_3_PHRASING_DIVERSIFICATION_NEXT.md",
    ]
    for fname in doc_files:
        fp = ROOT / fname
        if fp.is_file():
            files_to_add.append(fp)

    # Deduplicate and sort
    unique_files = sorted(list(set(files_to_add)))

    # Remove existing zip if present
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for fpath in unique_files:
            rel_path = fpath.relative_to(ROOT)
            zf.write(fpath, arcname=str(rel_path).replace("\\", "/"))

    zip_size_bytes = ZIP_PATH.stat().st_size
    zip_sha256 = compute_sha256(ZIP_PATH)
    print(f"Created {ZIP_PATH} ({zip_size_bytes:,} bytes, {len(unique_files)} files)")
    print(f"SHA256: {zip_sha256}")

    # Verify zip content
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        infolist = zf.infolist()
        print(f"Verified ZIP contains {len(infolist)} entries.")
        for item in infolist:
            for ext in EXCLUDED_EXTENSIONS:
                if item.filename.endswith(ext):
                    raise ValueError(f"Prohibited file type found in ZIP: {item.filename}")
            for edir in EXCLUDED_DIRS:
                if edir in item.filename:
                    raise ValueError(f"Prohibited directory found in ZIP: {item.filename}")
            if item.file_size > 10 * 1024 * 1024:
                raise ValueError(f"Unexpected large file in ZIP: {item.filename} ({item.file_size} bytes)")

    print("ZIP validation PASSED: No binary weights, venv, or secrets found.")


if __name__ == "__main__":
    main()
