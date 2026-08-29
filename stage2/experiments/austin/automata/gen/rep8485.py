"""rep8485.py : candidate repair of the 8485 rules (bounded evidence only).  Adds, after R1, the rules for the three
hole classes (hidden c at u.2.2 / J u.2 x / x.1 with d decoded; c = u.1 with d and B decoded; the structural form of
c = J u.2 x with d, B decoded) and measures the law on the hand instances, the closure fuzz and cf.deep_tests."""
import sys, os, random, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chk8485.py'), encoding='utf-8').read()
exec(src[src.index('rules = '):src.index('C = cf.Closed')])
law = normalise(parse_eq(catalog()[8485])); A, B = law[1]
U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def OP(a, b): return ('OP', a, b)
def JJ(a, b): return ('J', a, b)
def TG(e): return ('TG', e)
def EQ(a, b): return ('EQ', a, b)
def OPEQ(a, b): return ('OPEQ', a, b)
x = A1(V); Bv = A2(V); u1 = A1(U); T = A2(U)
beta = [TG(V), TG(Bv), EQ(A2(Bv), U), TG(U), EQ(A1(Bv), u1)]
gam = [TG(V), TG(U), EQ(Bv, u1), OPEQ(OP(u1, U), u1)]
R5 = (gam + [TG(u1), EQ(A2(u1), x)], x, 'g1:c=u.1')
R6 = (gam + [TG(x), EQ(A1(x), u1)], x, 'g1:c=x.1')
R3a = (beta + [TG(T), TG(A2(T)), EQ(A2(A2(T)), x), OPEQ(OP(A2(T), U), u1)], x, 'b:c=u.2.2')
R3b = (beta + [OPEQ(OP(JJ(T, x), U), u1)], x, 'b:c=Ju.2x')
R3c = (beta + [TG(x), OPEQ(OP(A1(x), U), u1)], x, 'b:c=x.1')
g7 = gam + [TG(x), EQ(A2(x), T), TG(T), EQ(A2(T), u1)]
gx = A1(x)
R7a = (g7 + [TG(gx), TG(A1(gx)), EQ(A2(A1(gx)), T), EQ(A2(gx), T)], x, 'g1:c=Ju.2x:a')
R7b = (g7 + [TG(gx), EQ(A1(gx), A1(T)), EQ(A2(gx), T)], x, 'g1:c=Ju.2x:b')
R7c = (g7 + [EQ(gx, A1(T)), OPEQ(OP(A1(T), T), A1(T))], x, 'g1:c=Ju.2x:c')
rep = [rules[0], R5, R6, R3a, R3b, R3c, R7a, R7b, R7c] + rules[1:]
def g(n): return ('g', n)
def J(a, b): return ('J', a, b)
def which(C, R, u, v):
    for i, (conds, e, tag) in enumerate(R):
        if C.check(conds, u, v) and C.ev(e, u, v) is not None: return tag if i else 'R1'
    return 'free'
def trace(C, R, s):
    x, y, z = s['x'], s['y'], s['z']
    P = C.op(z, x); Q = C.op(P, y); Rr = C.op(Q, y); S = C.op(x, Rr); Tt = C.op(y, S)
    return ' | '.join('%s:%s' % (n, which(C, R, a, b)) for n, a, b in [('z*x', z, x), ('P*y', P, y), ('Q*y', Q, y), ('x*R', x, Rr), ('y*S', y, S)]), Tt == x
w = J(g(1), g(0)); inst1 = {'x': g(0), 'y': J(w, J(J(J(g(2), w), w), w)), 'z': g(1)}
e = J(g(1), g(0)); TT = J(J(e, g(0)), g(0)); X2 = J(J(J(g(2), TT), TT), TT)
inst2 = {'x': X2, 'y': J(g(0), TT), 'z': TT}
inst2i = {'x': g(0), 'y': J(TT, X2), 'z': J(e, g(0))}
def closure_fuzz(C, N, seed):
    random.seed(seed); pool = [g(0), g(1), g(2)]; fails = []
    for it in range(N):
        a, b, q = (random.choice(pool) for _ in range(3)); r = random.random()
        t = C.evp(B, {'x': b, 'y': a, 'z': q}) if r < 0.6 else (C.op(a, b) if r < 0.8 else J(a, b))
        if size(t) <= 45: pool.append(t)
        if len(pool) > 300: pool.pop(random.randrange(3, len(pool)))
        s = {v: random.choice(pool) for v in ('x', 'y', 'z')}
        if random.random() < 0.3: s['z'] = s['x']
        if C.op(C.evp(A, s), C.evp(B, s)) != s['x']: fails.append(s)
    return fails
for name, R in (('shipped', rules), ('repaired', rep)):
    C = cf.Closed(law, R)
    print('==', name, len(R), 'rules')
    for nm, s in (('inst1', inst1), ('inst2 outer', inst2), ('inst2 inner', inst2i)):
        print('  ', nm, trace(C, R, s))
    t0 = time.time(); tot = 0; nf = 0; shown = {}
    for seed in (1, 2, 3):
        C = cf.Closed(law, R); f = closure_fuzz(C, 20000, seed); tot += 20000; nf += len(f)
        for s in f:
            tr = trace(C, R, s)[0]
            if tr not in shown: shown[tr] = (size(s['x']), size(s['y']), size(s['z']))
    print('   closure fuzz', tot, 'fails', nf, 'classes:', shown, round(time.time() - t0, 1), 's')
    t0 = time.time(); tot = 0; nf = 0
    for seed in (11, 12):
        C = cf.Closed(law, R); tested, f = cf.deep_tests(C, law, 10000, 300, seed); tot += tested; nf += len(f)
    print('   deep_tests', tot, 'fails', nf, round(time.time() - t0, 1), 's')
if '--rules' in sys.argv:
    for r in rep: print(cf.show_rule(r))
