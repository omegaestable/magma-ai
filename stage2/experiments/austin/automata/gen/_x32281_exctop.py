"""Which rule fires at each product of the law's chain on the ONE exceptional instance, under r135?"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
from _x32281_try1 import R1
from _x32281_try2 import R3
from _x32281_try5 import R5
import closedform as cf
from freemodel import size
RULES = [R1, R3, R5]
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))
def PA(s):
    s = s.strip()
    if s.startswith('g'): return ('g', int(s[1:]))
    d = 0
    for i, ch in enumerate(s[1:-1], 1):
        if ch == '(': d += 1
        elif ch == ')': d -= 1
        elif ch == '*' and d == 0: return ('J', PA(s[1:i]), PA(s[i+1:-1]))
    raise ValueError(s)
X = PA('(g2*g2)')
Y = PA('((((g2*g2)*((g2*(g2*g2))*(g2*g2)))*(g2*g2))*(((((g2*g2)*(((((g2*g2)*((g2*(g2*g2))*(g2*g2)))*(g2*g2))*(g2*g2))*(g2*g2)))*(g2*g2))*(((((g2*g2)*(((((g2*g2)*((g2*(g2*g2))*(g2*g2)))*(g2*g2))*(g2*g2))*(g2*g2)))*(g2*g2))*(g2*g2))*(g2*g2)))*(g2*g2)))')
Z = PA('g0')
C = cf.Closed(LAW, RULES)
def which(u, v):
    r = C.op(u, v)
    if r[0] == 'J' and r[1] == u and r[2] == v: return 'F', r
    for i, (conds, xe, tag) in enumerate(RULES):
        if C.check(conds, u, v) and C.ev(xe, u, v) is not None:
            return 'R%d(%s)' % (i + 1, tag), r
    return '?', r
P = C.op(X, Y); Q = C.op(P, Y); A = C.op(Z, Q); S = C.op(A, Y); T = C.op(Z, S)
for nm, (u, v) in (('P=op x y', (X, Y)), ('Q=op P y', (P, Y)), ('A=op z Q', (Z, Q)), ('S=op A y', (A, Y)), ('top=op z S', (Z, S))):
    w, r = which(u, v)
    print('%-11s %-12s sz(u)=%-4d sz(v)=%-4d -> sz %d' % (nm, w, size(u), size(v), size(r)))
print('top == x :', T == X)
print('a1(a1 y) =', sh(Y[1][1])[:80], '   x =', sh(X))
print('sz y =', size(Y), ' sz P =', size(P), ' sz Q =', size(Q), ' sz A =', size(A), ' sz S =', size(S))
