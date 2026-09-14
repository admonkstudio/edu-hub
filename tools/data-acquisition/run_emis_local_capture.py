#!/usr/bin/env python3
"""One-command local handoff for MOE/EMIS contract capture + offline analysis.

This wrapper performs only the two safe D1.3 preparation gates:
1. capture public EMIS page/form evidence;
2. analyze that evidence offline into an enumerator design contract.

It then packages only redacted/shareable evidence into one ZIP for handoff.
Untouched raw HTML remains local and is never included in the bundle. The tool
does not enumerate schools or submit search forms.
"""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
import subprocess
from pathlib import Path


def run(cmd: list[str]) -> int:
    print("+ " + " ".join(cmd), flush=True)
    return subprocess.call(cmd)


def build_shareable_bundle(output_dir: Path) -> Path:
    report_path = output_dir / "capture-report.json"
    contract_path = output_dir / "enumerator-contract.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    archive_path = output_dir.parent / "emis-local-capture-bundle.zip"

    shareable_files: list[Path] = [report_path, contract_path]
    for page in report.get("pages") or []:
        saved_html = page.get("saved_html")
        if saved_html:
            candidate = output_dir / str(saved_html)
            if candidate.exists():
                shareable_files.append(candidate)

    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in shareable_files:
            zf.write(path, arcname=f"emis-local-capture/{path.name}")

    return archive_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default="artifacts/emis-local-capture", type=Path)
    ap.add_argument("--timeout", type=float, default=45.0)
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    capture = repo_root / "tools" / "data-acquisition" / "emis_local_capture.py"
    analyzer = repo_root / "tools" / "data-acquisition" / "registry" / "analyze_emis_capture.py"
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = repo_root / output_dir

    capture_rc = run([
        sys.executable,
        str(capture),
        "--output-dir",
        str(output_dir),
        "--timeout",
        str(args.timeout),
    ])
    if capture_rc != 0:
        print(
            f"EMIS capture did not succeed (exit {capture_rc}). No analyzer or enumeration was run. "
            f"Diagnostic report, when available: {output_dir / 'capture-report.json'}",
            file=sys.stderr,
        )
        return capture_rc

    analyze_rc = run([
        sys.executable,
        str(analyzer),
        "--capture-dir",
        str(output_dir),
    ])
    if analyze_rc != 0:
        print(
            f"Capture succeeded but the contract is not yet sufficient for adapter design (exit {analyze_rc}). "
            f"Review {output_dir / 'enumerator-contract.json'}.",
            file=sys.stderr,
        )
        return analyze_rc

    archive_path = build_shareable_bundle(output_dir)

    print("EMIS D1.3 contract capture is ready for pilot-adapter implementation.")
    print(f"Capture report: {output_dir / 'capture-report.json'}")
    print(f"Enumerator contract: {output_dir / 'enumerator-contract.json'}")
    print(f"Shareable handoff bundle: {archive_path}")
    print("Raw HTML remains local and is not included in the bundle.")
    print("No school enumeration was performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
