#!/usr/bin/env python3
"""Rail 5c validation of the symmetry-broken search: completeness must not be
lost.  Runs shipped `_cp_search` and the prototype at small orders over many
random order-4/order-5 pairs with a generous node/time budget, and reports any
row where the shipped search finds a witness and the prototype does not
(unsound reduction) -- plus the converse (prototype stronger)."""
from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "stage2" / "solver"))
sys.path.insert(0, str(REPO / "stage2" / "experiments"))
import solver as S  # noqa: E402
from cp_symmetry_probe import cp_search2  # noqa: E402


def main() -> int:
    src = Path(sys.argv[1])
    orders = tuple(int(x) for x in sys.argv[2].split(","))
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    budget = float(sys.argv[4]) if len(sys.argv) > 4 else 10.0
    rows = [json.loads(l) for l in src.read_text(encoding="utf-8").splitlines() if l.strip()]
    random.Random(7).shuffle(rows)
    rows = rows[:limit]
    bad = []
    both = same = only_ship = only_new = neither = 0
    t0 = time.monotonic()
    for row in rows:
        eq1 = S.parse_equation(row["equation1"])
        eq2 = S.parse_equation(row["equation2"])
        for n in orders:
            b1 = [S.CONSTRAINT_MAX_NODES]
            t_a = S._cp_search(eq1, eq2, n, time.monotonic() + budget, b1)
            ok_a = t_a is not None and S.table_is_counterexample(eq1, eq2, t_a)
            exh_a = b1[0] > 0
            b2 = [S.CONSTRAINT_MAX_NODES]
            st = {}
            t_b = cp_search2(eq1, eq2, n, time.monotonic() + budget, b2, stats=st)
            ok_b = t_b is not None and S.table_is_counterexample(eq1, eq2, t_b)
            exh_b = st.get("exhausted", False)
            if ok_a and ok_b:
                both += 1
            elif ok_a and not ok_b:
                only_ship += 1
                if exh_b:
                    bad.append({"id": row["id"], "n": n,
                                "note": "prototype EXHAUSTED yet shipped found a witness"})
            elif ok_b and not ok_a:
                only_new += 1
            else:
                neither += 1
    print(json.dumps({"rows": len(rows), "orders": orders, "budget_s": budget,
                      "both": both, "only_shipped": only_ship,
                      "only_prototype": only_new, "neither": neither,
                      "UNSOUND": bad, "wall_s": round(time.monotonic() - t0, 1)},
                     indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
