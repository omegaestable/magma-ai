"""Negative control for mini-egg: it must never saturate a FALSE implication.
Draw random explicit_proof_false pairs from the ETP matrix and run the same
budgets as the positive tests. Any 'proved' here = soundness bug."""
import gzip
import json
import random
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "stage2" / "solver"))
sys.path.insert(0, str(REPO / "stage2" / "experiments"))
import solver as S
from egg_saturation import saturate

eqs = [l.strip() for l in (REPO / "data/exports/equations.txt").read_text(encoding="utf-8").splitlines() if l.strip()]
with gzip.open(REPO / "data/exports/general_outcomes.json.gz", "rt", encoding="utf-8") as h:
    M = json.load(h)["outcomes"]
n = len(eqs)

def upper(eq):
    def walk(t):
        if t[0] == "var":
            return ("var", t[1].upper())
        return ("op", walk(t[1]), walk(t[2]))
    return walk(eq["lhs"]), walk(eq["rhs"])

if __name__ == "__main__":
    rng = random.Random(20260723)
    false_pairs = []
    while len(false_pairs) < 25:
        i, j = rng.randint(1, n), rng.randint(1, n)
        if i != j and M[i-1][j-1].endswith("_false"):
            false_pairs.append((i, j))

    bugs = 0
    for i, j in false_pairs:
        eq1 = S.parse_equation(eqs[i-1])
        eq2 = S.parse_equation(eqs[j-1])
        t0 = time.monotonic()
        ok, st = saturate(upper(eq1), eq2["lhs"], eq2["rhs"], time_budget=6.0)
        dt = time.monotonic() - t0
        tag = "!!!BUG!!!" if ok else "ok(no)"
        if ok:
            bugs += 1
        print(f"Eq{i}=>Eq{j}: {tag} {dt:5.1f}s rounds={st['rounds']} enodes={st['enodes']}", flush=True)
    print(f"\n{bugs} false positives out of {len(false_pairs)}")
