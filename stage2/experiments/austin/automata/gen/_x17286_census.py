"""rule x chain-product firing census (the 40037 lesson): a rule firing at a product it was not
   derived for is how a validated model turns out false."""
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
TAGS=[r[2] for r in RULES]
g=lambda n:('g',n); J=lambda a,b:('J',a,b)
def encB(p,w): return J(w,J(w,J(p,w)))
def deep(n,a=2,b=3):
    t=g(a)
    for i in range(n): t=J(t,g(b))
    return t
def which(C,u,v):
    """index of the first rule whose guard holds at (u,v), or None"""
    for i,(conds,xr,tag) in enumerate(RULES):
        try:
            if C.check(conds,u,v) and C.ev(xr,u,v) is not None: return i
        except RecursionError: return None
    return None
PROD=['A=op(y,x)','P=op(x,z)','Q=op(z,P)','B=op(z,Q)','top=op(A,B)']
mat={}
JUNKS=[g(9), J(g(9),g(8)), deep(5), deep(13)]
pool=[g(0),g(1),g(2),J(g(0),g(1)),J(g(1),g(0)),encB(g(0),g(1)),encB(g(1),g(0)),
      encB(J(g(0),g(1)),g(2)), J(g(3),encB(g(0),g(1)))]
for junk in JUNKS:
    for p in (g(0),J(g(0),g(1))):
        pool += [J(junk,p), encB(p,junk), J(junk,encB(p,g(1)))]
n=0; fails=0
for x in pool:
    for y in pool:
        for z in pool:
            if size(x)+size(y)+size(z)>200: continue
            C=cf.Closed(law,RULES)
            try:
                A=C.op(y,x); P=C.op(x,z); Q=C.op(z,P); B=C.op(z,Q); top=C.op(A,B)
            except RecursionError: continue
            n+=1
            if top!=x: fails+=1
            for k,(a,b) in enumerate([(y,x),(x,z),(z,P),(z,Q),(A,B)]):
                i=which(C,a,b)
                if i is not None: mat[(i,k)]=mat.get((i,k),0)+1
print('triples: %d, law failures: %d'%(n,fails))
print()
print('%-14s %s'%('rule', ''.join('%-12s'%p.split('=')[0] for p in PROD)))
for i,t in enumerate(TAGS):
    row=''.join('%-12s'%(mat.get((i,k),0) or '.') for k in range(len(PROD)))
    print('R%d %-11s %s'%(i+1,t,row))
print()
print('empty cells (rule never fires at that product in this pool):')
for i,t in enumerate(TAGS):
    for k in range(len(PROD)):
        if (i,k) not in mat: print('   R%d %-12s at %s'%(i+1,t,PROD[k]))
