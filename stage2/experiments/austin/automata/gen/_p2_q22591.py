"""P2 experiment: the existential decoder for 22591 as ENC-INV / DEC-STRUCT.

Law 22591:  x = (y*(y*x)) * ((x*x)*z)
  P = op(y,x)   u = op(y,P)   S = op(x,x)   v = op(S,z)   top = op(u,v)

Baseline (gen/q22591b.py) has rules Ra, Rb only.  MODE is a bitmask of the extra rules:
  bit 0 (1)  Rc0  R4's op-guard form (kept only to document the gate cut; never fires)
  bit 1 (2)  Rc   P dec, S dec, v free      x = invsq(a1 v)
  bit 2 (4)  Rd   P dec, S dec, v dec       x = J v (J v (invsq v))
  bit 3 (8)  Re   P free, S dec, v dec      x = a2 (a2 u), structural v-check
so MODE 14 = Rc+Rd+Re, MODE 0 = baseline.
usage:  python gen/_p2_q22591.py <MODE> [xmax ymax zmax]
"""
import sys, os, time, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import qmod
qmod.UNARY = []
from qmod import sz, show, terms_upto, pvars

LAW = ('x', (('y', ('y', 'x')), (('x', 'x'), 'z')))
MODE = int(sys.argv[1]) if len(sys.argv) > 1 else 0


def J(a, b):
    return ('J', a, b)


def msr(a, b):
    sa, sb = sz(a), sz(b)
    return max(sa, sb) ** 2 + sa + sb


class Mod:
    def __init__(self, mode=None):
        self.memo = {}
        self.mode = MODE if mode is None else mode
        self.fired = {}

    def op(self, u, v):
        key = (u, v)
        r = self.memo.get(key)
        if r is not None:
            return r
        self.memo[key] = J(u, v)          # cycle guard
        r = self._op(u, v)
        self.memo[key] = r
        return r

    def g(self, a, b, m):
        """gated nested call: the recursion measure must strictly decrease."""
        return self.op(a, b) if msr(a, b) < m else J(a, b)

    def hit(self, tag, r):
        self.fired[tag] = self.fired.get(tag, 0) + 1
        return r

    def _op(self, u, v):
        m = msr(u, v)
        if u[0] == 'J' and v[0] == 'J':
            a, c = u[1], u[2]
            # ---- Ra : P free, v free.  u = (a*(a*b)); square checked against a1 v -------------
            if c[0] == 'J' and c[1] == a and self.g(c[2], c[2], m) == v[1]:
                return self.hit('Ra', c[2])
            # ---- Rb : S free, v free.  a1 v = (b*b); decoder checked on u --------------------
            if v[1][0] == 'J' and v[1][1] == v[1][2] and self.g(a, v[1][1], m) == c:
                return self.hit('Rb', v[1][1])
            # ---- Rc0 : R4's op-guard form.  GATE-CUT: msr(a1 u, invsq(a1 v)) > msr(u,v) ------
            if self.mode & 1:
                T = self.g(v[1], v[1], m)
                x = J(T, J(T, v[1]))
                if self.g(a, x, m) == c:
                    return self.hit('Rc0', x)
            # ---- Rc : P dec, S dec, v free.  ENC-INV x = invsq(a1 v); DEC-STRUCT on a1 u ----
            #      guard op(a1 u,x)==a2 u unfolded through Ra:  a1 u = J p (J p b'),
            #      b' = a2 u,  op(b',b') = a1 x = op(s,s).
            if self.mode & 2:
                s = v[1]
                if (a[0] == 'J' and a[2][0] == 'J' and a[2][1] == a[1] and a[2][2] == c
                        and self.g(c, c, m) == self.g(s, s, m)):
                    T = self.g(s, s, m)
                    return self.hit('Rc', J(T, J(T, s)))
        # ---- Rd : P dec, S dec, v dec.  v is itself the payload of op(S,z);  the u-side head
        #      constraint a1 x = op(P,P) forces S = invsq(v), hence x = invsq(S); op(S,S) = v is
        #      known from the guard, so x = J v (J v (invsq v)) -- ONE op call, on v.
        #      NOTE: v is a decoded payload, so it need NOT be a J-node; this rule must sit
        #      OUTSIDE the tg v = 2 test that Ra/Rb/Rc share.
        if (self.mode & 4) and u[0] == 'J':
            a, c = u[1], u[2]
            if (a[0] == 'J' and a[2][0] == 'J' and a[2][1] == a[1] and a[2][2] == c
                    and self.g(c, c, m) == v):
                T = self.g(v, v, m)
                return self.hit('Rd', J(v, J(v, J(T, J(T, v)))))
        # ---- Re : P free, S dec, v dec.  x = a2 (a2 u) is readable from u = J a (J a x); the
        #      v-side check is structural -- op(x,x) must be a DECODER of v, i.e. J r (J r v)
        #      (the z-side condition a1 z = op(v,v) is invisible at this pair and not needed).
        #      Like Rd this fires with v a decoded payload, so it sits outside tg v = 2.
        #      Rd and Re are mutually exclusive: Rd wants a2 u = payload of the decoder a1 u,
        #      Re wants a2 u = J (a1 u) x, and both together violate the occurs check.
        if (self.mode & 8) and u[0] == 'J':
            a, c = u[1], u[2]
            if c[0] == 'J' and c[1] == a:
                b = c[2]
                S = self.g(b, b, m)
                if S[0] == 'J' and S[2][0] == 'J' and S[2][1] == S[1] and S[2][2] == v:
                    return self.hit('Re', b)
        return J(u, v)

    def ev(self, p, s):
        if isinstance(p, str):
            return s[p]
        return self.op(self.ev(p[0], s), self.ev(p[1], s))


def M():
    return Mod()


def sweep(xmax, ymax, zmax, limit=12, mode=None):
    px = terms_upto(xmax, 1)
    py = terms_upto(ymax, 1)
    pz = terms_upto(zmax, 1)
    Mo = Mod(mode)
    n = 0
    fails = []
    for x in px:
        for y in py:
            for z in pz:
                n += 1
                s = {'x': x, 'y': y, 'z': z}
                try:
                    r = Mo.ev(LAW[1], s)
                except RecursionError:
                    fails.append((s, 'recursion'))
                    if len(fails) >= limit:
                        return n, fails, Mo
                    continue
                if r != x:
                    fails.append((dict(s), r))
                    if len(fails) >= limit:
                        return n, fails, Mo
    return n, fails, Mo


if __name__ == '__main__':
    xm = int(sys.argv[2]) if len(sys.argv) > 2 else 9
    ym = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    zm = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    t0 = time.time()
    n, f, Mo = sweep(xm, ym, zm)
    print('MODE %d  sweep x<=%d y<=%d z<=%d : n=%d fails=%d  fired=%s  (%.1fs)'
          % (MODE, xm, ym, zm, n, len(f), Mo.fired, time.time() - t0))
    seen = set()
    for s, r in f[:12]:
        k = tuple(sorted((a, show(b)) for a, b in s.items()))
        if k in seen:
            continue
        seen.add(k)
        print('  FAIL ' + '  '.join('%s=%s' % (a, show(b)) for a, b in sorted(s.items())),
              '->', show(r) if r != 'recursion' else r)
