"""Driver: validate a hand model of 12294 and explain its failures."""
import sys, time, json, importlib
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
import closedform as cf, smallcheck as sc, fuzz as fz
from freemodel import normalise, catalog, size
from laws import parse_eq

import _x12294_model as MM

EQ = 12294
law = normalise(parse_eq(catalog()[EQ]))
A, B = law[1]


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


def chain(C, s):
    """values of every product of the pattern, bottom up"""
    out = []

    def ev(p):
        if isinstance(p, str):
            return s[p]
        l = ev(p[0]); r = ev(p[1])
        res = C.op(l, r)
        out.append((p, l, r, res, res == ('J', l, r)))
        return res
    top = C.op(ev(A), ev(B))
    return out, top


def validate(rules, name='model', deep=3000, seeds=(3, 4, 5), fuzzN=12000, verbose=3, exh=(9, 1)):
    fails = []
    C = MM.Model(rules)
    t0 = time.time()
    n, f = sc.exhaustive(C, law, exh[0], exh[1], limit=25)
    fails += [(s, r, 'exh%d/%d' % exh, 0) for s, r in f]
    C = MM.Model(rules)
    n2, f2 = sc.exhaustive(C, law, 5, 2, limit=25)
    fails += [(s, r, 'exh5/2', 0) for s, r in f2]
    for sd in seeds:
        C = MM.Model(rules)
        t, ff = cf.deep_tests(C, law, deep, 300, sd)
        fails += [(s, r, 'deep', sd) for s, r in ff]
        C = MM.Model(rules)
        t3, f3 = fz.closure_fuzz(C, law, fuzzN, seed=sd + 200)
        fails += [(s, r, 'closure', sd) for s, r in f3]
        C = MM.Model(rules)
        t4, f4 = fz.critical_fuzz(C, law, fuzzN, seed=sd + 300)
        fails += [(s, r, 'critical', sd) for s, r in f4]
    kinds = {}
    for s, r, kind, sd in fails:
        k = ('rec' if r == 'recursion' else 'val') + ':' + kind
        kinds[k] = kinds.get(k, 0) + 1
    val = [f for f in fails if f[1] != 'recursion']
    print('%-10s rules=%d fails=%d val=%d %s  %.1fs' % (name, len(rules), len(fails), len(val), json.dumps(kinds), time.time() - t0), flush=True)
    val.sort(key=lambda f: sum(size(v) for v in f[0].values()))
    for s, r, kind, sd in val[:verbose]:
        print('  FAIL[%s/%s] %s' % (kind, sd, {k: show(v) for k, v in s.items()}), flush=True)
        C = MM.Model(rules)
        ch, top = chain(C, s)
        for p, l, rr, res, free in ch:
            print('     %-34s op(%s , %s) = %s  %s' % (str(p)[:34], show(l), show(rr), show(res), 'free' if free else 'DECODE'), flush=True)
        print('     TOP = %s   expected %s' % (show(top), show(s['x'])), flush=True)
    return val


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'RULES_V1'
    validate(getattr(MM, which), which)
