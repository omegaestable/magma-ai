"""Targeted case census: build Z (and Y, x) as encodings so the chain products decode."""
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
import closedform as cf
from freemodel import size

RULES = gen_rules()

def sh(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(' + sh(t[1]) + '*' + sh(t[2]) + ')'

def census(rules, N=4000, seed=11, maxsz=90, verbose=True):
    C = cf.Closed(LAW, rules)
    def isfree(r, a, b):
        return r[0] == 'J' and r[1] == a and r[2] == b
    def chain(x, Y, Z):
        s1 = C.op(x, Z); s2 = C.op(s1, Z); s3 = C.op(Y, s2); s4 = C.op(s3, Z); top = C.op(Y, s4)
        pat = ''.join('F' if isfree(r, a, b) else 'D'
                      for r, a, b in ((s1, x, Z), (s2, s1, Z), (s3, Y, s2), (s4, s3, Z)))
        return pat, top
    def enc(Y, x, Z):
        # the free-shape encoding: (Y * ((x*Z)*Z)) * Z
        return ('J', ('J', Y, ('J', ('J', x, Z), Z)), Z)
    random.seed(seed)
    pool = [('g', i) for i in range(4)]
    cnt = collections.Counter(); bad = collections.Counter(); ex = {}
    for it in range(N):
        # half the time build a fresh encoding and add it
        if random.random() < 0.5 and len(pool) < 3000:
            a, b, c = (random.choice(pool) for _ in range(3))
            t = enc(a, b, c)
            if size(t) <= maxsz:
                pool.append(t)
        x, Y, Z = (random.choice(pool) for _ in range(3))
        try:
            pat, top = chain(x, Y, Z)
        except RecursionError:
            continue
        cnt[pat] += 1
        if top != x:
            bad[pat] += 1
            ex.setdefault(pat, (x, Y, Z))
    if verbose:
        for p in sorted(cnt, key=lambda p: -cnt[p]):
            print('%-6s total %6d  FAIL %6d' % (p, cnt[p], bad[p]))
        print()
        for p, (x, Y, Z) in sorted(ex.items()):
            print(p, ' x=', sh(x), '\n     Y=', sh(Y), '\n     Z=', sh(Z))
    return cnt, bad, ex

if __name__ == '__main__':
    census(RULES)
