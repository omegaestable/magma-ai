"""Marathon harness fixture: budget_tokens=0 must deny all LLM calls.

Pre-fix the proxy's reservation gate used ``cap > 0`` so a budget of 0
read as "unlimited", silently letting the call through. Now ``cap == 0``
is an explicit deny — every reservation is rejected before forwarding,
and the marathon_llm helper preempts with the same semantics.

The probe makes two attempts and writes both results into a single
marker line:

  * ``helper_error`` — what ``marathon_llm.call_llm`` returned. Should be
    a "token budget is zero" error string, never a successful response.
  * ``got_402`` — whether a direct OpenAI SDK call hit the proxy's 402
    deny path. The runner allowlists ``OPENAI_BASE_URL`` /
    ``OPENAI_API_KEY``; the SDK targets the local proxy.

The harness asserts both branches refused the call.
"""
import json
import os
import sys

# Make marathon_llm importable.
sys.path.insert(0, os.environ.get("JUDGE_MARATHON_LIB_DIR", ""))

marker = {
    "id": "zero_budget_probe",
    "verdict": "true",
    "code": "(harness probe)",
    "helper_error": None,
    "helper_response_present": False,
    "got_402": False,
    "status_code": None,
    "error": "",
}

# Branch 1: helper-side preemption.
try:
    from marathon_llm import call_llm
    resp = call_llm("tiny prompt", config={"max_output_tokens": 16})
    if isinstance(resp, dict):
        marker["helper_error"] = resp.get("error")
        marker["helper_response_present"] = "response" in resp
    else:
        marker["helper_error"] = f"unexpected return: {type(resp).__name__}"
except Exception as exc:  # noqa: BLE001 — many shapes
    marker["helper_error"] = f"{type(exc).__name__}: {exc}"

# Branch 2: direct SDK to bypass the helper-side preemption and hit the
# proxy's reservation gate.
try:
    from openai import OpenAI, APIStatusError
    base_url = os.environ.get("OPENAI_BASE_URL", "")
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if base_url and api_key:
        client = OpenAI(api_key=api_key, base_url=base_url, timeout=10.0)
        try:
            client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": "tiny"}],
                max_tokens=16,
                temperature=0.0,
            )
            marker["error"] = "expected 402, got success"
        except APIStatusError as exc:
            marker["got_402"] = exc.status_code == 402
            marker["status_code"] = exc.status_code
            marker["error"] = str(exc)[:200]
        except Exception as exc:  # noqa: BLE001
            marker["error"] = f"{type(exc).__name__}: {exc}"[:200]
    else:
        marker["error"] = "OPENAI_BASE_URL / OPENAI_API_KEY not set"
except Exception as exc:  # noqa: BLE001
    marker["error"] = f"{type(exc).__name__}: {exc}"[:200]

with open(os.environ["JUDGE_MARATHON_OUTPUT"], "a", encoding="utf-8") as fh:
    fh.write(json.dumps(marker) + "\n")
