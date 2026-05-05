"""Marathon harness fixture: probes solver-side env for raw upstream secrets.

Writes a marker line describing what the solver process can see in its
environment. The harness asserts:

- raw upstream API keys (OPENROUTER_API_KEY etc.) are NOT present
- if proxy is active, OPENAI_BASE_URL points at 127.0.0.1
- if proxy is active, OPENAI_API_KEY is set (the proxy's per-run secret)

Together these confirm that the runner does not forward production
upstream credentials into the solver subprocess; the solver can only
reach the LLM through the local proxy on loopback.
"""
import json
import os
from urllib.parse import urlparse

# Names of raw upstream provider keys that must never be forwarded to the
# solver. If any of these is present in the solver env, the probe fails.
_RAW_UPSTREAM_KEYS = (
    "OPENROUTER_API_KEY",
    "DEEPSEEK_API_KEY",
    "KIMI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
)

leaked = sorted(name for name in _RAW_UPSTREAM_KEYS if os.environ.get(name))

base_url = os.environ.get("OPENAI_BASE_URL", "")
api_key = os.environ.get("OPENAI_API_KEY", "")
try:
    host = (urlparse(base_url).hostname or "").lower()
except (ValueError, TypeError):
    host = ""
base_url_is_loopback = host in {"127.0.0.1", "localhost", "::1"}

marker = {
    "id": "key_isolation_probe",
    "verdict": "true",
    "code": "(harness probe)",
    "leaked_upstream_keys": leaked,
    "openai_base_url_present": bool(base_url),
    "openai_base_url_is_loopback": base_url_is_loopback,
    "openai_api_key_present": bool(api_key),
}
with open(os.environ["JUDGE_MARATHON_OUTPUT"], "a", encoding="utf-8") as fh:
    fh.write(json.dumps(marker) + "\n")
