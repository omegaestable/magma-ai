"""Does a candidate rule set fix the recorded 38316 counterexample?  usage: _x38316_ce2.py set1,set2,..."""
import sys, os
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq
EQ = 38316
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
GEN = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/'
def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
z = g(2); y = J(g(0), J(J(g(2), J(g(1), g(0))), g(2))); x = J(J(y, J(g(3), g(2))), y)
for name in sys.argv[1].split(','):
    ns = {}; exec(open(GEN + '_x38316_rules_%s.py' % name, encoding='utf-8').read(), ns)
    RULES = ns['rules']; C = cf.Closed(law, RULES)
    try:
        a = C.op(z, x); b = C.op(y, a); c = C.op(b, y); d = C.op(x, c); top = C.op(y, d)
        print('%-8s %2d rules  a=%d b=%d c=%d d=%d top=%d  OK=%s' % (name, len(RULES), size(a), size(b), size(c), size(d), size(top), top == x))
    except RecursionError:
        print('%-8s %2d rules  RECURSION' % (name, len(RULES)))
