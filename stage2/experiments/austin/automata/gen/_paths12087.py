import sys, random
sys.path.insert(0, r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
import trace as tr

EQ = 12087
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
rules = [([('TG', ('V',)), ('TG', ('A1', ('V',))), ('TG', ('A1', ('A1', ('V',)))), ('EQ', ('U',), ('A1', ('A1', ('A1', ('V',))))), ('TG', ('A2', ('V',))), ('EQ', ('A2', ('A1', ('A1', ('V',)))), ('A1', ('A2', ('V',)))), ('EQ', ('A2', ('A1', ('V',))), ('A2', ('A2', ('V',))))], ('A2', ('A1', ('A1', ('V',)))), 'free'),
 ([('TG', ('V',)), ('TG', ('A1', ('V',))), ('TG', ('A1', ('A1', ('V',)))), ('EQ', ('U',), ('A1', ('A1', ('A1', ('V',))))), ('OPEQ', ('OP', ('A2', ('A1', ('A1', ('V',)))), ('A2', ('A1', ('V',)))), ('A2', ('V',)))], ('A2', ('A1', ('A1', ('V',)))), 'B1l'),
 ([('TG', ('V',)), ('TG', ('A2', ('V',))), ('OPEQ', ('OP', ('OP', ('U',), ('A1', ('A2', ('V',)))), ('A2', ('A2', ('V',)))), ('A1', ('V',)))], ('A1', ('A2', ('V',))), 'B0l'),
 ([('TG', ('V',)), ('TG', ('A1', ('V',))), ('TG', ('A2', ('A1', ('V',)))), ('TG', ('A1', ('A2', ('A1', ('V',))))), ('TG', ('A1', ('A1', ('A2', ('A1', ('V',)))))), ('OPEQ', ('OP', ('A1', ('A1', ('A1', ('A2', ('A1', ('V',)))))), ('A2', ('A1', ('V',)))), ('A2', ('V',))), ('OPEQ', ('OP', ('U',), ('A1', ('A1', ('A1', ('A2', ('A1', ('V',))))))), ('A1', ('A1', ('V',))))], ('A1', ('A1', ('A1', ('A2', ('A1', ('V',)))))), 'B00l,B1l')]

import freetest2 as ft
random.seed(999)
combos = {}
N = 4000
count_ok = 0
count_bad = 0
class Shim: pass
F = Shim(); F.vars = cf.pvars(law[1]); F.rhs = law[1]
pool = []
for i in range(N):
    T = tr.Tracing(law, rules)
    F.ev = lambda p, s: T.op(F.ev(p[0], s), F.ev(p[1], s)) if not isinstance(p, str) else s[p]
    s = ft.nested_triple(F, pool)
    if max(size(t) for t in s.values()) > 120:
        continue
    for t in s.values():
        if size(t) <= 40 and len(pool) < 400: pool.append(t)
    def which_rule(u, v):
        for i, (conds, x, tag) in enumerate(rules):
            if T.check(conds, u, v):
                return i
        return None
    def opc(a, b):
        r = T.op(a, b)
        which = which_rule(a, b)
        return r, which
    n1, w1 = opc(s['y'], s['x'])
    n2, w2 = opc(n1, s['z'])
    n3, w3 = opc(s['x'], s['z'])
    v, wv = opc(n2, n3)
    fin, wf = opc(s['y'], v)
    key = (w1, w2, w3, wv, wf)
    combos[key] = combos.get(key, 0) + 1
    if fin == s['x']:
        count_ok += 1
    else:
        count_bad += 1
        if count_bad <= 3:
            print('BAD', key, {k: size(vv) for k, vv in s.items()})

print('total', N, 'ok', count_ok, 'bad', count_bad)
print('distinct combos:', len(combos))
for k, v in sorted(combos.items(), key=lambda kv: -kv[1]):
    print(k, v)
