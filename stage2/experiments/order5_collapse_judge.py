"""Send a prototype completion certificate to the real local Lean judge.

`judge_rows.py` judges what the SHIPPED solver emits; this judges what the
lab3 prototype emits for a given row, which is the only thing that pins the
new inference (all-orientation superposition + merge seeding) as judge-legal
rather than merely kernel-legal (rail 3c).

Run at most ONE of these at a time -- check `Get-Process lean*` first.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "stage2" / "solver"))
sys.path.insert(0, str(REPO_ROOT / "stage2" / "tests"))
sys.path.insert(0, str(REPO_ROOT / "stage2" / "experiments"))
sys.path.insert(0, str(REPO_ROOT / "vendor" / "stage2-official"))
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
# Deployed caps, not verify.py's no-config fallback (rail 3b, third instance).
os.environ.setdefault("LEAN_TIMEOUT_SECONDS", "300")
os.environ.setdefault("MAX_CODE_LENGTH", "100000")
os.environ.setdefault("MAX_FALSE_CERT_BYTES", "20000")

import solver as S  # noqa: E402
import oracles  # noqa: E402
import order5_collapse_lab3 as L3  # noqa: E402
from real_rounds import DEFAULT_PROOF_POLICY  # noqa: E402

CLASSIFY = REPO_ROOT / "stage2/results/order5-classification-2026-08-27.jsonl"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", required=True)
    ap.add_argument("--variant", default="merge_supall_deep")
    ap.add_argument("--budget", type=float, default=30.0)
    ap.add_argument("--rows", default=str(CLASSIFY))
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    from judge.verify import verify_answer

    rows = {}
    for path in args.rows.split(","):
        for line in open(path, encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                rows[r["id"]] = r

    out = []
    for rid in args.ids.split(","):
        row = rows[rid]
        eq1 = S.parse_equation(row["equation1"])
        eq2 = S.parse_equation(row["equation2"])
        kw = dict(L3.VARIANTS[args.variant])
        runner = L3.run3_deepening if kw.pop("_deepen", False) else L3.run3
        res = runner(eq1, eq2, budget=args.budget, want_cert=True, **kw)
        if not res.get("cert"):
            print("%-24s no certificate (%s)" % (rid, res["route"]))
            continue
        code = res["cert"]
        try:
            oracles.check_true_lemma_chain_certificate(code, eq1, eq2)
            kernel = "OK"
        except Exception as exc:  # noqa: BLE001
            kernel = "FAIL:" + str(exc)[:120]
        banned = S.find_judge_banned_token(code) if hasattr(
            S, "find_judge_banned_token") else None
        # The judge only uses the ids to NAME the Lean defs (`Equation<id>`);
        # the equations themselves come from the text. The classification file
        # omits them, so recover them from the row id `order5_<eq1>_<eq2>`.
        parts = rid.split("_")
        eq1_id = row.get("eq1_id") or int(parts[-2])
        eq2_id = row.get("eq2_id") or int(parts[-1])
        problem = {"id": rid, "eq1_id": eq1_id,
                   "eq2_id": eq2_id,
                   "equation1": row["equation1"], "equation2": row["equation2"],
                   "proof_policy": DEFAULT_PROOF_POLICY}
        started = time.monotonic()
        try:
            result = verify_answer(problem, json.dumps(
                {"verdict": "true", "code": code}))
            status = result.get("status")
            err = result.get("error_code")
        except Exception as exc:  # noqa: BLE001
            status, err = "infra_error", "%s: %s" % (type(exc).__name__, exc)
        secs = round(time.monotonic() - started, 1)
        print("%-24s route=%-9s bytes=%-6d kernel=%-4s banned=%s judge=%s %s "
              "(%.1fs)" % (rid, res["route"], len(code.encode()), kernel,
                           banned, status, err or "", secs))
        out.append({"id": rid, "route": res["route"], "kernel": kernel,
                    "banned": banned, "status": status, "error_code": err,
                    "judge_seconds": secs, "bytes": len(code.encode()),
                    "code": code, "equation1": row["equation1"],
                    "equation2": row["equation2"]})
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            for r in out:
                fh.write(json.dumps(r) + "\n")


if __name__ == "__main__":
    main()
