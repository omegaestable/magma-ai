"""Trace one explicit instance of 40037 under a chosen rule set.

usage: _x40037_tr1.py "<x>" "<y>" "<z>" [--gen]      terms in  g0 / (a*b)  syntax
"""
import sys, os
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf, leangen, trace as tr
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq
import _x40037_rules as R

EQ = 40037
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
sub = [a for a in sys.argv[1:] if a.startswith('--sub=')]
rules = R.load_generated() if '--gen' in sys.argv else (
    [R.ALL[int(i) - 1] for i in sub[0][6:].split(',')] if sub else R.RULES)
show = tr.show


def parse(s):
    s = s.strip()
    if s.startswith('('):
        d = 0
        for i, c in enumerate(s):
            if c == '(':
                d += 1
            elif c == ')':
                d -= 1
            elif c == '*' and d == 1:
                return ('J', parse(s[1:i]), parse(s[i + 1:-1]))
        raise ValueError(s)
    return ('g', int(s[1:]))


args = [a for a in sys.argv[1:] if not a.startswith('--')]
X, Y, Z = parse(args[0]), parse(args[1]), parse(args[2])
print('nrules', len(rules))
print('x =', show(X), ' y =', show(Y), ' z =', show(Z))

T = tr.Tracing(law, rules)


def prod(name, a, b):
    T.trace_on = True; T.log = []; T.cuts = []
    r = T.op(a, b)
    T.trace_on = False
    w = T.log[-1][2] if T.log else None
    print('  %-4s = op(%s, %s)' % (name, show(a) if size(a) < 40 else '<%d>' % size(a), show(b) if size(b) < 40 else '<%d>' % size(b)))
    print('       = %s   [%s]' % (show(r) if size(r) < 60 else '<size %d>' % size(r),
                                  'free' if w is None else 'R%d %s' % (w + 1, rules[w][2])))
    for e, a2, b2, u2, v2 in T.cuts[:4]:
        print('       GATE CUT: %s at (%d,%d) vs (%d,%d)' % (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
    return r


s1 = prod('s1', Y, X)
s2 = prod('s2', s1, Y)
s3 = prod('s3', Z, s2)
s4 = prod('s4', X, s3)
s5 = prod('s5', Z, s4)
print('  goal x =', show(X), '  ->', 'OK' if s5 == X else 'FAIL')
okr = [i + 1 for i, (conds, xx, tag) in enumerate(rules) if tr.struct_ok(T, conds, Z, s4)]
print('  rules structurally holding at the final pair:', okr, [rules[i - 1][2] for i in okr])

F = fm.Free(law)
r1 = F.op(Y, X); r2 = F.op(r1, Y); r3 = F.op(Z, r2); r4 = F.op(X, r3); r5 = F.op(Z, r4)
print('  SEMANTIC: s1=%s s2=%s s3=%s s4=%s s5=%s  %s'
      % (show(r1), show(r2), show(r3), show(r4) if size(r4) < 40 else '<%d>' % size(r4),
         show(r5) if size(r5) < 40 else '<%d>' % size(r5), 'HOLDS' if r5 == X else 'FAILS'))
