"""trace 22591 instances under several modes.  usage: python gen/_p2_tr.py <modes csv> [case]"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
_ARGV = list(sys.argv)
sys.argv = [sys.argv[0], '0']
import _p2_q22591 as Q
from qmod import sz

J = Q.J
g = lambda n: ('g', n)


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


def sh(t, k=52):
    s = show(t)
    return s if len(s) <= k else s[:k] + '..'


def invsq(M, s):
    T = M.op(s, s)
    return J(T, J(T, s))


class Tr(Q.Mod):
    def __init__(self, mode):
        Q.Mod.__init__(self, mode)
        self.log = []

    def hit(self, tag, r):
        self.log.append(tag)
        return Q.Mod.hit(self, tag, r)

    def _op(self, u, v):
        n0 = len(self.log)
        r = Q.Mod._op(self, u, v)
        tag = self.log[n0] if len(self.log) > n0 else 'free'
        self.last = tag
        return r


def trace(mode, x, y, z, lab=''):
    M = Tr(mode)
    steps = []
    P = M.op(y, x); steps.append(('P=op(y,x)', P, M.last))
    u = M.op(y, P); steps.append(('u=op(y,P)', u, M.last))
    S = M.op(x, x); steps.append(('S=op(x,x)', S, M.last))
    v = M.op(S, z); steps.append(('v=op(S,z)', v, M.last))
    top = M.op(u, v); steps.append(('top', top, M.last))
    print('  mode %-3d %s   %s' % (mode, lab, 'OK' if top == x else '**FAIL**'))
    for nm, val, tag in steps:
        print('     %-10s = %-54s [%s]' % (nm, sh(val), tag))


if __name__ == '__main__':
    modes = [int(t) for t in _ARGV[1].split(',')] if len(_ARGV) > 1 else [0, 6, 14]
    M0 = Q.Mod(0)
    for w in [g(0), J(g(0), g(1))]:
        Iw = invsq(M0, w); IIw = invsq(M0, Iw); IIIw = invsq(M0, IIw)
        print('\n=== w = %s ===' % show(w))
        print('TTT-3 : x=I^3 w, y = J g3 (J g3 I^2 w), z = J (op(Iw,Iw)) g7')
        for m in modes:
            trace(m, IIIw, J(g(3), J(g(3), IIw)), J(M0.op(Iw, Iw), g(7)), 'TTT-3')
        print('FTT   : x=I^2 w, y = g1, z = J (op(w,w)) g7')
        for m in modes:
            trace(m, IIw, g(1), J(M0.op(w, w), g(7)), 'FTT')
