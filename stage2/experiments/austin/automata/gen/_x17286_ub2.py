"""RS on a RICH source of decoded pairs: constructed encodings + codes of codes."""
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
def show(t,cap=34):
    if size(t)>cap: return '<sz%d>'%size(t)
    return 'g%d'%t[1] if t[0]=='g' else '(%s*%s)'%(show(t[1],9999),show(t[2],9999))
def mk1(w,z): return J(z,J(z,J(w,z)))
def mk2(w,z): return J(z,J(z,op(w,z)))
def mk3(w,z): return J(z,op(z,op(w,z)))
base=[g(0),g(1),g(2),J(g(0),g(1)),J(g(1),g(0)),J(g(0),g(0)),J(g(2),J(g(0),g(1)))]
pool=list(base)
for w in base:
    for z in base[:5]:
        for mk in (mk1,mk2,mk3):
            try:
                t=mk(w,z)
                if size(t)<=140: pool.append(t)
            except RecursionError: pass
lvl2=[]
for w in pool[:30]:
    for z in base[:3]:
        try:
            t=mk1(w,z)
            if size(t)<=200: lvl2.append(t)
        except RecursionError: pass
pool += lvl2
# also the J(a1 P, P) shapes that R7 produces
for t in list(pool[:60]):
    if t[0]=='J': pool.append(J(t[1],t))
print('pool',len(pool),flush=True)
n=0; badRS=[]; badMax=[]
for u in pool:
    for v in pool:
        if size(u)+size(v)>300: continue
        try: r=op(u,v)
        except RecursionError: continue
        if r==J(u,v): continue
        n+=1
        if not (size(r)<size(v)): badRS.append((u,v,r))
        if not (size(r)<=max(size(u),size(v))): badMax.append((u,v,r))
print('decoded pairs:',n)
print('RS  (sz r < sz v)  : %d violations'%len(badRS))
for t in badRS[:5]: print('    u=%s v=%s r=%s  sz %d/%d/%d'%(show(t[0]),show(t[1]),show(t[2]),size(t[0]),size(t[1]),size(t[2])))
print('RSZ (sz r <= max)  : %d violations'%len(badMax))
for t in badMax[:5]: print('    u=%s v=%s r=%s  sz %d/%d/%d'%(show(t[0]),show(t[1]),show(t[2]),size(t[0]),size(t[1]),size(t[2])))
