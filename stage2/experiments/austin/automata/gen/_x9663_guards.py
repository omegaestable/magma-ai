"""Sweep A-slot guards for the 9663 free-term decoder carrier."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _idc_lib import G, J, sz, show, terms, check

LAW = ('y', (('z', 'y'), ('x', ('x', 'y'))))

def build(guard):
    memo = {}
    def op(u, v):
        k = (u, v)
        r = memo.get(k)
        if r is None:
            r = _op(u, v); memo[k] = r
        return r
    def _op(u, v):
        if v[0] == 'J':
            A, Q = v[1], v[2]
            if Q[0] == 'J':
                x, P = Q[1], Q[2]
                if op(x, u) == P and guard(op, A, u):
                    return x
        return J(u, v)
    return op

def g_free(op, A, u):
    return A[0] == 'J' and A[2] == u

def g_pay(op, A, u):
    if g_free(op, A, u): return True
    return u[0] == 'J' and u[2][0] == 'J' and A == u[2][1]

def g_pay2(op, A, u):
    """payload slot, and u really is a code: op(x',z)=P' for z read off u[1] free-ly."""
    if g_free(op, A, u): return True
    if u[0] == 'J' and u[2][0] == 'J' and A == u[2][1]:
        xp, Pp = u[2][1], u[2][2]
        if u[1][0] == 'J' and op(xp, u[1][2]) == Pp: return True
        if u[1][0] != 'J': return True          # A-slot of u itself decoded: accept
    return False

def g_wild(op, A, u):
    return True

def g_freeprod(op, A, u):
    """A is genuinely op(z,u) with the product free."""
    return A[0] == 'J' and A[2] == u and op(A[1], u) == A

GUARDS = {'free': g_free, 'pay': g_pay, 'pay2': g_pay2, 'wild': g_wild, 'freeprod': g_freeprod}

if __name__ == '__main__':
    ms = int(sys.argv[1]) if len(sys.argv) > 1 else 11
    gens = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    pool = terms(ms, gens)
    for name, gd in GUARDS.items():
        op = build(gd)
        n, f = check(op, LAW, pool, limit=3)
        print('%-9s pool=%d tested=%d FAILS=%d' % (name, len(pool), n, len(f)), flush=True)
        for s, r in f[:2]:
            print('    x=%s y=%s z=%s -> %s' % (show(s['x']), show(s['y']), show(s['z']),
                                                show(r) if r != 'RECURSION' else r), flush=True)
