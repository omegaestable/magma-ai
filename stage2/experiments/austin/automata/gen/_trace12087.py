import sys, os
sys.path.insert(0, r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq
import trace as tr

EQ = 12087
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
rules = [([('TG', ('V',)), ('TG', ('A1', ('V',))), ('TG', ('A1', ('A1', ('V',)))), ('EQ', ('U',), ('A1', ('A1', ('A1', ('V',))))), ('TG', ('A2', ('V',))), ('EQ', ('A2', ('A1', ('A1', ('V',)))), ('A1', ('A2', ('V',)))), ('EQ', ('A2', ('A1', ('V',))), ('A2', ('A2', ('V',))))], ('A2', ('A1', ('A1', ('V',)))), 'free'),
 ([('TG', ('V',)), ('TG', ('A1', ('V',))), ('TG', ('A1', ('A1', ('V',)))), ('EQ', ('U',), ('A1', ('A1', ('A1', ('V',))))), ('OPEQ', ('OP', ('A2', ('A1', ('A1', ('V',)))), ('A2', ('A1', ('V',)))), ('A2', ('V',)))], ('A2', ('A1', ('A1', ('V',)))), 'B1l'),
 ([('TG', ('V',)), ('TG', ('A2', ('V',))), ('OPEQ', ('OP', ('OP', ('U',), ('A1', ('A2', ('V',)))), ('A2', ('A2', ('V',)))), ('A1', ('V',)))], ('A1', ('A2', ('V',))), 'B0l')]

s = {'y': ('g', 3), 'x': ('J', ('J', ('J', ('g', 3), ('J', ('g', 0), ('g', 1))), ('g', 3)), ('J', ('J', ('g', 0), ('g', 1)), ('g', 3))), 'z': ('J', ('J', ('J', ('J', ('J', ('J', ('g', 3), ('J', ('g', 0), ('g', 1))), ('g', 3)), ('J', ('J', ('g', 0), ('g', 1)), ('g', 3))), ('J', ('g', 1), ('g', 3))), ('J', ('J', ('J', ('g', 3), ('J', ('g', 0), ('g', 1))), ('g', 3)), ('J', ('J', ('g', 0), ('g', 1)), ('g', 3)))), ('J', ('J', ('g', 1), ('g', 3)), ('J', ('J', ('J', ('g', 3), ('J', ('g', 0), ('g', 1))), ('g', 3)), ('J', ('J', ('g', 0), ('g', 1)), ('g', 3)))))}

def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))

print('LAW', EQ, cat[EQ])
print('law pattern', law)
print('INSTANCE')
for k, v in s.items():
    print(' ', k, '=', show(v), 'size', size(v))

T = tr.Tracing(law, rules)
A, B = law[1]

def evt(p):
    if isinstance(p, str):
        return s[p]
    a, b = evt(p[0]), evt(p[1])
    T.trace_on = True; T.log = []; T.cuts = []
    r = T.op(a, b)
    T.trace_on = False
    which = T.log[-1][2] if T.log else None
    print('  %-30s = %s   [%s]  size=%d' % (str(p), show(r) if size(r) < 80 else '<size %d>' % size(r), 'free' if which is None else 'R%d %s' % (which + 1, rules[which][2]), size(r)))
    for e, a2, b2, u2, v2 in T.cuts[:4]:
        print('      GATE CUT: %s at pair sizes (%d,%d) vs (u,v) sizes (%d,%d)' % (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
    return r

u = evt(A)
v = evt(B)
T.trace_on = True; T.log = []; T.cuts = []
r = T.op(u, v)
T.trace_on = False
print('FINAL op(A,B) =', show(r) if size(r) < 80 else '<size %d>' % size(r), ' expected x =', show(s['x']), ' [', ('free' if not T.log or T.log[-1][2] is None else 'R%d' % (T.log[-1][2] + 1)), ']')
for e, a2, b2, u2, v2 in T.cuts[:6]:
    print('      GATE CUT: %s at pair sizes (%d,%d) vs (u,v) sizes (%d,%d)' % (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))

okr = [i + 1 for i, (conds, x, tag) in enumerate(rules) if tr.struct_ok(T, conds, u, v)]
print('rules whose structural conditions hold at final pair:', okr, [rules[i-1][2] for i in okr])

F = fm.Free(law)
def evs(p):
    if isinstance(p, str):
        return s[p]
    return F.op(evs(p[0]), evs(p[1]))
rs = F.op(evs(A), evs(B))
print('SEMANTIC model verdict:', 'HOLDS' if rs == s['x'] else 'FAILS too, got %s' % (show(rs) if size(rs) < 80 else '<size %d>' % size(rs)), 'conflicts', len(F.conflicts))
