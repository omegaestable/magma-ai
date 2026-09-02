"""Falsification harness for the unbounded-receipt locator.

This is a new termination design after the ambient-bound counterfamily.  Give
``op(u,v)`` measure ``sz(v)`` and ``find(u,T,w,P)`` measure ``sz(w)+sz(T)``.
Then every call made by ``find`` to ``op`` strictly decreases, including
``op(J(a1(T),T),w)``, without requiring the receipt to be below ``P``.

The semantic branch therefore scans the literal list

    [a1(T), J(a1(T),T)] ++ L(a2(a2(T)))

with no arithmetic admission gate.  This file is only a falsifier; validity
still requires the chain-specific F1/F2 proofs and locator completeness.
"""
import _x17286_leanmirror as mir

g, J, tg, a1, a2, sz = mir.g, mir.J, mir.tg, mir.a1, mir.a2, mir.sz


class Mod(mir.Mod):
    def find(self, u, T, w, P):
        while True:
            if (tg(T) == 2 and tg(a1(T)) == 2 and tg(a2(a1(T))) == 2
                and a1(a1(T)) == a1(a2(a1(T)))
                and self.op(u, a1(a1(T))) == a2(a2(a1(T)))
                and self.op(a1(T), w) == P):
                return a1(T), 'V'
            if tg(T) == 2:
                r = J(a1(T), T)
                if (self.op(u, a1(T)) == a2(T)
                    and self.op(r, w) == P):
                    return r, 'W'
            if not (tg(T) == 2 and tg(a2(T)) == 2):
                return J(u, u), 'X'
            T = a2(a2(T))


def ambient_counterfamily():
    C = lambda w, p: J(w, J(w, p))
    s, a, c, q, b = (g(i) for i in range(5))
    t0 = J(J(J(J(g(5), g(6)), g(7)), g(8)), g(9))
    t = J(t0, g(10))
    A = J(a, s)
    k = C(t, J(s, t))
    x = C(k, s)
    R = a2(x)
    h = C(c, J(s, c))
    w = C(h, s)
    P = C(w, R)
    z = C(q, J(P, q))
    y = J(b, A)
    m = Mod()
    Q = m.op(z, m.op(x, z))
    B = m.op(z, Q)
    return m.op(m.op(y, x), B) == x, m.fired


def top_converse_probe():
    """Separate generic coded-left completeness from law-specific provenance."""
    C = lambda w, p: J(w, J(w, p))
    pool = mir.terms(5, 2)
    m = Mod()
    generic = law_cells = generic_bad = law_bad = 0
    witnesses = []
    for A in pool:
        for k in pool:
            x = C(k, m.op(A, k))       # cds(A,x) by construction
            for z in pool:
                P = m.op(x, z)
                generic += 1
                if m.op(A, C(z, P)) != x:
                    generic_bad += 1
                    if len(witnesses) < 3:
                        witnesses.append((A, x, z, P))
                for junk in (g(20), J(g(20), g(21))):
                    y = J(junk, A)
                    if m.op(y, x) != A:
                        continue
                    law_cells += 1
                    Q = m.op(z, P)
                    B = m.op(z, Q)
                    if m.op(A, B) != x:
                        law_bad += 1
    print('top converse:', generic, 'generic bad', generic_bad,
          'law-provenance cells', law_cells, 'law bad', law_bad)
    for A, x, z, P in witnesses:
        print('  generic witness sizes', tuple(map(sz, (A, x, z, P))))


if __name__ == '__main__':
    ok, fired = ambient_counterfamily()
    print('ambient-bound counterfamily repaired:', ok, dict(sorted(fired.items())))
    top_converse_probe()
    mir.Mod = Mod
    mir.stack()
