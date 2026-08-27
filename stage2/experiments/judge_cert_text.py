#!/usr/bin/env python3
"""Judge raw certificate TEXT against the real Lean judge at the deployed caps.

Unlike `judge_rows.py` (which re-solves a catalog row with the solver in THIS
tree) this takes finished certificates from a jsonl file, so it can judge the
output of a solver living in another checkout (a git worktree has no `.lake`
build, so its own `judge_rows.py` cannot run Lean). Always invoke the copy in
the main tree:

    C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe \
      C:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/judge_cert_text.py \
      --in certs.jsonl --out judged.jsonl

Input rows: {"id", "equation1", "equation2", "verdict", "code", ["eq1_id"], ["eq2_id"]}.
Output rows: the input row plus {"judge_status", "error_code", "judge_seconds",
"code_bytes", "verified_on", "toolchain"} -- the fixture schema of
`stage2/fixtures/judge_verified_certs.jsonl` minus `route`/`cert_shape`, which
the caller adds if it wants to append accepted rows to the fixture
(`--append-fixture` there is the ONLY safe way; never `--write-fixture`).

One Lean process at a time per caller; the judge's `lake env` times out under
heavy CPU load, so do not run this concurrently with a full audit.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "stage2" / "experiments"))
sys.path.insert(0, str(REPO / "vendor" / "stage2-official"))
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import local_runner_env  # noqa: E402

for _k, _v in local_runner_env.judge_cap_env().items():
    os.environ.setdefault(_k, _v)

from real_rounds import DEFAULT_PROOF_POLICY  # noqa: E402


def _toolchain() -> str:
    try:
        return (REPO / "vendor" / "stage2-official" / "lean-toolchain").read_text(encoding="utf-8").strip()
    except OSError:
        return "unknown"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--ids", default="", help="comma-separated ids to keep")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    from judge.verify import verify_answer

    rows = [json.loads(line) for line in args.inp.read_text(encoding="utf-8").splitlines() if line.strip()]
    if args.ids:
        want = set(args.ids.split(","))
        rows = [r for r in rows if str(r.get("id")) in want]
    if args.limit:
        rows = rows[: args.limit]
    toolchain = _toolchain()
    today = _dt.date.today().isoformat()
    accepted = 0
    with args.out.open("w", encoding="utf-8") as out:
        for row in rows:
            code = str(row["code"])
            verdict = str(row["verdict"]).lower()
            problem = {
                "id": str(row.get("id", "")),
                "eq1_id": row.get("eq1_id"),
                "eq2_id": row.get("eq2_id"),
                "equation1": row["equation1"],
                "equation2": row["equation2"],
                "proof_policy": DEFAULT_PROOF_POLICY,
            }
            started = time.monotonic()
            try:
                res = verify_answer(problem, json.dumps({"verdict": verdict, "code": code}))
                status, error_code = res.get("status"), res.get("error_code")
                message = res.get("message")
            except Exception as exc:  # noqa: BLE001
                status, error_code, message = "infra_error", f"{type(exc).__name__}: {exc}", None
            seconds = round(time.monotonic() - started, 1)
            record = dict(row)
            record.update({
                "judge_status": status,
                "error_code": error_code,
                "judge_seconds": seconds,
                "code_bytes": len(code.encode("utf-8", "surrogatepass")),
                "verified_on": today,
                "toolchain": toolchain,
            })
            if message and status != "accepted":
                record["judge_message"] = str(message)[:600]
            accepted += status == "accepted"
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            out.flush()
            print(json.dumps({"id": problem["id"], "verdict": verdict, "status": status,
                              "error_code": error_code, "seconds": seconds,
                              "bytes": record["code_bytes"]}), flush=True)
    print(f"accepted {accepted}/{len(rows)}", flush=True)
    return 0 if accepted == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
