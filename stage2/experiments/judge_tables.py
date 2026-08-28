#!/usr/bin/env python3
"""Judge a FALSE witness TABLE (not a solver route) against the real Lean judge.

Renders the table with the solver's own `false_certificate` / answer-payload
path so the bytes judged are the bytes the solver would emit, then calls
`judge.verify.verify_answer` with the DEPLOYED limits (rail 3b-iv).
Input: jsonl rows with equation1/equation2/table.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "stage2" / "solver"))
sys.path.insert(0, str(REPO / "stage2" / "experiments"))
sys.path.insert(0, str(REPO / "vendor" / "stage2-official"))
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("LEAN_TIMEOUT_SECONDS", "300")
os.environ.setdefault("MAX_CODE_LENGTH", "100000")
os.environ.setdefault("MAX_FALSE_CERT_BYTES", "20000")

import solver as S  # noqa: E402
from real_rounds import DEFAULT_PROOF_POLICY  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=Path, required=True)
    ap.add_argument("--ids", default="")
    ap.add_argument("--limit", type=int, default=3)
    args = ap.parse_args()
    from judge.verify import verify_answer

    rows = [json.loads(l) for l in args.rows.read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = [r for r in rows if r.get("table")]
    if args.ids:
        want = set(args.ids.split(","))
        rows = [r for r in rows if r["id"] in want]
    rows = rows[:args.limit]
    for r in rows:
        eq1 = S.parse_equation(str(r["equation1"]))
        eq2 = S.parse_equation(str(r["equation2"]))
        table = r["table"]
        n = len(table)
        assert S.table_is_counterexample(eq1, eq2, table), r["id"]
        code = S.false_certificate(n, table)
        payload = {"verdict": "false", "code": code}
        problem = {"id": r["id"], "eq1_id": r.get("eq1_id"), "eq2_id": r.get("eq2_id"),
                   "equation1": r["equation1"], "equation2": r["equation2"],
                   "proof_policy": DEFAULT_PROOF_POLICY}
        t0 = time.monotonic()
        try:
            res = verify_answer(problem, json.dumps(payload))
            st, ec = res.get("status"), res.get("error_code")
        except Exception as exc:  # noqa: BLE001
            st, ec = "infra_error", f"{type(exc).__name__}: {exc}"
        print(json.dumps({"id": r["id"], "order": n,
                          "code_bytes": len(code.encode("utf-8")),
                          "status": st, "error_code": ec,
                          "judge_s": round(time.monotonic() - t0, 1)}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
