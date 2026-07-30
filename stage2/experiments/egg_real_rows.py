"""Run mini-egg saturation directly on the actual TRUE-miss rows (eq1 |- goal).
Saturation aims at the goal itself; no ETP path needed. 20s/row budget.
Output: which currently-unsolvable benchmark rows the e-graph mechanism cracks.
"""
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "stage2" / "solver"))
sys.path.insert(0, str(REPO / "stage2" / "experiments"))
import solver as S
from egg_saturation import saturate
from audit_corpus import SETS, HF_SETS, load_problems

misses = [m for m in json.load(open(REPO / "stage2/results/skips-2026-07-23.json")) if m["answer"]]

by_set = {}
def get_problem(m):
    name = m["set"]
    if name not in by_set:
        p = SETS.get(name) or HF_SETS.get(name)
        by_set[name] = {r["id"]: r for r in load_problems(p)}
    return by_set[name][m["id"]]

def to_dia(text):
    return text.replace("*", "\u25c7")

def upper(eq):
    def walk(t):
        if t[0] == "var":
            return ("var", t[1].upper())
        return ("op", walk(t[1]), walk(t[2]))
    return walk(eq["lhs"]), walk(eq["rhs"])

def run_one(m):
    prob = get_problem(m)
    eq1 = S.parse_equation(to_dia(prob["equation1"]))
    eq2 = S.parse_equation(to_dia(prob["equation2"]))
    t0 = time.monotonic()
    ok, st = saturate(upper(eq1), eq2["lhs"], eq2["rhs"], time_budget=20.0, rounds=40)
    return m["id"], ok, time.monotonic() - t0, st


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    wins = []
    with ProcessPoolExecutor(max_workers=6) as pool:
        for rid, ok, dt, st in pool.map(run_one, misses, chunksize=1):
            if ok:
                wins.append(rid)
            print(f"{rid:28s} proved={'YES' if ok else 'no '} {dt:5.1f}s "
                  f"rounds={st['rounds']} enodes={st['enodes']}", flush=True)
    print(f"\n{len(wins)}/{len(misses)} TRUE misses cracked by mini-egg: {wins}")
