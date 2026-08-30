"""Instrument law 11081's chain: which rule fires at each of A,B,C,D and at the final product."""
import sys, os, random, collections, json
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen, freetest2 as ft
from freemodel import normalise, catalog, size, pvars
from laws import parse_eq

EQ = int(sys.argv[1]) if len(sys.argv) > 1 else 11081
N = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 7

cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
print('law', law, 'dualized', dualized)

src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ,
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}
exec(src, ns)
rules = ns['rules']
print('nrules', len(rules))


class Tracked(cf.Closed):
    def __init__(self, law, rules):
        cf.Closed.__init__(self, law, rules)
        self.rulefor = {}

    def op(self, u, v):
        key = (u, v)
        if key in self.memo:
            return self.memo[key]
        r = cf.Closed.op(self, u, v)
        if key not in self.rulefor:
            self.rulefor[key] = None
            if r[0] == 'J' and r[1] is u and r[2] is v:
                pass
            for i, (conds, x, tag) in enumerate(self.rules):
                if self.check(conds, u, v):
                    e = self.ev(x, u, v)
                    if e is not None:
                        self.rulefor[key] = i
                        break
        return r


C = Tracked(law, rules)
random.seed(SEED)


class Shim:
    pass


F = Shim(); F.vars = pvars(law[1]); F.rhs = law[1]; F.ev = lambda p, s: C.evp(p, s)
pool = []
cases = collections.Counter()
finalrule = collections.Counter()
tested = 0
fails = 0
while tested < N:
    s = ft.nested_triple(F, pool)
    if max(size(t) for t in s.values()) > 120:
        continue
    x, y, z = s['x'], s['y'], s['z']
    try:
        A = C.op(y, x)
        B = C.op(x, A)
        Cc = C.op(z, y)
        D = C.op(B, Cc)
        R = C.op(y, D)
    except RecursionError:
        continue
    tested += 1
    for t in s.values():
        if size(t) <= 40 and len(pool) < 400:
            pool.append(t)
    if R != x:
        fails += 1
    key = tuple('.' if C.rulefor.get(k) is None else str(C.rulefor[k] + 1)
                for k in ((y, x), (x, A), (z, y), (B, Cc)))
    fr = C.rulefor.get((y, D))
    cases[key + (('R%d' % (fr + 1)) if fr is not None else 'FREE',)] += 1
    finalrule[('R%d' % (fr + 1)) if fr is not None else 'FREE'] += 1

print('tested', tested, 'fails', fails)
print('final-rule histogram:', dict(finalrule))
print('case table  (A,B,C,D fired-rule ; final rule)  -- "." = free')
for k, n in cases.most_common(40):
    print('   A=%-4s B=%-4s C=%-4s D=%-4s  ->  %-6s   %d' % (k[0], k[1], k[2], k[3], k[4], n))
