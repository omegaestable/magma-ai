"""Run `egg_ladder_route` on chosen rows and verify every certificate it emits
with the independent offline kernel (`oracles`), not just the solver's own
replay.

Usage:
    python stage2/experiments/ladder_probe.py --open
    python stage2/experiments/ladder_probe.py --ids hard3_0314 --effort standard
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "stage2" / "solver"))
sys.path.insert(0, str(REPO_ROOT / "stage2" / "tests"))

import oracles  # noqa: E402
import solver as S  # noqa: E402

from egg_bytes_probe import OPEN_ROWS, load_rows  # noqa: E402


def run(row: dict, effort: str) -> dict:
    S.set_effort(effort)
    S.clear_term_caches()
    eq1 = S.parse_equation(str(row["equation1"]))
    eq2 = S.parse_equation(str(row["equation2"]))
    started = time.monotonic()
    got = S.egg_ladder_route(eq1, eq2)
    out = {"id": row.get("id"), "label": row.get("answer"),
           "seconds": round(time.monotonic() - started, 2)}
    if got is None:
        out["route"] = None
        return out
    route, code = got
    out["route"] = route
    out["bytes"] = len(code.encode("utf-8"))
    out["shape"] = oracles.classify_true_certificate(code)
    try:
        oracles.check_no_banned_tactics(code)
        if out["shape"] == "lemma_chain":
            oracles.check_true_lemma_chain_certificate(code, eq1, eq2)
        elif out["shape"] == "lemma":
            oracles.check_true_lemma_certificate(code, eq1, eq2)
        elif out["shape"] == "exact_expr":
            oracles.check_true_exact_certificate(code, eq1, eq2)
        else:
            raise oracles.OracleError(f"unexpected shape {out['shape']}")
        out["kernel"] = "ok"
    except oracles.OracleError as exc:
        out["kernel"] = f"FAIL: {exc}"
    out["code"] = code
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", default="")
    ap.add_argument("--open", action="store_true")
    ap.add_argument("--effort", default="fast")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    rows = load_rows()
    ids = list(OPEN_ROWS) if args.open else [
        i for i in args.ids.split(",") if i.strip()]
    results = []
    for row_id in ids:
        row = rows.get(row_id)
        if row is None:
            print(json.dumps({"id": row_id, "error": "not found"}))
            continue
        try:
            res = run(row, args.effort)
        except Exception as exc:  # noqa: BLE001
            res = {"id": row_id, "error": f"{type(exc).__name__}: {exc}"}
        results.append(res)
        summary = {k: v for k, v in res.items() if k != "code"}
        print(json.dumps(summary, ensure_ascii=False), flush=True)
    if args.out:
        Path(args.out).write_text(
            json.dumps(results, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
