"""Is RS really true?  Construct the R2 case with a BIG junk a1(a2 u) -- the shape the pool lacked."""
import sys, os
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.dirname(HERE)); sys.path.insert(0,HERE)
sys.setrecursionlimit(30000)
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
EQ=17286
law=normalise(parse_eq(catalog()[EQ]))
BASE=cf.Extractor(law).rules(exist=False)
U=('U',); V=('V',)
A1e=lambda e:('A1',e); A2e=lambda e:('A2',e); OP=lambda a,b:('OP',a,b); JE=lambda a,b:('J',a,b)
P_=A2e(A2e(V)); X_=JE(A1e(P_),P_)
R8b=([('TG',V),('TG',A2e(V)),('EQ',A1e(V),A1e(A2e(V))),('TG',P_),
      ('OPEQ',OP(U,A1e(P_)),A2e(P_)),('OPEQ',OP(X_,A1e(V)),P_)], X_, 'DDb')
RULES=[r for r in BASE if r[2]!='Bs']+[R8b]
C=cf.Closed(law,RULES); op=C.op
g=lambda n:('g',n); J=lambda a,b:('J',a,b)
def show(t,cap=30):
    if size(t)>cap: return '<sz%d>'%size(t)
    return 'g%d'%t[1] if t[0]=='g' else '(%s*%s)'%(show(t[1],9999),show(t[2],9999))
def encB(p,w): return J(w,J(w,J(p,w)))
# r = J(BIG, W2) with op r c = a2 r = W2 via R1, where c = encB(W2, d)
W2 = g(0); d = g(1)
c = encB(W2, d)                       # sz 7
BIG = J(J(J(g(3),g(4)),J(g(5),g(6))), J(J(g(7),g(8)),J(g(2),g(3))))   # sz 15
r = J(BIG, W2)
u = J(g(9), r)
v = J(c, J(c, W2))
print('sz c=%d sz r=%d sz u=%d sz v=%d' % (size(c),size(r),size(u),size(v)))
print('op r c =', show(op(r,c)), ' (want a2 r =', show(W2), ')')
res = op(u,v)
print('op u v =', show(res), 'sz', size(res))
print('a2 u   =', show(r), 'sz', size(r))
print('RS claim  sz(op u v) < sz v :', size(res), '<', size(v), '->', size(res) < size(v))
print('RSZ claim sz(op u v) <= max(sz u, sz v) :', size(res), '<=', max(size(u),size(v)),
      '->', size(res) <= max(size(u),size(v)))
print()
print('is this a genuine model pair?  op u v == a2 u :', res == r)
