import sys, os
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 34889
cat = catalog()
orig = normalise(parse_eq(cat[EQ]))
print('cat text        :', cat[EQ])
print('orig normalised :', orig)
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
print('dualized        :', dualized)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
print('law modelled    :', law)


def pp(p):
    if isinstance(p, str):
        return p
    return '(%s*%s)' % (pp(p[0]), pp(p[1]))


print('law text        : x = %s' % pp(law[1]))
