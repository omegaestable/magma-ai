"""Byte-exact certificate snapshot for the egg-routed rows.

249 audited rows are served by the `egg_*` engines, so any refactor of the
saturation core is a coverage risk on a large fraction of the corpus. This tool
records `(row id, route, certificate bytes)` for a fast, route-diverse sample
and diffs a later run against it, so "the engine still emits the same proof" is
a checkable claim rather than a hope.

    # before a refactor
    python stage2/experiments/egg_cert_snapshot.py --write <out.json>
    # after
    python stage2/experiments/egg_cert_snapshot.py --check <out.json>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "stage2" / "solver"))

import solver as S  # noqa: E402

from egg_bytes_probe import load_rows  # noqa: E402

RESULTS_DIR = REPO_ROOT / "stage2" / "results"


def latest_audits() -> list[Path]:
    """The newest `audit-*.json` reports, official and HF.

    Deliberately discovered rather than hard-coded: a snapshot tool that quietly
    reads a stale audit picks stale rows and reports a clean diff on coverage that
    has already moved.
    """
    official = sorted(p for p in RESULTS_DIR.glob("audit-2*.json")
                      if "-hf" not in p.name)
    hf = sorted(RESULTS_DIR.glob("audit-2*-hf.json"))
    return [p for p in (official[-1:] + hf[-1:])]


def egg_rows(per_route: int) -> list[tuple[str, str]]:
    """Fastest `per_route` rows for each egg route label in the newest audit."""
    buckets: dict[str, list[tuple[float, str]]] = {}
    audits = latest_audits()
    print(f"reading {[p.name for p in audits]}")
    for path in audits:
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for payload in data["sets"].values():
            recs = payload["rows"] if isinstance(payload, dict) and "rows" in payload else payload
            for rec in recs:
                route = str(rec.get("route", ""))
                if "egg" not in route:
                    continue
                buckets.setdefault(route, []).append(
                    (float(rec.get("seconds", 999)), str(rec["id"])))
    picked: list[tuple[str, str]] = []
    for route, items in sorted(buckets.items()):
        items.sort()
        picked.extend((row_id, route) for _s, row_id in items[:per_route])
    return picked


def solve(row: dict, effort: str) -> tuple[str, str] | None:
    S.set_effort(effort)
    S.clear_term_caches()
    record = S.solve_problem(row, false_time_budget=2.0)
    if record is None:
        return None
    return str(record["route"]), record["answer"]["code"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write")
    ap.add_argument("--check")
    ap.add_argument("--per-route", type=int, default=8)
    ap.add_argument("--effort", default="fast")
    args = ap.parse_args()

    rows = load_rows()
    targets = egg_rows(args.per_route)
    results: dict[str, dict] = {}
    for row_id, expected_route in targets:
        row = rows.get(row_id)
        if row is None:
            continue
        started = time.monotonic()
        got = solve(row, args.effort)
        entry = {"expected_route": expected_route,
                 "seconds": round(time.monotonic() - started, 2)}
        if got is None:
            entry["route"] = None
        else:
            route, code = got
            entry["route"] = route
            entry["sha256"] = hashlib.sha256(code.encode("utf-8")).hexdigest()
            entry["bytes"] = len(code.encode("utf-8"))
        results[row_id] = entry
        print(f"{row_id}: {entry.get('route')} {entry.get('bytes')} "
              f"({entry['seconds']}s)", flush=True)

    if args.write:
        Path(args.write).write_text(
            json.dumps(results, indent=1, sort_keys=True), encoding="utf-8")
        print(f"\nwrote {len(results)} entries to {args.write}")
        return

    baseline = json.loads(Path(args.check).read_text(encoding="utf-8"))
    same = drift = lost = 0
    for row_id, base in sorted(baseline.items()):
        now = results.get(row_id)
        if now is None:
            continue
        if now.get("route") is None and base.get("route") is not None:
            lost += 1
            print(f"LOST   {row_id}: was {base['route']}")
        elif now.get("sha256") == base.get("sha256"):
            same += 1
        else:
            drift += 1
            print(f"DRIFT  {row_id}: {base.get('route')} {base.get('bytes')}B "
                  f"-> {now.get('route')} {now.get('bytes')}B")
    print(f"\nidentical={same} drifted={drift} lost={lost}")
    sys.exit(1 if (drift or lost) else 0)


if __name__ == "__main__":
    main()
