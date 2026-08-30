"""Which rule fires at each position of 21864's own evaluation chain?
positions: P=op(z,x)  u=op(y,P)  Q=op(x,y)  v=op(x,Q)  top=op(u,v)
usage: python gen/_p2_chain21864.py [maxsize=7] [gens=2]
"""
import sys, os, itertools, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
import _x21864_rules as RR

T8 = RR.GEN[:5] + [RR.R4c, RR.R5c, RR.RA, RR.R6d, RR.R6e, RR.RB, RR.RB2, RR.RD]
RULES = [r for i, r in enumerate(T8) if i not in {2, 8}]      # the shipped 11
law = normalise(parse_eq(catalog()[21864]))
J = lambda a, b: ('J', a, b)


def terms_upto(ms, gens):
    by = {1: [('g', i) for i in range(gens)]}
    for n in range(3, ms + 1, 2):
        by[n] = []
        for a in range(1, n - 1, 2):
            b = n - 1 - a
            if b in by:
                for s in by[a]:
                    for t in by[b]:
                        by[n].append(('J', s, t))
    out = []
    for n in sorted(by):
        out += by[n]
    return out


def which(C, a, b):
    """index of the rule that fires on (a,b), or None."""
    before = dict(C.fired)
    r = C.op(a, b)
    if r == J(a, b):
        # could still be rule-produced; check by diffing the counter of the OUTER call only
        pass
    for i, (conds, x, tag) in enumerate(RULES):
        if C.check(conds, a, b):
            rr = C.ev(x, a, b)
            if rr is not None:
                return i, r
    return None, r


ms = int(sys.argv[1]) if len(sys.argv) > 1 else 7
gn = int(sys.argv[2]) if len(sys.argv) > 2 else 2
pool = terms_upto(ms, gn)
C = cf.Closed(law, RULES)
cnt = {k: collections.Counter() for k in ('P', 'u', 'Q', 'v', 'top')}
ex = {k: {} for k in cnt}
n = 0
bad = 0
for x, y, z in itertools.product(pool, repeat=3):
    n += 1
    try:
        iP, P = which(C, z, x); iu, u = which(C, y, P)
        iQ, Q = which(C, x, y); iv, v = which(C, x, Q)
        it, top = which(C, u, v)
    except RecursionError:
        continue
    for k, i in (('P', iP), ('u', iu), ('Q', iQ), ('v', iv), ('top', it)):
        tag = 'free' if i is None else 'R%d[%s]' % (i + 1, RULES[i][2])
        cnt[k][tag] += 1
        ex[k].setdefault(tag, (x, y, z))
    if top != x:
        bad += 1
print('pool %d terms (size<=%d, %d gens), %d assignments, %d law failures' % (len(pool), ms, gn, n, bad))
for k in ('P', 'u', 'Q', 'v', 'top'):
    print('  %-4s %s' % (k, dict(cnt[k])))
    for tag, (x, y, z) in ex[k].items():
        if tag != 'free':
            def sh(t):
                return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))
            print('        %-22s first at x=%s y=%s z=%s' % (tag, sh(x), sh(y), sh(z)))
