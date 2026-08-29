import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
import leangen

EQ = 28626
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chk28626.py')
src = open(p, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns)
rules = ns['rules']
A, B = law[1]

def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))

w = ('g', 0)
y = ('J', ('J', ('J', w, ('g',1)), w), w)
x = ('J', ('J', ('g', 1), y), y)
z = x
s = {'x': x, 'y': y, 'z': z}
print('y =', show(y))
print('x =', show(x))

class Tracing(cf.Closed):
    def __init__(self, law, rules):
        super().__init__(law, rules)
        self.log = []; self.cuts = []; self.trace_on = False
    def ev(self, e, u, v):
        if e[0] == 'OP' and self.trace_on:
            a = self.ev(e[1], u, v); b = self.ev(e[2], u, v)
            if a is None or b is None: return None
            if not cf.gate_ok(a, b, u, v):
                self.cuts.append((e, a, b, u, v)); return None
            return self.op(a, b)
        return super().ev(e, u, v)
    def op(self, u, v):
        key = (u, v)
        if key in self.memo: return self.memo[key]
        if key in self.inprog:
            self.cycles += 1; return ('J', u, v)
        self.inprog.add(key)
        res = None; which = None
        for i, (conds, x, tag) in enumerate(self.rules):
            if self.check(conds, u, v):
                r = self.ev(x, u, v)
                if r is not None:
                    res = r; which = i; break
        self.inprog.discard(key)
        if res is None: res = ('J', u, v)
        self.memo[key] = res
        if self.trace_on: self.log.append((u, v, which, res))
        return res

T = Tracing(law, rules)
def evt(p, label):
    if isinstance(p, str): return s[p]
    a, b = evt(p[0], None), evt(p[1], None)
    T.trace_on = True; T.log = []; T.cuts = []
    r = T.op(a, b)
    T.trace_on = False
    which = T.log[-1][2] if T.log else None
    tag = 'free' if which is None else 'R%d %s' % (which + 1, rules[which][2])
    print('  %-14s op(%-40s, %-40s) = %-40s [%s]' % (label or str(p), show(a), show(b), show(r), tag))
    for e, a2, b2, u2, v2 in T.cuts[:6]:
        print('      GATE CUT: %s at pair sizes (%d,%d) vs (u,v) sizes (%d,%d)' % (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
    return r
u = evt(A, None); v = evt(B, None)
T.trace_on = True; T.log = []; T.cuts = []
r = T.op(u, v); T.trace_on = False
which = T.log[-1][2] if T.log else None
tag = 'free' if which is None else 'R%d %s' % (which + 1, rules[which][2])
print('FINAL op(u,v) = %s  expected x = %s  [%s]' % (show(r), show(x), tag))
for e, a2, b2, u2, v2 in T.cuts[:6]:
    print('      GATE CUT: %s at pair sizes (%d,%d) vs (u,v) sizes (%d,%d)' % (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))

def struct_ok(C, conds, u, v):
    for c in conds:
        if c[0] == 'OPEQ' or any(cf.nested_op(e) for e in c[1:]): continue
        if c[0] == 'TG':
            t = C.ev(c[1], u, v)
            if t is None or t[0] != 'J': return False
        elif c[0] == 'EQ':
            a = C.ev(c[1], u, v); b = C.ev(c[2], u, v)
            if a is None or b is None or a != b: return False
    return True
okr = [i + 1 for i, (conds, xx, tag) in enumerate(rules) if struct_ok(T, conds, u, v)]
print('  rules whose structural conditions hold at final pair:', okr, [rules[i-1][2] for i in okr])

# also check each rule's OPEQ conditions manually at the final pair
for i, (conds, xx, tag) in enumerate(rules):
    ok = T.check(conds, u, v)
    print('  rule', i+1, tag, 'check=', ok)
