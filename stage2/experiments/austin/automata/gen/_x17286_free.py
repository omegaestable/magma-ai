"""is  op a (op a b)  always free in the repaired 17286 model?  and Q = op z (op x z)?"""
import sys, os, itertools, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
sys.setrecursionlimit(30000)
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
EQ = 17286
law = normalise(parse_eq(catalog()[EQ]))
BASE = cf.Extractor(law).rules(exist=False)
U=('U',); V=('V',)
A1=lambda e:('A1',e); A2=lambda e:('A2',e); OP=lambda a,b:('OP',a,b); JE=lambda a,b:('J',a,b)
P_=A2(A2(V)); X_=JE(A1(P_),P_)
R8b=([('TG',V),('TG',A2(V)),('EQ',A1(V),A1(A2(V))),('TG',P_),
      ('OPEQ',OP(U,A1(P_)),A2(P_)),('OPEQ',OP(X_,A1(V)),P_)], X_, 'DDb')
RULES=[r for r in BASE if r[2]!='Bs']+[R8b]
g=lambda n:('g',n); J=lambda a,b:('J',a,b)
def show(t,cap=40):
    if size(t)>cap: return '<sz%d>'%size(t)
    return 'g%d'%t[1] if t[0]=='g' else '(%s*%s)'%(show(t[1],9999),show(t[2],9999))
def encB(p,w): return J(w,J(w,J(p,w)))
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
T = terms(9,2)
print('terms', len(T))
bad_aa=[]; bad_q=[]; bad_b=[]
C=cf.Closed(law,RULES)
for a in T:
    for b in T:
        if size(a)+size(b)>13: continue
        try:
            W=C.op(a,b); R=C.op(a,W)
        except RecursionError: continue
        if R!=J(a,W): bad_aa.append((a,b,W,R))
print('op a (op a b) NOT free:', len(bad_aa))
for t in bad_aa[:6]: print('   a=%s b=%s W=%s R=%s'%(show(t[0]),show(t[1]),show(t[2]),show(t[3])))
# Q = op z (op x z) and B = op z Q in the chain
for x in T:
    for z in T:
        if size(x)+size(z)>13: continue
        try:
            P=C.op(x,z); Q=C.op(z,P); B=C.op(z,Q)
        except RecursionError: continue
        if Q!=J(z,P): bad_q.append((x,z,P,Q))
        if B!=J(z,Q): bad_b.append((x,z,Q,B))
print('Q = op z (op x z) NOT free:', len(bad_q))
for t in bad_q[:6]: print('   x=%s z=%s P=%s Q=%s'%(show(t[0]),show(t[1]),show(t[2]),show(t[3])))
print('B = op z Q NOT free:', len(bad_b))
for t in bad_b[:6]: print('   x=%s z=%s Q=%s B=%s'%(show(t[0]),show(t[1]),show(t[2]),show(t[3])))
# random deeper
random.seed(5)
pool=[g(0),g(1),g(2)]
for _ in range(400):
    def rnd(d):
        if d==0 or random.random()<0.3: return random.choice(pool)
        return J(rnd(d-1),rnd(d-1))
    a=rnd(3); b=rnd(3)
    if random.random()<0.5: b=encB(rnd(2),rnd(2))
    if random.random()<0.3: a=encB(rnd(2),rnd(2))
    try:
        W=C.op(a,b); R=C.op(a,W)
    except RecursionError: continue
    if R!=J(a,W): bad_aa.append((a,b,W,R))
    pool.append(a); pool.append(W)
    if len(pool)>60: pool=pool[-60:]
print('after random: op a (op a b) NOT free:', len(bad_aa))
