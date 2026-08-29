"""trace.py <eq_id> [--closed-only] [--n 1500]

Find the first failing instance of a closed-form package (gen/chk<eq>.py rules) and explain it:
  * the instance (terms), the evaluation chain of the law's pattern with, for every product, the rule that
    fired (or `free`), and every msr-gate cut met while evaluating the final product (a genuine reading whose
    nested guard needs a pair no smaller than (u, v) — the 6912 case);
  * the semantic free model's verdict on the same instance (found the reading / also fails);
  * the list of rules whose STRUCTURAL conditions hold at the final product (guards ignored) — a rule that is
    structurally right but whose op-guard was cut is a gate problem, none = a missing mode.
"""
import sys, os, json, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import closedform as cf
import fuzz as fz
import freemodel as fm
from freemodel import normalise, catalog, pvars, size
from laws import parse_eq

def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))

def load_rules(eq):
    import importlib.util
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gen', 'chk%d.py' % eq)
    src = open(p, encoding='utf-8').read().split('C = cf.Closed')[0]
    ns = {}; exec(src, ns)
    return ns['rules']

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

def main():
    eq = int(sys.argv[1])
    N = int(sys.argv[sys.argv.index('--n') + 1]) if '--n' in sys.argv else 1500
    cat = catalog(); orig = normalise(parse_eq(cat[eq]))
    dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
    law = ('x', cf.Extractor.__init__.__globals__['normalise'](orig) if False else orig)[1] if False else None
    import leangen
    law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
    rules = load_rules(eq)
    C = cf.Closed(law, rules)
    fails = []
    for sd in (eq * 7 + 3, eq * 7 + 14):
        t, f = cf.deep_tests(C, law, N, 120, sd); fails += f
        if fails: break
        t2, f2 = fz.fuzz(cf.Closed(law, rules), law, rules, 6000, seed=sd + 100); fails += f2
        if fails: break
    fails = [f for f in fails if f[1] != 'recursion']
    if not fails:
        print(json.dumps(dict(eq=eq, result='no failure found'))); return
    fails.sort(key=lambda f: sum(size(t) for t in f[0].values()))
    s, got = fails[0]
    print('LAW', eq, cat[eq], '(dualized)' if dualized else '')
    print('INSTANCE', {k: show(v) for k, v in s.items()})
    T = Tracing(law, rules)
    A, B = law[1]
    # evaluate the pattern bottom-up with tracing, print each product
    def evt(p):
        if isinstance(p, str): return s[p]
        a, b = evt(p[0]), evt(p[1])
        T.trace_on = True; T.log = []; T.cuts = []
        r = T.op(a, b)
        T.trace_on = False
        which = T.log[-1][2] if T.log else None
        print('  %-40s = %s   [%s]' % (cf.show_expr(('OP', ('U',), ('V',))) if False else str(p), show(r) if size(r) < 60 else '<size %d>' % size(r), 'free' if which is None else 'R%d %s' % (which + 1, rules[which][2])))
        for e, a2, b2, u2, v2 in T.cuts[:4]:
            print('      GATE CUT: %s at pair sizes (%d,%d) vs (u,v) sizes (%d,%d)' % (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
        return r
    u = evt(A); v = evt(B)
    T.trace_on = True; T.log = []; T.cuts = []
    r = T.op(u, v); T.trace_on = False
    print('  FINAL op(A,B) = %s  expected x = %s  [%s]' % (show(r) if size(r) < 60 else '<size %d>' % size(r), show(s['x']), 'free' if not T.log or T.log[-1][2] is None else 'R%d' % (T.log[-1][2] + 1)))
    for e, a2, b2, u2, v2 in T.cuts[:6]:
        print('      GATE CUT: %s at pair sizes (%d,%d) vs (u,v) sizes (%d,%d)' % (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
    okr = [i + 1 for i, (conds, x, tag) in enumerate(rules) if struct_ok(T, conds, u, v)]
    print('  rules whose structural conditions hold at the final pair:', okr, [rules[i - 1][2] for i in okr])
    if '--closed-only' not in sys.argv:
        F = fm.Free(law)
        def evs(p):
            if isinstance(p, str): return s[p]
            return F.op(evs(p[0]), evs(p[1]))
        rs = F.op(evs(A), evs(B))
        print('  SEMANTIC model: %s (conflicts %d)' % ('law HOLDS' if rs == s['x'] else 'law FAILS too (got %s)' % (show(rs) if size(rs) < 60 else '<size %d>' % size(rs)), len(F.conflicts)))

if __name__ == '__main__':
    main()
