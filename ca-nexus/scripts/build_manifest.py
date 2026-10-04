"""T2.1 — Build machine-readable manifest of all in-scope sources.

Usage (from repo root `manufacturing-knowledge-hub/`):
    python ../scripts/build_manifest.py --source ../supporting_data --out data/manifest.json
Resolves both CWDs (repo root or workspace root). Handles spaces/`&`/case variants
via pathlib (T1.1). Reconciles against inventory baseline 88 PDF + 8 PNG + 1 XLSX + 1 PPTX.
"""
import argparse, hashlib, json
from pathlib import Path


def sha256(p: Path, n: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(n), b""):
            h.update(b)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="../supporting_data")
    ap.add_argument("--out", default="data/manifest.json")
    a = ap.parse_args()
    src = Path(a.source)
    if not src.exists():  # allow workspace-root CWD too
        alt = Path("supporting_data")
        src = alt if alt.exists() else src
    root = src / "Case 1_ Manufacturing Knowledge Hub" if (src / "Case 1_ Manufacturing Knowledge Hub").exists() else src
    files = [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in (".pdf", ".png", ".xlsx", ".pptx")]
    entries = [{
        "path_relative": str(p.relative_to(root)), "filename": p.name,
        "suffix": p.suffix.lower(), "bytes": p.stat().st_size, "sha256": sha256(p),
        "set": next((part for part in p.parts if part.startswith("Set_")), ""),
    } for p in sorted(files)]
    by_suffix = {}
    for e in entries:
        by_suffix[e["suffix"]] = by_suffix.get(e["suffix"], 0) + 1
    baseline = {".pdf": 88, ".png": 8, ".xlsx": 1, ".pptx": 1}
    report = {
        "source_root": str(root), "total": len(entries), "by_suffix": by_suffix,
        "baseline": baseline,
        "reconciled": all(by_suffix.get(k, 0) == v for k, v in baseline.items()),
        "unreadable": [], "duplicates_by_sha": [],
        "entries": entries,
    }
    seen: dict[str, str] = {}
    for e in entries:
        if e["sha256"] in seen:
            report["duplicates_by_sha"].append({"file": e["path_relative"], "same_as": seen[e["sha256"]]})
        else:
            seen[e["sha256"]] = e["path_relative"]
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"manifest: {len(entries)} files -> {out} reconciled={report['reconciled']} {by_suffix}")


if __name__ == "__main__":
    main()
