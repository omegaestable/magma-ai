"""Validation driver for the quotient-carrier models.

check(M_factory, LAW, ...) runs
  (a) exhaustive over the law's variables on term pools (with the E/Q constructors present),
      splitting off any variable the model makes irrelevant;
  (b) deep random tests on several seeds;
  (c) closure fuzz + critical-pair fuzz;
and prints a de-duplicated failure list keyed on the *essential* variables.
"""
import sys, os, itertools, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qmod
from qmod import Model, E, sz, show, terms_upto, rand_term, pvars, deep, closure_fuzz, critical_fuzz


def ev(M, p, s):
    if isinstance(p, str):
        return s[p]
    return M.op(ev(M, p[0], s), ev(M, p[1], s))


def exh_pairs(M, law, essential, fixed, pools, limit=8):
    """exhaustive over `essential` variables drawn from the given pools (one pool per variable);
    the other variables are set from `fixed`."""
    fails = []
    n = 0
    for vals in itertools.product(*pools):
        s = dict(zip(essential, vals))
        s.update(fixed)
        n += 1
        if n % 100000 == 0 and len(M.memo) > 400000:
            M.memo.clear()
        try:
            r = ev(M, law[1], s)
        except RecursionError:
            fails.append((dict(s), 'recursion'))
            continue
        if r != s[law[0]]:
            fails.append((dict(s), r))
            if len(fails) >= limit:
                break
    return n, fails


def report(tag, n, fails, secs):
    print('%-22s n=%-10d fails=%-5d  %.1fs' % (tag, n, len(fails), secs), flush=True)
    seen = set()
    for s, r in fails[:8]:
        k = tuple(sorted((a, show(b)) for a, b in s.items()))
        if k in seen:
            continue
        seen.add(k)
        print('    FAIL ' + '  '.join('%s=%s' % (a, show(b)) for a, b in sorted(s.items())),
              '->', show(r) if r != 'recursion' else r, flush=True)


def check(Mf, law, essential, irrelevant, sizes=((7, 1), (5, 2), (5, 3)), big=(9, 1, 5),
          deepN=20000, seeds=(3, 4, 5), fuzzN=12000, verbose=True):
    allv = pvars(law[1])
    ok = True
    # irrelevance of the square variable: op(z,z) must be one fixed element
    M = Mf()
    vals = set(M.op(t, t) for t in terms_upto(7, 2))
    print('squares op(z,z) over %d terms -> %d distinct value(s)%s'
          % (len(terms_upto(7, 2)), len(vals),
             ': ' + str([show(v) for v in vals]) if len(vals) <= 3 else ''), flush=True)
    for ms, g in sizes:
        pool = terms_upto(ms, g)
        M = Mf()
        t0 = time.time()
        fixed = {v: ('g', 0) for v in irrelevant}
        n, f = exh_pairs(M, law, essential, fixed, [pool] * len(essential))
        report('exh<=%d/%dgen' % (ms, g), n, f, time.time() - t0)
        ok &= not f
    if big:
        ms, g, small = big
        big_pool = terms_upto(ms, g)
        small_pool = terms_upto(small, g)
        for i in range(len(essential)):
            pools = [small_pool] * len(essential)
            pools[i] = big_pool
            M = Mf()
            t0 = time.time()
            n, f = exh_pairs(M, law, essential, {v: ('g', 0) for v in irrelevant}, pools)
            report('exh %s<=%d rest<=%d' % (essential[i], ms, small), n, f, time.time() - t0)
            ok &= not f
    for sd in seeds:
        t0 = time.time()
        n, f = deep(Mf(), law, deepN, sd)
        report('deep seed%d' % sd, n, f, time.time() - t0)
        ok &= not f
        t0 = time.time()
        n, f = closure_fuzz(Mf(), law, fuzzN, sd + 100)
        report('closure seed%d' % sd, n, f, time.time() - t0)
        ok &= not f
        t0 = time.time()
        n, f = critical_fuzz(Mf(), law, fuzzN, sd + 200)
        report('critical seed%d' % sd, n, f, time.time() - t0)
        ok &= not f
    print('VALIDATED' if ok else 'FAILED', flush=True)
    return ok
