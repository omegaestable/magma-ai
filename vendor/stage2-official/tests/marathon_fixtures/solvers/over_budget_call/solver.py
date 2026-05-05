"""Marathon harness fixture: triggers the proxy's reservation-pattern
pre-call check by bypassing the helper.

The harness preseeds the proxy's settled counter close to the budget
(``JUDGE_MARATHON_TEST_PRESEED_TOKENS = budget - 5``). This solver then
opens an OpenAI client directly — bypassing ``marathon_llm.call_llm``'s
own pre-check — and asks for a completion whose reservation
(prompt_estimate + max_out) exceeds the remaining headroom. The proxy
must reject with a 402 BEFORE forwarding upstream.

Pre-fix the proxy only checked ``settled >= budget``, so this same
call would slip past the gate and the upstream would burn whatever
tokens the response cost, blowing the budget. The reservation pattern
closes that race; this fixture is the regression.

We write a marker line to the output JSONL describing what the SDK
saw (status code + error message), then exit cleanly. The harness
inspects the marker.
"""
import json
import os

base_url = os.environ["OPENAI_BASE_URL"]
api_key = os.environ["OPENAI_API_KEY"]

marker = {
    "id": "over_budget_call_probe",
    "verdict": "true",
    "code": "(harness probe)",
    "got_402": False,
    "status_code": None,
    "error": "",
}
try:
    from openai import OpenAI, APIStatusError
    client = OpenAI(api_key=api_key, base_url=base_url, timeout=30.0)
    try:
        client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": "tiny prompt"}],
            max_tokens=4096,
            temperature=0.0,
        )
        marker["error"] = "expected 402, got success"
    except APIStatusError as exc:
        marker["got_402"] = exc.status_code == 402
        marker["status_code"] = exc.status_code
        marker["error"] = str(exc)[:200]
    except Exception as exc:  # noqa: BLE001 — many shapes
        marker["error"] = f"{type(exc).__name__}: {exc}"[:200]
except Exception as exc:  # noqa: BLE001 — SDK import or client errors
    marker["error"] = f"{type(exc).__name__}: {exc}"[:200]

with open(os.environ["JUDGE_MARATHON_OUTPUT"], "a", encoding="utf-8") as fh:
    fh.write(json.dumps(marker) + "\n")
