"""validate the EXACT emitted 7-rule set (R4 [Bs] dropped, R8b added)."""
import sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
sys.setrecursionlimit(30000)
import closedform as cf, revalidate as rv
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
print('rules', len(RULES), [r[2] for r in RULES], flush=True)
t0=time.time()
f = rv.run_tests(law, RULES, [3,4,5], 3000, 12000)
print('run_tests seeds[3,4,5]: %d fails (%.0f s)' % (len(f), time.time()-t0), flush=True)
for sd in (11, 101, 1009, 121016):
    C = cf.Closed(law, RULES); n, ff = cf.deep_tests(C, law, 20000, 300, sd)
    print('  deep seed %-8d %5d tested %d fails (%.0f s)' % (sd, n, len(ff), time.time()-t0), flush=True)
f2 = rv.run_tests(law, RULES, [EQ*7+3, EQ*7+14, 7, 99], 3000, 12000)
print('run_tests seeds[orig,7,99]: %d fails (%.0f s)' % (len(f2), time.time()-t0), flush=True)
