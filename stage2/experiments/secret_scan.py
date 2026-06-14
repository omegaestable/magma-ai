"""Scan tracked repository files for accidentally committed API keys.

This helper is intentionally conservative and prints only file paths and line
numbers. It does not print matched secret text.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SECRET_PATTERNS = {
    "openrouter_key": re.compile(r"sk-or-v1-[A-Za-z0-9]{32,}"),
    "openai_key": re.compile(r"sk-[A-Za-z0-9]{32,}"),
}
SKIP_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
}


def git_files(include_untracked: bool) -> list[Path] | None:
    try:
        tracked = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        return None

    paths = [ROOT / item for item in tracked if item]
    if include_untracked:
        try:
            untracked = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            ).stdout.splitlines()
        except (OSError, subprocess.CalledProcessError):
            untracked = []
        paths.extend(ROOT / item for item in untracked if item)
    return paths


def walk_files() -> list[Path]:
    paths: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(ROOT).parts
        if any(part in SKIP_PARTS for part in rel_parts):
            continue
        paths.append(path)
    return paths


def scan_file(path: Path) -> list[tuple[str, int]]:
    findings: list[tuple[str, int]] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return findings
    except OSError:
        return findings
    for line_number, line in enumerate(text.splitlines(), start=1):
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(line):
                findings.append((name, line_number))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--include-untracked",
        action="store_true",
        help="Also scan untracked non-ignored files.",
    )
    args = parser.parse_args()

    paths = git_files(args.include_untracked)
    if paths is None:
        paths = walk_files()

    failed = False
    for path in sorted(set(paths)):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(ROOT).parts
        if any(part in SKIP_PARTS for part in rel_parts):
            continue
        findings = scan_file(path)
        for name, line_number in findings:
            failed = True
            rel = path.relative_to(ROOT)
            print(f"{rel}:{line_number}: {name}", file=sys.stderr)

    if failed:
        print("secret_scan_failed", file=sys.stderr)
        return 1
    print("secret_scan_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
