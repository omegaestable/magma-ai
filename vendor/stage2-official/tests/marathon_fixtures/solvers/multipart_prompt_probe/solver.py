"""Marathon harness fixture: list-of-parts content must inflate the
prompt-estimate the same way string content does.

Pre-fix the proxy estimated prompt length via ``len(content)`` directly;
when ``content`` was a list of ``{"type": "text", "text": "..."}`` parts
the result was the *list length* (one or two) rather than the sum of
the part lengths, so a multi-MB prompt got reserved for ~1 token. The
attacker then asked for max_tokens=1 and slipped past the budget gate
even though the actual upstream cost (and the ``usage.total_tokens``
that came back) was far above the remaining headroom.

The harness preseeds settled tokens to ``budget - 5`` and pads the
prompt to ~50_000 characters across two text parts. Reservation is
``50_000/4 + max_tokens`` ≈ 12_500 + N, which is far above the 5 tokens
of headroom — the proxy must reject with 402 before forwarding upstream.

This fixture also covers the validator: it sends ONE call with text-only
parts (must succeed up to the budget gate) and a SECOND call with a
non-text part (must be rejected with 400 by ``_validate_messages``).
"""
import json
import os

base_url = os.environ["OPENAI_BASE_URL"]
api_key = os.environ["OPENAI_API_KEY"]

marker = {
    "id": "multipart_prompt_probe",
    "verdict": "true",
    "code": "(harness probe)",
    "text_parts_status": None,
    "text_parts_error": "",
    "image_part_status": None,
    "image_part_error": "",
}

big_chunk = "X" * 25_000  # 50k chars total in two parts, ~12_500 tokens

try:
    from openai import OpenAI, APIStatusError
    client = OpenAI(api_key=api_key, base_url=base_url, timeout=10.0)

    # Branch 1: legitimate text-only multipart. Pre-fix this reserved
    # only ~1 token; post-fix it reserves ~12_500. With the preseed
    # leaving 5 tokens of headroom, the post-fix proxy must 402.
    try:
        client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": big_chunk},
                    {"type": "text", "text": big_chunk},
                ],
            }],
            max_tokens=4,
            temperature=0.0,
        )
        marker["text_parts_status"] = 200
        marker["text_parts_error"] = "expected 402, got success"
    except APIStatusError as exc:
        marker["text_parts_status"] = exc.status_code
        marker["text_parts_error"] = str(exc)[:200]
    except Exception as exc:  # noqa: BLE001 — many shapes
        marker["text_parts_error"] = f"{type(exc).__name__}: {exc}"[:200]

    # Branch 2: non-text content part — proxy must reject with 400 from
    # the validator BEFORE it even attempts to forward.
    try:
        client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url",
                     "image_url": {"url": "data:image/png;base64,AAAA"}},
                ],
            }],
            max_tokens=4,
            temperature=0.0,
        )
        marker["image_part_status"] = 200
        marker["image_part_error"] = "expected 400, got success"
    except APIStatusError as exc:
        marker["image_part_status"] = exc.status_code
        marker["image_part_error"] = str(exc)[:200]
    except Exception as exc:  # noqa: BLE001
        marker["image_part_error"] = f"{type(exc).__name__}: {exc}"[:200]
except Exception as exc:  # noqa: BLE001 — SDK import etc.
    marker["text_parts_error"] = f"{type(exc).__name__}: {exc}"[:200]

with open(os.environ["JUDGE_MARATHON_OUTPUT"], "a", encoding="utf-8") as fh:
    fh.write(json.dumps(marker) + "\n")
