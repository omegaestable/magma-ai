#!/usr/bin/env python3
"""Build and optionally run local LLM plumbing probes for Stage 2.

The script is secret-safe by design: it reports only whether an upstream key
is present and never prints key values. It uses the official vendored runner
for any probe execution.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
TMP_DIR = REPO_ROOT / "tmp_stage2_smoke"
OFFICIAL_DIR = REPO_ROOT / "vendor" / "stage2-official"
SUBMISSION_DIR = REPO_ROOT / "stage2" / "submissions"
DEFAULT_MANIFEST = TMP_DIR / "2026-05-16-hard-mix-150-seed20260516.jsonl"
DEFAULT_SUMMARY = TMP_DIR / "2026-05-16-marathon-hard-mix-150-seed20260516-after-witness-zero-token" / "summary.json"
DEFAULT_FIXTURE = TMP_DIR / "unresolved_true_llm_probe.jsonl"
DEFAULT_SOLO_OUTPUT = TMP_DIR / "unresolved_true_llm_probe_result.json"
DEFAULT_MARATHON_DIR = TMP_DIR / "unresolved_true_llm_probe_marathon"
PROXY_SMOKE_DIR = TMP_DIR / "llm_proxy_smoke_submission"
PROXY_SMOKE_FIXTURE = TMP_DIR / "llm_proxy_smoke.jsonl"
PROXY_SMOKE_CONFIG = TMP_DIR / "llm_proxy_smoke_config.json"
PROXY_SMOKE_SOLO_OUTPUT = TMP_DIR / "llm_proxy_smoke_result.json"
PROXY_SMOKE_MARATHON_DIR = TMP_DIR / "llm_proxy_smoke_marathon"


def _windows_user_env(name: str) -> str:
    if os.name != "nt":
        return ""
    try:
        import winreg
    except ImportError:
        return ""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _value_type = winreg.QueryValueEx(key, name)
    except OSError:
        return ""
    return str(value or "")


def upstream_key_value() -> str:
    value = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY") or ""
    if value:
        return value
    # Existing VS Code terminals do not always inherit User-environment changes
    # made by the setup helper. Read the Windows User env directly for local
    # probes, then pass it only to child runners through their process env.
    return _windows_user_env("OPENROUTER_API_KEY") or _windows_user_env("OPENAI_API_KEY")


def upstream_key_shape() -> dict[str, Any]:
    value = upstream_key_value()
    return {
        "present": bool(value),
        "length": len(value),
        "starts_sk_or_v1": value.startswith("sk-or-v1-"),
        "has_whitespace": any(ch.isspace() for ch in value),
    }

PROXY_SMOKE_SOLVER = r'''
#!/usr/bin/env python3
import json
import os
import sys

PROMPT = "Return exactly: ok\n{solver.probe}\n"

LEAN_CODE = """import JudgeProblem

def submission : Goal := by
  intro G _ h
  exact h
"""


def run_solo():
    line = sys.stdin.readline()
    if not line:
        return
    json.loads(line)
    print(json.dumps({"call": "llm", "context": {"probe": "transport-smoke"}}), flush=True)
    response_line = sys.stdin.readline()
    response = json.loads(response_line) if response_line else {}
    if "error" in response:
        print(json.dumps({"llm_error": str(response.get("error"))[:160]}), file=sys.stderr, flush=True)
    else:
        print(json.dumps({"llm_response_seen": bool(response.get("response") is not None)}), file=sys.stderr, flush=True)
    print(json.dumps({"call": "judge", "verdict": "true", "code": LEAN_CODE}), flush=True)


def run_marathon():
    lib_dir = os.environ.get("JUDGE_MARATHON_LIB_DIR")
    if lib_dir and lib_dir not in sys.path:
        sys.path.insert(0, lib_dir)
    from marathon_llm import call_llm

    response = call_llm(
        "Return exactly: ok",
        config={
            "model": "openai/gpt-oss-120b",
            "provider": "deepinfra/bf16",
            "max_output_tokens": 16,
            "temperature": 0.0,
            "reasoning_effort": "low",
        },
        max_seconds=120,
    )
    if "error" in response:
        print(json.dumps({"llm_error": str(response.get("error"))[:160]}), file=sys.stderr, flush=True)
    else:
        print(json.dumps({"llm_response_seen": bool(response.get("response") is not None), "tokens_used_total": response.get("tokens_used_total")}), file=sys.stderr, flush=True)

    manifest_path = os.environ["JUDGE_MARATHON_MANIFEST"]
    output_path = os.environ["JUDGE_MARATHON_OUTPUT"]
    with open(manifest_path, encoding="utf-8") as handle:
        problem = json.loads(handle.readline())
    with open(output_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps({"id": problem["id"], "verdict": "true", "code": LEAN_CODE}, separators=(",", ":")))
        handle.write("\n")


if __name__ == "__main__":
    if os.environ.get("JUDGE_MARATHON_MANIFEST"):
        run_marathon()
    else:
        run_solo()
'''.lstrip()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_summary(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def upstream_key_present() -> bool:
    return bool(upstream_key_value())


def print_key_status() -> None:
    shape = upstream_key_shape()
    print(
        "upstream_key_present={present} value_hidden=true length={length} "
        "starts_sk_or_v1={starts_sk_or_v1} has_whitespace={has_whitespace}".format(
            present=str(shape["present"]).lower(),
            length=shape["length"],
            starts_sk_or_v1=str(shape["starts_sk_or_v1"]).lower(),
            has_whitespace=str(shape["has_whitespace"]).lower(),
        )
    )


def validate_upstream_key() -> None:
    shape = upstream_key_shape()
    if not shape["present"]:
        raise SystemExit("upstream key not found in process or Windows User environment")
    if not shape["starts_sk_or_v1"]:
        raise SystemExit("configured upstream key does not look like an OpenRouter key")
    if shape["length"] < 40:
        raise SystemExit("configured upstream key is too short")
    if shape["has_whitespace"]:
        raise SystemExit("configured upstream key contains whitespace")


def select_unresolved_true(
    manifest_path: Path,
    summary_path: Path,
    limit: int,
) -> list[dict[str, Any]]:
    manifest = {row["id"]: row for row in load_jsonl(manifest_path)}
    summary = load_summary(summary_path)
    selected: list[dict[str, Any]] = []
    for result in summary.get("per_problem", []):
        if result.get("status") != "not_attempted":
            continue
        problem = manifest.get(result.get("id"))
        if problem is None or problem.get("answer") is not True:
            continue
        selected.append(problem)
        if len(selected) >= limit:
            break
    return selected


def write_fixture(rows: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")


def runner_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if not env.get("OPENROUTER_API_KEY") and not env.get("OPENAI_API_KEY"):
        upstream_key = upstream_key_value()
        if upstream_key:
            env["OPENROUTER_API_KEY"] = upstream_key
    userprofile = env.get("USERPROFILE")
    if userprofile:
        elan_bin = str(Path(userprofile) / ".elan" / "bin")
        path = env.get("PATH", "")
        if elan_bin not in path.split(os.pathsep):
            env["PATH"] = elan_bin + os.pathsep + path
    return env


def run_command(command: list[str], cwd: Path) -> int:
    print("running:", " ".join(command))
    completed = subprocess.run(command, cwd=cwd, env=runner_env(), check=False)
    return int(completed.returncode)


def run_solo(
    fixture_path: Path,
    output_path: Path,
    submission_dir: Path = SUBMISSION_DIR,
    config_path: Path | None = None,
) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "pipeline.runner",
        "--submission",
        str(submission_dir),
        "--problems",
        str(fixture_path),
        "--output",
        str(output_path),
    ]
    if config_path is not None:
        command.extend(["--config", str(config_path)])
    return run_command(command, OFFICIAL_DIR)


def run_marathon(
    fixture_path: Path,
    output_dir: Path,
    budget_tokens: int,
    budget_seconds: int,
    submission_dir: Path = SUBMISSION_DIR,
) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "scripts/run_marathon.py",
        "--solver",
        str(submission_dir),
        "--manifest",
        str(fixture_path),
        "--budget-tokens",
        str(budget_tokens),
        "--budget-seconds",
        str(budget_seconds),
        "--output-dir",
        str(output_dir),
    ]
    return run_command(command, OFFICIAL_DIR)


def write_proxy_smoke_inputs() -> tuple[Path, Path, Path]:
    PROXY_SMOKE_DIR.mkdir(parents=True, exist_ok=True)
    (PROXY_SMOKE_DIR / "solver.py").write_text(PROXY_SMOKE_SOLVER, encoding="utf-8")
    problem = {
        "id": "llm_proxy_smoke_0001",
        "eq1_id": 1,
        "eq2_id": 1,
        "equation1": "x = x",
        "equation2": "x = x",
        "answer": True,
    }
    write_fixture([problem], PROXY_SMOKE_FIXTURE)
    config = json.loads((OFFICIAL_DIR / "pipeline" / "config.json").read_text(encoding="utf-8"))
    config["solver"]["timeout_seconds"] = 180
    config["llm"]["max_output_tokens"] = 16
    config["llm"]["reasoning_effort"] = "low"
    PROXY_SMOKE_CONFIG.write_text(json.dumps(config, indent=2), encoding="utf-8")
    return PROXY_SMOKE_DIR, PROXY_SMOKE_FIXTURE, PROXY_SMOKE_CONFIG


def run_proxy_smoke(budget_tokens: int, budget_seconds: int) -> int:
    submission_dir, fixture_path, config_path = write_proxy_smoke_inputs()
    PROXY_SMOKE_SOLO_OUTPUT.unlink(missing_ok=True)
    shutil.rmtree(PROXY_SMOKE_MARATHON_DIR, ignore_errors=True)
    print(f"proxy_smoke_submission={submission_dir}")
    print(f"proxy_smoke_fixture={fixture_path}")
    print(f"proxy_smoke_config={config_path}")
    exit_code = run_solo(
        fixture_path,
        PROXY_SMOKE_SOLO_OUTPUT,
        submission_dir=submission_dir,
        config_path=config_path,
    )
    summarize_solo_output(PROXY_SMOKE_SOLO_OUTPUT)
    exit_code = run_marathon(
        fixture_path,
        PROXY_SMOKE_MARATHON_DIR,
        budget_tokens,
        budget_seconds,
        submission_dir=submission_dir,
    ) or exit_code
    summarize_marathon_output(PROXY_SMOKE_MARATHON_DIR)
    return exit_code


def run_direct_openrouter_smoke() -> int:
    validate_upstream_key()
    try:
        from openai import OpenAI
        import openai
    except ImportError as exc:
        print(f"direct_openrouter_import_error={exc}")
        return 1

    client = OpenAI(
        api_key=upstream_key_value(),
        base_url="https://openrouter.ai/api/v1",
        timeout=120,
    )
    base = {
        "model": "openai/gpt-oss-120b",
        "messages": [{"role": "user", "content": "Return exactly: ok"}],
        "max_tokens": 16,
        "temperature": 0.0,
    }
    pinned_provider = {
        "provider": {
            "order": ["DeepInfra"],
            "quantizations": ["bf16"],
            "allow_fallbacks": False,
        }
    }
    tests = [
        ("plain", {}),
        ("provider_deepinfra_bf16", {"extra_body": pinned_provider}),
        (
            "provider_deepinfra_bf16_reasoning_low",
            {"extra_body": {**pinned_provider, "reasoning": {"effort": "low"}}},
        ),
    ]
    ok = True
    for name, extra in tests:
        kwargs = dict(base)
        kwargs.update(extra)
        try:
            completion = client.chat.completions.create(**kwargs)
            usage = getattr(completion, "usage", None)
            total_tokens = getattr(usage, "total_tokens", None) if usage is not None else None
            content = (completion.choices[0].message.content or "")[:40]
            print(f"direct_openrouter_{name}=ok total_tokens={total_tokens} response_prefix={content!r}")
        except openai.APIError as exc:
            ok = False
            print(f"direct_openrouter_{name}=api_error {str(exc)[:240]}")
        except Exception as exc:  # noqa: BLE001
            ok = False
            print(f"direct_openrouter_{name}=error {type(exc).__name__}: {str(exc)[:240]}")
    return 0 if ok else 1


def summarize_solo_output(path: Path) -> None:
    if not path.exists():
        print(f"solo_output_missing={path}")
        return
    rows = json.loads(path.read_text(encoding="utf-8"))
    solved = sum(1 for row in rows if row.get("solved"))
    llm_calls = sum(int(row.get("llm_calls", 0) or 0) for row in rows)
    missing_key = 0
    for row in rows:
        for entry in row.get("log", []):
            text = json.dumps(entry, ensure_ascii=False)
            if "OPENAI_API_KEY or OPENROUTER_API_KEY not set" in text:
                missing_key += 1
                break
    print(f"solo_rows={len(rows)} solved={solved} llm_calls={llm_calls} missing_key_rows={missing_key}")


def summarize_marathon_output(output_dir: Path) -> None:
    summary_path = output_dir / "summary.json"
    if not summary_path.exists():
        print(f"marathon_summary_missing={summary_path}")
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    print(
        "marathon_score={score} attempted={attempted} not_attempted={not_attempted} "
        "tokens_used={tokens_used} tokens_exhausted={tokens_exhausted}".format(**summary)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--run-solo", action="store_true")
    parser.add_argument("--solo-output", type=Path, default=DEFAULT_SOLO_OUTPUT)
    parser.add_argument("--run-marathon", action="store_true")
    parser.add_argument("--marathon-output-dir", type=Path, default=DEFAULT_MARATHON_DIR)
    parser.add_argument("--marathon-budget-tokens", type=int, default=32768)
    parser.add_argument("--marathon-budget-seconds", type=int, default=600)
    parser.add_argument("--run-proxy-smoke", action="store_true")
    parser.add_argument("--run-direct-openrouter-smoke", action="store_true")
    parser.add_argument("--key-status", action="store_true")
    args = parser.parse_args()

    if args.key_status:
        print_key_status()
        return 0

    if args.run_proxy_smoke:
        print_key_status()
        validate_upstream_key()
        return run_proxy_smoke(args.marathon_budget_tokens, args.marathon_budget_seconds)

    if args.run_direct_openrouter_smoke:
        print_key_status()
        return run_direct_openrouter_smoke()

    if args.limit <= 0:
        raise SystemExit("--limit must be positive")
    if not args.manifest.exists():
        raise SystemExit(f"manifest not found: {args.manifest}")
    if not args.summary.exists():
        raise SystemExit(f"summary not found: {args.summary}")

    print_key_status()
    rows = select_unresolved_true(args.manifest, args.summary, args.limit)
    if not rows:
        raise SystemExit("no unresolved TRUE rows selected")
    write_fixture(rows, args.fixture)
    print(f"fixture={args.fixture} rows={len(rows)} ids={','.join(row['id'] for row in rows)}")

    exit_code = 0
    if args.run_solo:
        exit_code = run_solo(args.fixture, args.solo_output) or exit_code
        summarize_solo_output(args.solo_output)
    else:
        print("solo_run=skipped")

    if args.run_marathon:
        exit_code = run_marathon(
            args.fixture,
            args.marathon_output_dir,
            args.marathon_budget_tokens,
            args.marathon_budget_seconds,
        ) or exit_code
        summarize_marathon_output(args.marathon_output_dir)
    else:
        print("marathon_run=skipped")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
