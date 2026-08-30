# -*- coding: utf-8 -*-
"""Find generators refuting eq2=20034  x = (y*y)*((z*(x*x))*z)  in the cand4 magma
(served op is FLIPPED: a*b = op b a), and print the exact `change` line for `theorem rhs`."""
import sys, itertools
D = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D)
import closedform as cf, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq
law = ('x', leangen.dual_pat(normalise(parse_eq(catalog()[38316]))[1]))
ns = {}; exec(open(D + '/gen/_x38316_rules_cand4.py', encoding='utf-8').read(), ns)
C = cf.Closed(law, ns['rules'])
g = lambda n: ('g', n)
star = lambda a, b: C.op(b, a)          # the served magma
for A, B, Cc in itertools.product(range(3), repeat=3):
    x, y, z = g(A), g(B), g(Cc)
    rhs = star(star(y, y), star(star(z, star(x, x)), z))
    if rhs != x:
        print('x=g%d y=g%d z=g%d  ->  rhs size %d, != x' % (A, B, Cc, size(rhs)))
        print('  have := h (g %d) (g %d) (g %d)' % (A, B, Cc))
        print('  change ¬ g %d = op (op (g %d) (op (op (g %d) (g %d)) (g %d))) (op (g %d) (g %d))'
              % (A, Cc, A, A, Cc, B, B))
        break
