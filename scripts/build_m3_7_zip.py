"""Package M3.7 review bundle zip excluding weights, virtualenvs, and secrets."""

import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "runs/m3_7_calibration_handoff"
ZIP_PATH = OUT_DIR / "review_bundle.zip"

EXCLUDED_EXTENSIONS = {".safetensors", ".bin", ".pt", ".pth", ".onnx", ".pyc", ".zip"}
EXCLUDED_DIRS = {".venv", ".git", "__pycache__", ".pytest_cache", ".idea", ".vscode"}


def should_include(rel_path: Path) -> bool:
    parts = rel_path.parts
    for part in parts:
        if part in EXCLUDED_DIRS:
            return False
    if rel_path.suffix in EXCLUDED_EXTENSIONS:
        return False
    if "api_key" in rel_path.name.lower() or "secret" in rel_path.name.lower():
        return False
    return True


def main():
    print("Creating review_bundle.zip for M3.7 Calibration Handoff...")
    files_to_add = []

    # 1. runs/m3_7_calibration_handoff/ artifacts
    for p in OUT_DIR.rglob("*"):
        if p.is_file() and p.name != "review_bundle.zip" and should_include(p.relative_to(ROOT)):
            files_to_add.append(p)

    # 2. Source code in src/erabi/
    for p in (ROOT / "src/erabi").rglob("*"):
        if p.is_file() and should_include(p.relative_to(ROOT)):
            files_to_add.append(p)

    # 3. Relevant scripts
    script_names = [
        "scripts/audit_semantic_states.py",
        "scripts/run_m3_7_handoff.py",
        "scripts/verify_m3_7_api.py",
        "scripts/build_m3_6_data.py",
    ]
    for sname in script_names:
        sp = ROOT / sname
        if sp.is_file():
            files_to_add.append(sp)

    # 4. Relevant tests
    for p in (ROOT / "tests").rglob("*"):
        if p.is_file() and should_include(p.relative_to(ROOT)):
            files_to_add.append(p)

    # 5. Datasets (m3_6_cal and smoke)
    for p in (ROOT / "data/m3_6_cal").rglob("*"):
        if p.is_file() and should_include(p.relative_to(ROOT)):
            files_to_add.append(p)
    files_to_add.append(ROOT / "examples/smoke_cases.jsonl")

    # 6. Documentation and project metadata
    for fname in ["STATUS.md", "pyproject.toml", "AGENTS.md", "docs/ERABI_DESIGN.md"]:
        fp = ROOT / fname
        if fp.is_file():
            files_to_add.append(fp)

    # Deduplicate
    unique_files = sorted(list(set(files_to_add)))

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for fpath in unique_files:
            rel_path = fpath.relative_to(ROOT)
            zf.write(fpath, arcname=str(rel_path).replace("\\", "/"))

    zip_size_bytes = ZIP_PATH.stat().st_size
    print(f"Created {ZIP_PATH} ({zip_size_bytes:,} bytes, {len(unique_files)} files)")

    # Verify zip content
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        infolist = zf.infolist()
        print(f"Verified ZIP contains {len(infolist)} files.")
        for item in infolist:
            for ext in EXCLUDED_EXTENSIONS:
                if item.filename.endswith(ext):
                    raise ValueError(f"Prohibited file type found in ZIP: {item.filename}")
            for edir in EXCLUDED_DIRS:
                if edir in item.filename:
                    raise ValueError(f"Prohibited directory found in ZIP: {item.filename}")
    print("ZIP validation PASSED: No binary weights, venv, or cache files found.")


if __name__ == "__main__":
    main()
