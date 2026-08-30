"""Validate the FIVE-rule variant of the rec12234.lean model (R4 = 'B00l,B1l' dropped, which
validated-removal says is droppable) and check the two structural invariants the proof will use:

  INV  : op u v decoded  =>  sz (op u v) + sz u < sz v
  DIG  : op u v decoded  =>  L or M or N   (see the docstring of dig_branch below)
"""
import sys, time, random
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
sys.setrecursionlimit(30000)
import closedform as cf
import fuzz as fz
import smallcheck as sc
import leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 12234
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig


def J(a, b): return ('J', a, b)
def isJ(t): return t[0] == 'J'
def a1(t): return t[1] if isJ(t) else t
def a2(t): return t[2] if isJ(t) else t
def oc(t): return a2(a2(t)) if size(a1(t)) < size(a2(a2(t))) else a2(a1(t))
def msr(a, b):
    m = max(size(a), size(b)); return m * m + size(a) + size(b)


class M5:
    """rec12234.lean's op with rule 4 removed"""
    def __init__(self, *a, **k):
        self.memo = {}; self.fired = {}

    def op(self, u, v):
        key = (u, v); r = self.memo.get(key)
        if r is not None: return r
        def call(a, b): return self.op(a, b) if msr(a, b) < msr(u, v) else J(u, v)
        k = 0
        if (isJ(v) and isJ(a1(v)) and isJ(a1(a1(v))) and u == a2(a1(v)) and isJ(a2(v))
                and a2(a1(a1(v))) == a1(a2(v)) and u == a2(a2(v))):
            k, res = 1, a2(a1(a1(v)))
        elif (isJ(v) and isJ(a1(v)) and isJ(a1(a1(v))) and u == a2(a1(v))
                and msr(a2(a1(a1(v))), u) < msr(u, v) and a2(v) == call(a2(a1(a1(v))), u)):
            k, res = 2, a2(a1(a1(v)))
        elif (isJ(v) and isJ(a1(v)) and u == a2(a1(v)) and isJ(a2(v)) and u == a2(a2(v))
                and msr(oc(a1(a2(v))), a1(a2(v))) < msr(u, v)
                and a1(a1(v)) == call(oc(a1(a2(v))), a1(a2(v)))):
            k, res = 3, a1(a2(v))
        elif (isJ(v) and isJ(a2(v)) and u == a2(a2(v)) and isJ(u) and isJ(oc(u))
                and a1(a2(v)) == a2(oc(u)) and msr(oc(u), u) < msr(u, v)
                and a1(v) == call(oc(u), u)):
            k, res = 5, a1(a2(v))
        elif (isJ(v) and isJ(a2(v)) and u == a2(a2(v)) and isJ(u)
                and msr(oc(u), u) < msr(u, v)
                and msr(oc(a1(a2(v))), a1(a2(v))) < msr(u, v)
                and a1(v) == call(oc(u), u) and oc(u) == call(oc(a1(a2(v))), a1(a2(v)))):
            k, res = 6, a1(a2(v))
        else:
            res = J(u, v)
        if k: self.fired[k] = self.fired.get(k, 0) + 1
        self.memo[key] = res
        return res

    def ev(self, e, u, v):
        k = e[0]
        if k == 'U': return u
        if k == 'V': return v
        if k in ('A1', 'A2'):
            t = self.ev(e[1], u, v)
            if t is None or t[0] != 'J': return None
            return t[1] if k == 'A1' else t[2]
        if k == 'OP':
            a = self.ev(e[1], u, v); b = self.ev(e[2], u, v)
            if a is None or b is None or not cf.gate_ok(a, b, u, v): return None
            return self.op(a, b)
        if k == 'J':
            a = self.ev(e[1], u, v); b = self.ev(e[2], u, v)
            if a is None or b is None: return None
            return ('J', a, b)
        raise ValueError(e)

    def evp(self, p, s):
        if isinstance(p, str): return s[p]
        return self.op(self.evp(p[0], s), self.evp(p[1], s))


src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk12234.py',
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns)
rules = [r for r in ns['rules'] if r[2] != 'B00l,B1l']


def dig_branch(Mo, u, v):
    """which digest branch holds for a decoded (u,v); None = NONE HOLDS (invariant broken)"""
    r = Mo.op(u, v)
    if r == J(u, v): return 'free'
    ok = []
    if (isJ(a1(v)) and isJ(a1(a1(v))) and u == a2(a1(v)) and r == a2(a1(a1(v)))
            and (a2(v) == J(r, u) or a2(v) == Mo.op(r, u))):
        ok.append('L')
    if (isJ(a2(v)) and u == a2(a1(v)) and u == a2(a2(v)) and r == a1(a2(v))
            and a2(v) == J(r, u)):
        ok.append('M')
    if (isJ(a2(v)) and u == a2(a2(v)) and r == a1(a2(v)) and a2(v) == J(r, u)):
        ok.append('N')
    return ','.join(ok) if ok else None


def check_invariants(Mo, pairs):
    bad_inv = []; bad_dig = []; bad_oc = []
    for (u, v) in pairs:
        r = Mo.op(u, v)
        if r == J(u, v): continue
        if not (size(r) + size(u) < size(v)): bad_inv.append((u, v, r))
        if dig_branch(Mo, u, v) is None: bad_dig.append((u, v, r))
        if u != oc(v): bad_oc.append((u, v, r))
    return bad_inv, bad_dig, bad_oc


def run_tests(seeds, N, NF):
    fails = []
    for ms, gn in ((9, 1), (5, 2)):
        n, f = sc.exhaustive(M5(), law, ms, gn, limit=25)
        fails += [(s, r, 'exh%d/%d' % (ms, gn), 0) for s, r in f]
        print('  exh%d/%d assignments=%d fails=%d' % (ms, gn, n, len(f)), flush=True)
    for sd in seeds:
        t, f = cf.deep_tests(M5(), law, N, 600, sd)
        fails += [(s, r, 'deep', sd) for s, r in f]
        t2, f2 = fz.fuzz(M5(), law, rules, NF, seed=sd + 100)
        fails += [(s, r, 'fuzz', sd) for s, r in f2]
        t3, f3 = fz.closure_fuzz(M5(), law, NF, seed=sd + 200)
        fails += [(s, r, 'closure', sd) for s, r in f3]
        t4, f4 = fz.critical_fuzz(M5(), law, NF, seed=sd + 300)
        fails += [(s, r, 'critical', sd) for s, r in f4]
        print('  seed %d: deep %d/%d fuzz %d/%d closure %d/%d critical %d/%d'
              % (sd, len(f), t, len(f2), t2, len(f3), t3, len(f4), t4), flush=True)
    return fails


if __name__ == '__main__':
    t0 = time.time()
    fails = run_tests([3, 4, 5], 3000, 12000)
    kinds = {}
    for s, r, kind, sd in fails:
        k = ('recursion' if r == 'recursion' else 'value') + ':' + kind
        kinds[k] = kinds.get(k, 0) + 1
    print('5-RULE run_tests fails', len(fails), kinds, round(time.time() - t0, 1), 's')
    def show(t):
        if t == 'recursion': return 'recursion'
        return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))
    for s, r, kind, sd in fails[:5]:
        print('  FAIL', kind, 'seed', sd, {k: show(v) for k, v in s.items()}, '->', show(r))
    for sd in (20260829, 777):
        t, f = cf.deep_tests(M5(), law, 20000, 900, sd)
        print('5-RULE deep_tests seed', sd, 'tested', t, 'fails', len(f))

    # ---- invariants, over every pair the model actually evaluates ----
    Mo = M5()
    random.seed(5)
    cf.deep_tests(Mo, law, 4000, 300, 31)
    for ms, gn in ((9, 1), (5, 2)):
        sc.exhaustive(Mo, law, ms, gn, limit=None)
    pairs = list(Mo.memo.keys())
    bi, bd, bo = check_invariants(Mo, pairs)
    print('pairs evaluated', len(pairs), ' INV violations', len(bi),
          ' DIG violations', len(bd), ' oc violations', len(bo))
    for (u, v, r) in (bi + bd + bo)[:3]:
        print('   u', size(u), 'v', size(v), 'r', size(r), 'branch', dig_branch(Mo, u, v),
              'oc ok', u == oc(v))
    # Dfree under the 5-rule model
    from itertools import product
    viol = 0
    pool = sc.terms_upto(9, 1) + sc.terms_upto(5, 2)
    for x, y, z in product(pool[:30], repeat=3):
        A = Mo.op(z, x); B = Mo.op(A, y); C = Mo.op(x, y)
        if Mo.op(B, C) != J(B, C): viol += 1
    print('Dfree violations on exhaustive small (5-rule):', viol)
