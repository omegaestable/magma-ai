"""Empirical test of the RELOCATION lemma for the 5-rule 11081 model.

For every pair (u,v) that the whole validator battery ever evaluated and for which some branch fires,
check that at least one of
  (alpha)  tg (a2 (a1 v)) = 2  and  op (a1 (a2 (a1 v))) v  fires
  (beta)   tg (a2 v) = 2  and  op (a2 (a2 v)) v  fires  and  a2 (a1 v) = op (a2 (a2 v)) (a1 (a1 v))
holds, and report the per-branch breakdown of the ones that satisfy neither.
"""
import sys, collections, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen, fuzz as fz, smallcheck as sc
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 11081
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ,
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}
exec(src, ns)
allrules = ns['rules']
rules = [allrules[i - 1] for i in (1, 2, 4, 8, 9)]


def branch(C, u, v):
    for i, (conds, x, tag) in enumerate(C.rules):
        if C.check(conds, u, v):
            if C.ev(x, u, v) is not None:
                return i + 1
    return 0


def a1(t):
    return t[1] if t[0] == 'J' else t


def a2(t):
    return t[2] if t[0] == 'J' else t


def isJ(t):
    return t[0] == 'J'


def fires(C, u, v):
    return branch(C, u, v) != 0


brk = collections.Counter()
bad = []
tot = collections.Counter()
t0 = time.time()
for name, mk in (('exh9', lambda C: sc.exhaustive(C, law, 9, 1, limit=25)),
                 ('exh5', lambda C: sc.exhaustive(C, law, 5, 2, limit=25)),
                 ('deep3', lambda C: cf.deep_tests(C, law, 3000, 240, 3)),
                 ('fuzz3', lambda C: fz.fuzz(C, law, rules, 12000, seed=103)),
                 ('clos3', lambda C: fz.closure_fuzz(C, law, 12000, seed=203)),
                 ('crit3', lambda C: fz.critical_fuzz(C, law, 12000, seed=303)),
                 ('fuzz4', lambda C: fz.fuzz(C, law, rules, 12000, seed=104)),
                 ('clos4', lambda C: fz.closure_fuzz(C, law, 12000, seed=204)),
                 ('crit4', lambda C: fz.critical_fuzz(C, law, 12000, seed=304)),
                 ('fuzz5', lambda C: fz.fuzz(C, law, rules, 12000, seed=105)),
                 ('clos5', lambda C: fz.closure_fuzz(C, law, 12000, seed=205)),
                 ('crit5', lambda C: fz.critical_fuzz(C, law, 12000, seed=305))):
    C = cf.Closed(law, rules)
    mk(C)
    pairs = list(C.memo.keys())
    for (u, v) in pairs:
        b = branch(C, u, v)
        if not b:
            continue
        tot[b] += 1
        w = a1(a2(a1(v)))
        alpha = isJ(a1(v)) and isJ(a2(a1(v))) and fires(C, w, v)
        zz = a2(a2(v))
        beta = (isJ(v) and isJ(a2(v)) and isJ(a1(v)) and fires(C, zz, v)
                and a2(a1(v)) == C.op(zz, a1(a1(v))))
        if not (alpha or beta):
            brk[b] += 1
            if len(bad) < 5:
                bad.append((b, u, v))
    print('%-6s pairs=%d  %.0fs' % (name, len(pairs), time.time() - t0), flush=True)

print('branch firing totals :', dict(tot))
print('neither alpha nor beta:', dict(brk))
for b, u, v in bad:
    print('  branch', b, 'sizes u=%d v=%d' % (size(u), size(v)))
