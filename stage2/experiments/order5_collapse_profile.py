"""Profile one order-5 completion run to find the throughput bottleneck."""
from __future__ import annotations

import cProfile
import json
import os
import pstats
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "stage2", "solver"))
sys.path.insert(0, os.path.join(ROOT, "stage2", "experiments"))
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import solver as S  # noqa: E402
from order5_collapse_lab import CLASSIFY, VARIANTS, load, run_completion  # noqa: E402

row_id = sys.argv[1] if len(sys.argv) > 1 else "order5_17591_11190"
variant = sys.argv[2] if len(sys.argv) > 2 else "shipped"
budget = float(sys.argv[3]) if len(sys.argv) > 3 else 15.0

rows = {r["id"]: r for r in load(CLASSIFY)}
row = rows[row_id]
eq1 = S.parse_equation(row["equation1"])
eq2 = S.parse_equation(row["equation2"])
kw = dict(VARIANTS[variant])

pr = cProfile.Profile()
pr.enable()
res = run_completion(eq1, eq2, budget=budget, want_cert=False, **kw)
pr.disable()
print(json.dumps({k: v for k, v in res.items() if k != "cert"}))
st = pstats.Stats(pr)
st.sort_stats("tottime").print_stats(18)
