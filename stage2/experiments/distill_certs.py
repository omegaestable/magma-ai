"""Turn solver-produced certificates into `DISTILLED_CERTS` entries.

Why this exists: some rows are only reachable at `deep` effort, where the engine
needs minutes. Distillation makes the *result* available at any tier as an O(1)
content-keyed lookup — keyed on the renaming-invariant canonical text of both
equations (rail 5h), never on a benchmark id (rail 9).

Hard rule: **an entry may only be added after the real Lean judge has accepted
it.** This tool enforces that by judging every certificate before printing it,
and it refuses to emit anything for a row the judge did not accept.

    python stage2/experiments/distill_certs.py --ids hard3_0314 --effort deep

Writes, for each accepted row:
  - a ready-to-paste `DISTILLED_CERTS` entry on stdout / to --out-python
  - an append-only line for stage2/fixtures/judge_verified_certs.jsonl
    (with --append-fixture; the fixture is never rewritten wholesale, because
    `judge_rows.py --write-fixture` truncates it to just that run's rows)
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

import oracles  # noqa: E402
import solver as S  # noqa: E402

from judge_rows import all_problems, to_judge_problem  # noqa: E402

FIXTURE_PATH = REPO_ROOT / "stage2" / "fixtures" / "judge_verified_certs.jsonl"


def kernel_check(code: str, eq1: dict, eq2: dict, verdict: str) -> str:
    try:
        oracles.check_no_banned_tactics(code)
        if verdict == "false":
            oracles.check_false_certificate(code, eq1, eq2)
            return "false_table"
        shape = oracles.classify_true_certificate(code)
        if shape == "lemma_chain":
            oracles.check_true_lemma_chain_certificate(code, eq1, eq2)
        elif shape == "lemma":
            oracles.check_true_lemma_certificate(code, eq1, eq2)
        elif shape == "exact_expr":
            oracles.check_true_exact_certificate(code, eq1, eq2)
        elif shape == "singleton":
            oracles.check_true_singleton_certificate(code, eq1)
        else:
            return f"{shape} (not kernel-checkable)"
        return shape
    except oracles.OracleError as exc:
        return f"KERNEL FAIL: {exc}"


def python_entry(eq1: dict, eq2: dict, name: str, verdict: str,
                 code: str) -> str:
    key1 = S.canonical_eq_text(eq1)
    key2 = S.canonical_eq_text(eq2)
    return (f'    ("{key1}",\n'
            f'     "{key2}"): ("{verdict}", "{name}", """{code}"""),\n')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", required=True)
    ap.add_argument("--effort", choices=("fast", "standard", "deep"),
                    default="deep")
    ap.add_argument("--false-budget", type=float, default=2.0)
    ap.add_argument("--out-python", type=Path, default=None)
    ap.add_argument("--append-fixture", action="store_true")
    ap.add_argument("--fixture-out", type=Path, default=None,
                    help="write the fixture lines here instead of appending to "
                         "judge_verified_certs.jsonl — lets two distillation "
                         "runs proceed in parallel without interleaving their "
                         "appends into the shared fixture")
    args = ap.parse_args()

    from judge.verify import verify_answer

    catalog = all_problems()
    ids = [i.strip() for i in args.ids.split(",") if i.strip()]
    entries: list[str] = []
    fixture_lines: list[str] = []
    stamp = time.strftime("%Y-%m-%d")

    for rid in ids:
        problem = catalog.get(rid)
        if problem is None:
            print(f"{rid}: not found")
            continue
        S.set_effort(args.effort)
        S.clear_term_caches()
        started = time.monotonic()
        record = S.solve_problem(problem, false_time_budget=args.false_budget)
        solve_secs = round(time.monotonic() - started, 1)
        if record is None:
            print(f"{rid}: SKIP after {solve_secs}s at effort={args.effort}")
            continue
        verdict = record["answer"]["verdict"]
        code = record["answer"]["code"]
        route = str(record["route"])
        eq1 = S.parse_equation(str(problem["equation1"]))
        eq2 = S.parse_equation(str(problem["equation2"]))
        shape = kernel_check(code, eq1, eq2, verdict)

        started = time.monotonic()
        try:
            result = verify_answer(to_judge_problem(problem), json.dumps(
                {"verdict": verdict, "code": code}))
            status = result.get("status")
            error = result.get("error_code")
        except Exception as exc:  # noqa: BLE001
            status, error = "infra_error", f"{type(exc).__name__}: {exc}"
        judge_secs = round(time.monotonic() - started, 1)

        print(f"{rid}: {route} {len(code.encode('utf-8'))}B solve={solve_secs}s "
              f"judge={status} ({judge_secs}s) kernel={shape}"
              + (f" error={error}" if error else ""))
        if status != "accepted":
            print(f"  -> NOT distilled ({status}); an entry the judge has not "
                  f"accepted must never enter the table")
            continue
        # Name the entry by equation ids when available; content is the key, so
        # the name is only a human label for the route string.
        name = f"e{problem.get('eq1_id', '?')}_e{problem.get('eq2_id', '?')}"
        entries.append(python_entry(eq1, eq2, name, verdict, code))
        fixture_lines.append(json.dumps({
            "id": rid, "route": route, "verdict": verdict,
            "cert_shape": shape if not shape.startswith(("KERNEL", "other")) else "other",
            "code": code, "judge_status": "accepted",
            "judge_seconds": judge_secs, "verified_on": stamp,
        }, separators=(",", ":")))

    if entries:
        blob = "".join(entries)
        if args.out_python:
            args.out_python.write_text(blob, encoding="utf-8")
            print(f"\nWrote {len(entries)} DISTILLED_CERTS entries to "
                  f"{args.out_python}")
        else:
            print("\n# --- paste into DISTILLED_CERTS ---")
            print(blob)
    if fixture_lines and args.fixture_out:
        args.fixture_out.write_text("\n".join(fixture_lines) + "\n",
                                    encoding="utf-8")
        print(f"Wrote {len(fixture_lines)} fixture line(s) to {args.fixture_out}")
    if fixture_lines and args.append_fixture:
        with FIXTURE_PATH.open("a", encoding="utf-8") as handle:
            for line in fixture_lines:
                handle.write(line + "\n")
        print(f"Appended {len(fixture_lines)} line(s) to {FIXTURE_PATH.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
