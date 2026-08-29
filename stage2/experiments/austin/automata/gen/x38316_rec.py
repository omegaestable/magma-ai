"""x38316_rec.py [deep|small|fam|all] -- a recursive characterisation of the free model of the L-form law
   x = y * (x * ((y * (z * x)) * y))      (the dual of 38316)
with the three existentially quantified decoders located by candidate accessor positions:

  op(u, v) = p           iff  v = J p U  and  Tp(u, p, U)
  Tp(u, p, U)  ("U = (u * (q * p)) * u for some q")
      iff  exists V in {U.1, u.2.2, u.1.2, u.1.1.2.2}:  op(V, u) = U  and  Bp(u, p, V)
  Bp(u, p, V)  ("V = u * (q * p) for some q")
      iff  (V = J u W  and op(u, W) = V and Qp(p, W))                      -- W1: u * W free
        or (op(V, p) = J V p  and op(u, J V p) = V)                        -- W2: q = V, p = (u*(r*V))*u  [= Tp(u, V, p)]
        or (p = J W _  and op(u, W) = V and Qp(p, W))                      -- W3: q * p decodes to W = p.1
  Qp(p, W)     ("W = q * p for some q")
      iff  exists q in {W.1, p.2.2, p.1.2, p.1.1.2.2}:  op(q, p) = W

Least fixed point: a nested question that needs itself is answered "no fire" (cycle counter reported).
"""
import sys, os, json, random, time, itertools
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
sys.setrecursionlimit(100000)
import closedform as cf
import fuzz as fz
import freetest2 as ft
from freemodel import normalise, catalog, pvars, size, rand_term
from laws import parse_eq

def dual_pat(p):
    return p if isinstance(p, str) else (dual_pat(p[1]), dual_pat(p[0]))

EQ = 38316
src = open(os.path.join(HERE, 'gen', 'chk%d.py' % EQ), encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns)
oldrules = ns['rules']
orig = normalise(parse_eq(catalog()[EQ]))
law = ('x', dual_pat(orig[1]))
A, B = law[1]

def a1(t): return t[1] if t[0] == 'J' else t
def a2(t): return t[2] if t[0] == 'J' else t
def J(a, b): return ('J', a, b)

def show(t):
    if t == 'recursion': return t
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))

class Rec:
    def __init__(self):
        self.memo = {}; self.inprog = set(); self.cyc = 0; self.fires = 0; self.branch = {}
    def op(self, u, v):
        key = (u, v)
        m = self.memo.get(key)
        if m is not None: return m
        if key in self.inprog:
            self.cyc += 1; return J(u, v)
        self.inprog.add(key)
        res = J(u, v)
        if v[0] == 'J':
            if self.Tp(u, v[1], v[2]):
                res = v[1]; self.fires += 1
        self.inprog.discard(key)
        self.memo[key] = res
        return res
    def Tp(self, u, p, U):
        cands = [a1(U), a2(a2(u)), a2(a1(u)), a2(a2(a1(a1(u))))]
        seen = []
        for i, V in enumerate(cands):
            if V in seen: continue
            seen.append(V)
            if self.op(V, u) == U and self.Bp(u, p, V):
                self.branch['V%d' % i] = self.branch.get('V%d' % i, 0) + 1
                return True
        return False
    def Bp(self, u, p, V):
        if V[0] == 'J' and V[1] == u:
            W = V[2]
            if self.op(u, W) == V and self.Qp(p, W):
                self.branch['W1'] = self.branch.get('W1', 0) + 1; return True
        W = J(V, p)
        if self.op(V, p) == W and self.op(u, W) == V:
            self.branch['W2'] = self.branch.get('W2', 0) + 1; return True
        if p[0] == 'J':
            W = p[1]
            if self.op(u, W) == V and self.Qp(p, W):
                self.branch['W3'] = self.branch.get('W3', 0) + 1; return True
        return False
    def Qp(self, p, W):
        cands = [a1(W), a2(a2(p)), a2(a1(p)), a2(a2(a1(a1(p))))]
        seen = []
        for i, q in enumerate(cands):
            if q in seen: continue
            seen.append(q)
            if self.op(q, p) == W:
                self.branch['q%d' % i] = self.branch.get('q%d' % i, 0) + 1
                return True
        return False
    # --- Closed-compatible interface for deep_tests / fuzz ---
    def evp(self, p, s):
        if isinstance(p, str): return s[p]
        return self.op(self.evp(p[0], s), self.evp(p[1], s))
    def ev(self, e, u, v):
        k = e[0]
        if k == 'U': return u
        if k == 'V': return v
        if k == 'A1':
            t = self.ev(e[1], u, v)
            return None if t is None or t[0] != 'J' else t[1]
        if k == 'A2':
            t = self.ev(e[1], u, v)
            return None if t is None or t[0] != 'J' else t[2]
        if k == 'OP':
            a = self.ev(e[1], u, v); b = self.ev(e[2], u, v)
            return None if a is None or b is None else self.op(a, b)
        if k == 'J':
            a = self.ev(e[1], u, v); b = self.ev(e[2], u, v)
            return None if a is None or b is None else J(a, b)
        raise ValueError(e)

def lawval(C, s):
    return C.op(C.evp(A, s), C.evp(B, s))

def check_triple(C, s):
    try:
        return lawval(C, s) == s['x']
    except RecursionError:
        return 'recursion'

mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
g = lambda i: ('g', i)

if mode in ('fam', 'all'):
    C = Rec()
    fails = []
    def T(u, r, V): return C.op(C.op(u, C.op(r, V)), u)
    # hand-derived coincidence families; each is a triple (x, y, z) that must satisfy the L-form law
    fams = []
    # smallcheck failure of the 3-rule skeleton
    fams.append(('small1', dict(y=g(0), x=J(g(0), g(0)), z=J(J(g(0), J(g(0), g(0))), g(0)))))
    fams.append(('small2', dict(y=g(0), x=J(g(0), g(0)), z=J(J(g(0), J(J(g(0), g(0)), g(0))), g(0)))))
    # (b): y = J U X, X = (V*(q'*U))*V, z = V, x = (y*(r*V))*y, with V big and U tiny
    for U, V, q, r in [(g(0), J(J(g(1), g(2)), g(1)), g(2), g(1)), (g(0), g(1), g(2), g(0)), (J(g(0), g(1)), J(g(2), J(g(1), g(2))), g(0), g(2))]:
        y = J(U, J(J(V, J(q, U)), V)); x = J(J(y, J(r, V)), y); fams.append(('b', dict(x=x, y=y, z=V)))
    # (c): y = J U X with X = Y*V (decode: V = J X (J (J Y (J t X)) Y)), U = J (J V (J t' Y)) V; z = V, x = (y*(r*V))*y
    for X, Y, t, t2, r in [(g(0), g(1), g(2), g(0), g(1)), (J(g(0), g(1)), g(2), g(0), g(1), g(2))]:
        V = J(X, J(J(Y, J(t, X)), Y)); U = J(J(V, J(t2, Y)), V); y = J(U, X); x = J(J(y, J(r, V)), y)
        fams.append(('c', dict(x=x, y=y, z=V)))
    # (f): V' any, V = J (J u (J r' V')) u, p = J V' u, U = J V u, v = J p U: op(u, v) = p  (u = y, p = x)
    for u, Vp, rp in [(g(0), g(1), g(2)), (J(g(0), g(1)), g(2), g(0))]:
        V = J(J(u, J(rp, Vp)), u); p = J(Vp, u)
        # law triple: x = p, y = u, z: need P1 = z*x with op(y, P1) = V: z = V, P1 = J V p, op(u, J V p) = V
        fams.append(('f', dict(x=p, y=u, z=V)))
    # (g): u = J V (J (J V (J t' V)) V), p = J (J (J u (J s V)) u) u, v = J p V: op(u, v) = p; law triple x = p, y = u, z = ?
    for V, tp, s in [(g(0), g(1), g(2)), (J(g(0), g(1)), g(2), g(0))]:
        u = J(V, J(J(V, J(tp, V)), V)); p = J(J(J(u, J(s, V)), u), u)
        # z such that (y*(z*x))*y = V: y*(z*x) = V decode... z = V per derivation (q = V)
        fams.append(('g', dict(x=p, y=u, z=V)))
    # generic sanity
    fams.append(('gen', dict(x=g(0), y=g(1), z=g(2))))
    for name, s in fams:
        ok = check_triple(C, s)
        print('FAM', name, 'ok', ok, {k: size(v) for k, v in s.items()})
        if ok is not True: fails.append((name, s))
        # also report the intermediate products' fire pattern
        x, y, z = s['x'], s['y'], s['z']
        P1 = C.op(z, x); P2 = C.op(y, P1); P3 = C.op(P2, y); P4 = C.op(x, P3); P5 = C.op(y, P4)
        print('    fires: P1', P1 != J(z, x), 'P2', P2 != J(y, P1), 'P3', P3 != J(P2, y), 'P4', P4 != J(x, P3), 'P5', P5 != J(y, P4))
    print('FAM fails', len(fails), 'cycles', C.cyc, 'branches', C.branch, flush=True)
    for name, s in fails: print('  FAIL', name, {k: show(v) for k, v in s.items()}, '->', show(lawval(C, s)))

if mode in ('deep', 'all'):
    for sd in (11, 12, 13, 21):
        C = Rec()
        t0 = time.time()
        t, f = cf.deep_tests(C, law, 3000, 600, sd)
        print('deep seed', sd, 'tested', t, 'fails', len(f), 'cycles', C.cyc, 'fires', C.fires, 'secs', round(time.time() - t0, 1), 'branches', C.branch, flush=True)
        for s, r in f[:3]: print('  FAIL', {k: show(v) for k, v in s.items()}, '->', show(r))
    C = Rec()
    t0 = time.time()
    t, f = fz.fuzz(C, law, oldrules, 12000, seed=5)
    print('fuzz tested', t, 'fails', len(f), 'cycles', C.cyc, 'secs', round(time.time() - t0, 1), 'branches', C.branch, flush=True)
    for s, r in f[:3]: print('  FAIL', {k: show(v) for k, v in s.items()}, '->', show(r))

if mode in ('small', 'all'):
    def terms_upto(maxsize, gens):
        by = {1: [('g', i) for i in range(gens)]}
        for n in range(3, maxsize + 1, 2):
            by[n] = []
            for a in range(1, n - 1, 2):
                b = n - 1 - a
                if b in by:
                    for s in by[a]:
                        for t in by[b]: by[n].append(('J', s, t))
        out = []
        for n in sorted(by): out += by[n]
        return out
    for maxsize, gens in ((9, 1), (5, 2), (7, 2), (11, 1), (5, 3)):
        C = Rec()
        pool = terms_upto(maxsize, gens)
        t0 = time.time(); fails = []; n = 0
        for vals in itertools.product(pool, repeat=3):
            s = dict(zip(['x', 'y', 'z'], vals)); n += 1
            ok = check_triple(C, s)
            if ok is not True: fails.append((s, ok))
        fails.sort(key=lambda f: sum(size(t) for t in f[0].values()))
        print('SMALL maxsize', maxsize, 'gens', gens, 'assignments', n, 'fails', len(fails), 'cycles', C.cyc, 'fires', C.fires, 'secs', round(time.time() - t0, 1), 'branches', C.branch, flush=True)
        for s, r in fails[:4]: print('  FAIL', {k: show(v) for k, v in s.items()}, '->', r if r == 'recursion' else show(lawval(C, s)))
