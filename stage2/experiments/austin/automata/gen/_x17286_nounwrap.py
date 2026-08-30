"""Is the UNBOUNDED unwrap list still needed now that branch R (reconstruction) exists?
If not, the Lean `op` is a bounded if-chain -- no mutual recursion, no `find` helper."""
import sys, os, importlib.util
HERE=os.path.dirname(os.path.abspath(__file__))
spec=importlib.util.spec_from_file_location('lab', os.path.join(HERE,'_x17286_lab.py'))
lab=importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
g,J,sz,show,encB,Mod,chain,deep,terms = lab.g,lab.J,lab.sz,lab.show,lab.encB,lab.Mod,lab.chain,lab.deep,lab.terms

class NoUnwrap(Mod):
    def unwraps(self, P): return []          # candidates = [a1 P] only, plus branches U and R

def run(cls, name):
    tot=0; bad=[]
    # exhaustive
    for mx,gn,lim in ((7,2,15),(9,1,15)):
        T=terms(mx,gn); M=cls()
        for x in T:
            for y in T:
                for z in T:
                    if sz(x)+sz(y)+sz(z)>lim: continue
                    try: top,_=chain(M,x,y,z)
                    except RecursionError: continue
                    tot+=1
                    if top!=x: bad.append(('exh',x,y,z,top))
    # level-k descent
    for lvl in range(0,4):
        for junk in (g(9), deep(13)):
            ws=[g(20+i) for i in range(lvl+2)]
            M=cls()
            for seed,base in ((1,g(0)),(2,J(g(0),g(1)))):
                ts=[base]
                for w in ws: ts.append(encB(ts[-1],w))
                cands=[]
                for t in ts:
                    cands.append(t); cands.append(J(junk,t))
                    if t[0]=='J': cands+=[t[1],t[2]]
                cands=[c for c in cands if sz(c)<=400][:14]
                n=0
                for x in cands:
                    for y in cands:
                        for z in cands:
                            if sz(x)+sz(y)+sz(z)>700 or n>4000: continue
                            n+=1
                            try: top,_=chain(M,x,y,z)
                            except RecursionError: continue
                            tot+=1
                            if top!=x: bad.append(('lvl%d'%lvl,x,y,z,top))
    # the V1 probe families
    for k in range(0,5):
        M=cls(); ws=[g(20+i) for i in range(k)]
        for pay in (g(0), J(g(0),g(1)), encB(g(0),g(1))):
            t=pay
            for w in ws: t=encB(t,w)
            x=t
            for junk in (g(9), J(g(9),g(8)), deep(9)):
                y=J(junk,pay)
                for wz in (g(30), J(g(30),g(31))):
                    for zl in range(0,3):
                        for base in ((x[2] if x[0]=='J' else x), x):
                            z=base
                            for i in range(zl+1): z=encB(z,J(wz,g(40+i)))
                            if sz(x)+sz(y)+sz(z)>900: continue
                            try: top,_=chain(M,x,y,z)
                            except RecursionError: continue
                            tot+=1
                            if top!=x: bad.append(('probe%d'%k,x,y,z,top))
    print('%-12s %d chains, %d bad'%(name,tot,len(bad)))
    seen=set()
    for b in bad:
        if b[0] in seen: continue
        seen.add(b[0])
        print('    %-8s x=%s y=%s z=%s -> %s'%(b[0],show(b[1]),show(b[2]),show(b[3]),show(b[4])))
    return len(bad)

run(Mod,      'v6 (unwraps)')
run(NoUnwrap, 'no unwraps')
