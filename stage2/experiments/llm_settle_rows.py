#!/usr/bin/env python3
"""Use real LLM calls to SETTLE unlabeled rows, soundness-only.

For a row with no ground-truth label (e.g. the generated order-5 samples), a
label comparison is impossible — but verification is not: a TRUE certificate
the offline kernel accepts proves the implication, and a FALSE table
`check_false_certificate` accepts (exhaustive over the finite table) refutes
it. Either outcome *settles* the row. Everything else is "unsettled" and
costs only the call.

Runs the SHIPPED pipeline end to end (solver.PROMPT -> model ->
candidate_from_llm_text_with_reason -> oracles), so it measures the production
Marathon LLM lane — including the egg fallback for proposed lemmas — not a
bespoke prompt.

Two-phase by contract (CLAUDE.md rail 6): threads for network, processes for
the CPU-bound parse+verify.

Usage:
    python stage2/experiments/llm_settle_rows.py --file <rows.jsonl> \
        --reasoning low --workers 8 --out stage2/results/llm-settle-<date>.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "stage2" / "solver"))
sys.path.insert(0, str(REPO / "stage2" / "tests"))
sys.path.insert(0, str(REPO / "stage2" / "experiments"))

import oracles  # noqa: E402
import solver as S  # noqa: E402
from llm_balanced_eval import API_KEY, _client, fill_prompt  # noqa: E402


def call_llm(prompt: str, args) -> dict:
    import openai
    extra_body: dict = {"reasoning": {"effort": args.reasoning}}
    if not args.no_provider_pin:
        extra_body["provider"] = {"order": ["DeepInfra"], "allow_fallbacks": False,
                                  "quantizations": ["bf16"]}
    last_err = ""
    for attempt in range(args.retries + 1):
        try:
            t0 = time.monotonic()
            resp = _client(args.http_timeout).chat.completions.create(
                model=args.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=args.max_tokens,
                temperature=0.0,
                seed=0,
                extra_body=extra_body,
            )
            choice = resp.choices[0]
            msg = choice.message
            content = getattr(msg, "content", None) or ""
            reasoning = (getattr(msg, "reasoning", None)
                         or getattr(msg, "reasoning_content", None) or "")
            return {
                "text": content or reasoning,
                "truncated": choice.finish_reason == "length",
                "completion_tokens": getattr(resp.usage, "completion_tokens", None),
                "seconds": round(time.monotonic() - t0, 1),
            }
        except (openai.APITimeoutError, openai.APIConnectionError,
                openai.RateLimitError, openai.InternalServerError) as e:
            last_err = f"{type(e).__name__}: {str(e)[:160]}"
            time.sleep(min(2 ** attempt, 8))
        except Exception as e:  # noqa: BLE001
            return {"error": f"{type(e).__name__}: {str(e)[:200]}"}
    return {"error": last_err or "llm call failed after retries"}


def fetch_one(job) -> dict:
    problem, args = job
    row: dict = {"id": str(problem.get("id")),
                 "eq1": problem.get("equation1"), "eq2": problem.get("equation2")}
    analysis = S.solver_analysis(problem)
    prompt = fill_prompt(S.PROMPT, problem, analysis, "")
    result = call_llm(prompt, args)
    if "error" in result:
        row.update(status="llm_error", detail=result["error"])
        return row
    row.update(seconds=result["seconds"], truncated=result["truncated"],
               completion_tokens=result["completion_tokens"],
               _text=result["text"])
    return row


def settle_one(job) -> dict:
    row, problem, effort = job
    if row.get("status") == "llm_error":
        return row
    S.set_effort(effort)
    S.set_hard_deadline(None)
    S.clear_term_caches()
    text = row.pop("_text", "")
    candidate, reason = S.candidate_from_llm_text_with_reason(
        problem, text, allow_raw_true=False)
    row["reject_reason"] = reason
    if candidate is None:
        row["status"] = "unsettled"
        obj = S.extract_json_object(text) or {}
        row["claimed_verdict"] = str(obj.get("verdict", "")).lower() or None
        return row
    answer = candidate["answer"]
    verdict, code = answer["verdict"], answer["code"]
    row["route"] = candidate["route"]
    eq1 = S.parse_equation(str(problem["equation1"]))
    eq2 = S.parse_equation(str(problem["equation2"]))
    try:
        if verdict == "false":
            oracles.check_false_certificate(code, eq1, eq2)
            row["status"] = "settled_false"
        else:
            oracles.check_no_banned_tactics(code, candidate["route"])
            shape = oracles.classify_true_certificate(code)
            if shape == "exact_expr":
                oracles.check_true_exact_certificate(code, eq1, eq2)
            elif shape == "singleton":
                oracles.check_true_singleton_certificate(code, eq1)
            elif shape == "lemma":
                oracles.check_true_lemma_certificate(code, eq1, eq2)
            elif shape == "lemma_chain":
                oracles.check_true_lemma_chain_certificate(code, eq1, eq2)
            else:
                raise oracles.OracleError(f"unverifiable shape {shape}")
            row["status"] = "settled_true"
        row["code_bytes"] = len(code.encode("utf-8"))
        row["code"] = code
    except oracles.OracleError as exc:
        row["status"] = "unsound_candidate"
        row["detail"] = str(exc)[:200]
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", type=Path, required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--model", default="openai/gpt-oss-120b")
    ap.add_argument("--reasoning", default="low")
    ap.add_argument("--max-tokens", type=int, default=16384)
    ap.add_argument("--http-timeout", type=float, default=300.0)
    ap.add_argument("--retries", type=int, default=2)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--verify-workers", type=int, default=6)
    ap.add_argument("--no-provider-pin", action="store_true",
                    help="drop the deployed DeepInfra/bf16 pin (needed for "
                         "models DeepInfra does not serve, e.g. gemma)")
    ap.add_argument("--effort", choices=("fast", "standard", "deep"),
                    default="fast")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    if not API_KEY:
        print("No OpenRouter key found (.env or environment).", file=sys.stderr)
        return 2
    problems = [json.loads(line) for line
                in args.file.read_text(encoding="utf-8").splitlines()
                if line.strip()]
    if args.limit:
        problems = problems[: args.limit]
    print(f"settling {len(problems)} rows model={args.model} "
          f"reasoning={args.reasoning}", flush=True)

    t0 = time.monotonic()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        fetched = list(pool.map(fetch_one, ((p, args) for p in problems)))
    calls_ok = sum(1 for r in fetched if r.get("status") != "llm_error")
    tokens = sum(r.get("completion_tokens") or 0 for r in fetched)
    print(f"phase1: {calls_ok}/{len(fetched)} calls ok, {tokens} completion "
          f"tokens, {time.monotonic() - t0:.0f}s", flush=True)

    by_id = {str(p.get("id")): p for p in problems}
    jobs = [(row, by_id[row["id"]], args.effort) for row in fetched]
    t1 = time.monotonic()
    with ProcessPoolExecutor(max_workers=args.verify_workers) as pool:
        settled = list(pool.map(settle_one, jobs, chunksize=4))
    print(f"phase2: {time.monotonic() - t1:.0f}s", flush=True)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as handle:
        for row in settled:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    counts: dict[str, int] = {}
    for row in settled:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    print(f"statuses: {counts}")
    print(f"total completion tokens: {tokens}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
