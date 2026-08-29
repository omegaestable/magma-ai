import sys, os, json
sys.path.insert(0, r'c:\Users\nacho\Documents\GitHub\magma-ai\stage2\experiments\austin\automata')
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
import trace as tr

eq = 6912
cat = catalog(); orig = normalise(parse_eq(cat[eq]))
law = orig
rules = tr.load_rules(eq)

U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
a1u = A1(U); a2u = A2(U)
a1a1u = A1(a1u); a2a1u = A2(a1u)
a1a2u = A1(a2u); a2a2u = A2(a2u)
a1a2a2u = A1(a2a2u); a2a2a2u = A2(a2a2u)
a2v = A2(V)
deep3 = ([
  ('TG', V), ('EQ', U, A1(V)), ('TG', U), ('TG', a1u),
  ('EQ', a1a1u, a2a1u), ('TG', a2u), ('EQ', a1a2u, a1a1u),
  ('TG', a2a2u), ('EQ', a1a2a2u, a2a2a2u),
  ('EQ', a2v, a1a1u),
], a2a2u, 'DEEP3~')
deep4 = ([
  ('TG', V), ('EQ', U, A1(V)), ('TG', U), ('TG', a2u),
  ('TG', a1a2u),
  ('EQ', a1a2u, a2a2u),
  ('EQ', a2v, a1a2u),
], a1a2u, 'DEEP4~')
rules = rules[:10]+[deep3,deep4]+rules[10:]
C = cf.Closed(law, rules)

def g(n): return ('g', n)
def J(a,b): return ('J', a, b)

p = J(g(0),g(1)); q = J(g(0),g(2))
y = J(p,q)
z = J(y,y)
x = J(J(y,z),z)
s = dict(y=y, z=z, x=x)
print('INSTANCE', {k: tr.show(v) for k,v in s.items()})

T = tr.Tracing(law, rules)
A, B = law[1]
def evt(p_):
    if isinstance(p_, str): return s[p_]
    a, b = evt(p_[0]), evt(p_[1])
    T.trace_on = True; T.log=[]; T.cuts=[]
    r = T.op(a,b)
    T.trace_on = False
    which = T.log[-1][2] if T.log else None
    print('  %-30s = %s   [%s]' % (str(p_), tr.show(r) if size(r)<100 else '<size %d>'%size(r), 'free' if which is None else 'R%d %s'%(which+1, rules[which][2])))
    return r
u = evt(A); v = evt(B)
T.trace_on = True; T.log=[]
r = T.op(u,v); T.trace_on=False
which = T.log[-1][2] if T.log else None
print('  FINAL op(A,B) =', tr.show(r) if size(r)<100 else '<size %d>'%size(r), ' expected x =', tr.show(s['x']) if size(s['x'])<100 else '<size %d>'%size(s['x']), ' [', 'free' if which is None else 'R%d %s'%(which+1, rules[which][2]), ']')
print()
print("shape check: is x == J(J(y,z),z)?", s['x']==J(J(y,z),z))
print("size y", size(y), "size z", size(z), "size x", size(x))
