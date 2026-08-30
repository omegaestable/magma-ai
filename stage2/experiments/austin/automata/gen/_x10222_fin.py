"""Exhaustive small finite-model search for eq1 = 10222 (x = y*((x*y)*((z*y)*y))) and, for any model
found, a check of eq2 = 20034 (x = (y*y)*((z*(x*x))*z)).

DFS over the n x n table with pruning: after each assignment, every law instance whose evaluation is
fully determined must hold.
"""
import sys, os, itertools, time

def parse(s):
    lhs, rhs = s.split('=')
    def split_top(t):
        d = 0
        for i, ch in enumerate(t):
            if ch == '(': d += 1
            elif ch == ')': d -= 1
            elif ch == '*' and d == 0:
                return t[:i], t[i + 1:]
        return None
    def p(t):
        t = t.strip()
        sp = split_top(t)
        if sp is not None:
            return (p(sp[0]), p(sp[1]))
        if t.startswith('(') and t.endswith(')'):
            return p(t[1:-1])
        return t
    return p(lhs), p(rhs)

EQ1 = "x = y * ((x * y) * ((z * y) * y))"
EQ2 = "x = (y * y) * ((z * (x * x)) * z)"

def vars_of(t, acc=None):
    if acc is None: acc = []
    if isinstance(t, str):
        if t not in acc: acc.append(t)
    else:
        vars_of(t[0], acc); vars_of(t[1], acc)
    return acc

def ev(t, s, T, n):
    if isinstance(t, str): return s[t]
    a = ev(t[0], s, T, n)
    if a is None: return None
    b = ev(t[1], s, T, n)
    if b is None: return None
    return T[a * n + b]

def search(n, law, limit=1, nontrivial=True):
    L, R = law
    vs = vars_of(R)
    T = [None] * (n * n)
    cells = [(i, j) for i in range(n) for j in range(n)]
    out = []
    def ok():
        for vals in itertools.product(range(n), repeat=len(vs)):
            s = dict(zip(vs, vals))
            r = ev(R, s, T, n)
            if r is None: continue
            if r != s[L]: return False
        return True
    def rec(k):
        if len(out) >= limit: return
        if k == len(cells):
            if not nontrivial or len(set(T)) > 1:
                out.append(list(T))
            return
        i, j = cells[k]
        for v in range(n):
            T[i * n + j] = v
            if ok(): rec(k + 1)
            T[i * n + j] = None
    rec(0)
    return out

def holds(law, T, n):
    L, R = law
    vs = vars_of(R)
    for vals in itertools.product(range(n), repeat=len(vs)):
        s = dict(zip(vs, vals))
        if ev(R, s, T, n) != s[L]: return False
    return True

if __name__ == '__main__':
    law1 = parse(EQ1); law2 = parse(EQ2)
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    for n in range(2, nmax + 1):
        t0 = time.time()
        ms = search(n, law1, limit=3)
        print('n=%d nontrivial models: %d  (%.1fs)' % (n, len(ms), time.time() - t0), flush=True)
        for T in ms:
            print('   T =', T, ' eq2 holds:', holds(law2, T, n), flush=True)
