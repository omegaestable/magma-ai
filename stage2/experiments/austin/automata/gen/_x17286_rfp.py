"""When P = op x z DECODES, is it always `a2 x = P` (the RF-left branch), or can `Enc x P` occur?"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
sys.setrecursionlimit(30000)
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
EQ=17286
law = normalise(parse_eq(catalog()[EQ]))
BASE = cf.Extractor(law).rules(exist=False)
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
def tg(t): return 2 if t[0]=='J' else 1
def a1(t): return t[1] if t[0]=='J' else t
def a2(t): return t[2] if t[0]=='J' else t
def encs(w,v):
    s=[]
    if tg(v)==2 and tg(a2(v))==2 and a1(v)==a1(a2(v)) and tg(a2(a2(v)))==2 \
       and a1(a2(a2(v)))==w and a1(v)==a2(a2(a2(v))): s.append(1)
    if tg(v)==2 and tg(a2(v))==2 and a1(v)==a1(a2(v)) and a2(a2(v))==op(w,a1(v)): s.append(2)
    if tg(v)==2 and a2(v)==op(a1(v),op(w,a1(v))): s.append(3)
    return s
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
stat={}; ex={}
for x in T:
    for z in T:
        if size(x)+size(z)>13: continue
        try: P=op(x,z)
        except RecursionError: continue
        if P==J(x,z): continue                      # P free, not our case
        left = (tg(x)==2 and a2(x)==P)
        right = encs(x,P)
        k=(left, tuple(right))
        stat[k]=stat.get(k,0)+1
        ex.setdefault(k,(x,z,P))
print('P = op x z DECODED, classified by RF x P = (a2 x = P) or Enc x P:')
for k in sorted(stat,key=str):
    x,z,P=ex[k]
    print('   a2x=P:%-5s Enc-shapes:%-9s  %6d   e.g. x=%s z=%s P=%s'%(k[0],str(k[1]),stat[k],show(x),show(z),show(P)))
tot=sum(stat.values()); neither=sum(v for k,v in stat.items() if not k[0] and not k[1])
print('total decoded P: %d ; NEITHER branch of RF: %d'%(tot,neither))
