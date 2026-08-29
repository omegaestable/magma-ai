import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf
import fuzz as fz
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq
import leangen

EQ = 28626
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import importlib.util
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chk28626.py')
src = open(p, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns)
rules = ns['rules']

C = cf.Closed(law, rules)
fails = None
for sd in range(1, 60):
    t, f = cf.deep_tests(C, law, 20000, 60, sd)
    real = [x for x in f if x[1] != 'recursion']
    if real:
        print('seed', sd, 'fails', len(real))
        fails = real
        break

if not fails:
    print('no fail found in seeds 1..59')
    sys.exit(0)

def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))

fails.sort(key=lambda f: sum(size(t) for t in f[0].values()))
s, got = fails[0]
print('INSTANCE (sizes):', {k: size(v) for k, v in s.items()})
print('INSTANCE:')
for k, v in s.items():
    print(' ', k, '=', show(v))
print('got', show(got) if size(got) < 200 else '<size %d>' % size(got), 'expected x=', show(s['x']))

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

T = Tracing(law, rules)
A, B = law[1]
def evt(p):
    if isinstance(p, str): return s[p]
    a, b = evt(p[0]), evt(p[1])
    T.trace_on = True; T.log = []; T.cuts = []
    r = T.op(a, b)
    T.trace_on = False
    which = T.log[-1][2] if T.log else None
    print('  %-30s = %s   [%s]' % (str(p), show(r) if size(r) < 100 else '<size %d>' % size(r), 'free' if which is None else 'R%d %s' % (which + 1, rules[which][2])))
    for e, a2, b2, u2, v2 in T.cuts[:4]:
        print('      GATE CUT: %s at pair sizes (%d,%d) vs (u,v) sizes (%d,%d)' % (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
    return r
u = evt(A); v = evt(B)
T.trace_on = True; T.log = []; T.cuts = []
r = T.op(u, v); T.trace_on = False
print('  FINAL op(A,B) = %s  expected x = %s  [%s]' % (show(r) if size(r) < 100 else '<size %d>' % size(r), show(s['x']), 'free' if not T.log or T.log[-1][2] is None else 'R%d' % (T.log[-1][2] + 1)))
for e, a2, b2, u2, v2 in T.cuts[:6]:
    print('      GATE CUT: %s at pair sizes (%d,%d) vs (u,v) sizes (%d,%d)' % (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
okr = [i + 1 for i, (conds, x, tag) in enumerate(rules) if struct_ok(T, conds, u, v)]
print('  rules whose structural conditions hold at the final pair:', okr, [rules[i - 1][2] for i in okr])
F = fm.Free(law)
def evs(p):
    if isinstance(p, str): return s[p]
    return F.op(evs(p[0]), evs(p[1]))
rs = F.op(evs(A), evs(B))
print('  SEMANTIC model: %s (conflicts %d)' % ('law HOLDS' if rs == s['x'] else 'law FAILS too (got %s)' % (show(rs) if size(rs) < 100 else '<size %d>' % size(rs)), len(F.conflicts)))
