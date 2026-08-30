# -*- coding: utf-8 -*-
"""10218 forcing suite v3 -- now ALSO fires R4 and R6, which force2 never did.

Why force2 missed them: R4 differs from R3/R2 only in that `a2 v = op (a2 (a1 u)) u` is DECODED,
and R6 differs from R2 only in that `a1 v = op (a2 (a1 u)) u` is DECODED.  Build those free and the
earlier rule fires instead.  So the inner product of each rule's OWN guard must itself be an encoding
(one level deeper than force2 went).

enc(P,u,Q) = J (J P u) (J (J Q P) u),  op u (enc P u Q) = P   [R1]

usage: _x10218_force3.py [rules-source]     default gen/rep10218/chk10218.py
"""
import sys, os, itertools, collections, importlib.util
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
law = normalise(parse_eq(catalog()[10218]))

def load(path):
    spec = importlib.util.spec_from_file_location('chk', path)
    src = open(spec.origin, encoding='utf-8').read().split('C = cf.Closed')[0]
    ns = {'__name__': 'chk'}; exec(compile(src, spec.origin, 'exec'), ns); return ns['rules']

RULES = load(sys.argv[1]) if len(sys.argv) > 1 else load(os.path.join(HERE, 'gen', 'rep10218', 'chk10218.py'))
def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def a1(t): return t[1] if t[0] == 'J' else t
def a2(t): return t[2] if t[0] == 'J' else t
def show(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))
def enc(P, u, Q): return J(J(P, u), J(J(Q, P), u))

BASE = [g(0), g(1), g(2), J(g(0), g(1)), J(g(1), g(2))]
GEN = [g(0), g(1), g(2)]                      # generators only, where the recipe needs one

def cases(op):
    """yield (tag, x, y, z); `op` is the model's operation (needed to build decoded products)"""
    out = []
    def at_t1(u, v, z): out.append((u, v, z))          # (u,v) = (x,y)
    def at_t2(u, v):    out.append((v, BASE[0], u))    # (u,v) = (z,x)
    # ---- R2: P := enc(Pp,B,Q) so op B P = Pp decodes
    for Pp, B, Q, u in itertools.product(BASE[:4], BASE[:3], BASE[:3], BASE[:3]):
        P = enc(Pp, B, Q); v = J(J(P, u), J(Pp, u))
        yield ('R2', u, v, Q); yield ('R2', v, BASE[0], u)
    # ---- R3: u := enc(Wt, J A2 P, Q) so op (a2 (a1 u)) u = Wt decodes
    for A2, P, Wt, Q in itertools.product(BASE[:3], BASE[:4], BASE[:3], BASE[:3]):
        m = J(A2, P); u = enc(Wt, m, Q); v = J(J(P, u), Wt)
        yield ('R3', u, v, Q); yield ('R3', v, BASE[0], u)
    # ---- R4 (NEW): m and W generators, P := enc(m,B,Q2), u := enc(W,m,Q), v := J (J P u) W
    for m, B, Q2, W, Q in itertools.product(GEN, BASE[:3], BASE[:3], GEN, BASE[:3]):
        P = enc(m, B, Q2); u = enc(W, m, Q); v = J(J(P, u), W)
        yield ('R4', u, v, Q); yield ('R4', v, BASE[0], u)
    # ---- R5: u := enc(D,P,Q) so op P u = D decodes
    for P, Q, D in itertools.product(BASE[:4], BASE[:3], BASE[:3]):
        uu = enc(D, P, Q); v = J(op(P, uu), J(J(Q, P), uu))
        yield ('R5', uu, v, Q); yield ('R5', v, BASE[0], uu)
    # ---- R6 (NEW): Rp, P' generators; R := enc(Rp,Bq,Qq), u := enc(P',R,Q'), v := J P' (J Rp u)
    for Rp, Bq, Qq, Pp2, Qp in itertools.product(GEN, BASE[:3], BASE[:3], GEN, BASE[:3]):
        R = enc(Rp, Bq, Qq); u = enc(Pp2, R, Qp); v = J(Pp2, J(Rp, u))
        yield ('R6', u, v, Qq); yield ('R6', v, BASE[0], u)

def evaluate(rules, verbose=False):
    WH = {}
    class W(cf.Closed):
        def op(self, u, v):
            k = (u, v)
            if k in self.memo: return self.memo[k]
            r = super().op(u, v)
            if r != ('J', u, v) and k not in WH:
                for i, rl in enumerate(rules):
                    s = cf.Closed(law, rules); s.memo = self.memo
                    if s.check(rl[0], u, v): WH[k] = i; break
                else: WH[k] = -1
            return r
    C = W(law, rules); op = C.op
    tab = collections.Counter(); bad = []; n = 0
    for tag, x, y, z in cases(op):
        try:
            t1 = op(x, y); t2 = op(z, x); t3 = op(t2, y); t4 = op(t1, t3); t5 = op(y, t4)
        except RecursionError:
            continue
        n += 1
        m = tuple('F' if val == J(*a) else 'R%d' % (WH.get(a, -1) + 1)
                  for a, val in (((x, y), t1), ((z, x), t2), ((t2, y), t3),
                                 ((t1, t3), t4), ((y, t4), t5)))
        tab[(tag,) + m] += 1
        if t5 != x: bad.append((tag, x, y, z, m, t5))
    if verbose:
        print('  %-6s %-32s %s' % ('tag', '(t1..t5)', 'count'))
        for k, c in sorted(tab.items(), key=lambda kv: (kv[0][0], -kv[1])):
            print('  %-6s %-32s %d' % (k[0], str(k[1:]), c))
        fired = {k[0]: set() for k in tab}
        for k in tab:
            for e in k[1:]:
                if e != 'F': fired[k[0]].add(e)
        print('  RULES ACTUALLY FIRED per tag:', {t: sorted(s) for t, s in sorted(fired.items())})
    return n, bad

if __name__ == '__main__':
    n, bad = evaluate(RULES, verbose=True)
    print('\nforce3: %d assignments, %d law failures' % (n, len(bad)))
    for tag, x, y, z, m, r in bad[:3]:
        print('  [%s] %s' % (tag, str(m)))
        print('    x =', show(x)[:220]); print('    y =', show(y)[:220]); print('    z =', show(z)[:220])
