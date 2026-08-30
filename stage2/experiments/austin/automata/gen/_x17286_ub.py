"""Is a decoded result always smaller than the RIGHT argument?  (32281's RS, for this model)"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
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
def terms(maxsz,gens):
    out={1:[g(i) for i in range(gens)]}
    for n in range(2,maxsz+1):
        cur=[]
        for a in range(1,n):
            b=n-1-a
            if b<1: continue
            for t1 in out.get(a,()):
                for t2 in out.get(b,()): cur.append(J(t1,t2))
        out[n]=cur
    return [t for n in sorted(out) for t in out[n]]
T=terms(9,2)
n=0; badRS=[]; badUB=[]; badMax=[]
for u in T:
    for v in T:
        if size(u)+size(v)>13: continue
        try: r=op(u,v)
        except RecursionError: continue
        if r==J(u,v): continue
        n+=1
        if not (size(r)<size(v)): badRS.append((u,v,r))
        if u[0]=='J' and r==u[2] and not (size(r)<size(v)): badUB.append((u,v,r))
        if not (size(r)<=max(size(u),size(v))): badMax.append((u,v,r))
print('decoded pairs:', n)
print('RS  (sz r < sz v)              : %d violations' % len(badRS))
for t in badRS[:4]: print('    u=%s v=%s r=%s'%(show(t[0]),show(t[1]),show(t[2])))
print('UB  (u-side decode, sz r < sz v): %d violations' % len(badUB))
for t in badUB[:4]: print('    u=%s v=%s r=%s'%(show(t[0]),show(t[1]),show(t[2])))
print('RSZ (sz r <= max)              : %d violations' % len(badMax))
