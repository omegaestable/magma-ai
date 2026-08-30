# -*- coding: utf-8 -*-
"""Two constructions no earlier oracle generates, per the coordinator:

(a) LARGE JUNK.  In `x = y * (((y*x)*z) * (x*z))` the variable no rule constrains is the junk slot inside
    the encodings (the `q` of enc(a,b,c)).  Every earlier census drew it from a small pool.  Here it is
    drawn from a pool that deliberately contains large terms.

(b) PER-RULE FORCING / LEVEL-3 DESCENT.  S7's deep rules read `x` one level inside `z` (P4) or two levels
    inside (P5,P6).  Build the instance that needs THREE levels: z = enc(x, p, q) with p = enc(x, p2, q2)
    and p2 = enc(x, p3, q3), so that op(x,z), op(x,N3) and op(x, op(x,N3)) all decode.  That is the
    construction `AD`'s deep branch descends through, and no census so far builds it.
"""
import sys, os, random, collections, json, time
D = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D); sys.path.insert(0, os.path.join(D, 'gen'))
import closedform as cf
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq
EQ = 12087
law = normalise(parse_eq(catalog()[EQ]))
R1 = cf.Extractor(law).rules(exist=False)
TAGS = [r[2] for r in R1]
S7 = [R1[i] for i in [0, 1, 2, 3, 5, 8, 10]]
FULL13 = list(R1)


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


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s.%s)' % (show(t[1]), show(t[2]))


def run(name, rules, seed, bigjunk, levels, N):
    C = C2(law, rules); random.seed(seed)
    small = [rand_term(random.randint(1, 3), 2) for _ in range(120)]
    big = [rand_term(random.randint(5, 9), 3) for _ in range(120)]     # (a) the large junk pool
    junk = big if bigjunk else small
    def enc(a, b, c): return C.op(C.op(C.op(a, b), c), C.op(b, c))
    def dec(u, v): return C.op(u, v) != ('J', u, v)
    bad = 0; hits = 0; cells = collections.Counter(); worst = None
    for i in range(N):
        try:
            y = random.choice(small)
            x = enc(y, random.choice(small), random.choice(junk))       # forces op(y,x) to decode
            if not dec(y, x): continue
            # (b) build a chain of `levels` nested x-encodings, innermost first
            p = random.choice(small)
            for _ in range(levels):
                p = enc(x, p, random.choice(junk))
            z = enc(x, p, random.choice(junk))
            if not dec(x, z): continue
            N1 = C.op(y, x); N2 = C.op(N1, z); N3 = C.op(x, z)
            V = C.op(N2, N3); Rr = C.op(y, V)
        except RecursionError:
            continue
        hits += 1
        d3 = dec(x, N3)
        cells[('F' if not dec(y, x) else 'D', 'F' if not dec(N1, z) else 'D',
               'F' if not dec(x, z) else 'D', 'F' if not dec(N2, N3) else 'D',
               'lvl2' if d3 else 'lvl1')] += 1
        if Rr != x:
            bad += 1
            t = size(x) + size(y) + size(z)
            if worst is None or t < worst[0]: worst = (t, y, x, z, Rr)
    print('%-8s seed=%d bigjunk=%-5s levels=%d hits=%-5d BAD=%d' % (name, seed, bigjunk, levels, hits, bad), flush=True)
    for k, n in cells.most_common(6):
        print('      %-42s %d' % (str(k), n), flush=True)
    if worst:
        t, y, x, z, Rr = worst
        print('   SMALLEST BAD total=%d  y=%d x=%d z=%d' % (t, size(y), size(x), size(z)), flush=True)
        print('     y =', show(y)[:200], flush=True)
        print('     x =', show(x)[:200], flush=True)
        print('     z =', show(z)[:300], flush=True)
        json.dump({'y': y, 'x': x, 'z': z}, open(os.path.join(D, 'gen', '_w3_12087_deep3_bad.json'), 'w'))
    return bad


tot = 0
for lv in (0, 1, 2):
    for bj in (False, True):
        for sd in (5, 19):
            tot += run('S7', S7, sd, bj, lv, 500)
print('S7 TOTAL BAD', tot, flush=True)
tot2 = 0
for lv in (1, 2):
    tot2 += run('full13', FULL13, 5, True, lv, 500)
print('full13 TOTAL BAD', tot2, flush=True)
