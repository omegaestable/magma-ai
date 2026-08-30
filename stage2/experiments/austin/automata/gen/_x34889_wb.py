"""Workbench for law 34889 (modelled dual L-form: x = z * ((x * (z * x)) * (y * y))).

Provides: law, DSL helpers, rule-set loaders, a validator wrapper and a failure classifier that
reports, for every failing instance, which rule fired at each product of the evaluation chain.
Import only; run with a subcommand for the canned reports.
"""
import sys, os, json, collections
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf
import revalidate as rv
import fuzz as fz
import leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 34889
cat = catalog()
orig = normalise(parse_eq(cat[EQ]))
DUALIZED = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
LAW = ('x', leangen.dual_pat(orig[1])) if DUALIZED else orig
A, B = LAW[1]

U = ('U',)
V = ('V',)


def A1(e):
    return ('A1', e)


def A2(e):
    return ('A2', e)


def OP(a, b):
    return ('OP', a, b)


def JJ(a, b):
    return ('J', a, b)


def TG(e):
    return ('TG', e)


def EQ_(a, b):
    return ('EQ', a, b)


def OPEQ(a, b):
    return ('OPEQ', a, b)


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


def sh(t, cap=40):
    return show(t) if size(t) < cap else '<%d>' % size(t)


def gen_rules(**kw):
    X = cf.Extractor(LAW)
    return X.rules(**kw)


def chk_rules(path=None):
    path = path or 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ
    src = open(path, encoding='utf-8').read().split('C = cf.Closed')[0]
    ns = {}
    exec(src, ns)
    return ns['rules']


def validate(rules, seeds=(3, 4, 5), N=3000, NF=12000):
    fails = rv.run_tests(LAW, rules, list(seeds), N, NF)
    real = [f for f in fails if f[1] != 'recursion']
    kinds = collections.Counter(f[2] for f in real)
    return real, kinds


# ---- failure classifier ----------------------------------------------------
# The pattern is  A = z ,  B = ((x*(z*x)) * (y*y)).
# Products, in evaluation order: W = z*x, P = x*W, Q = y*y, R = P*Q, FINAL = z*R.

CHAIN = [('W', ('z', 'x')), ('P', ('x', ('z', 'x'))), ('Q', ('y', 'y')),
         ('R', (('x', ('z', 'x')), ('y', 'y')))]


class Who(cf.Closed):
    """Closed that records which rule index produced each memoised pair."""

    def __init__(self, law, rules):
        super().__init__(law, rules)
        self.who = {}
        self.cuts = []
        self.trace_on = False

    def ev(self, e, u, v):
        if e[0] == 'OP' and self.trace_on:
            a = self.ev(e[1], u, v)
            b = self.ev(e[2], u, v)
            if a is None or b is None:
                return None
            if not cf.gate_ok(a, b, u, v):
                self.cuts.append((e, a, b, u, v))
                return None
            return self.op(a, b)
        return super().ev(e, u, v)

    def op(self, u, v):
        key = (u, v)
        if key in self.memo:
            return self.memo[key]
        if key in self.inprog:
            self.cycles += 1
            return ('J', u, v)
        self.inprog.add(key)
        res = None
        which = None
        for i, (conds, x, tag) in enumerate(self.rules):
            if self.check(conds, u, v):
                r = self.ev(x, u, v)
                if r is not None:
                    res = r
                    which = i
                    break
        self.inprog.discard(key)
        if res is None:
            res = ('J', u, v)
        self.memo[key] = res
        self.who[key] = which
        return res


def classify(rules, s):
    """returns (modevec, final_tag, result, T, u, v)"""
    T = Who(LAW, rules)
    vals = {}

    def evt(p):
        if isinstance(p, str):
            return s[p]
        a, b = evt(p[0]), evt(p[1])
        r = T.op(a, b)
        vals[p] = (a, b, r)
        return r

    u = s[A] if isinstance(A, str) else evt(A)
    v = evt(B)
    T.trace_on = True
    T.cuts = []
    if (u, v) in T.memo:
        del T.memo[(u, v)]
    r = T.op(u, v)
    T.trace_on = False

    def tag(key):
        w = T.who.get(key)
        return 'FREE' if w is None else 'R%d:%s' % (w + 1, rules[w][2])

    vec = tuple(tag((vals[p][0], vals[p][1])) if p in vals else '?' for _, p in CHAIN)
    return vec, tag((u, v)), r, T, u, v


def report(rules, seeds=(3, 4, 5), N=3000, NF=12000, top=12, maxinspect=250):
    real, kinds = validate(rules, seeds, N, NF)
    print('rules=%d  fails=%d  kinds=%s' % (len(rules), len(real), dict(kinds)))
    if not real:
        return real
    real.sort(key=lambda f: sum(size(t) for t in f[0].values()))
    buckets = collections.Counter()
    examples = {}
    for s, got, kind, sd in real[:maxinspect]:
        try:
            vec, fin, r, T, u, v = classify(rules, s)
        except RecursionError:
            buckets[(('recursion',), '')] += 1
            continue
        key = (vec, fin)
        buckets[key] += 1
        examples.setdefault(key, (s, got, kind, T.cuts[:2], u, v))
    for key, n in buckets.most_common(top):
        print('  %3d  chain W/P/Q/R = %s   FINAL=%s' % (n, key[0], key[1]))
        if key in examples:
            s, got, kind, cuts, u, v = examples[key]
            print('        e.g. [%s] %s' % (kind, {k: sh(t) for k, t in s.items()}))
            print('        u=%s  v=%s  got=%s' % (sh(u, 30), sh(v, 30), sh(got, 30) if got != 'recursion' else 'rec'))
            for e, a2, b2, u2, v2 in cuts:
                print('        GATE CUT %s  pair (%d,%d) vs (%d,%d)' % (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
    return real


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'chk'
    R = {'chk': chk_rules, 'gen': gen_rules}[which]()
    for i, r in enumerate(R):
        print('R%d %s' % (i + 1, cf.show_rule(r)))
    report(R)
