import sys; sys.path.insert(0,'.')
import nfcore as nf
nf.ALLOW_E=False
from nfcore import S, show
def J(a,b): return ('J',a,b)
def mk(on):
    m={}; fired={'R1':0,'D':0,'D2':0,'R4':0}
    def op(u,v):
        k=(u,v); r=m.get(k)
        if r is not None: return r
        r=None; tag=None
        if u==v: r,tag=S,'R1'
        elif v==S and u[0]=='J':
            if on.get('D',True) and u[1][0]=='J':
                a,b,q=u[1][1],u[1][2],u[2]
                if op(a,q)==b and op(a,b)==J(a,b): r,tag=q,'D'
            if r is None and on.get('D2',True) and u[2][0]=='J' and u[2][2]==u[1]: r,tag=u[2],'D2'
        if r is None: r,tag=J(u,v),'R4'
        fired[tag]+=1; m[k]=r; return r
    return op,fired
law=nf.get_law(27859)
for on,name in (({},'full'),({'D':False},'no D'),({'D2':False},'no D2')):
    op,fired=mk(on); bad=None
    for ms,g in ((7,1),(6,2)):
        n,f=nf.exhaustive(op,law,nf.carrier_upto(ms,g,use_E=False),limit=2)
        if f: bad=(ms,g,f[0]); break
    print(name, 'fails' if bad else 'OK', ('at carrier<=%d g%d: %s -> %s'%(bad[0],bad[1],{k:show(v) for k,v in bad[2][0].items()}, show(bad[2][1]) if bad[2][1]!='recursion' else 'rec')) if bad else '', 'firings',fired if not on else '')
