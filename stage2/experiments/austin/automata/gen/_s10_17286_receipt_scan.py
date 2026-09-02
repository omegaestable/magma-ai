"""Termination-aware control for scanning the reconstruction receipt at every rung.

This is a new locator design, not a repair of the refuted root-only locator.  While
walking ``T := a2(a2(T))`` it tests both literal candidates

    a1(T),  R(T) = J(a1(T), T).

The R(T) call is admitted only when the receipt remains below the original payload
``P`` and its operation pair is below the current mutual recursion measure.  The
first gate preserves the existing locator result bound; the second is what Lean needs
to call ``op(R(T), w)`` even though the receipt is larger than traversal term ``T``.
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
                # Strictly below the ambient op/opTail call.  The other recursive
                # check, op(u,a1(T)), is smaller because a1(T) is a proper subterm.
                if (sz(r) < sz(P)
                    and sz(r) + sz(w) < sz(u) + 2 * sz(w) + sz(T) + 2
                    and self.op(u, a1(T)) == a2(T)
                    and self.op(r, w) == P):
                    return r, 'W'
            if not (tg(T) == 2 and tg(a2(T)) == 2):
                return J(u, u), 'X'
            T = a2(a2(T))


def deep_receipt_control():
    m = Mod()
    a, k, h, q, r = (g(i) for i in range(5))
    s = J(a, k)
    t = J(k, s)
    x = J(k, t)
    w = J(h, J(h, J(t, h)))
    p = J(w, J(w, t))
    z = J(q, J(q, J(p, q)))
    y = J(r, a)
    p0 = m.op(x, z)
    q0 = m.op(z, p0)
    b = m.op(z, q0)
    return m.op(m.op(y, x), b) == x, m.fired


if __name__ == '__main__':
    ok, fired = deep_receipt_control()
    print('deep R(T) control:', ok, dict(sorted(fired.items())))
    mir.Mod = Mod
    mir.stack()
