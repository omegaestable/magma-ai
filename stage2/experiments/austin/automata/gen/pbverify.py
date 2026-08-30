"""pbverify.py -- INDEPENDENT verification of the quotient-carrier models.

Written from scratch for the synthesis pass: it shares no code with qmod.py / qcheck.py /
nfcore.py / nftest.py / qz_lib.py, so a bug in an angle's own checker cannot hide itself here.
Only the models' `op` functions are imported (they are the artefacts under test).

Usage:  python gen/pbverify.py <model> [quick|full]
  models: tags12073 tags27859 nf12073 nf27859 qz12073
"""
import sys, os, itertools, random, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
sys.setrecursionlimit(300000)

# --------------------------------------------------------------------------- laws
# rhs patterns, mine, transcribed from the catalog strings printed by freemodel.catalog()
#   12073  x = y * (((y * x) * x) * (z * z))
#   27859  x = ((y * (y * x)) * x) * (z * z)
RHS = {
    12073: ('y', ((('y', 'x'), 'x'), ('z', 'z'))),
    27859: ((('y', ('y', 'x')), 'x'), ('z', 'z')),
}
# goals, per row
GOALS = {
    'research_order5_hard_0007': (12073, 28770, (((('y', 'y'), 'y'), 'x'), ('y', 'z'))),
    'research_order5_hard_0022': (12073, 41082, (((((('y', 'y'), 'z'), 'x'), 'x'), 'z'))),
    'research_order5_hard_0050': (27859, 4916, ('y', ('x', ('x', ('y', ('z', 'z')))))),
    'research_order5_hard_0099': (27859, 25964, (('y', (('x', 'x'), 'y')), ('z', 'z'))),
}


# --------------------------------------------------------------------------- models
class Spec:
    def __init__(self, name, eq, op, atoms, unary, binary):
        self.name, self.eq, self.op = name, eq, op
        self.atoms, self.unary, self.binary = atoms, unary, binary
        self._sz = {}

    def sz(self, t):
        r = self._sz.get(t)
        if r is None:
            if len(t) == 3:
                r = 1 + self.sz(t[1]) + self.sz(t[2])
            elif len(t) == 2 and t[0] in self.unary:
                r = 1 + self.sz(t[1])
            else:
                r = 1
            self._sz[t] = r
        return r

    def show(self, t):
        if t[0] == 'g':
            return 'g%d' % t[1]
        if len(t) == 3:
            return '(%s*%s)' % (self.show(t[1]), self.show(t[2]))
        if len(t) == 2 and t[0] in self.unary:
            return '%s[%s]' % (t[0], self.show(t[1]))
        return t[0]


def load(which):
    if which == 'tags12073':
        import q12073e
        m = q12073e.M()
        return Spec('tags12073', 12073, m.op, ['g', ('E',)], (), 'J')
    if which == 'tags27859':
        import q27859
        m = q27859.M()
        return Spec('tags27859', 27859, m.op, ['g', ('E',)], (), 'J')
    if which == 'nf12073':
        import nf12073
        return Spec('nf12073', 12073, nf12073.op, ['g', ('S',)], ('E',), 'J')
    if which == 'nf27859':
        import nf27859
        return Spec('nf27859', 27859, nf27859.op, ['g', ('S',)], (), 'J')
    if which == 'qz12073':
        import qz_m24
        return Spec('qz12073', 12073, qz_m24.op, ['g', ('E',)], ('C',), 'P')
    raise SystemExit('unknown model ' + which)


# --------------------------------------------------------------------------- enumeration
def pool_upto(sp, maxsize, gens):
    base = []
    for a in sp.atoms:
        if a == 'g':
            base += [('g', i) for i in range(gens)]
        else:
            base.append(a)
    by = {1: base}
    for n in range(2, maxsize + 1):
        cur = []
        for c in sp.unary:
            for t in by.get(n - 1, ()):
                cur.append((c, t))
        for a in range(1, n - 1):
            for s in by.get(a, ()):
                for t in by.get(n - 1 - a, ()):
                    cur.append((sp.binary, s, t))
        by[n] = cur
    out = []
    for n in range(1, maxsize + 1):
        out += by[n]
    return out


def ev(sp, p, s):
    if isinstance(p, str):
        return s[p]
    return sp.op(ev(sp, p[0], s), ev(sp, p[1], s))


def rterm(sp, depth, gens, rng):
    if depth <= 0 or rng.random() < 0.33:
        cs = [('g', rng.randrange(gens))]
        for a in sp.atoms:
            if a != 'g':
                cs.append(a)
        return rng.choice(cs)
    if sp.unary and rng.random() < 0.28:
        return (rng.choice(sp.unary), rterm(sp, depth - 1, gens, rng))
    return (sp.binary, rterm(sp, depth - 1, gens, rng), rterm(sp, depth - 1, gens, rng))


# --------------------------------------------------------------------------- tests
def run_exh(sp, pools, label, cap=6):
    """pools = dict var -> list of terms. full product."""
    rhs = RHS[sp.eq]
    vs = ['x', 'y', 'z']
    n = 0
    fails = []
    t0 = time.time()
    for vx in pools['x']:
        for vy in pools['y']:
            for vz in pools['z']:
                s = {'x': vx, 'y': vy, 'z': vz}
                n += 1
                try:
                    got = ev(sp, rhs, s)
                except RecursionError:
                    fails.append((s, 'RECURSION'))
                    if len(fails) >= cap:
                        return n, fails, time.time() - t0
                    continue
                if got != vx:
                    fails.append((s, got))
                    if len(fails) >= cap:
                        return n, fails, time.time() - t0
    return n, fails, time.time() - t0


def run_deep(sp, N, seed, gens=3, depth=4, cap=6):
    rng = random.Random(seed)
    rhs = RHS[sp.eq]
    fails = []
    n = 0
    pool = []
    t0 = time.time()
    for i in range(N):
        s = {}
        for v in ('x', 'y', 'z'):
            if pool and rng.random() < 0.4:
                s[v] = rng.choice(pool)
            else:
                s[v] = rterm(sp, rng.randrange(1, depth + 1), gens, rng)
        mode = rng.random()
        if mode < 0.30:
            # a variable becomes an encoding: the value of the law's rhs on other data
            s0 = {v: rterm(sp, rng.randrange(1, depth), gens, rng) for v in ('x', 'y', 'z')}
            if rng.random() < 0.5:
                s0['y'] = s['y']
            try:
                enc = ev(sp, rhs, s0)
            except RecursionError:
                continue
            s[rng.choice(['x', 'y', 'z'])] = enc
        elif mode < 0.45:
            a, b = rng.sample(['x', 'y', 'z'], 2)
            s[a] = s[b]
        elif mode < 0.55:
            # x := a product of the model's own values
            try:
                s['x'] = sp.op(s['y'], s['z'])
            except RecursionError:
                continue
        n += 1
        try:
            got = ev(sp, rhs, s)
        except RecursionError:
            fails.append((s, 'RECURSION'))
            if len(fails) >= cap:
                break
            continue
        if got != s['x']:
            fails.append((s, got))
            if len(fails) >= cap:
                break
        if len(pool) < 500:
            for v in s.values():
                if sp.sz(v) <= 45:
                    pool.append(v)
            if sp.sz(got) <= 45:
                pool.append(got)
    return n, fails, time.time() - t0


def _subpats(p, acc=None):
    if acc is None:
        acc = []
    if not isinstance(p, str):
        acc.append(p)
        _subpats(p[0], acc)
        _subpats(p[1], acc)
    return acc


def run_idprobe(sp, N, seed, gens=2, cap=6):
    """the test that killed four qz models (and 22591): a variable set to one of the model's own
    CODES -- the value of a proper subterm of the law's rhs, i.e. the encoding whose decode is
    supposed to give the payload back -- nested 1-3 levels, y biased to squares and to products of
    a square, z small.  (Setting x to the whole rhs is useless on a valid model: it returns x.)"""
    rng = random.Random(seed)
    rhs = RHS[sp.eq]
    codes = [p for p in _subpats(rhs) if p is not rhs]
    fails = []
    n = 0
    small = [('g', i) for i in range(gens)]
    for a in sp.atoms:
        if a != 'g':
            small.append(a)
    small += [(sp.binary, ('g', 0), ('g', 0)), (sp.binary, ('g', 0), ('g', 1))]
    t0 = time.time()
    for i in range(N):
        y = rng.choice(small)
        if rng.random() < 0.5:
            y = sp.op(y, y)             # y a square
        if rng.random() < 0.4:
            y = sp.op(y, rng.choice(small))
        z = rng.choice(small)
        x = rng.choice(small)
        for lvl in range(rng.randrange(1, 4)):
            s0 = {'x': x, 'y': y if rng.random() < 0.7 else rng.choice(small),
                  'z': rng.choice(small)}
            try:
                x = ev(sp, rng.choice(codes), s0)
            except RecursionError:
                break
            if sp.sz(x) > 500:
                break
            if rng.random() < 0.3:
                x = sp.op(x, rng.choice(small))
        n += 1
        s = {'x': x, 'y': y, 'z': z}
        try:
            got = ev(sp, rhs, s)
        except RecursionError:
            fails.append((s, 'RECURSION'))
            if len(fails) >= cap:
                break
            continue
        if got != x:
            fails.append((s, got))
            if len(fails) >= cap:
                break
    return n, fails, time.time() - t0


def report(sp, tag, n, fails, dt):
    st = 'OK  ' if not fails else 'FAIL'
    print('  %s %-34s n=%-12d %6.1fs  fails=%d' % (st, tag, n, dt, len(fails)))
    for s, got in fails[:3]:
        print('        x=%s' % sp.show(s['x']))
        print('        y=%s' % sp.show(s['y']))
        print('        z=%s' % sp.show(s['z']))
        print('        got=%s' % (got if isinstance(got, str) else sp.show(got)))
    return not fails


def goals(sp):
    ok = True
    for rid, (eq1, eq2, g) in GOALS.items():
        if eq1 != sp.eq:
            continue
        found = None
        cand = [('g', 0), ('g', 1)]
        for a in sp.atoms:
            if a != 'g':
                cand.append(a)
        for vx in cand:
            for vy in cand:
                for vz in cand:
                    s = {'x': vx, 'y': vy, 'z': vz}
                    try:
                        r = ev(sp, g, s)
                    except RecursionError:
                        continue
                    if r != vx:
                        found = (s, r)
                        break
                if found:
                    break
            if found:
                break
        if found:
            s, r = found
            print('  OK   goal %s (eq2 %d) refuted at x=%s y=%s z=%s -> %s'
                  % (rid, eq2, sp.show(s['x']), sp.show(s['y']), sp.show(s['z']), sp.show(r)))
        else:
            print('  FAIL goal %s (eq2 %d): NO refutation among the atom triples' % (rid, eq2))
            ok = False
    # non-triviality
    a, b = ('g', 0), ('g', 1)
    print('  %s non-trivial: op g0 g1 = %s (!= g0: %s)'
          % ('OK  ', sp.show(sp.op(a, b)), sp.op(a, b) != a))
    return ok


def zfree(sp, gens=2, maxsize=7):
    """the models all put `u = v -> <the square constant>` as the FIRST, unconditional rule, so
    z*z is the same element for every z and the 3-variable law is a 2-variable law.  Verify."""
    p = pool_upto(sp, maxsize, gens)
    vals = set(sp.op(t, t) for t in p)
    print('  %s squares: |{op t t : sz t<=%d, %dgen, %d terms}| = %d  %s'
          % ('OK  ' if len(vals) == 1 else 'FAIL', maxsize, gens, len(p), len(vals),
             sp.show(next(iter(vals))) if len(vals) == 1 else sorted(map(sp.show, vals))[:4]))
    return len(vals) == 1


def main_full(sp, budget=12_000_000):
    """big (x,y) exhaustive sweeps + the mixed-size product, z pinned (justified by zfree)."""
    allok = zfree(sp)
    z1 = [('g', 0)]
    plans = []
    for gens in (1, 2, 3):
        best = None
        for ms in range(3, 14):
            p = pool_upto(sp, ms, gens)
            if len(p) * len(p) <= budget:
                best = (ms, gens, p)
            else:
                break
        if best:
            plans.append(best)
    for ms, gens, p in plans:
        allok &= report(sp, 'FULL exh(x,y) size<=%d/%dgen (pool %d)' % (ms, gens, len(p)),
                        *run_exh(sp, {'x': p, 'y': p, 'z': z1}, ''))
    # the mixed-size product, both orders, pushed as far as the budget allows
    msmall = plans[0][0]
    for mbig in range(msmall + 2, 16):
        pb = pool_upto(sp, mbig, 1)
        pm = pool_upto(sp, msmall, 1)
        if len(pb) * len(pm) > budget:
            break
        last = (mbig, pb, pm)
    mbig, pb, pm = last
    allok &= report(sp, 'FULL mixed x<=%d y<=%d (1gen)' % (mbig, msmall),
                    *run_exh(sp, {'x': pb, 'y': pm, 'z': z1}, ''))
    allok &= report(sp, 'FULL mixed y<=%d x<=%d (1gen)' % (mbig, msmall),
                    *run_exh(sp, {'x': pm, 'y': pb, 'z': z1}, ''))
    for sd in (13571113, 88008800):
        allok &= report(sp, 'FULL deep seed %d' % sd, *run_deep(sp, 40000, sd, depth=5))
    return allok


def main():
    which = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else 'quick'
    sp = load(which)
    print('=== %s (law %d) mode=%s' % (sp.name, sp.eq, mode))
    if mode == 'full':
        ok = main_full(sp)
        print('  ---- goal refutations')
        ok &= goals(sp)
        print('=== %s FULL: %s' % (sp.name, 'ALL PASS' if ok else 'FAILURES ABOVE'))
        return
    allok = True

    # 1. full 3-variable exhaustive over the WHOLE inductive carrier
    for ms, gens in ((4, 2), (5, 1)) if mode == 'quick' else ((4, 2), (5, 1), (5, 2), (6, 1)):
        p = pool_upto(sp, ms, gens)
        allok &= report(sp, 'exh3 size<=%d/%dgen (pool %d)' % (ms, gens, len(p)),
                        *run_exh(sp, {'x': p, 'y': p, 'z': p}, ''))

    # 2. (x,y) exhaustive at larger size, z over a small pool
    zsmall = pool_upto(sp, 3, 1)
    for ms, gens in ((7, 1), (5, 2)) if mode == 'quick' else ((8, 1), (6, 2), (5, 3)):
        p = pool_upto(sp, ms, gens)
        allok &= report(sp, 'exh(x,y) size<=%d/%dgen z<=3 (pool %d)' % (ms, gens, len(p)),
                        *run_exh(sp, {'x': p, 'y': p, 'z': zsmall}, ''))

    # 3. THE MIXED SWEEP: one variable large, another medium (rail 37 / the shape that killed
    #    22591 and the four qz models). Both orders.
    big, med = (9, 5) if mode == 'quick' else (11, 6)
    pb, pm = pool_upto(sp, big, 1), pool_upto(sp, med, 1)
    allok &= report(sp, 'mixed x<=%d y<=%d (1gen)' % (big, med),
                    *run_exh(sp, {'x': pb, 'y': pm, 'z': zsmall}, ''))
    allok &= report(sp, 'mixed y<=%d x<=%d (1gen)' % (big, med),
                    *run_exh(sp, {'x': pm, 'y': pb, 'z': zsmall}, ''))

    # 4. deep random, FRESH seeds never used by any angle
    for sd in (20260830, 771131, 4242424):
        allok &= report(sp, 'deep seed %d' % sd, *run_deep(sp, 25000, sd))

    # 5. identity probe
    for sd in (515151, 909091):
        allok &= report(sp, 'idprobe seed %d' % sd, *run_idprobe(sp, 20000, sd))

    print('  ---- goal refutations')
    allok &= goals(sp)
    print('=== %s: %s' % (sp.name, 'ALL PASS' if allok else 'FAILURES ABOVE'))


if __name__ == '__main__':
    main()
