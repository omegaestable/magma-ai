"""Validate the model that gen/rec12234.lean's `op` ACTUALLY implements (the `oc` variant), to the
full standard of DEEP_SESSION_6 testing protocol item 1.

gen/chk12234.py's DSL rules use `u.1.2` where the Lean uses `oc u`; they are different functions, so the
DSL validation does not cover the Lean file.  This mirrors the Lean `op` exactly (checked line by line
against rec12234.lean) and runs smallcheck.exhaustive + deep + fuzz + closure_fuzz + critical_fuzz.
"""
import sys, os, time, json
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
sys.setrecursionlimit(20000)
import closedform as cf
import fuzz as fz
import smallcheck as sc
import leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 12234
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
assert not dualized


def J(a, b): return ('J', a, b)
def isJ(t): return t[0] == 'J'
def a1(t): return t[1] if isJ(t) else t
def a2(t): return t[2] if isJ(t) else t
def oc(t): return a2(a2(t)) if size(a1(t)) < size(a2(a2(t))) else a2(a1(t))
def msr(a, b):
    m = max(size(a), size(b)); return m * m + size(a) + size(b)


class LeanModel:
    """exact mirror of rec12234.lean's `op`"""
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
        elif (isJ(v) and isJ(a1(v)) and u == a2(a1(v)) and isJ(u)
                and msr(oc(u), u) < msr(u, v) and msr(oc(oc(u)), oc(u)) < msr(u, v)
                and a2(v) == call(oc(u), u) and a1(a1(v)) == call(oc(oc(u)), oc(u))):
            k, res = 4, oc(u)
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
        """the DSL expression evaluator (fuzz.instances needs it); same as cf.Closed.ev but on this op"""
        k = e[0]
        if k == 'U': return u
        if k == 'V': return v
        if k == 'A1':
            t = self.ev(e[1], u, v)
            if t is None or t[0] != 'J': return None
            return t[1]
        if k == 'A2':
            t = self.ev(e[1], u, v)
            if t is None or t[0] != 'J': return None
            return t[2]
        if k == 'OP':
            a = self.ev(e[1], u, v); b = self.ev(e[2], u, v)
            if a is None or b is None: return None
            if not cf.gate_ok(a, b, u, v): return None
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
ns = {}; exec(src, ns); rules = ns['rules']


def run_tests(seeds, N, NF):
    fails = []
    for ms, gn in ((9, 1), (5, 2)):
        n, f = sc.exhaustive(LeanModel(), law, ms, gn, limit=25)
        fails += [(s, r, 'exh%d/%d' % (ms, gn), 0) for s, r in f]
        print('  exh%d/%d assignments=%d fails=%d' % (ms, gn, n, len(f)), flush=True)
    for sd in seeds:
        t, f = cf.deep_tests(LeanModel(), law, N, 600, sd)
        fails += [(s, r, 'deep', sd) for s, r in f]
        t2, f2 = fz.fuzz(LeanModel(), law, rules, NF, seed=sd + 100)
        fails += [(s, r, 'fuzz', sd) for s, r in f2]
        t3, f3 = fz.closure_fuzz(LeanModel(), law, NF, seed=sd + 200)
        fails += [(s, r, 'closure', sd) for s, r in f3]
        t4, f4 = fz.critical_fuzz(LeanModel(), law, NF, seed=sd + 300)
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
    print('run_tests fails', len(fails), kinds, round(time.time() - t0, 1), 's')
    def show(t):
        if t == 'recursion': return 'recursion'
        return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))
    for s, r, kind, sd in fails[:5]:
        print('  FAIL', kind, 'seed', sd, {k: show(v) for k, v in s.items()}, '->', show(r))
    for sd in (20260829, 777):
        t, f = cf.deep_tests(LeanModel(), law, 20000, 900, sd)
        print('deep_tests seed', sd, 'tested', t, 'fails', len(f))
