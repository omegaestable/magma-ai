"""Marathon harness fixture: a failing upstream call must bill the
reservation, not settle 0.

Pre-fix the proxy's settle path used ``actual=0`` whenever
``forward_upstream`` raised. A solver that aimed at a flaky / slow
upstream could trigger a timeout (which can cost real upstream tokens
on partial generation) yet have the proxy bill nothing — turning every
failure into a free call. Post-fix the failure path bills the full
reservation as a pessimistic upper bound.

The harness points the proxy at a closed loopback port (``127.0.0.1:1``)
via ``inject_runner_env``. The solver makes ONE chat-completion request
with ``max_retries=0`` so the proxy receives exactly one POST. Inside
the proxy, ``forward_upstream`` will fail (connection refused), and the
proxy must settle the reservation against itself. The harness then
inspects ``MarathonRunResult.tokens_used`` to confirm settled grew.
"""
import json
import os

base_url = os.environ["OPENAI_BASE_URL"]
api_key = os.environ["OPENAI_API_KEY"]

marker = {
    "id": "upstream_fail_probe",
    "verdict": "true",
    "code": "(harness probe)",
    "status_code": None,
    "error": "",
}
try:
    from openai import OpenAI, APIStatusError
    # max_retries=0 so the proxy sees exactly one request. We don't
    # want retry-multiplied billing skewing the assertion.
    client = OpenAI(api_key=api_key, base_url=base_url, timeout=10.0,
                    max_retries=0)
    try:
        client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": "tiny"}],
            max_tokens=64,
            temperature=0.0,
        )
        marker["error"] = "expected upstream failure, got success"
    except APIStatusError as exc:
        marker["status_code"] = exc.status_code
        marker["error"] = str(exc)[:200]
    except Exception as exc:  # noqa: BLE001 — many shapes
        marker["error"] = f"{type(exc).__name__}: {exc}"[:200]
except Exception as exc:  # noqa: BLE001 — SDK import etc.
    marker["error"] = f"{type(exc).__name__}: {exc}"[:200]

with open(os.environ["JUDGE_MARATHON_OUTPUT"], "a", encoding="utf-8") as fh:
    fh.write(json.dumps(marker) + "\n")
