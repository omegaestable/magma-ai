"""_x17286_inst.py -- dissect the x=y=z failing instance for law 17286."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
sys.setrecursionlimit(30000)
import closedform as cf, leangen
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 17286
orig = normalise(parse_eq(catalog()[EQ]))
law = orig
RULES = cf.Extractor(law).rules(exist=False)

g = lambda n: ('g', n)
J = lambda a, b: ('J', a, b)


def show(t, cap=200):
    if size(t) > cap: return '<sz%d>' % size(t)
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1], 9999), show(t[2], 9999))


t = J(g(1), g(0))
s = J(t, J(t, J(g(0), t)))
v = J(s, J(s, g(0)))
print('v =', show(v), 'sz', size(v))

# --- closed model, with the rule that fires at each product
C = cf.Closed(law, RULES)


def opt(a, b):
    before = dict(C.fired)
    r = C.op(a, b)
    after = dict(C.fired)
    d = [k for k in after if after[k] != before.get(k, 0)]
    return r, d


for name, (a, b) in [('A=op(y,x)', (v, v))]:
    pass

A = C.op(v, v)
print('A = op(v,v) =', show(A), ' free?', A == J(v, v))
P = A
Q = C.op(v, P)
print('Q = op(v,A) =', show(Q), ' free?', Q == J(v, P))
B = C.op(v, Q)
print('B = op(v,Q) =', show(B), ' free?', B == J(v, Q))
top = C.op(A, B)
print('top = op(A,B) =', show(top), ' == v?', top == v)
print('fired rule counts:', C.fired)

# which rule fires on (v,v)?
for i, (conds, xr, tag) in enumerate(RULES):
    C2 = cf.Closed(law, RULES)
    ok = C2.check(conds, v, v)
    print('  rule%d [%s] on (v,v): %s -> %s' % (i + 1, tag, ok, show(C2.ev(xr, v, v)) if ok else '-'))

print()
# --- semantic model
for md in (400, 2000):
    F = fm.Free(law, maxdepth=md)
    try:
        sA = F.op(v, v)
        sQ = F.op(v, sA)
        sB = F.op(v, sQ)
        stop = F.op(sA, sB)
        print('SEM(maxdepth=%d): A=%s Q=%s B=%s top=%s ok=%s' % (
            md, show(sA, 30), show(sQ, 30), show(sB, 30), show(stop, 30), stop == v))
        print('   conflicts=%d tainted=%d escapes=%d spurious=%d unverified=%d cycles=%d bail=%d rbail=%d cuts=%d junk_used=%d' %
              (len(F.conflicts), F.tainted, F.escapes, F.spurious, F.unverified, F.cycles, F.bail, F.rbail, F.cuts, F.junk_used))
    except Exception as e:
        print('SEM(%d) ERR' % md, repr(e)[:200])

# --- does the law hold in the semantic model for the *pattern* evaluation?
F = fm.Free(law)
s_assign = {'x': v, 'y': v, 'z': v}
try:
    lhsv = F.ev(law[1], s_assign)
    print('F.ev(rhs pattern) =', show(lhsv, 30), 'ok=', lhsv == v)
except Exception as e:
    print('F.ev ERR', repr(e)[:200])
