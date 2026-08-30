"""Is CMP true?  Enc w v  &  RF u w  =>  op u v = w  ?   (exact mirror of the Lean predicates)"""
import sys, os, itertools
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
A1e=lambda e:('A1',e); A2e=lambda e:('A2',e); OP=lambda a,b:('OP',a,b); JE=lambda a,b:('J',a,b)
P_=A2e(A2e(V)); X_=JE(A1e(P_),P_)
R8b=([('TG',V),('TG',A2e(V)),('EQ',A1e(V),A1e(A2e(V))),('TG',P_),
      ('OPEQ',OP(U,A1e(P_)),A2e(P_)),('OPEQ',OP(X_,A1e(V)),P_)], X_, 'DDb')
RULES=[r for r in BASE if r[2]!='Bs']+[R8b]
C = cf.Closed(law, RULES)
g=lambda n:('g',n); J=lambda a,b:('J',a,b)
def show(t,cap=34):
    if size(t)>cap: return '<sz%d>'%size(t)
    return 'g%d'%t[1] if t[0]=='g' else '(%s*%s)'%(show(t[1],9999),show(t[2],9999))
def tg(t): return 2 if t[0]=='J' else 1
def a1(t): return t[1] if t[0]=='J' else t
def a2(t): return t[2] if t[0]=='J' else t
def op(a,b): return C.op(a,b)
def enc_shapes(w,v):
    """which of the three Enc shapes hold"""
    s=[]
    if tg(v)==2 and tg(a2(v))==2 and a1(v)==a1(a2(v)) and tg(a2(a2(v)))==2 \
       and a1(a2(a2(v)))==w and a1(v)==a2(a2(a2(v))): s.append(1)
    if tg(v)==2 and tg(a2(v))==2 and a1(v)==a1(a2(v)) and a2(a2(v))==op(w,a1(v)): s.append(2)
    if tg(v)==2 and a2(v)==op(a1(v),op(w,a1(v))): s.append(3)
    return s
def rf_shapes(u,w):
    s=[]
    if tg(u)==2 and a2(u)==w: s.append(0)
    s += [10+k for k in enc_shapes(u,w)]
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
T = terms(7,2)
print('terms', len(T), flush=True)
tested=0; bad={}
for v in T:
    for w in T:
        es = enc_shapes(w,v)
        if not es: continue
        for u in T:
            rs = rf_shapes(u,w)
            if not rs: continue
            tested+=1
            r = op(u,v)
            if r != w:
                key=(tuple(es),tuple(rs))
                bad.setdefault(key,[]).append((u,v,w,r))
print('CMP hypothesis instances tested:', tested)
print('CMP FAILURES by (Enc shapes, RF shapes):')
for k in sorted(bad, key=str):
    print('   Enc%s RF%s : %d   e.g. u=%s v=%s w=%s -> %s' %
          (k[0], k[1], len(bad[k]), show(bad[k][0][0]), show(bad[k][0][1]),
           show(bad[k][0][2]), show(bad[k][0][3])))
if not bad: print('   NONE -- CMP holds on this range')
