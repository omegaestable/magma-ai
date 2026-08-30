"""rule x chain-product census, with the CONSTRUCTED families that actually reach each cell."""
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
    for i,(conds,xr,tag) in enumerate(RULES):
        try:
            if C.check(conds,u,v) and C.ev(xr,u,v) is not None: return i
        except RecursionError: return None
    return None
PROD=['A','P','Q','B','top']
TRIPLES=[]
# ffff
TRIPLES.append((g(0),g(1),g(2)))
# Dfff : A decodes (x = encB(pa,wa), y = J(junk,pa)), z a generator
for junk in (g(7), deep(5), deep(13)):
    for pa in (g(5), J(g(5),g(4))):
        TRIPLES.append((encB(pa,g(6)), J(junk,pa), g(2)))
# fDff : P decodes (x = J(q,px), z = encB(px,w)), A free
for q in (g(4), deep(7)):
    for px in (g(5), J(g(5),g(6))):
        TRIPLES.append((J(q,px), g(1), encB(px,g(6))))
# DDff : both decode
for junk in (g(7), deep(5), deep(13), deep(21)):
    for pa in (g(5), J(g(5),g(4)), encB(g(5),g(4))):
        for wa in (g(6), J(g(6),g(7))):
            x=encB(pa,wa); TRIPLES.append((x, J(junk,pa), encB(x[2],g(8))))
# the deep-test diagonal
t=J(g(1),g(0)); s=J(t,J(t,J(g(0),t))); v0=J(s,J(s,g(0)))
TRIPLES.append((v0,v0,v0))
# A-decoded via R2/R3 flavours
x1=g(6); Aq=g(5); tail=J(x1,J(Aq,x1))
TRIPLES.append((J(x1,tail), J(g(7),Aq), encB(tail,g(8))))
TRIPLES.append((J(x1,tail), J(deep(9),Aq), encB(tail,g(8))))
mat={}; n=0; fails=0
for (x,y,z) in TRIPLES:
    C=cf.Closed(law,RULES)
    try:
        A=C.op(y,x); P=C.op(x,z); Q=C.op(z,P); B=C.op(z,Q); top=C.op(A,B)
    except RecursionError: continue
    n+=1
    if top!=x: fails+=1; print('  LAW FAIL x sz%d y sz%d z sz%d'%(size(x),size(y),size(z)))
    for k,(a,b) in enumerate([(y,x),(x,z),(z,P),(z,Q),(A,B)]):
        i=which(C,a,b)
        if i is not None: mat[(i,k)]=mat.get((i,k),0)+1
print('triples: %d, law failures: %d'%(n,fails))
print('%-15s%s'%('rule',''.join('%-8s'%p for p in PROD)))
for i,t2 in enumerate(TAGS):
    print('R%d %-12s%s'%(i+1,t2,''.join('%-8s'%(mat.get((i,k),0) or '.') for k in range(5))))
print()
print('cells where a rule fires at a product it was NOT derived for:')
DERIVED={0:{0,1,4},1:{4},2:{4},3:{4},4:{4},5:{4},6:{4}}
odd=[(i,k) for (i,k) in mat if k not in DERIVED[i]]
for i,k in sorted(odd): print('   R%d %-12s at %s  (%d)'%(i+1,TAGS[i],PROD[k],mat[(i,k)]))
if not odd: print('   none')
