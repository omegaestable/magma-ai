# -*- coding: utf-8 -*-
"""Full wave-3 validation of the 5-rule candidate S5 found by the strong-oracle minimisation, plus its
emitted skeleton size."""
import sys, os, random, collections, json, time
D = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D); sys.path.insert(0, os.path.join(D, 'gen'))
import closedform as cf, revalidate as rv, smallcheck as sc, leangen
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq
EQ = 12087
law = normalise(parse_eq(catalog()[EQ]))
R1 = cf.Extractor(law).rules(exist=False)
TAGS = [r[2] for r in R1]
S5_TAGS = ['free', 'B00l,B1l', 'B00l,B1l|B1:fflf', 'B00l,B1l|B1:fllf', 'B0l']
S5 = [R1[TAGS.index(t)] for t in S5_TAGS]
print('S5 =', [r[2] for r in S5], flush=True)

exec(open(os.path.join(D, 'gen', '_w3_12087_min2.py'), encoding='utf-8').read().split('# sanity')[0]
     .split('R1 = cf.Extractor')[0].split('import closedform as cf')[1].join(['', '']) ) if False else None

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

def census(rules, N, seed, deep2=False):
    C = C2(law, rules); random.seed(seed)
    base = [rand_term(random.randint(1, 3), 2) for _ in range(200)]
    def enc(a, b, c): return C.op(C.op(C.op(a, b), c), C.op(b, c))
    def st(u, v):
        r = C.op(u, v)
        return 'F' if r == ('J', u, v) else str(C.ruleof.get((u, v)))
    if deep2:
        pool = list(base)
        for _ in range(400):
            try: pool.append(enc(random.choice(pool), random.choice(pool), random.choice(pool)))
            except RecursionError: pass
        base = pool
    bad = 0; hits = 0
    for i in range(N):
        try:
            y = random.choice(base); p = random.choice(base); q = random.choice(base)
            x = enc(y, p, q)
            if st(y, x) == 'F': continue
            mode = random.randrange(4)
            if mode == 0: p2 = random.choice(base)
            elif mode == 1: p2 = enc(x, random.choice(base), random.choice(base))
            elif mode == 2: p2 = enc(random.choice(base), random.choice(base), random.choice(base))
            else: p2 = enc(random.choice(base), x, random.choice(base))
            Z = random.choice(base)
            z = enc(x, p2, Z) if random.random() < 0.8 else enc(random.choice(base), p2, Z)
            if st(x, z) == 'F': continue
            N1 = C.op(y, x); N2 = C.op(N1, z); N3 = C.op(x, z); V = C.op(N2, N3); Rr = C.op(y, V)
        except RecursionError:
            continue
        hits += 1
        if Rr != x: bad += 1
    return hits, bad

t0 = time.time()
n1, f1 = sc.exhaustive(cf.Closed(law, S5), law, 9, 1, limit=5)
n2, f2 = sc.exhaustive(cf.Closed(law, S5), law, 5, 2, limit=5)
print('exhaustive 9/1 %d fails=%d ; 5/2 %d fails=%d' % (n1, len(f1), n2, len(f2)), flush=True)
fails = rv.run_tests(law, S5, [3, 4, 5], 3000, 12000)
real = [f for f in fails if f[1] != 'recursion']
print('run_tests fails=%d real=%d (%.0fs)' % (len(fails), len(real), time.time() - t0), flush=True)
for f in real[:3]:
    print('   ', f[2], f[3], {k: size(v) for k, v in f[0].items()}, flush=True)
for sd in (101, 202, 303):
    C = cf.Closed(law, S5); t, ff = cf.deep_tests(C, law, 20000, 300, sd)
    print('deep20k sd=%d real=%d' % (sd, len([q for q in ff if q[1] != 'recursion'])), flush=True)
for sd in (5, 13, 23, 31):
    for d2 in (False, True):
        h, b = census(S5, 1500, sd, d2)
        print('both-decoded census sd=%d deep2=%s hits=%d BAD=%d' % (sd, d2, h, b), flush=True)
print('total %.0fs' % (time.time() - t0), flush=True)
res = leangen.emit(EQ, os.path.join(D, 'gen', '_w3_12087_S5'), rules_override=S5)
print(json.dumps(res), flush=True)
p = os.path.join(D, 'gen', '_w3_12087_S5', 'rec%d.lean' % EQ)
txt = open(p, encoding='utf-8').read()
print('skeleton bytes', len(txt.encode('utf-8')), 'head', len(txt[:txt.index('/-- THE LAW')].encode('utf-8')), flush=True)
