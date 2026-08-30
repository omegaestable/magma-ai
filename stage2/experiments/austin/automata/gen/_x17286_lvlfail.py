"""print the level-k descent failures for 17286 in full."""
import sys, os
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.dirname(HERE)); sys.path.insert(0,HERE)
sys.setrecursionlimit(40000)
import closedform as cf
import freemodel as fm
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
def encB(p,w): return J(w,J(w,J(p,w)))
def show(t,cap=60):
    if size(t)>cap: return '<sz%d>'%size(t)
    return 'g%d'%t[1] if t[0]=='g' else '(%s*%s)'%(show(t[1],9999),show(t[2],9999))
def tower(base,ws):
    ts=[base]
    for w in ws: ts.append(encB(ts[-1],w))
    return ts
def which(C,u,v):
    for i,(conds,xr,tag) in enumerate(RULES):
        try:
            if C.check(conds,u,v) and C.ev(xr,u,v) is not None: return i+1
        except RecursionError: return None
    return None
lvl=1; junk=g(9); ws=[g(20+i) for i in range(lvl+2)]
seen=set()
for seed,base in ((1,g(0)),(2,J(g(0),g(1)))):
    ts=tower(base,ws)
    cands=[]
    for k,t in enumerate(ts):
        cands.append(t); cands.append(J(junk,t))
        if t[0]=='J': cands += [t[1],t[2]]
    cands=[c for c in cands if size(c)<=400][:14]
    n=0
    for x in cands:
        for y in cands:
            for z in cands:
                if size(x)+size(y)+size(z)>700: continue
                if n>4000: break
                C=cf.Closed(law,RULES)
                try:
                    A=C.op(y,x); P=C.op(x,z); Q=C.op(z,P); B=C.op(z,Q); top=C.op(A,B)
                except RecursionError: continue
                n+=1
                if top==x: continue
                key=(x,y,z)
                if key in seen: continue
                seen.add(key)
                cell=''.join('D' if b else 'f' for b in (A!=J(y,x),P!=J(x,z),Q!=J(z,P),B!=J(z,Q)))
                print('=== FAIL seed%d cell=%s cycles=%d'%(seed,cell,C.cycles))
                for nm,t in (('x',x),('y',y),('z',z)):
                    print('   %s = %s   sz %d'%(nm,show(t),size(t)))
                print('   A=op(y,x) = %s  sz %d  rule %s'%(show(A),size(A),which(C,y,x)))
                print('   P=op(x,z) = %s  sz %d  rule %s'%(show(P),size(P),which(C,x,z)))
                print('   Q=op(z,P) = %s  sz %d  rule %s'%(show(Q),size(Q),which(C,z,P)))
                print('   B=op(z,Q) = %s  sz %d  rule %s'%(show(B),size(B),which(C,z,Q)))
                print('   top       = %s  sz %d  rule %s   WANT %s'%(show(top),size(top),which(C,A,B),show(x)))
                F=fm.Free(law)
                try:
                    sA=F.op(y,x); sP=F.op(x,z); sQ=F.op(z,sP); sB=F.op(z,sQ); st=F.op(sA,sB)
                    print('   SEMANTIC top=%s ok=%s conflicts=%d'%(show(st),st==x,len(F.conflicts)))
                except Exception as e:
                    print('   SEMANTIC ERR',repr(e)[:90])
