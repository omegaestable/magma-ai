"""Census of the five chain products' free/decoded pattern for law 38316 (cand6, 5 rules).

chain: a = op z x ; b = op y a ; c = op b y ; d = op x c ; top = op y d
prints, for each (aF,bF,cF,dF,topF) pattern, the count and one witness.
usage: python gen/_x38316_cells.py [N] [seed]
"""
import sys, os, random, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
import freetest2 as ft

law = normalise(parse_eq(catalog()[38316]))
sys.path.insert(0, os.path.join(HERE, 'rep38316c'))
import importlib.util
spec = importlib.util.spec_from_file_location("chk", os.path.join(HERE, 'rep38316c', 'chk38316.py'))
# don't exec chk (it runs tests); pull the rules out of the source instead
src = open(os.path.join(HERE, 'rep38316c', 'chk38316.py'), encoding='utf-8').read()
rl = [l for l in src.splitlines() if l.startswith('rules = ')][0]
ns = {}
exec(rl, ns)
rules = ns['rules']
C = cf.Closed(law, rules)


def cls(u, v):
    r = C.op(u, v)
    return ('F' if r == ('J', u, v) else 'D'), r


def chain(x, y, z):
    fa, a = cls(z, x)
    fb, b = cls(y, a)
    fc, c = cls(b, y)
    fd, d = cls(x, c)
    ft_, top = cls(y, d)
    return (fa, fb, fc, fd, ft_), top, (a, b, c, d)


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 11
    random.seed(seed)

    class Shim:
        pass
    F = Shim(); F.vars = ['x', 'y', 'z']; F.rhs = law[1]; F.ev = lambda p, s: C.evp(p, s)
    pool = []
    cnt = collections.Counter()
    wit = {}
    bad = 0
    for i in range(N):
        s = ft.nested_triple(F, pool)
        if max(size(t) for t in s.values()) > 120:
            continue
        x, y, z = s['x'], s['y'], s['z']
        try:
            pat, top, mids = chain(x, y, z)
        except RecursionError:
            continue
        if top != x:
            bad += 1
        cnt[pat] += 1
        if pat not in wit:
            wit[pat] = (x, y, z, mids)
        for t in s.values():
            if size(t) <= 40 and len(pool) < 400:
                pool.append(t)
    print("law failures:", bad)
    for pat, n in cnt.most_common():
        print(''.join(pat), n)
    print()
    for pat, n in cnt.most_common():
        if pat[3] == 'D' or pat[4] == 'F':
            x, y, z, mids = wit[pat]
            print(''.join(pat), n, 'x=', x, ' y=', y, ' z=', z)


if __name__ == '__main__':
    main()


def enum_terms(maxsize, ngen):
    by = {1: [('g', i) for i in range(ngen)]}
    for s in range(2, maxsize + 1):
        cur = []
        for s1 in range(1, s):
            s2 = s - 1 - s1
            if s2 < 1:
                continue
            for a in by.get(s1, []):
                for b in by.get(s2, []):
                    cur.append(('J', a, b))
        by[s] = cur
    out = []
    for s in range(1, maxsize + 1):
        out += by.get(s, [])
    return out


def exhaustive(maxsize=5, ngen=2):
    ts = enum_terms(maxsize, ngen)
    print("terms", len(ts))
    cnt = collections.Counter()
    wit = {}
    bad = 0
    for x in ts:
        for y in ts:
            for z in ts:
                try:
                    pat, top, mids = chain(x, y, z)
                except RecursionError:
                    continue
                if top != x:
                    bad += 1
                cnt[pat] += 1
                if pat not in wit:
                    wit[pat] = (x, y, z, mids)
    print("law failures:", bad)
    for pat, n in cnt.most_common():
        print(''.join(pat), n, ('' if (pat[3] == 'F' and pat[4] == 'D') else
                                ('  x=%s y=%s z=%s' % wit[pat][:3])))
