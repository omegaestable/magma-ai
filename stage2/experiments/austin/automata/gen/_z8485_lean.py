"""_z8485_lean.py -- INDEPENDENT transcription of the Lean `op` in gen/f8485r.lean.

Written from the Lean source alone (not from closedform.py), so it is a second implementation
of the same object and a disagreement with `closedform.Closed` is itself a finding.

Terms: ('g', i) | ('J', a, b)   -- same rep as freemodel.
"""
import sys, os
sys.setrecursionlimit(100000)

def sz(t, _m={}):
    r = _m.get(id(t))
    s = _m.get(t)
    if s is not None: return s
    s = 1 if t[0] == 'g' else sz(t[1]) + sz(t[2]) + 1
    _m[t] = s
    return s

def tg(t): return 1 if t[0] == 'g' else 2
def a1(t): return t[1] if t[0] == 'J' else t
def a2(t): return t[2] if t[0] == 'J' else t

def msr(u, v):
    m = sz(u) if sz(u) >= sz(v) else sz(v)
    return m * m + sz(u) + sz(v)

def P1(u, v):
    return (tg(v) == 2 and tg(a2(v)) == 2 and tg(a1(a2(v))) == 2
            and tg(a1(a1(a2(v)))) == 2
            and a1(v) == a2(a1(a1(a2(v))))
            and u == a2(a1(a2(v)))
            and u == a2(a2(v)))

def P2(u, v):
    return tg(v) == 2 and tg(a1(v)) == 2 and tg(a2(a1(v))) == 2

def P3(u, v):
    return tg(v) == 2 and tg(u) == 2 and tg(a2(u)) == 2 and tg(a2(a2(u))) == 2

def P4(u, v):
    return (tg(v) == 2 and tg(u) == 2 and tg(a2(u)) == 2 and tg(a2(a2(u))) == 2
            and tg(a1(a2(a2(u)))) == 2)


class LeanOp:
    """Faithful evaluator of the Lean definition.  `fired` records which branch fired per (u,v)."""

    def __init__(self):
        self.memo = {}
        self.fired = {}          # (u,v) -> 0 (free) | 1..4
        self.counts = [0, 0, 0, 0, 0]

    def _chain(self, z, u, v):
        """the three gated steps  op(op(op(z, a1 v), u), u); returns (ok, value)"""
        M = msr(u, v)
        b = a1(v)
        if not msr(z, b) < M: return (False, None)
        p = self.op(z, b)
        if not msr(p, u) < M: return (False, None)
        p = self.op(p, u)
        if not msr(p, u) < M: return (False, None)
        p = self.op(p, u)
        return (True, p)

    def op(self, u, v):
        key = (u, v)
        r = self.memo.get(key)
        if r is not None: return r
        res = None; br = 0
        if P1(u, v):
            res = a1(v); br = 1
        else:
            if P2(u, v):
                ok, p3 = self._chain(a2(a2(a1(v))), u, v)
                if ok and a2(v) == p3:
                    res = a1(v); br = 2
            if res is None and P3(u, v):
                ok, p6 = self._chain(a1(a2(a2(u))), u, v)
                if ok and a2(v) == p6:
                    res = a1(v); br = 3
            if res is None and P4(u, v):
                ok, p9 = self._chain(a1(a1(a2(a2(u)))), u, v)
                if ok and a2(v) == p9:
                    res = a1(v); br = 4
        if res is None:
            res = ('J', u, v); br = 0
        self.memo[key] = res
        self.fired[key] = br
        self.counts[br] += 1
        return res

    # the law:  x = y * (x * (((z*x)*y)*y))
    def law_lhs(self, x, y, z):
        P = self.op(z, x)
        Q = self.op(P, y)
        R = self.op(Q, y)
        S = self.op(x, R)
        return self.op(y, S)

    def cells(self, x, y, z):
        P = self.op(z, x); Q = self.op(P, y); R = self.op(Q, y)
        S = self.op(x, R); T = self.op(y, S)
        return (self.fired[(z, x)], self.fired[(P, y)], self.fired[(Q, y)],
                self.fired[(x, R)], self.fired[(y, S)]), T


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))
