"""Which rule fires per (u,v); does a single v ever admit both the left-form (R1/R2) and the
right-form (R3) decode?  And how many distinct u decode against one v?"""
import sys, os, random
sys.path.insert(0, r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq

EQ = 12087
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
src = open('gen/chk12087.py', encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']

class C2(cf.Closed):
    def __init__(self, law, rules):
        super().__init__(law, rules)
        self.ruleof = {}
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
terms = [rand_term(random.randint(1, 4), 3) for _ in range(4000)]
for i in range(8000):
    s = {'x': random.choice(terms), 'y': random.choice(terms), 'z': random.choice(terms)}
    try: C.evp(law[1], s)
    except RecursionError: pass
for i in range(30000):
    try: C.op(random.choice(terms), random.choice(terms))
    except RecursionError: pass

byv = {}
for (u, v), i in C.ruleof.items():
    byv.setdefault(v, []).append((u, i))
mixed = []
multi = []
for v, lst in byv.items():
    kinds = set(0 if i < 2 else 1 for u, i in lst)
    us = set(u for u, i in lst)
    if len(kinds) > 1: mixed.append((v, lst))
    if len(us) > 1: multi.append((v, lst))
print('decoded pairs', len(C.ruleof), 'distinct v', len(byv))
print('v admitting BOTH forms:', len(mixed))
for v, lst in mixed[:3]:
    print('   v=', v, 'entries=', [(size(u), i) for u, i in lst])
print('v admitting >1 distinct u:', len(multi))
for v, lst in multi[:5]:
    print('   v sz=', size(v), 'entries=', [(size(u), i) for u, i in lst])
