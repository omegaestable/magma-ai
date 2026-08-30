"""Instrument `find` during the REAL oracle stack: which unwrap-chain positions are examined, and
which satisfy cds / the reproduce test.  Guides findNone's hypothesis."""
import sys, os, importlib.util
HERE=os.path.dirname(os.path.abspath(__file__))
spec=importlib.util.spec_from_file_location('mir', os.path.join(HERE,'_x17286_leanmirror.py'))
mir=importlib.util.module_from_spec(spec); spec.loader.exec_module(mir)
g,J,tg,a1,a2,sz,show,encB,deep,terms,chain = (mir.g,mir.J,mir.tg,mir.a1,mir.a2,mir.sz,mir.show,
                                              mir.encB,mir.deep,mir.terms,mir.chain)
POS={}; HIT={}; CDSONLY={}; REPONLY={}; CALLS=[0]
class Mod(mir.Mod):
    def find(self, u, T, w, P):
        CALLS[0]+=1
        k=0
        while True:
            c=a1(T)
            POS[k]=POS.get(k,0)+1
            okc = (tg(T)==2 and tg(a1(T))==2 and tg(a2(a1(T)))==2
                   and a1(a1(T))==a1(a2(a1(T))) and self.op(u,a1(a1(T)))==a2(a2(a1(T))))
            okp = (self.op(a1(T),w)==P) if tg(T)==2 else False
            if okc and okp:
                HIT[k]=HIT.get(k,0)+1; return c,'V'
            if okc: CDSONLY[k]=CDSONLY.get(k,0)+1
            elif okp: REPONLY[k]=REPONLY.get(k,0)+1
            if not (tg(T)==2 and tg(a2(T))==2): return J(u,u),'X'
            T=a2(a2(T)); k+=1
def run():
    M=Mod()
    for mx,gn in ((7,2),(9,1)):
        T=terms(mx,gn)
        for x in T:
            for y in T:
                for z in T:
                    if sz(x)+sz(y)+sz(z)>15: continue
                    try: chain(M,x,y,z)
                    except RecursionError: pass
    for lvl in range(0,4):
        for junk in (g(9),deep(13)):
            ws=[g(20+i) for i in range(lvl+2)]; M2=Mod()
            for seed,base in ((1,g(0)),(2,J(g(0),g(1)))):
                ts=[base]
                for w in ws: ts.append(encB(ts[-1],w))
                cands=[]
                for t in ts:
                    cands.append(t); cands.append(J(junk,t))
                    if t[0]=='J': cands+=[t[1],t[2]]
                cands=[c for c in cands if sz(c)<=400][:14]
                k=0
                for x in cands:
                    for y in cands:
                        for z in cands:
                            if sz(x)+sz(y)+sz(z)>700 or k>4000: continue
                            k+=1
                            try: chain(M2,x,y,z)
                            except RecursionError: pass
    for k in range(0,6):
        M3=Mod(); ws=[g(20+i) for i in range(k)]
        for pay in (g(0),J(g(0),g(1)),encB(g(0),g(1))):
            x=pay
            for w in ws: x=encB(x,w)
            for junk in (g(9),J(g(9),g(8)),deep(9)):
                y=J(junk,pay)
                for wz in (g(30),J(g(30),g(31))):
                    for zl in range(0,3):
                        for base in ((x[2] if x[0]=='J' else x), x):
                            z=base
                            for i in range(zl+1): z=encB(z,J(wz,g(40+i)))
                            if sz(x)+sz(y)+sz(z)>900: continue
                            try: chain(M3,x,y,z)
                            except RecursionError: pass
run()
print('find calls: %d'%CALLS[0])
print('positions examined      :', dict(sorted(POS.items())))
print('BOTH cds and reproduce  :', dict(sorted(HIT.items())))
print('cds only (repro failed) :', dict(sorted(CDSONLY.items())))
print('reproduce only (no cds) :', dict(sorted(REPONLY.items())))
