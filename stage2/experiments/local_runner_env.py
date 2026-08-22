#!/usr/bin/env python3
"""Repo-local environment bootstrap for Stage 2 helper scripts."""

from __future__ import annotations

from collections.abc import Mapping
import json
import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
REPO_ENV_PATH = REPO_ROOT / ".env"
SUPPORTED_LOCAL_ENV_KEYS = (
    "OPENROUTER_API_KEY",
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "SAIR_STAGE2_MODEL",
)
UPSTREAM_KEY_NAMES = ("OPENROUTER_API_KEY", "OPENAI_API_KEY")

# `vendor/stage2-official/judge/verify.py` reads these three from the environment
# and falls back to its own module constants (50,000 / 10,000 / 120) when they
# are absent. The deployed runner never uses that fallback: `pipeline/proxy.py`
# hands the judge `pipeline/config.json`'s `judge` block instead. Anything that
# judges locally without setting them is therefore measuring a *stricter* judge
# than production and will invent failures.
#
# Found the expensive way twice. 2026-08-13: `judge_rows.py` had been reading the
# fallback and a 59,820-byte certificate's "rejection" was written down as a
# property of the judge, which halved the solver's own caps for two weeks
# (CLAUDE.md rail 3b, third instance). 2026-08-21: the *Marathon* runners had
# never been given the same fix, so a real 200-row run scored 199/200 with one
# `malformed` on an 88,539-byte certificate that is `accepted` with only the cap
# changed (rail 3b-iv). It lives here, in tracked code that every runner already
# imports, rather than in `tmp_stage2_smoke/real-run-tools/` — which `.gitignore`
# excludes, and which is exactly how the completion pipeline once ended up
# existing on one machine.
JUDGE_CONFIG_PATH = REPO_ROOT / "vendor" / "stage2-official" / "pipeline" / "config.json"
JUDGE_ENV_FROM_CONFIG = {
    "LEAN_TIMEOUT_SECONDS": "lean_timeout_seconds",
    "MAX_CODE_LENGTH": "max_code_length",
    "MAX_FALSE_CERT_BYTES": "max_false_cert_bytes",
}


def judge_cap_env(config_path: Path = JUDGE_CONFIG_PATH) -> dict[str, str]:
    """The judge caps the deployment passes, read from the config it passes them from.

    Read rather than hardcoded on purpose: a copy here could drift from
    `config.json` silently, and drifting mirrors of this exact file are what rail
    3b is about. Returns {} if the vendored snapshot is missing, so a checkout
    without `vendor/` still runs -- it just judges at the library defaults, which
    is the pre-2026-08-21 behaviour and no worse.
    """
    try:
        judge = json.loads(config_path.read_text(encoding="utf-8"))["judge"]
    except (OSError, KeyError, ValueError):
        return {}
    return {name: str(judge[key])
            for name, key in JUDGE_ENV_FROM_CONFIG.items() if key in judge}


def _strip_optional_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def repo_env_values(env_path: Path = REPO_ENV_PATH) -> dict[str, str]:
    if not env_path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            continue
        name, raw_value = line.split("=", 1)
        name = name.strip()
        if name not in SUPPORTED_LOCAL_ENV_KEYS:
            continue
        values[name] = _strip_optional_quotes(raw_value.strip())
    return values


def windows_user_env(name: str) -> str:
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


def load_local_runner_env(base_env: Mapping[str, str] | None = None) -> tuple[dict[str, str], dict[str, str]]:
    env = dict(base_env if base_env is not None else os.environ)
    sources: dict[str, str] = {}
    repo_values = repo_env_values()
    for key in SUPPORTED_LOCAL_ENV_KEYS:
        current_value = env.get(key, "")
        if current_value:
            sources[key] = "process_env"
            continue
        repo_value = repo_values.get(key, "")
        if repo_value:
            env[key] = repo_value
            sources[key] = "repo_env"
            continue
        legacy_value = windows_user_env(key) if key in UPSTREAM_KEY_NAMES else ""
        if legacy_value:
            env[key] = legacy_value
            sources[key] = "windows_user_env"
            continue
        sources[key] = "missing"
    # An explicit value in the caller's environment always wins; this only fills
    # in what would otherwise silently fall back to the library defaults.
    for name, value in judge_cap_env().items():
        if not env.get(name):
            env[name] = value
            sources[name] = "judge_config"
    return env, sources


def upstream_key_state(base_env: Mapping[str, str] | None = None) -> dict[str, str]:
    env, sources = load_local_runner_env(base_env)
    for key in UPSTREAM_KEY_NAMES:
        value = env.get(key, "")
        if value:
            return {
                "name": key,
                "value": value,
                "source": sources.get(key, "process_env"),
                "repo_env_path": str(REPO_ENV_PATH),
            }
    return {
        "name": "",
        "value": "",
        "source": "missing",
        "repo_env_path": str(REPO_ENV_PATH),
    }