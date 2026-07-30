"""Run solver-emitted certificates through the REAL local Lean judge.

The offline oracles in `stage2/tests/` are an upper bound on judge acceptance;
this is ground truth. Use it whenever you touch a certificate builder, and
especially for certificate shapes the proof kernel cannot check
(`classify_true_certificate` -> "other"), where offline evidence is weak or,
for laws forcing a trivial magma, absent entirely.

Lean works on Windows via `elan` despite the setup docs saying WSL/Linux only.

    # specific rows
    python stage2/experiments/judge_rows.py --ids hard2_0080,normal_0747

    # every certificate the proof kernel cannot check, from an audit report
    python stage2/experiments/judge_rows.py --from-audit stage2/results/audit.json \
        --shape other

    # refresh the pinned judge-verified fixture used by the offline gate
    python stage2/experiments/judge_rows.py --from-audit stage2/results/audit.json \
        --shape other --write-fixture

Caveat learned the hard way: the judge shells out to `lake env`, which has a
30 s timeout. Under heavy CPU load (e.g. racing a full `audit_corpus.py` run)
that times out and every row reports an infrastructure error. Run this with the
machine otherwise idle.
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

# The judge renders Lean source containing ◇; a cp1252 console kills the run.
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import oracles  # noqa: E402
import solver as S  # noqa: E402

FIXTURE_PATH = REPO_ROOT / "stage2" / "fixtures" / "judge_verified_certs.jsonl"

SETS = {
    "sample_20": "sample_20.json",
    "sample_200": "sample_200.json",
    "normal": "normal.jsonl",
    "hard1": "hard1.jsonl",
    "hard2": "hard2.jsonl",
    "hard3": "hard3.jsonl",
}
PROBLEMS_DIR = REPO_ROOT / "data" / "stage2_official_problems"
HF_DIR = REPO_ROOT / "data" / "hf_cache"

# Reuse the single source of truth rather than restating it: a bare
# verify_answer(problem, ...) omits the runner's proof policy and is therefore
# NOT runner-equivalent (Operational Note 4), and a hand-written policy silently
# fails the judge's schema check.
from real_rounds import DEFAULT_PROOF_POLICY  # noqa: E402


def load_problems(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    return json.loads(text)


def all_problems() -> dict[str, dict]:
    """Every benchmark problem by id, official sets first."""
    out: dict[str, dict] = {}
    for name in ("normal", "hard1", "hard2", "hard3", "sample_200", "sample_20"):
        path = PROBLEMS_DIR / SETS[name]
        if not path.exists():
            continue
        for problem in load_problems(path):
            out.setdefault(str(problem.get("id", "")), problem)
    if HF_DIR.exists():
        for path in sorted(HF_DIR.glob("evaluation_*.jsonl")):
            for problem in load_problems(path):
                out.setdefault(str(problem.get("id", "")), problem)
    return out


def to_judge_problem(problem: dict) -> dict:
    return {
        "id": problem.get("id"),
        "eq1_id": problem.get("eq1_id"),
        "eq2_id": problem.get("eq2_id"),
        "equation1": problem["equation1"],
        "equation2": problem["equation2"],
        "proof_policy": DEFAULT_PROOF_POLICY,
    }


def judge_one(problem: dict, *, effort: str, false_budget: float) -> dict:
    from judge.verify import verify_answer

    rid = str(problem.get("id", ""))
    S.set_effort(effort)
    S.clear_term_caches()
    record = S.solve_problem(problem, false_time_budget=false_budget)
    if record is None:
        return {"id": rid, "status": "skip"}

    answer = record["answer"]
    code = answer["code"]
    row = {
        "id": rid,
        "route": str(record["route"]),
        "verdict": answer["verdict"],
        "code_bytes": len(code.encode("utf-8")),
        "cert_shape": oracles.classify_true_certificate(code)
        if answer["verdict"] == "true" else "false_table",
    }
    started = time.monotonic()
    try:
        result = verify_answer(to_judge_problem(problem), json.dumps(
            {"verdict": answer["verdict"], "code": code}))
        row["status"] = result.get("status")
        row["error_code"] = result.get("error_code")
    except Exception as exc:  # noqa: BLE001 - infra failure is not a cert failure
        row["status"] = "infra_error"
        row["error_code"] = f"{type(exc).__name__}: {exc}"
    row["judge_seconds"] = round(time.monotonic() - started, 1)
    row["code"] = code
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", default="", help="comma-separated problem ids")
    ap.add_argument("--from-audit", type=Path, default=None,
                    help="audit_corpus.py JSON report to pull row ids from")
    ap.add_argument("--shape", default="",
                    help="with --from-audit, only rows with this cert_shape "
                         "(e.g. 'other' = the certs the proof kernel cannot check)")
    ap.add_argument("--effort", choices=("fast", "standard", "deep"), default="fast")
    ap.add_argument("--false-budget", type=float, default=2.0)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--write-fixture", action="store_true",
                    help=f"write accepted rows to {FIXTURE_PATH.name} for the gate")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    ids: list[str] = [i.strip() for i in args.ids.split(",") if i.strip()]
    if args.from_audit:
        report = json.loads(args.from_audit.read_text(encoding="utf-8"))
        for _set_name, blob in report["sets"].items():
            for row in blob["rows"]:
                if row.get("status") != "solved":
                    continue
                if args.shape and row.get("cert_shape") != args.shape:
                    continue
                ids.append(str(row["id"]))
    # Preserve order, drop duplicates (sample_* mirror rows in normal).
    ids = list(dict.fromkeys(ids))
    if args.limit:
        ids = ids[: args.limit]
    if not ids:
        print("no row ids selected; pass --ids or --from-audit")
        return 2

    catalog = all_problems()
    missing = [i for i in ids if i not in catalog]
    if missing:
        print(f"[warn] {len(missing)} unknown id(s): {missing[:5]}")

    rows: list[dict] = []
    counts = {"accepted": 0, "other": 0, "skip": 0}
    print(f"judging {len(ids) - len(missing)} row(s) at effort={args.effort}\n")
    for rid in ids:
        problem = catalog.get(rid)
        if problem is None:
            continue
        row = judge_one(problem, effort=args.effort,
                        false_budget=args.false_budget)
        rows.append(row)
        if row["status"] == "accepted":
            counts["accepted"] += 1
        elif row["status"] == "skip":
            counts["skip"] += 1
        else:
            counts["other"] += 1
        print(f"  {rid:<32} {str(row['status']):<12} "
              f"{row.get('judge_seconds', 0):>6}s  {row.get('route', '-')}",
              flush=True)

    print(f"\naccepted {counts['accepted']}  "
          f"not-accepted {counts['other']}  skipped {counts['skip']}")
    bad = [r for r in rows if r["status"] not in ("accepted", "skip")]
    if bad:
        print("\nNOT ACCEPTED:")
        for r in bad:
            print(f"  {r['id']} {r.get('route')}: {r['status']} {r.get('error_code')}")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
        print(f"\nWrote {args.out}")

    if args.write_fixture:
        accepted = [r for r in rows if r["status"] == "accepted"]
        FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y-%m-%d")
        with FIXTURE_PATH.open("w", encoding="utf-8") as handle:
            for r in accepted:
                handle.write(json.dumps({
                    "id": r["id"],
                    "route": r["route"],
                    "verdict": r["verdict"],
                    "cert_shape": r["cert_shape"],
                    "code": r["code"],
                    "judge_status": "accepted",
                    "judge_seconds": r["judge_seconds"],
                    "verified_on": stamp,
                }, separators=(",", ":")) + "\n")
        print(f"Wrote {len(accepted)} judge-verified certs to {FIXTURE_PATH}")

    # Infrastructure failures are not certificate failures; surface separately.
    if any(r["status"] == "infra_error" for r in rows):
        print("\n[warn] infra errors present - is `lake env` starved for CPU?")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
