#!/usr/bin/env python3
"""Run the frozen label-blind HF150 fixture through the official Marathon proxy."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

import local_runner_env


REPO_ROOT = Path(__file__).resolve().parents[2]
PARITY_RUNNER = REPO_ROOT / "stage2" / "experiments" / "run_playground_parity_llm.py"
DEFAULT_FIXTURE = (
    REPO_ROOT
    / "tmp_stage2_smoke"
    / "2026-07-17-hf150-baseline"
    / "combined.runner.jsonl"
)
DEFAULT_OUTPUT_DIR = REPO_ROOT / "tmp_stage2_smoke" / "2026-07-17-hf150-gptoss-candidate"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
REFERENCE_MODEL = "openai/gpt-oss-120b"
AUDITED_REPO_HEAD = "b90fa579ff62d6b0c4fe165b73180efbe9dc2a8b"
EXPECTED_RUNNER_SHA256 = "65ae5ae031bb48cf8e8ceacc9a2880d4aa7156221798cb72189244e78ae44b07"
EXPECTED_COMBINED_ID_SHA256 = "903c2e1aa23b579639379e540d325f00b05e58f86e01d1adb1f8ee4eebcf778a"
EXPECTED_SOURCE_SHA256 = {
    "evaluation_hard": "5dcef7a57e3a6500247b92bd671d60032f6fe0d397d5388b85f4ebf4d9288213",
    "evaluation_order5": "040016d463efdff41625bffda2c4bfbba0caa093fa5936b42c232ccf1ab104f2",
}
REQUIRED_RUNNER_KEYS = {
    "id",
    "index",
    "difficulty",
    "eq1_id",
    "eq2_id",
    "equation1",
    "equation2",
}
ORDERED_ID_HASH_SEPARATOR = "\\n"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ordered_id_sha256(rows: list[dict[str, Any]]) -> str:
    payload = ORDERED_ID_HASH_SEPARATOR.join(str(row["id"]) for row in rows)
    payload += ORDERED_ID_HASH_SEPARATOR
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise SystemExit(f"{path}:{line_number}: expected a JSON object")
        rows.append(row)
    return rows


def validate_fixture(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise SystemExit(f"runner fixture not found: {path}")
    rows = load_rows(path)
    if len(rows) != 150:
        raise SystemExit(f"expected exactly 150 runner rows, found {len(rows)}")
    leaked = [str(row.get("id", "")) for row in rows if "answer" in row]
    if leaked:
        raise SystemExit(f"runner fixture leaks answer labels in {len(leaked)} rows")
    ids = [row.get("id") for row in rows]
    if any(not isinstance(row_id, str) or not row_id for row_id in ids):
        raise SystemExit("runner fixture contains a missing or invalid id")
    if len(set(ids)) != len(ids):
        raise SystemExit("runner fixture contains duplicate ids")

    for line_number, row in enumerate(rows, 1):
        missing = REQUIRED_RUNNER_KEYS - set(row)
        if missing:
            raise SystemExit(f"runner fixture row {line_number} missing keys {sorted(missing)}")
        if set(row) != REQUIRED_RUNNER_KEYS:
            extras = sorted(set(row) - REQUIRED_RUNNER_KEYS)
            raise SystemExit(f"runner fixture row {line_number} has unexpected keys {extras}")
        if isinstance(row["index"], bool) or not isinstance(row["index"], int):
            raise SystemExit(f"runner fixture row {line_number} has invalid index")
        for key in ("eq1_id", "eq2_id"):
            if isinstance(row[key], bool) or not isinstance(row[key], int):
                raise SystemExit(f"runner fixture row {line_number} has invalid {key}")
        for key in ("difficulty", "equation1", "equation2"):
            if not isinstance(row[key], str) or not row[key].strip():
                raise SystemExit(f"runner fixture row {line_number} has invalid {key}")

    actual_sha256 = sha256_file(path)
    if actual_sha256 != EXPECTED_RUNNER_SHA256:
        raise SystemExit(
            f"runner fixture hash drift: expected {EXPECTED_RUNNER_SHA256}, found {actual_sha256}"
        )
    id_sha256 = ordered_id_sha256(rows)
    if id_sha256 != EXPECTED_COMBINED_ID_SHA256:
        raise SystemExit(
            f"runner fixture ID-order drift: expected {EXPECTED_COMBINED_ID_SHA256}, found {id_sha256}"
        )

    metadata_path = path.parent / "metadata.json"
    if not metadata_path.is_file():
        raise SystemExit(f"fixture provenance metadata not found: {metadata_path}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if not isinstance(metadata, dict) or metadata.get("schema_version") != 1:
        raise SystemExit("fixture provenance metadata has an unsupported schema")
    if metadata.get("analysis_only") is not True:
        raise SystemExit("fixture provenance metadata is not marked analysis_only")
    if metadata.get("audited_repo_head") != AUDITED_REPO_HEAD:
        raise SystemExit("fixture provenance audited_repo_head drift")
    if metadata.get("expected_combined_ordered_id_sha256") != EXPECTED_COMBINED_ID_SHA256:
        raise SystemExit("fixture provenance combined ID digest drift")
    sources = metadata.get("sources")
    if not isinstance(sources, dict) or set(sources) != set(EXPECTED_SOURCE_SHA256):
        raise SystemExit("fixture provenance source set drift")
    for source, expected_sha256 in EXPECTED_SOURCE_SHA256.items():
        source_info = sources.get(source)
        if not isinstance(source_info, dict) or source_info.get("sha256") != expected_sha256:
            raise SystemExit(f"fixture provenance source hash drift for {source}")
    artifacts = metadata.get("artifacts")
    combined = artifacts.get("combined") if isinstance(artifacts, dict) else None
    if not isinstance(combined, dict):
        raise SystemExit("fixture provenance is missing the combined artifact")
    expected_combined_fields = {
        "rows": 150,
        "true": 100,
        "false": 50,
        "runner_sha256": EXPECTED_RUNNER_SHA256,
        "ordered_id_sha256": EXPECTED_COMBINED_ID_SHA256,
    }
    for key, expected in expected_combined_fields.items():
        if combined.get(key) != expected:
            raise SystemExit(f"fixture provenance combined {key} drift")
    return rows


def repo_key_shape() -> dict[str, Any]:
    values = local_runner_env.repo_env_values()
    key = values.get("OPENROUTER_API_KEY", "")
    base_url = values.get("OPENAI_BASE_URL", "")
    if base_url and base_url.rstrip("/") != OPENROUTER_BASE_URL.rstrip("/"):
        raise SystemExit("repo .env OPENAI_BASE_URL is not the official OpenRouter endpoint")
    if values.get("OPENAI_API_KEY", ""):
        raise SystemExit("repo .env contains OPENAI_API_KEY; keep only OPENROUTER_API_KEY for this run")
    shape = {
        "present": bool(key),
        "length": len(key),
        "starts_sk_or_v1": key.startswith("sk-or-v1-"),
        "has_whitespace": any(char.isspace() for char in key),
        "source": "repo_env" if key else "missing",
        "value_hidden": True,
    }
    if not shape["present"]:
        raise SystemExit(
            "repo .env has no OPENROUTER_API_KEY; use set_openrouter_repo_env.ps1 -FromClipboard first"
        )
    if not shape["starts_sk_or_v1"] or shape["length"] < 40 or shape["has_whitespace"]:
        raise SystemExit("repo .env OPENROUTER_API_KEY has an invalid shape")
    return shape


def clean_child_env() -> dict[str, str]:
    env = dict(os.environ)
    for key in local_runner_env.SUPPORTED_LOCAL_ENV_KEYS:
        env.pop(key, None)
    env["OPENAI_BASE_URL"] = OPENROUTER_BASE_URL
    env["SAIR_STAGE2_MODEL"] = REFERENCE_MODEL
    env["LEAN_TIMEOUT_SECONDS"] = "300"
    env["MAX_CODE_LENGTH"] = "100000"
    env["MAX_FALSE_CERT_BYTES"] = "20000"
    env["PYTHONUTF8"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    user_profile = env.get("USERPROFILE", "")
    if user_profile:
        elan_bin = Path(user_profile) / ".elan" / "bin"
        lean = elan_bin / "lean.exe"
        lake = elan_bin / "lake.exe"
        if lean.is_file():
            env["LEAN_BIN"] = str(lean)
        if lake.is_file():
            env["LAKE_BIN"] = str(lake)
        path_parts = env.get("PATH", "").split(os.pathsep)
        if str(elan_bin) not in path_parts:
            env["PATH"] = str(elan_bin) + os.pathsep + env.get("PATH", "")
    return env


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--compression-ratio", type=float, default=0.5)
    parser.add_argument("--budget-tokens", type=int, default=None)
    parser.add_argument("--budget-seconds", type=float, default=None)
    parser.add_argument("--skip-package", action="store_true")
    parser.add_argument("--keep-output", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    fixture = args.fixture.resolve()
    output_dir = args.output_dir.resolve()
    rows = validate_fixture(fixture)
    key_shape = repo_key_shape()
    if args.compression_ratio <= 0:
        raise SystemExit("--compression-ratio must be positive")
    if args.budget_tokens is not None and args.budget_tokens <= 0:
        raise SystemExit("--budget-tokens must be positive")
    if args.budget_seconds is not None and args.budget_seconds <= 0:
        raise SystemExit("--budget-seconds must be positive")

    command = [
        sys.executable,
        str(PARITY_RUNNER),
        "--fixture-mode",
        "existing",
        "--fixture",
        str(fixture),
        "--skip-solo",
        "--skip-direct-openrouter-smoke",
        "--output-dir",
        str(output_dir),
        "--compression-ratio",
        str(args.compression_ratio),
    ]
    if args.budget_tokens is not None:
        command.extend(["--marathon-budget-tokens", str(args.budget_tokens)])
    if args.budget_seconds is not None:
        command.extend(["--marathon-budget-seconds", str(args.budget_seconds)])
    if args.skip_package:
        command.append("--skip-package")
    if args.keep_output:
        command.append("--keep-output")

    print(
        "fixture_rows={rows} answer_fields=0 key_source={source} key_present={present} "
        "key_length={length} value_hidden=true model={model} base_url={base_url}".format(
            rows=len(rows), model=REFERENCE_MODEL, base_url=OPENROUTER_BASE_URL, **key_shape
        )
    )
    print("running:", " ".join(command))
    if args.dry_run:
        print("dry_run=true")
        return 0
    completed = subprocess.run(command, cwd=REPO_ROOT, env=clean_child_env(), check=False)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
