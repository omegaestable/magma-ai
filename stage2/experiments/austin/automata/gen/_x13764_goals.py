import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x13764_lab import *
import _x13764_v9 as V

op, opr = mk_op(V.rules)

G = [('g', 0), ('g', 1), ('g', 2)]

# goals as nested tuples over variable names
GOALS = {
    22455: ('x', (('y', ('x', 'x')), (('y', 'z'), 'y'))),      # x = (y*(x*x))*((y*z)*y)
    20034: ('x', (('y', 'y'), (('z', ('x', 'x')), 'z'))),      # x = (y*y)*((z*(x*x))*z)
    22818: ('x', (('y', ('z', 'y')), (('x', 'x'), 'y'))),      # x = (y*(z*y))*((x*x)*y)
}


def ev(p, s, flip):
    if isinstance(p, str):
        return s[p]
    a = ev(p[0], s, flip); b = ev(p[1], s, flip)
    return op(b, a) if flip else op(a, b)


def law_ok(flip):
    """sanity: the served magma satisfies eq1 in its own orientation"""
    # the modelled (dual L-form) law is always  x = y*((x*((z*y)*y))*y) under `op`
    bad = 0
    for x in G:
        for y in G:
            for z in G:
                r, _ = chain(op, x, y, z)
                if r != x:
                    bad += 1
    return bad


print('law violations on generators:', law_ok(False))

for gid, (lhsv, rhsp) in GOALS.items():
    flip = (gid == 22818)
    found = None
    for tup in itertools.product(range(3), repeat=3):
        s = {'x': ('g', tup[0]), 'y': ('g', tup[1]), 'z': ('g', tup[2])}
        if s[lhsv] != ev(rhsp, s, flip):
            found = (s, ev(rhsp, s, flip))
            break
    print(gid, 'flip=%s' % flip, 'refuting:', None if not found else
          {k: show(v) for k, v in found[0].items()}, '->', None if not found else show(found[1]))
