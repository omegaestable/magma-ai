"""nfablate.py -- rule ablation for the 12073 normal-form model: which rules are load-bearing?

Builds `op` from a switchable rule set, counts firings, and re-runs the exhaustive carrier check
with each rule individually disabled.
"""
import sys, os, time, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import nfcore as nf
from nfcore import S, show
from freemodel import pvars

def E(t): return ('E', t)
def J(a, b): return ('J', a, b)

def make(on):
    memo = {}
    fired = {k: 0 for k in 'R1 R2 R5 R3 R7 R8 R6 R4'.split()}
    def op(u, v):
        k = (u, v)
        r = memo.get(k)
        if r is not None: return r
        r = None; tag = None
        if u == v and on.get('R1', True): r, tag = S, 'R1'
        elif v == S and on.get('R2', True): r, tag = E(u), 'R2'
        elif on.get('R5', True) and u != S and v[0] == 'E' and v[1][0] == 'E' and v[1][1][0] == 'E' and v[1][1][1] == u:
            r, tag = S, 'R5'
        if r is None and on.get('R3', True) and v[0] == 'E' and v[1][0] == 'J':
            p, q = v[1][1], v[1][2]
            if q != S and op(u, q) == p and op(p, q) == J(p, q): r, tag = q, 'R3'
        if r is None and on.get('R7', True) and v[0] == 'E' and v[1] != S and u[0] == 'E' and u[1][0] == 'J' \
                and u[1][2] == v[1] and op(S, v[1]) == u[1][1]:
            r, tag = u, 'R7'
        if r is None and on.get('R8', True) and v[0] == 'E' and v[1] == u and u[0] == 'E' and u[1][0] == 'J' \
                and u[1][2] != S and op(S, u[1][2]) == u[1][1]:
            r, tag = E(u[1][2]), 'R8'
        if r is None and on.get('R6', True) and v[0] == 'E' and v[1] != S and op(u, v[1]) == S and op(S, v[1]) == J(S, v[1]):
            r, tag = E(J(S, v[1])), 'R6'
        if r is None: r, tag = J(u, v), 'R4'
        fired[tag] += 1
        memo[k] = r
        return r
    return op, fired

def check(op, law, sizes=((6, 1), (5, 2), (4, 3))):
    tot = 0
    for ms, g in sizes:
        pool = nf.carrier_upto(ms, g)
        n, f = nf.exhaustive(op, law, pool, limit=2)
        tot += len(f)
        if f: return len(f), f[0], (ms, g)
    return 0, None, None

if __name__ == '__main__':
    law = nf.get_law(12073)
    op, fired = make({})
    t0 = time.time()
    n, f, where = check(op, law)
    print('full rule set: fails', n, 'in', round(time.time() - t0, 1), 's')
    print('firings:', fired)
    for rule in ['R5', 'R3', 'R7', 'R8', 'R6']:
        op2, fired2 = make({rule: False})
        n2, f2, w2 = check(op2, law)
        msg = 'ok (rule is DEAD)' if n2 == 0 else 'FAILS at %s: %s -> %s' % (
            w2, {k: show(v) for k, v in f2[0].items()}, show(f2[1]) if f2[1] != 'recursion' else 'recursion')
        print('without %s: %s' % (rule, msg), flush=True)
