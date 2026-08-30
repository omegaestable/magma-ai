"""Re-validate F1/F2/CMP/the law with the JUNK VARIABLE VARIED -- the defect that killed RS's pool.
In op(y,x) the component a1 u = y is unconstrained by every rule; vary it over sizes."""
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
g=lambda n:('g',n); J=lambda a,b:('J',a,b)
def show(t,cap=30):
    if size(t)>cap: return '<sz%d>'%size(t)
    return 'g%d'%t[1] if t[0]=='g' else '(%s*%s)'%(show(t[1],9999),show(t[2],9999))
def encB(p,w): return J(w,J(w,J(p,w)))
def deep(n,a=2,b=3):
    t=g(a)
    for i in range(n): t=J(t,g(b))
    return t
JUNKS=[g(9), J(g(9),g(8)), deep(3), deep(7), deep(11), deep(17), deep(25),
       encB(g(9),g(8)), J(deep(9),deep(5))]

def fresh(): return cf.Closed(law,RULES)

# ---------- 1. the LAW itself, DD cell, junk varied ----------
print('== 1. law on the DD cell with the junk variable y = J(JUNK, pa) varied ==')
bad=0; n=0
for junk in JUNKS:
    for pa in (g(5), J(g(5),g(4)), encB(g(5),g(4))):
        for wa in (g(6), J(g(6),g(7)), deep(5,6,7)):
            for w in (g(8), J(g(8),g(7))):
                x=encB(pa,wa); y=J(junk,pa); z=encB(x[2],w)
                C=fresh()
                try:
                    A=C.op(y,x); P=C.op(x,z); Q=C.op(z,P); B=C.op(z,Q); top=C.op(A,B)
                except RecursionError: continue
                n+=1
                if top!=x:
                    bad+=1
                    if bad<=3: print('   FAIL junk sz%d x sz%d z sz%d -> %s'%(size(junk),size(x),size(z),show(top)))
print('   %d instances, %d law failures'%(n,bad))

# ---------- 2. F1 / F2 freeness with junk varied everywhere ----------
print('== 2. F1 (op z (op x z) free) and F2 with junk-varied x,z ==')
pool=[]
for junk in JUNKS:
    for p in (g(0), J(g(0),g(1)), encB(g(0),g(1))):
        pool += [J(junk,p), encB(p,junk), encB(junk,p), J(p,junk),
                 encB(p,g(1)), J(junk,encB(p,g(1)))]
pool += [g(0),g(1),J(g(0),g(1)),encB(g(0),g(1))]
b1=[]; b2=[]; n=0
for x in pool:
    for z in pool:
        if size(x)+size(z)>260: continue
        C=fresh()
        try:
            P=C.op(x,z); Q=C.op(z,P); B=C.op(z,Q)
        except RecursionError: continue
        n+=1
        if Q!=J(z,P): b1.append((x,z,P,Q))
        if B!=J(z,Q): b2.append((x,z,Q,B))
print('   %d (x,z) pairs; F1 violations %d ; F2 violations %d'%(n,len(b1),len(b2)))
for t in b1[:3]: print('    F1 x=%s z=%s P=%s Q=%s'%(show(t[0]),show(t[1]),show(t[2]),show(t[3])))
for t in b2[:3]: print('    F2 x=%s z=%s Q=%s B=%s'%(show(t[0]),show(t[1]),show(t[2]),show(t[3])))
