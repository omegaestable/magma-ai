"""CMP by CONSTRUCTION: build v satisfying each Enc shape and u satisfying each RF shape."""
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
op = C.op
def encs(w,v):
    s=[]
    if tg(v)==2 and tg(a2(v))==2 and a1(v)==a1(a2(v)) and tg(a2(a2(v)))==2 \
       and a1(a2(a2(v)))==w and a1(v)==a2(a2(a2(v))): s.append(1)
    if tg(v)==2 and tg(a2(v))==2 and a1(v)==a1(a2(v)) and a2(a2(v))==op(w,a1(v)): s.append(2)
    if tg(v)==2 and a2(v)==op(a1(v),op(w,a1(v))): s.append(3)
    return s
def rfs(u,w):
    s=[]
    if tg(u)==2 and a2(u)==w: s.append(0)
    s += [10+k for k in encs(u,w)]
    return s
# constructors for v given (w, zz): the three depths
def mkv1(w,zz): return J(zz,J(zz,J(w,zz)))                 # fully free
def mkv2(w,zz): return J(zz,J(zz,op(w,zz)))               # inner product decoded
def mkv3(w,zz): return J(zz,op(zz,op(w,zz)))              # middle product decoded
POOL=[g(0),g(1),g(2),J(g(0),g(1)),J(g(1),g(0)),J(g(0),g(0)),
      J(g(2),J(g(0),g(1))),J(J(g(0),g(1)),g(2))]
# enrich the pool with model-built encodings (codes of codes)
extra=[]
for w in POOL[:6]:
    for zz in POOL[:4]:
        extra += [mkv1(w,zz), mkv2(w,zz), mkv3(w,zz)]
POOL = POOL + extra
print('pool', len(POOL), flush=True)
tested=0; bad={}; cov={}
for w in POOL:
    for zz in POOL:
        for mk in (mkv1,mkv2,mkv3):
            try: v = mk(w,zz)
            except RecursionError: continue
            if size(v) > 120: continue
            try: es = encs(w,v)
            except RecursionError: continue
            if not es: continue
            us = [J(g(9),w), J(J(g(9),g(8)),w)]                    # RF-left
            for zz2 in POOL[:8]:                                   # RF via Enc u w: w encodes u
                for mk2 in (mkv1,mkv2,mkv3):
                    pass
            # u such that Enc u w holds: w must BE an encoding of u
            for cand in POOL:
                try:
                    if encs(cand, w): us.append(cand)
                except RecursionError: pass
            for u in us:
                try:
                    rs = rfs(u,w)
                    if not rs: continue
                    r = op(u,v)
                except RecursionError: continue
                tested+=1
                key=(tuple(es),tuple(rs))
                cov[key]=cov.get(key,0)+1
                if r != w: bad.setdefault(key,[]).append((u,v,w,r))
print('instances tested:', tested)
print('coverage by (Enc shapes, RF shapes):')
for k in sorted(cov, key=str): print('   Enc%-9s RF%-12s %d' % (str(k[0]), str(k[1]), cov[k]))
print('FAILURES:')
for k in sorted(bad, key=str):
    print('   Enc%s RF%s : %d  e.g. u=%s v=%s w=%s -> %s' %
          (k[0],k[1],len(bad[k]),show(bad[k][0][0]),show(bad[k][0][1]),show(bad[k][0][2]),show(bad[k][0][3])))
if not bad: print('   NONE')
