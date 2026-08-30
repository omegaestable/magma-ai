"""Does the r13 counterexample also break r135 / the 18-rule xrep set?  And find more of them."""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
from _x32281_try1 import R1
from _x32281_try2 import R3
from _x32281_try5 import R5
import closedform as cf, fuzz as fz
from freemodel import size
J = lambda a, b: ('J', a, b); g = lambda n: ('g', n)
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))
def P(s):
    """parse '(a*b)' / 'gN'"""
    s = s.strip()
    if s.startswith('g'): return ('g', int(s[1:]))
    assert s[0] == '(' and s[-1] == ')'
    d = 0
    for i, ch in enumerate(s[1:-1], 1):
        if ch == '(': d += 1
        elif ch == ')': d -= 1
        elif ch == '*' and d == 0: return ('J', P(s[1:i]), P(s[i+1:-1]))
    raise ValueError(s)

X = P('(g2*g2)')
Y = P('((((g2*g2)*((g2*(g2*g2))*(g2*g2)))*(g2*g2))*(((((g2*g2)*(((((g2*g2)*((g2*(g2*g2))*(g2*g2)))*(g2*g2))*(g2*g2))*(g2*g2)))*(g2*g2))*(((((g2*g2)*(((((g2*g2)*((g2*(g2*g2))*(g2*g2)))*(g2*g2))*(g2*g2))*(g2*g2)))*(g2*g2))*(g2*g2))*(g2*g2)))*(g2*g2)))')
Z = P('g0')
print('parsed sizes', size(X), size(Y), size(Z))

# 18-rule set from the emitted package
import importlib.util
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xrep32281', 'chk32281.py'), encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}
exec(src, ns)
R18 = ns['rules']

SETS = {'r13': [R1, R3], 'r135': [R1, R3, R5], 'xrep18': R18}
for name, RULES in SETS.items():
    C = cf.Closed(LAW, RULES)
    try:
        p = C.op(X, Y); q = C.op(p, Y); a = C.op(Z, q); s = C.op(a, Y); top = C.op(Z, s)
    except RecursionError:
        print('%-8s RECURSION' % name); continue
    def fr(r, u, v): return r[0] == 'J' and r[1] == u and r[2] == v
    pat = ''.join('F' if fr(*t) else 'D' for t in ((p, X, Y), (q, p, Y), (a, Z, q), (s, a, Y), (top, Z, s)))
    print('%-8s pat=%s  top==x: %s   (top size %d)' % (name, pat, top == X, size(top)))
