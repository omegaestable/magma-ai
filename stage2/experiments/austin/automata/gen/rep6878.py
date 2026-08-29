"""rep6878.py [--emit] [N per seed]

Repair of the generated rule set for law 6878  x = y * (y * ((z * x) * (x * y))).

The generator's 3 rules miss every case where x*y is decoded together with another product.  Writing
a = z*x, b = x*y, c = a*b (the outer y*c is provably always free), the invariant "op(p,q) decoded  =>
q = J(p, ..)" gives x = u.1 whenever b is decoded and z = x.1 whenever a is decoded; c decoded forces
b decoded and b.1 = a.  Six mutually exclusive cases:
  R1  a,b free            x = v.2.1.2      (generator)
  R2  b decoded, a free   x = u.1          (generator's R2 re-read through the invariant)
  R3  a decoded, b free   x = v.2.2.1      (generator)
  R4  a,b decoded         x = u.1          (NEW)
  R5a c decoded, a free   x = u.1          (NEW)
  R5b c decoded, a decoded x = u.1         (NEW)
Nested products: A = op(u.1,u) [b], B = op(u.1.1,u.1) [a], C = op(v.2.2.1.1, v.2.2.1) [a in R3], D = op(A.1, A) [c].
"""
import sys, os, time, random
sys.path.insert(0, 'C:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf
import fuzz as fz
from freemodel import normalise, catalog, size
from laws import parse_eq

law = normalise(parse_eq(catalog()[6878]))
U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def OP(a, b): return ('OP', a, b)
def TG(e): return ('TG', e)
def EQ(a, b): return ('EQ', a, b)
def OPEQ(o, t): return ('OPEQ', o, t)
v2 = A2(V); v21 = A1(v2); v22 = A2(v2)
u1 = A1(U); u11 = A1(u1)
Aop = OP(u1, U)
Bop = OP(u11, u1)
Cop = OP(A1(A1(v22)), A1(v22))
Dop = OP(A1(Aop), Aop)
R1 = ([TG(V), EQ(U, A1(V)), TG(v2), TG(v21), TG(v22), EQ(A2(v21), A1(v22)), EQ(U, A2(v22))], A2(v21), 'free')
R2 = ([TG(V), EQ(U, A1(V)), TG(v2), TG(v21), TG(U), EQ(A2(v21), u1), OPEQ(Aop, v22)], u1, 'B11l')
R3 = ([TG(V), EQ(U, A1(V)), TG(v2), TG(v22), EQ(U, A2(v22)), TG(A1(v22)), OPEQ(Cop, v21)], A1(v22), 'B10l')
R4 = ([TG(V), EQ(U, A1(V)), TG(v2), TG(U), TG(u1), OPEQ(Bop, v21), OPEQ(Aop, v22)], u1, 'B00')
R5a = ([TG(V), EQ(U, A1(V)), TG(U), TG(Aop), TG(A1(Aop)), EQ(A2(A1(Aop)), u1), OPEQ(Dop, v2)], u1, 'C1')
R5b = ([TG(V), EQ(U, A1(V)), TG(U), TG(u1), TG(Aop), OPEQ(Bop, A1(Aop)), OPEQ(Dop, v2)], u1, 'C0')
rules = [R1, R2, R3, R4, R5a, R5b]

def g(n): return ('g', n)
def J(a, b): return ('J', a, b)
def show(t):
    if t[0] == 'g': return 'g%d' % t[1]
    return '(%s %s)' % (show(t[1]), show(t[2]))

def which(C, u, v):
    for i, (conds, e, tag) in enumerate(C.rules):
        if C.check(conds, u, v) and C.ev(e, u, v) is not None: return 'R%d[%s]' % (i + 1, tag)
    return 'free'

def run(name, s, expect_rule=None):
    C = cf.Closed(law, rules)
    x, y, z = s['x'], s['y'], s['z']
    a = C.op(z, x); b = C.op(x, y); c = C.op(a, b); w = C.op(y, c); t = C.op(y, w)
    ok = t == x
    print('%s: %s   [z*x:%s x*y:%s a*b:%s y*c:%s y*w:%s]' % (name, 'OK' if ok else 'FAIL', which(C, z, x), which(C, x, y), which(C, a, b), which(C, y, c), which(C, y, w)))
    if not ok:
        for k in ('x', 'y', 'z'): print('   %s = %s' % (k, show(s[k])))
        print('   T = %s' % show(t))
    return ok

def hand_instances():
    res = []
    z = g(0); zp = g(3); xpp = g(5); y1 = g(4); ypp = g(6)
    # R4: x encoded by z, y encoded by x
    x = J(z, J(J(zp, xpp), J(xpp, z))); y = J(x, J(J(y1, ypp), J(ypp, x)))
    res.append(run('R4 (a,b decoded)', {'x': x, 'y': y, 'z': z}))
    # R5a: c decoded, a free
    x = g(5); z = g(0); a = J(z, x); b = J(a, J(J(g(7), g(8)), J(g(8), a))); y = J(x, J(J(g(9), b), J(b, x)))
    res.append(run('R5a (c decoded, a free)', {'x': x, 'y': y, 'z': z}))
    # R5b: c decoded, a decoded
    z = g(0); x = J(z, J(J(g(3), g(5)), J(g(5), z))); a = g(5); b = J(a, J(J(g(7), g(8)), J(g(8), a))); y = J(x, J(J(g(9), b), J(b, x)))
    res.append(run('R5b (c, a decoded)', {'x': x, 'y': y, 'z': z}))
    # R2 / R3 controls
    x = g(5); y = J(x, J(J(y1, ypp), J(ypp, x))); z = g(0)
    res.append(run('R2 (b decoded)', {'x': x, 'y': y, 'z': z}))
    x = J(z, J(J(zp, xpp), J(xpp, z))); y = g(7)
    res.append(run('R3 (a decoded)', {'x': x, 'y': y, 'z': z}))
    # coincidences: z = y, z = x, x = y on top of the R4/R5 shapes
    x = J(z, J(J(zp, xpp), J(xpp, z))); y = J(x, J(J(y1, ypp), J(ypp, x)))
    res.append(run('R4 with z := y', {'x': x, 'y': y, 'z': y}))
    res.append(run('R4 with z := x', {'x': x, 'y': y, 'z': x}))
    res.append(run('R4 with x := y', {'x': y, 'y': y, 'z': z}))
    res.append(run('R4 with y := x', {'x': x, 'y': x, 'z': z}))
    # nested: the R5a payload c' is itself an R-shaped term
    x = g(5); z = g(0); a = J(z, x); cp = J(g(2), J(J(g(3), g(4)), J(g(4), g(2))))
    b = J(a, J(J(g(7), cp), J(cp, a))); y = J(x, J(J(g(9), b), J(b, x)))
    res.append(run('R5a nested payload', {'x': x, 'y': y, 'z': z}))
    # x encoded by y (x = payload of y? no: x = J(y, ...) encodes something by y) and y encodes by x is impossible; try x = J(y, E)
    y = g(1); x = J(y, J(J(g(2), g(3)), J(g(3), y))); z = g(0)
    res.append(run('x encodes by y', {'x': x, 'y': y, 'z': z}))
    z = y
    res.append(run('x encodes by y, z := y', {'x': x, 'y': y, 'z': z}))
    return all(res)

def main():
    N = int([a for a in sys.argv[1:] if a.isdigit()][0]) if any(a.isdigit() for a in sys.argv[1:]) else 10000
    print('rules:')
    for i, r in enumerate(rules): print('  R%d %s' % (i + 1, cf.show_rule(r)))
    ok = hand_instances()
    print('hand instances all OK:', ok)
    t0 = time.time(); tot = 0; nf = 0
    for seed in (11, 12, 13, 14):
        C = cf.Closed(law, rules)
        tested, fails = cf.deep_tests(C, law, N, 300, seed)
        tot += tested; nf += len(fails)
        for s, l in fails[:2]:
            print('  deep FAIL seed', seed, {k: size(v) for k, v in s.items()}, 'got', 'recursion' if l == 'recursion' else show(l)[:200])
        print('  seed', seed, 'tested', tested, 'fails', len(fails), 'fired', dict(sorted(C.fired.items())), 'cycles', C.cycles, 'secs', round(time.time() - t0, 1), flush=True)
    print('deep total', tot, 'fails', nf)
    ft = 0; ff = 0
    for seed in (21, 22):
        C = cf.Closed(law, rules)
        t2, f2 = fz.fuzz(C, law, rules, 12000, seed=seed)
        ft += t2; ff += len(f2)
        for s, l in f2[:2]:
            print('  fuzz FAIL seed', seed, {k: size(v) for k, v in s.items()}, 'got', 'recursion' if l == 'recursion' else show(l)[:200])
        print('  fuzz seed', seed, 'tested', t2, 'fails', len(f2), 'fired', dict(sorted(C.fired.items())), flush=True)
    print('fuzz total', ft, 'fails', ff)
    if '--emit' in sys.argv:
        if nf or ff or not ok:
            print('NOT emitting: failures'); return
        import leangen
        out = 'C:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/rep6878'
        res = leangen.emit(6878, out, rules_override=rules)
        print('emit:', res)

if __name__ == '__main__':
    main()
