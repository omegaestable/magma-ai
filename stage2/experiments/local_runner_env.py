#!/usr/bin/env python3
"""Repo-local environment bootstrap for Stage 2 helper scripts."""

from __future__ import annotations

from collections.abc import Mapping
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