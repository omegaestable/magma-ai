"""Lever 3: re-extract 12087 with closedform2 and minimise against the CENSUS (what killed S6)."""
import sys, os, random, collections, json, time, itertools
D = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D); sys.path.insert(0, os.path.join(D, 'gen'))
import closedform as cf, closedform2 as cf2
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq
EQ = 12087
law = normalise(parse_eq(catalog()[EQ]))
R1 = cf.Extractor(law).rules(exist=False)
try:
    R2, info = cf2.extract(law)
    print('cf2.extract info:', json.dumps(info)[:400])
except Exception as e:
    print('cf2.extract failed:', e); R2 = cf2.Extractor(law).rules()
print('closedform  rules:', len(R1), [r[2] for r in R1])
print('closedform2 rules:', len(R2), [r[2] for r in R2])

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
        for i, (conds, xx, tag) in enumerate(self.rules):
            if self.check(conds, u, v):
                r = self.ev(xx, u, v)
                if r is not None:
                    res = r; ri = i; break
        self.inprog.discard(key)
        if res is None: res = ('J', u, v)
        else: self.ruleof[key] = ri
        self.memo[key] = res
        return res

def tree(rules, N, seed):
    """the 16-cell case tree of gen/_w3_12087_tree.py, returns (hits, bad)"""
    C = C2(law, rules); random.seed(seed)
    base = [rand_term(random.randint(1, 3), 2) for _ in range(150)]
    def enc(a, b, c): return C.op(C.op(C.op(a, b), c), C.op(b, c))
    pool = list(base)
    for _ in range(300):
        try: pool.append(enc(random.choice(pool), random.choice(pool), random.choice(pool)))
        except RecursionError: pass
    bad = 0; hits = 0
    for i in range(N):
        try:
            mode = i % 6
            y = random.choice(pool)
            if mode == 0: x = random.choice(pool); z = random.choice(pool)
            elif mode == 1: x = enc(y, random.choice(pool), random.choice(pool)); z = random.choice(pool)
            elif mode == 2: x = random.choice(pool); z = enc(x, random.choice(pool), random.choice(pool))
            elif mode == 3:
                x = enc(y, random.choice(pool), random.choice(pool)); z = enc(x, random.choice(pool), random.choice(pool))
            elif mode == 4:
                x = random.choice(pool); z = enc(C.op(y, x), random.choice(pool), random.choice(pool))
            else:
                x = enc(y, random.choice(pool), random.choice(pool)); z = enc(C.op(y, x), random.choice(pool), random.choice(pool))
            N1 = C.op(y, x); N2 = C.op(N1, z); N3 = C.op(x, z); V = C.op(N2, N3); Rr = C.op(y, V)
        except RecursionError:
            continue
        hits += 1
        if Rr != x: bad += 1
    return hits, bad

import smallcheck as sc
def ok(rules, N=700, seeds=(5, 19)):
    n1, f1 = sc.exhaustive(cf.Closed(law, rules), law, 9, 1, limit=1)
    if f1: return False
    n2, f2 = sc.exhaustive(cf.Closed(law, rules), law, 5, 2, limit=1)
    if f2: return False
    for sd in seeds:
        h, b = tree(rules, N, sd)
        if b: return False
    return True

# all 6-subsets of S7 (the coordinator's point: only one was tested)
S7 = [R1[i] for i in [0,1,2,3,5,8,10]]
print('=== S7 ok=%s' % ok(S7), flush=True)
for j in range(7):
    sub = S7[:j] + S7[j+1:]
    print('  S7 minus %-24s ok=%s' % (S7[j][2], ok(sub)), flush=True)

# census-driven greedy minimisation from the closedform2 set
keep = list(R2)
removed = []
changed = True
while changed:
    changed = False
    for i in range(len(keep) - 1, -1, -1):
        if keep[i][2] == 'free': continue
        trial = keep[:i] + keep[i+1:]
        if ok(trial):
            removed.append(keep[i][2]); keep = trial; changed = True
            print('  dropped %-24s -> %d rules' % (removed[-1], len(keep)), flush=True)
            break
print('MINIMAL (census-driven):', len(keep), [r[2] for r in keep])
json.dump([r[2] for r in keep], open('gen/_w3_12087_min.json', 'w'))
