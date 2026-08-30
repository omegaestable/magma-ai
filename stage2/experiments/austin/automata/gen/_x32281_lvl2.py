"""Hand-built level-2 attack on [R1,R3]: use a KEY-violating pair (u0,v0) as (x,Z)."""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
from _x32281_try1 import R1, R2
from _x32281_try2 import R3
import closedform as cf
from freemodel import size

def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(' + sh(t[1]) + '*' + sh(t[2]) + ')'
def J(a, b): return ('J', a, b)
def g(i): return ('g', i)

def r1_struct(u, v):
    try:
        return (v[0] == 'J' and v[1][0] == 'J' and v[1][1] == u and v[1][2][0] == 'J'
                and v[1][2][1][0] == 'J' and v[1][2][1][2] == v[1][2][2] and v[1][2][1][2] == v[2])
    except Exception:
        return False

def find_keybad(RULES, seeds=(202, 3, 4, 5, 77, 101, 303, 404, 505, 606)):
    """collect pairs where a rule fired but a1(a1 v) != u"""
    import fuzz as fz
    out = []
    for sd in seeds:
        C = cf.Closed(LAW, RULES)
        cf.deep_tests(C, LAW, 20000, 300, sd)
        fz.critical_fuzz(C, LAW, 12000, seed=sd + 300)
        fz.closure_fuzz(C, LAW, 12000, seed=sd + 200)
        for (u, v), w in C.memo.items():
            if w[0] == 'J' and w[1] == u and w[2] == v:
                continue
            if not (v[0] == 'J' and v[1][0] == 'J' and v[1][1] == u):
                out.append((u, v, w))
        if out:
            break
    return out

def law_val(C, x, Y, Z):
    P = C.op(x, Z); Q = C.op(P, Z); R = C.op(Y, Q); S = C.op(R, Z); top = C.op(Y, S)
    def fr(r, a, b): return r[0] == 'J' and r[1] == a and r[2] == b
    pat = ''.join('F' if fr(r, a, b) else 'D' for r, a, b in
                  ((P, x, Z), (Q, P, Z), (R, Y, Q), (S, R, Z)))
    return pat, top

RULES = [R1, R3]
bad = find_keybad(RULES)
print('KEY-violating fired pairs found:', len(bad))
if bad:
    u0, v0, w0 = bad[0]
    print('u0 size', size(u0), 'v0 size', size(v0), 'w0 size', size(w0))
    print('u0 =', sh(u0)[:120])
    C = cf.Closed(LAW, RULES)
    for Yi in range(4):
        Y = g(Yi)
        pat, top = law_val(C, u0, Y, v0)
        print('  Y=g%d pattern %s  law holds? %s' % (Yi, pat, top == u0))
    # also try Y = subterms
    for Y in (u0, v0[1], v0[2]):
        pat, top = law_val(C, u0, Y, v0)
        print('  Y=<size %d> pattern %s  law holds? %s' % (size(Y), pat, top == u0))
