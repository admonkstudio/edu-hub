#!/usr/bin/env python3
"""One-command local handoff for MOE/EMIS contract capture + offline analysis.

This wrapper performs only the safe D1.3 preparation gates:
1. capture public EMIS page/form evidence with GET requests;
2. discover bounded same-origin school-search endpoints from that evidence;
3. submit only the root page's top-level school-category navigation buttons;
4. analyze the resulting saved search-form evidence offline.

It packages only redacted/shareable evidence into one ZIP for handoff. Untouched
raw HTML remains local and is never included in the bundle. The tool does not
select search filters, enumerate schools or follow result pagination.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from urllib.parse import urldefrag, urlparse

EMIS_ORIGIN = "search.emis.gov.eg"
SEED_TARGETS = [
    "https://search.emis.gov.eg/",
    "https://search.emis.gov.eg/search_schgov.aspx",
    "https://search.emis.gov.eg/search_schpriv.aspx",
    "https://search.emis.gov.eg/sch_data.aspx",
]


def run(cmd: list[str]) -> int:
    print("+ " + " ".join(cmd), flush=True)
    return subprocess.call(cmd)


def is_safe_discovery_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    if parsed.scheme not in {"http", "https"}:
        return False
    if parsed.hostname != EMIS_ORIGIN:
        return False
    path = (parsed.path or "/").lower()
    if path == "/":
        return True
    if not path.endswith((".aspx", ".ashx", ".asmx")):
        return False
    return any(token in path for token in ("school", "sch", "search", "emis"))


def discover_targets(report: dict, seeds: list[str] | None = None, limit: int = 12) -> list[str]:
    """Return bounded same-origin public endpoints found in captured evidence."""
    ordered: list[str] = []
    seen: set[str] = set()

    def add(value: str | None) -> None:
        if not value:
            return
        clean_url, _fragment = urldefrag(str(value))
        if clean_url in seen or not is_safe_discovery_url(clean_url):
            return
        seen.add(clean_url)
        ordered.append(clean_url)

    for seed in seeds or SEED_TARGETS:
        add(seed)

    for page in report.get("pages") or []:
        for link in page.get("candidate_links") or []:
            if isinstance(link, dict):
                add(link.get("href"))
        for value in page.get("inline_endpoint_refs") or []:
            add(value)
        for form in page.get("forms") or []:
            if isinstance(form, dict):
                add(form.get("action"))

    return ordered[: max(1, limit)]


def capture_command(capture: Path, output_dir: Path, timeout: float, targets: list[str]) -> list[str]:
    cmd = [
        sys.executable,
        str(capture),
        "--output-dir",
        str(output_dir),
        "--timeout",
        str(timeout),
    ]
    for target in targets:
        cmd.extend(["--url", target])
    return cmd


def load_report(output_dir: Path) -> dict:
    path = output_dir / "capture-report.json"
    return json.loads(path.read_text(encoding="utf-8"))


def build_shareable_bundle(output_dir: Path) -> Path:
    report_path = output_dir / "capture-report.json"
    contract_path = output_dir / "enumerator-contract.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    archive_path = output_dir.parent / "emis-local-capture-bundle.zip"

    shareable_files: list[Path] = [report_path]
    if contract_path.exists():
        shareable_files.append(contract_path)

    for page in report.get("pages") or []:
        saved_html = page.get("saved_html")
        if saved_html:
            candidate = output_dir / str(saved_html)
            if candidate.exists():
                shareable_files.append(candidate)

    unique_files: list[Path] = []
    seen: set[Path] = set()
    for path in shareable_files:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique_files.append(path)

    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in unique_files:
            zf.write(path, arcname=f"emis-local-capture/{path.name}")

    return archive_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default="artifacts/emis-local-capture", type=Path)
    ap.add_argument("--timeout", type=float, default=45.0)
    ap.add_argument("--discovery-limit", type=int, default=12)
    ap.add_argument("--max-root-buttons", type=int, default=6)
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    capture = repo_root / "tools" / "data-acquisition" / "emis_local_capture.py"
    navigation_probe = repo_root / "tools" / "data-acquisition" / "emis_navigation_probe.py"
    analyzer = repo_root / "tools" / "data-acquisition" / "registry" / "analyze_emis_capture.py"
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = repo_root / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    targets = list(SEED_TARGETS)
    capture_rc = run(capture_command(capture, output_dir, args.timeout, targets))
    if capture_rc != 0:
        print(
            f"EMIS GET capture did not produce any reachable page (exit {capture_rc}). "
            f"Diagnostic report, when available: {output_dir / 'capture-report.json'}",
            file=sys.stderr,
        )
        return capture_rc

    first_report = load_report(output_dir)
    discovered = discover_targets(first_report, targets, args.discovery_limit)
    extras = [url for url in discovered if url not in targets]
    if extras:
        print("Discovered additional EMIS contract endpoint(s):")
        for url in extras:
            print(f"  {url}")
        targets = discovered
        capture_rc = run(capture_command(capture, output_dir, args.timeout, targets))
        if capture_rc != 0:
            print(
                f"Expanded EMIS GET contract capture failed (exit {capture_rc}). "
                f"Review {output_dir / 'capture-report.json'}.",
                file=sys.stderr,
            )
            return capture_rc

    # The live directory uses ASP.NET submit buttons for category navigation.
    # This bounded probe POSTs only those top-level buttons; it does not choose
    # filters or submit a school search.
    navigation_rc = run([
        sys.executable,
        str(navigation_probe),
        "--output-dir",
        str(output_dir),
        "--timeout",
        str(args.timeout),
        "--max-buttons",
        str(args.max_root_buttons),
    ])
    if navigation_rc != 0:
        print(
            f"Top-level EMIS navigation probe did not resolve a search page (exit {navigation_rc}). "
            "The diagnostic bundle will still be produced.",
            file=sys.stderr,
        )

    analyze_rc = run([
        sys.executable,
        str(analyzer),
        "--capture-dir",
        str(output_dir),
    ])

    archive_path = build_shareable_bundle(output_dir)

    if analyze_rc != 0:
        print(
            f"Capture succeeded but the contract is not yet sufficient for pilot adapter design (exit {analyze_rc}).",
            file=sys.stderr,
        )
        print(f"Enumerator contract: {output_dir / 'enumerator-contract.json'}")
        print(f"Shareable diagnostic bundle: {archive_path}")
        print("Raw HTML remains local and is not included in the bundle.")
        return analyze_rc

    print("EMIS D1.3 contract capture is ready for bounded pilot-adapter implementation.")
    print(f"Capture report: {output_dir / 'capture-report.json'}")
    print(f"Enumerator contract: {output_dir / 'enumerator-contract.json'}")
    print(f"Shareable handoff bundle: {archive_path}")
    print("Raw HTML remains local and is not included in the bundle.")
    print("No school search, school enumeration or result pagination was performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
