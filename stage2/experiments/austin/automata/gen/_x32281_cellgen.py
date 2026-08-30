"""Census keyed on GD's actual disjunct.  disj2 = guard product FREE (TOP applies);
disj3 = guard product DECODED (the R3 cell).  Cross with A-freeness and the nine gates."""
import sys, random, collections
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
from _x32281_lib import *
from _x32281_try1 import R1
from _x32281_try2 import R3
from _x32281_try5 import R5
import closedform as cf
from freemodel import size as sz
RULES = [R1, R3, R5]
C = cf.Closed(LAW, RULES); op = C.op
J = lambda a, b: ('J', a, b); g = lambda n: ('g', n)
a1 = lambda t: t[1] if t[0]=='J' else t
a2 = lambda t: t[2] if t[0]=='J' else t
tg = lambda t: 2 if t[0]=='J' else 1
def E(u,p,w): return J(J(u,J(J(p,w),w)),w)
def P1(u,v):
    try:
        return (tg(v)==2 and tg(a1(v))==2 and u==a1(a1(v)) and tg(a2(a1(v)))==2
                and tg(a1(a2(a1(v))))==2 and a2(a1(a2(a1(v))))==a2(a2(a1(v)))
                and a2(a1(a2(a1(v))))==a2(v))
    except Exception: return False
def which(u,v):
    try: r = op(u,v)
    except RecursionError: return 'REC'
    if r[0]=='J' and r[1]==u and r[2]==v: return 'F'
    for i,(cd,xe,t) in enumerate(RULES):
        if C.check(cd,u,v) and C.ev(xe,u,v) is not None: return ['R1','R2','R5'][i]
    return '?'
random.seed(99)
G=[g(i) for i in range(6)]
def mk(d):
    if d==0 or random.random()<0.45: return random.choice(G)
    return E(mk(d-1),mk(d-1),mk(d-1))
c=collections.Counter(); g4bad=g5bad=p5bad=0; slack=[10**9,10**9]; lawbad=0
def trial(x,y,z):
    global g4bad,g5bad,p5bad,lawbad
    try:
        P=op(x,y); Q=op(P,y); A=op(z,Q); S=op(A,y); T=op(z,S)
    except RecursionError: return
    if T!=x: lawbad+=1
    if P==J(x,y): return
    if P1(x,y): c[('disj1 P1','Afree' if A==J(z,Q) else 'ADEC',which(z,S))]+=1; return
    w=a2(y); Cg=op(op(P,w),w)          # TR's C, uniform for R2 and R3
    if a1(y)!=op(x,Cg): c[('*** guard mismatch',)]+=1; return
    free = (op(x,Cg)==J(x,Cg))
    d='disj2 (guard free)' if free else 'disj3 (guard DECODED)'
    c[(d,'Afree' if A==J(z,Q) else 'ADEC',which(z,S))]+=1
    if free: return
    # the R3 cell: check p5 == C and gates g4/g5
    p4=op(a1(a1(w)),w); p5=op(p4,w); p6=op(a1(y),p5); p7=op(z,p6)
    if p5!=Cg: p5bad+=1; return
    if not sz(p6)<sz(S): g4bad+=1
    if not sz(p7)+sz(p5)+1<sz(S): g5bad+=1
    slack[0]=min(slack[0],sz(S)-sz(p6)); slack[1]=min(slack[1],sz(S)-(sz(p7)+sz(p5)+1))
for _ in range(6000): trial(mk(2),mk(2),mk(1))
for _ in range(6000):
    w=mk(1);r=mk(1);k=mk(1);v=mk(1);Q0=E(k,r,w)
    trial(Q0,E(Q0,Q0,v),random.choice(G)); trial(mk(1),E(mk(1),mk(1),mk(1)),random.choice(G))
for _ in range(9000):
    w=mk(1);r=mk(1);k=mk(1);v=mk(1);Q0=E(k,r,w)
    x,y,z=Q0,E(Q0,Q0,v),random.choice(G)
    try:
        P=op(x,y);Q=op(P,y);A=op(z,Q);S=op(A,y)
    except RecursionError: continue
    if A==J(z,Q) or S!=J(A,y): continue
    for z2 in (g(0),g(1),g(4),E(g(0),g(1),g(2))): trial(z,S,z2)
print('law failures:',lawbad)
for k in sorted(c,key=str): print('  %-58s %d'%(str(k),c[k]))
print('p5 != C:',p5bad,' g4 violations:',g4bad,' g5 violations:',g5bad,' min slack',slack)
