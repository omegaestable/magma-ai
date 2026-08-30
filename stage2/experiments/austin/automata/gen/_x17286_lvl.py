"""LEVEL-k DESCENT for 17286 (adapted from gen/_w3_12087_deep3.py).

17286's decode: op(u,v) = a2 u  when v = encB(a2 u, w) = J(w,J(w,J(a2 u,w))).
Build a TOWER  t_{k+1} = encB(t_k, w_k)  so the decoder can descend k levels in the same argument,
then drive the law's chain  op(op y x) (op z (op z (op x z)))  with x,y,z drawn from the tower.
Levels 0..3, two seeds, both junk pools, fresh evaluator each time (cycles must be 0)."""
import sys, os, random
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.dirname(HERE)); sys.path.insert(0,HERE)
sys.setrecursionlimit(40000)
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
def encB(p,w): return J(w,J(w,J(p,w)))
def show(t,cap=26):
    if size(t)>cap: return '<sz%d>'%size(t)
    return 'g%d'%t[1] if t[0]=='g' else '(%s*%s)'%(show(t[1],9999),show(t[2],9999))
def deep(n,a=2,b=3):
    t=g(a)
    for i in range(n): t=J(t,g(b))
    return t
def fresh(): return cf.Closed(law,RULES)

def tower(base, ws):
    """t_0 = base ; t_{k+1} = encB(t_k, w_k)"""
    ts=[base]
    for w in ws: ts.append(encB(ts[-1], w))
    return ts

def chain(C,x,y,z):
    A=C.op(y,x); P=C.op(x,z); Q=C.op(z,P); B=C.op(z,Q); top=C.op(A,B)
    cell=''.join('D' if b else 'f' for b in (A!=J(y,x),P!=J(x,z),Q!=J(z,P),B!=J(z,Q)))
    return top,cell,(A,P,Q,B)

print('%-5s %-9s %-8s %-7s %-7s %-7s %-9s'%('lvl','junk','tested','lawbad','F1bad','F2bad','cycles'))
for lvl in range(0,4):
    for jname,junk in (('small',g(9)),('big',deep(13))):
        ws=[g(20+i) for i in range(lvl+2)]
        bad=f1bad=f2bad=0; n=0; cyc=0
        for seed in (1,2):
            random.seed(seed)
            ts=tower(g(0) if seed==1 else J(g(0),g(1)), ws)
            # candidates: every tower level, its pieces, and left-arguments J(junk, t_k)
            cands=[]
            for k,t in enumerate(ts):
                cands.append(t); cands.append(J(junk,t))
                if t[0]=='J': cands += [t[1], t[2]]
            cands=[c for c in cands if size(c)<=400][:14]
            for x in cands:
                for y in cands:
                    for z in cands:
                        if size(x)+size(y)+size(z)>700: continue
                        if n>4000: break
                        C=fresh()
                        try: top,cell,(A,P,Q,B)=chain(C,x,y,z)
                        except RecursionError: continue
                        n+=1; cyc+=C.cycles
                        if top!=x: bad+=1
                        if Q!=J(z,P): f1bad+=1
                        if B!=J(z,Q): f2bad+=1
        print('%-5d %-9s %-8d %-7d %-7d %-7d %-9d'%(lvl,jname,n,bad,f1bad,f2bad,cyc))
