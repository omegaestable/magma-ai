"""Verify the DFFD failing instance found by gen/_x28626_modes2.py, with a FRESH Closed."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf, leangen
from closedform import Extractor
from freemodel import normalise, catalog, size
from laws import parse_eq
import freemodel as fm

EQ = 28626
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
rules = Extractor(law).rules(exist=False)
A, B = law[1]

def P(s):
    """parse '((g0*g2)*g1)' into a term"""
    s = s.strip()
    if s.startswith('g'):
        return ('g', int(s[1:]))
    assert s[0] == '(' and s[-1] == ')', s
    d = 0
    for i, ch in enumerate(s[1:-1], 1):
        if ch == '(': d += 1
        elif ch == ')': d -= 1
        elif ch == '*' and d == 0:
            return ('J', P(s[1:i]), P(s[i + 1:-1]))
    raise AssertionError(s)

def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))

y = P('((((((g0*g2)*((g2*g0)*g0))*(g0*g2))*((g2*g2)*g2))*(((g0*g2)*((g2*g0)*g0))*(g0*g2)))*(((g0*g2)*((g2*g0)*g0))*(g0*g2)))')
x = P('(((g2*g2)*g2)*g2)')
z = P('(g2*g2)')
s = {'x': x, 'y': y, 'z': z}
print('sizes', {k: size(v) for k, v in s.items()})

C = cf.Closed(law, rules)
a = C.op(y, x); b = C.op(a, y); c = C.op(b, y); d = C.op(x, z); f = C.op(c, d)
print('a free?', a == ('J', y, x), 'a =', show(a))
print('b free?', b == ('J', a, y))
print('c free?', c == ('J', b, y))
print('d free?', d == ('J', x, z), 'd =', show(d))
print('FINAL', show(f), 'expected x =', show(x), 'MATCH' if f == x else 'FAIL')
print('cycles', C.cycles)

# which rules hold structurally at the final pair
import trace as tr
T = tr.Tracing(law, rules)
T.trace_on = True
a2 = T.op(y, x); b2 = T.op(a2, y); c2 = T.op(b2, y); d2 = T.op(x, z)
T.log = []; T.cuts = []
f2 = T.op(c2, d2)
print('trace final rule', T.log[-1][2] if T.log else None, 'res', show(f2))
for e, aa, bb, uu, vv in T.cuts[:8]:
    print('  GATE CUT', cf.show_expr(e), 'pair sizes', (size(aa), size(bb)), 'vs', (size(uu), size(vv)))
ok = [i + 1 for i, (conds, xx, tag) in enumerate(rules) if tr.struct_ok(T, conds, c2, d2)]
print('structurally ok rules at final pair:', ok, [rules[i - 1][2] for i in ok])

# semantic free model verdict
F = fm.Free(law, maxdepth=80)
def evs(p):
    if isinstance(p, str): return s[p]
    return F.op(evs(p[0]), evs(p[1]))
try:
    r = F.op(evs(A), evs(B))
    print('SEMANTIC final', show(r) if size(r) < 80 else '<size %d>' % size(r), 'match', r == x, 'conflicts', len(F.conflicts))
except RecursionError:
    print('SEMANTIC recursion')
