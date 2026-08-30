#!/usr/bin/env python3
"""Read-only competition-readiness audit for the Stage 2 repository.

The previous script generated a May-era report from hard-coded result files and
still diagnosed an upstream budget ambiguity that no longer exists. This
replacement checks the repository that will actually be handed off. It writes
nothing unless --json-out is supplied explicitly.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[2]
STAGE2 = ROOT / "stage2"
SOURCE = STAGE2 / "solver" / "solver.py"
PACKER = STAGE2 / "solver" / "minify_submission.py"
NOTE = STAGE2 / "solver" / "SUBMISSION_NOTE.md"
SUBMISSION_DIR = STAGE2 / "submissions"
ARTIFACT = SUBMISSION_DIR / "solver.py"
FIXTURE = STAGE2 / "fixtures" / "judge_verified_certs.jsonl"
VENDOR = ROOT / "vendor" / "stage2-official"
CONFIG = VENDOR / "pipeline" / "config.json"
OFFICIAL_EQ5 = VENDOR / "examples" / "problems" / "eq_size5.txt"
MIRROR_EQ5 = ROOT / "data" / "stage2_official_problems" / "eq_size5.txt"

EXPECTED_CONFIG = {
    ("solver", "timeout_seconds"): 3600,
    ("sandbox", "memory_mb"): 2048,
    ("sandbox", "cpus"): 2,
    ("sandbox", "pids_limit"): 64,
    ("sandbox", "tmpfs_size_mb"): 64,
    ("judge", "lean_timeout_seconds"): 300,
    ("judge", "max_code_length"): 100_000,
    ("judge", "max_false_cert_bytes"): 20_000,
    ("judge", "max_solver_bytes"): 500_000,
    ("llm", "max_output_tokens"): 65_536,
    ("llm", "temperature"): 0.0,
    ("llm", "reasoning_effort"): "low",
    ("llm", "seed"): 0,
}
CURRENT_DOCS = (
    ROOT / "CLAUDE.md",
    ROOT / "CURRENT_STATE.md",
    ROOT / "README.md",
    ROOT / "RESTART_CHECKLIST.md",
    STAGE2 / "docs" / "LATEST_HANDOFF.md",
    STAGE2 / "docs" / "playground-preflight.md",
    NOTE,
    VENDOR / "UPSTREAM.md",
)
MD_LINK = re.compile(
    r"(?<!!)\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))"
    r"(?:\s+['\"][^'\"]*['\"])?\s*\)"
)
FENCE = re.compile(r"^\s*(" + "```" + r"|~~~)")


@dataclass
class Check:
    name: str
    status: str
    detail: str
    data: dict[str, object] = field(default_factory=dict)


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def parse_python(path: Path) -> tuple[ast.Module | None, str | None]:
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path)), None
    except (OSError, SyntaxError, UnicodeError) as exc:
        return None, f"{type(exc).__name__}: {exc}"


def literal_assignments(tree: ast.Module) -> dict[str, object]:
    values: dict[str, object] = {}
    for node in tree.body:
        if isinstance(node, ast.AnnAssign):
            target, value = node.target, node.value
        elif isinstance(node, ast.Assign) and len(node.targets) == 1:
            target, value = node.targets[0], node.value
        else:
            continue
        if not isinstance(target, ast.Name) or value is None:
            continue
        try:
            values[target.id] = ast.literal_eval(value)
        except (ValueError, TypeError, SyntaxError):
            pass
    return values


def official_config() -> Check:
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return Check("official_config", "fail", f"cannot read config: {exc}")
    drift: list[str] = []
    for keys, expected in EXPECTED_CONFIG.items():
        value: object = config
        for key in keys:
            value = value[key] if isinstance(value, dict) and key in value else None
        if value != expected:
            drift.append(f"{'.'.join(keys)}={value!r}, expected {expected!r}")
    toolchain = (VENDOR / "lean-toolchain").read_text(encoding="utf-8").strip()
    if "v4.33.1" not in toolchain:
        drift.append(f"lean-toolchain={toolchain!r}, expected v4.33.1")
    return Check(
        "official_config",
        "fail" if drift else "pass",
        "; ".join(drift) if drift else "deployed caps and Lean 4.33.1 pin match",
        {"config": relative(CONFIG), "lean_toolchain": toolchain},
    )


def submission_checks() -> list[Check]:
    entries = sorted(path.name for path in SUBMISSION_DIR.iterdir()) if SUBMISSION_DIR.exists() else []
    layout_ok = entries == ["solver.py"] and ARTIFACT.is_file()
    checks = [Check(
        "submission_layout",
        "pass" if layout_ok else "fail",
        f"entries={entries or ['<missing>']}",
        {"entries": entries},
    )]
    if not ARTIFACT.is_file():
        checks.append(Check("submission_artifact", "fail", "solver.py is missing"))
        return checks
    tree, error = parse_python(ARTIFACT)
    values = literal_assignments(tree) if tree else {}
    prompt_ok = isinstance(values.get("PROMPT"), str) and bool(values["PROMPT"].strip())
    size = ARTIFACT.stat().st_size
    good = size <= 500_000 and error is None and prompt_ok
    checks.append(Check(
        "submission_artifact",
        "pass" if good else "fail",
        f"{size} bytes; syntax={'ok' if error is None else error}; PROMPT={prompt_ok}",
        {"bytes": size, "sha256": sha256(ARTIFACT), "prompt_literal": prompt_ok},
    ))
    return checks


def source_checks() -> list[Check]:
    _source_tree, source_error = parse_python(SOURCE)
    checks = [Check(
        "solver_source",
        "pass" if source_error is None else "fail",
        f"syntax={'ok' if source_error is None else source_error}; {SOURCE.stat().st_size} bytes",
        {"sha256": sha256(SOURCE)},
    )]
    packer_tree, error = parse_python(PACKER)
    if error or packer_tree is None:
        checks.append(Check("generated_data_disclosure", "fail", f"cannot parse packer: {error}"))
        return checks
    packed = literal_assignments(packer_tree).get("PACKED_TABLES")
    if not isinstance(packed, dict):
        checks.append(Check("generated_data_disclosure", "fail", "PACKED_TABLES is not literal"))
        return checks
    note = NOTE.read_text(encoding="utf-8")
    missing = sorted(name for name in packed if f"`{name}`" not in note)
    good = not missing and "PROMPT" not in packed
    checks.append(Check(
        "generated_data_disclosure",
        "pass" if good else "fail",
        f"{len(packed)} payloads; missing={missing}; PROMPT packed={'PROMPT' in packed}",
        {"packed_payloads": sorted(packed), "missing_from_note": missing},
    ))
    return checks


def without_fences(text: str) -> str:
    kept: list[str] = []
    active: str | None = None
    for line in text.splitlines():
        match = FENCE.match(line)
        if match:
            marker = match.group(1)
            active = marker if active is None else (None if marker == active else active)
            kept.append("")
        else:
            kept.append(line if active is None else "")
    return "\n".join(kept)


def link_path(document: Path, raw: str) -> Path | None:
    target = unquote(raw.strip())
    if not target or target.startswith(("#", "/", "\\")):
        return None
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
        return None
    target = target.split("#", 1)[0].split("?", 1)[0]
    return (document.parent / target).resolve() if target else None


def markdown_check() -> Check:
    # Include untracked-but-unignored files so a newly added handoff or README
    # is checked before it is committed, not only after CI sees it.
    result = git("ls-files", "--cached", "--others", "--exclude-standard", "--", "*.md")
    if result.returncode:
        return Check("markdown", "fail", result.stderr.strip() or "git ls-files failed")
    documents = sorted({ROOT / line for line in result.stdout.splitlines() if line.strip()})
    broken: list[dict[str, object]] = []
    encoding_errors: list[str] = []
    no_newline: list[str] = []
    per_file: list[dict[str, object]] = []
    total_links = 0
    for document in documents:
        bad = 0
        links = 0
        try:
            raw = document.read_bytes()
            text = raw.decode("utf-8")
        except (OSError, UnicodeError) as exc:
            encoding_errors.append(f"{relative(document)}: {exc}")
            per_file.append({"path": relative(document), "status": "encoding_error", "links": 0})
            continue
        if raw and not raw.endswith(b"\n"):
            no_newline.append(relative(document))
        for number, line in enumerate(without_fences(text).splitlines(), start=1):
            for match in MD_LINK.finditer(line):
                path = link_path(document, match.group(1) or match.group(2))
                if path is None:
                    continue
                links += 1
                total_links += 1
                if not path.exists():
                    bad += 1
                    broken.append({
                        "document": relative(document),
                        "line": number,
                        "target": match.group(1) or match.group(2),
                        "resolved": relative(path),
                    })
        per_file.append({
            "path": relative(document),
            "status": "broken" if bad else "ok",
            "links": links,
            "broken": bad,
        })
    status = "fail" if broken or encoding_errors else ("warn" if no_newline else "pass")
    return Check(
        "markdown",
        status,
        f"{len(documents)} files; {total_links} local links; {len(broken)} broken; "
        f"{len(encoding_errors)} encoding errors; {len(no_newline)} without final newline",
        {
            "files": per_file,
            "broken_links": broken,
            "encoding_errors": encoding_errors,
            "no_final_newline": no_newline,
        },
    )


def data_and_docs_checks() -> list[Check]:
    missing_docs = [relative(path) for path in CURRENT_DOCS if not path.is_file()]
    checks = [Check(
        "current_docs",
        "pass" if not missing_docs else "fail",
        f"{len(CURRENT_DOCS) - len(missing_docs)}/{len(CURRENT_DOCS)} present; missing={missing_docs}",
    )]
    if OFFICIAL_EQ5.is_file() and MIRROR_EQ5.is_file():
        official_hash, mirror_hash = sha256(OFFICIAL_EQ5), sha256(MIRROR_EQ5)
        same = official_hash == mirror_hash
        checks.append(Check(
            "eq_size5_mirror",
            "pass" if same else "fail",
            f"byte-identical={same}; bytes={OFFICIAL_EQ5.stat().st_size}",
            {"official_sha256": official_hash, "mirror_sha256": mirror_hash},
        ))
    else:
        checks.append(Check("eq_size5_mirror", "fail", "one or both mirrors are missing"))
    return checks


def hygiene_checks() -> list[Check]:
    secret_result = git("ls-files", "--", ".env", "*.pem", "*.key")
    tracked_secrets = [line for line in secret_result.stdout.splitlines() if line.strip()]
    checks = [Check(
        "tracked_secret_files",
        "pass" if secret_result.returncode == 0 and not tracked_secrets else "fail",
        f"tracked secret-shaped files={tracked_secrets}",
        {"tracked": tracked_secrets},
    )]
    skipped = {".git", ".lake", ".venv", ".venv311"}
    pycache: list[str] = []
    for root, dirs, _files in os.walk(ROOT):
        dirs[:] = [name for name in dirs if name not in skipped]
        if Path(root).name == "__pycache__":
            pycache.append(relative(Path(root)))
            dirs[:] = []
    logs = sorted(path.name for path in ROOT.glob("*.log"))
    caches = [name for name in (".pytest_cache", ".ruff_cache") if (ROOT / name).exists()]
    checks.append(Check(
        "workspace_hygiene",
        "warn" if pycache or logs or caches else "pass",
        f"pycache={len(pycache)}; root_logs={logs}; tool_caches={caches}",
        {"pycache": sorted(pycache), "root_logs": logs, "tool_caches": caches},
    ))
    status = git("status", "--short", "--branch")
    lines = status.stdout.splitlines()
    checks.append(Check(
        "git_state",
        "fail" if status.returncode else ("warn" if len(lines) > 1 else "pass"),
        lines[0] if lines else (status.stderr.strip() or "unknown"),
        {"changes": lines[1:]},
    ))
    return checks


def build_checks() -> list[Check]:
    checks = [official_config(), *submission_checks(), *source_checks()]
    checks.extend(data_and_docs_checks())
    checks.append(markdown_check())
    checks.extend(hygiene_checks())
    if FIXTURE.is_file():
        checks.append(Check(
            "judge_fixture",
            "pass",
            f"{FIXTURE.stat().st_size} bytes",
            {"sha256": sha256(FIXTURE)},
        ))
    else:
        checks.append(Check("judge_fixture", "fail", f"missing {relative(FIXTURE)}"))
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, help="optional explicit JSON report path")
    parser.add_argument("--strict-warnings", action="store_true")
    args = parser.parse_args()
    checks = build_checks()
    summary = {
        level: sum(check.status == level for check in checks)
        for level in ("pass", "warn", "fail")
    }
    report = {
        "schema": 1,
        "repo": str(ROOT),
        "python": sys.version.split()[0],
        "checks": [asdict(check) for check in checks],
        "summary": summary,
    }
    for check in checks:
        print(f"[{check.status.upper():4}] {check.name}: {check.detail}")
        if check.name == "markdown":
            for broken in check.data.get("broken_links", []):
                print(
                    f"       {broken['document']}:{broken['line']} -> "
                    f"{broken['target']} ({broken['resolved']})"
                )
            for path in check.data.get("no_final_newline", []):
                print(f"       no final newline: {path}")
    if args.json_out:
        output = args.json_out if args.json_out.is_absolute() else ROOT / args.json_out
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {relative(output)}")
    print("Summary: " + ", ".join(f"{key}={value}" for key, value in summary.items()))
    if summary["fail"]:
        return 1
    if args.strict_warnings and summary["warn"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
