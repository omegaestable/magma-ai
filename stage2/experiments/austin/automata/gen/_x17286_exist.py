"""_x17286_exist.py -- does the exist-mode extraction close the hole?"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
sys.setrecursionlimit(30000)
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 17286
law = normalise(parse_eq(catalog()[EQ]))
g = lambda n: ('g', n)
J = lambda a, b: ('J', a, b)
t = J(g(1), g(0)); s = J(t, J(t, J(g(0), t))); v = J(s, J(s, g(0)))


def show(x, cap=40):
    if size(x) > cap: return '<sz%d>' % size(x)
    return 'g%d' % x[1] if x[0] == 'g' else '(%s*%s)' % (show(x[1], 9999), show(x[2], 9999))


def chain(rules, x, y, z):
    C = cf.Closed(law, rules)
    A = C.op(y, x); P = C.op(x, z); Q = C.op(z, P); B = C.op(z, Q); top = C.op(A, B)
    return top, ''.join('D' if b else 'f' for b in (A != J(y, x), P != J(x, z), Q != J(z, P), B != J(z, Q)))


for exist in (False, True):
    R = cf.Extractor(law).rules(exist=exist)
    print('exist=%s: %d rules' % (exist, len(R)))
    for i, r in enumerate(R, 1):
        print('   R%d %s' % (i, cf.show_rule(r)))
    top, cell = chain(R, v, v, v)
    print('   diagonal v: cell=%s top=%s want=%s -> %s' % (cell, show(top), show(v), top == v))
    print()
