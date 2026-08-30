"""Which rule saves full12 on the guard-2 witness, and does adding it repair f4?"""
import sys, time, collections
D = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D)
import closedform as cf, trace as tr, revalidate as rv
import importlib.util
G = D + '/gen/'
show = tr.show; J = lambda a, b: ('J', a, b); g = lambda n: ('g', n)
sv = list(sys.argv); sys.argv = [sys.argv[0]]
r12 = importlib.util.spec_from_file_location('_x23357_rep', G + '_x23357_rep.py')
M12 = importlib.util.module_from_spec(r12); r12.loader.exec_module(M12)
s2 = importlib.util.spec_from_file_location('_w3_23357_sets2', G + '_w3_23357_sets2.py')
S = importlib.util.module_from_spec(s2); s2.loader.exec_module(S)
law = M12.law; TAG12 = {r[2]: r for r in M12.rules}


class CT(cf.Closed):
    def __init__(self, law, rules):
        super().__init__(law, rules); self.ruleof = {}
    def op(self, u, v):
        key = (u, v); m = self.memo.get(key)
        if m is not None: return m
        if key in self.inprog:
            self.cycles += 1; return ('J', u, v)
        self.inprog.add(key); res = None
        for i, (c, x, t) in enumerate(self.rules):
            if self.check(c, u, v):
                r = self.ev(x, u, v)
                if r is not None:
                    res = r; self.fired[i] = self.fired.get(i, 0) + 1; self.ruleof[key] = i; break
        self.inprog.discard(key)
        if res is None: res = ('J', u, v)
        self.memo[key] = res; return res


y1 = J(J(g(3), g(2)), g(3)); x1 = J(g(2), J(g(3), g(0)))
y = J(J(y1, x1), y1); z = J(x1, J(y1, g(0))); x = g(7)


def toprule(rules):
    C = CT(law, rules)
    A = C.op(y, x); U = C.op(A, y); B = C.op(y, z); V = C.op(x, B); top = C.op(U, V)
    i = C.ruleof.get((U, V))
    return (top == x), (rules[i][2] if i is not None else 'FREE')


for nm, rl in (('full12', list(M12.rules)), ('min6', [TAG12[t] for t in
        ['free', 'Bs|rd:A0', 'Bs|ex:Qa', 'Bs|ex:Qb', 'A0s,B1s|rd:A0', 'As']])):
    ok, t = toprule(rl)
    print('%-8s law=%s   TOP RULE = %s' % (nm, ok, t), flush=True)

F4 = S.SETS['f4']
CAND = {
    'f4+B1s':        [F4[0], TAG12['B1s'], F4[1], F4[2], F4[3]],
    'f4+A0sB1s':     [F4[0], F4[1], TAG12['A0s,B1s'], F4[2], F4[3]],
    'f4+B1srd':      [F4[0], TAG12['B1s|rd:A0'], F4[1], F4[2], F4[3]],
    'f4+B1s+A0sB1s': [F4[0], TAG12['B1s'], F4[1], TAG12['A0s,B1s'], F4[2], F4[3]],
}
for nm, rl in CAND.items():
    ok, t = toprule(rl)
    t0 = time.time()
    f = [q for q in rv.run_tests(law, rl, [3, 4, 5], 3000, 12000) if q[1] != 'recursion']
    print('%-15s %d rules  witness law=%-5s top=%-16s run_tests fails %d (%.0fs)'
          % (nm, len(rl), ok, t, len(f), time.time() - t0), flush=True)
    if f:
        print('     first:', {a: b for a, b in f[0][0].items()}, flush=True)
