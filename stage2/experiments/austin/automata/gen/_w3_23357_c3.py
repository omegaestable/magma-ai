"""23357 C3 constructed guard test.

Force A = op(y, x) and B = op(y, z) through the R1/B1s shape from the
same decoded pair (p, q).  This is the missing interaction after C1 (only B
decoded) and C2 (only V decoded): it makes both chain inputs to the two
halves of the top product decoded, and reports the realised cell as its
positive control.
"""
import collections
import importlib.util
import sys

D = "c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata"
G = D + "/gen/"
sys.path.insert(0, D)

import closedform as cf
import fuzz as fz
from freemodel import size, rand_term

J = lambda a, b: ("J", a, b)
g = lambda n: ("g", n)

spec = importlib.util.spec_from_file_location("rep23357", G + "_x23357_rep.py")
rep = importlib.util.module_from_spec(spec)
argv = list(sys.argv)
sys.argv = [sys.argv[0]]
spec.loader.exec_module(rep)
sys.argv = argv

law, rules = rep.law, rep.rules
base = cf.Closed(law, rules)
pool = [g(i) for i in range(4)]
for depth in range(3):
    for u, v in fz.instances(rules, pool, 14, depth, base):
        for t in (u, v):
            if size(t) <= 60 and t not in pool:
                pool.append(t)
        try:
            value = base.op(u, v)
            if size(value) <= 60 and value not in pool:
                pool.append(value)
        except RecursionError:
            pass
for seed in range(200):
    t = rand_term(seed % 4 + 1, 3)
    if t not in pool:
        pool.append(t)

decoded = [(p, q) for p in pool for q in pool if base.op(p, q) != J(p, q)]
small = [t for t in pool if size(t) <= 12]
print("pool", len(pool), "decoded pairs", len(decoded), flush=True)

cells = collections.Counter()
top_rules = collections.Counter()
bad = 0
tested = 0
worst = None
for p, q in decoded[:400]:
    for r in small[:5]:
        for s in small[:5]:
            # R1/B1s reads q from both (y,x) and (y,z).
            y = J(J(p, q), p)
            x = J(q, J(p, s))
            z = J(q, J(p, r))
            model = cf.Closed(law, rules)
            try:
                A = model.op(y, x)
                U = model.op(A, y)
                B = model.op(y, z)
                V = model.op(x, B)
                top = model.op(U, V)
            except RecursionError:
                continue
            tested += 1
            cell = ("AD" if A != J(y, x) else "AF",
                    "UD" if U != J(A, y) else "UF",
                    "BD" if B != J(y, z) else "BF",
                    "VD" if V != J(x, B) else "VF")
            cells[cell] += 1
            if top != x:
                bad += 1
                total = size(x) + size(y) + size(z)
                if worst is None or total < worst[0]:
                    worst = (total, x, y, z, cell)

print("tested", tested, "BAD", bad, flush=True)
print("cells", dict(cells), flush=True)
if worst:
    print("smallest bad", worst, flush=True)
if not any(cell[0] == "AD" and cell[2] == "BD" for cell in cells):
    raise SystemExit("C3 positive control failed: no A/B-decoded cell")
