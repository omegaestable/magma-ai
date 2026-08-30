"""Targeted: for each v that decodes for some u, try MANY other u' against the same v."""
import sys, os, random
sys.path.insert(0, r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen
from freemodel import normalise, catalog, size, rand_term, all_subpatterns
from laws import parse_eq

EQ = 12087
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
src = open('gen/chk12087.py', encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']

def subterms(t, acc):
    acc.append(t)
    if t[0] == 'J':
        subterms(t[1], acc); subterms(t[2], acc)
    return acc

class C2(cf.Closed):
    def __init__(self, law, rules):
        super().__init__(law, rules); self.ruleof = {}
    def op(self, u, v):
        key = (u, v)
        m = self.memo.get(key)
        if m is not None: return m
        if key in self.inprog:
            self.cycles += 1; return ('J', u, v)
        self.inprog.add(key)
        res = None; ri = None
        for i, (conds, x, tag) in enumerate(self.rules):
            if self.check(conds, u, v):
                r = self.ev(x, u, v)
                if r is not None:
                    res = r; ri = i; self.fired[i] = self.fired.get(i, 0) + 1; break
        self.inprog.discard(key)
        if res is None: res = ('J', u, v)
        else: self.ruleof[key] = ri
        self.memo[key] = res
        return res

C = C2(law, rules)
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 11)
terms = [rand_term(random.randint(1, 4), 3) for _ in range(3000)]
for i in range(5000):
    s = {'x': random.choice(terms), 'y': random.choice(terms), 'z': random.choice(terms)}
    try: C.evp(law[1], s)
    except RecursionError: pass
for i in range(15000):
    try: C.op(random.choice(terms), random.choice(terms))
    except RecursionError: pass

vs = sorted(set(v for (u, v) in C.ruleof), key=size)
print('decoded v count', len(vs))
mixed = 0; multi = 0; ex = []
pool = terms
for v in vs:
    orig_us = [(u, i) for (u, vv), i in C.ruleof.items() if vv == v]
    cands = list(subterms(v, []))
    cands += [random.choice(pool) for _ in range(40)]
    hits = dict(((u, i) for u, i in orig_us))
    for u in cands:
        try:
            r = C.op(u, v)
        except RecursionError:
            continue
        if (u, v) in C.ruleof:
            hits[u] = C.ruleof[(u, v)]
    kinds = set(0 if i < 2 else 1 for i in hits.values())
    if len(kinds) > 1:
        mixed += 1
        if len(ex) < 3: ex.append((v, hits))
    if len(hits) > 1:
        multi += 1
        if len(ex) < 3: ex.append((v, hits))
print('v with BOTH forms:', mixed)
print('v with >1 decoding u:', multi)
for v, h in ex[:3]:
    print('  v=', v)
    for u, i in h.items(): print('     u=', u, 'rule', i, 'res', C.op(u, v))
