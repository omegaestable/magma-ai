import sys, time, importlib; sys.path.insert(0,'.')
import nfcore as nf
for modname, eq in (('nf12073',12073),('nf27859',27859)):
    m=importlib.import_module(modname); nf.ALLOW_E=getattr(m,'USE_E',True)
    law=nf.get_law(eq); tot=0; bad=0
    print('===',eq, nf.catalog()[eq], flush=True)
    for seed in (999001, 4242, 777777):
        n1,f1=nf.deep_random(m.op,law,30000,seed)
        n2,f2=nf.closure_random(m.op,law,15000,seed+5)
        n3,f3=nf.critical_random(m.op,law,15000,seed+9)
        tot+=n1+n2+n3; bad+=len(f1)+len(f2)+len(f3)
        print('  seed',seed,'deep',len(f1),'/',n1,' closure',len(f2),'/',n2,' critical',len(f3),'/',n3, flush=True)
        for s,r in (f1+f2+f3)[:2]: print('    FAIL',{k:nf.show(v) for k,v in s.items()},'->',nf.show(r) if r!='recursion' else r)
    print('  TOTAL random tests',tot,'fails',bad, flush=True)
