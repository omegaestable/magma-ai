"""Print the counterexample the rule/slot hunter finds for the never-validated 6-rule 23357 set."""
import sys, time
D = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D)
import closedform as cf, trace as tr
from freemodel import size
import importlib.util
G = D + '/gen/'
spec = importlib.util.spec_from_file_location('_x23357_rep', G + '_x23357_rep.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
law = mod.law
TAG = {r[2]: r for r in mod.rules}
SETS = {
    'min6': ['free', 'Bs|rd:A0', 'Bs|ex:Qa', 'Bs|ex:Qb', 'A0s,B1s|rd:A0', 'As'],
    'full12': [r[2] for r in mod.rules],
}
hspec = importlib.util.spec_from_file_location('_x23357_hunt', G + '_x23357_hunt.py')
show = tr.show

NAMES = sys.argv[1:] or ['min6']
sys.argv = [sys.argv[0]]      # _x23357_hunt.py reads sys.argv[1] as its rules-module path
for name in NAMES:
    rules = [TAG[t] for t in SETS[name]]
    hm = importlib.util.module_from_spec(hspec); hspec.loader.exec_module(hm)
    hm.rules = rules; hm.law = law
    tot = 0
    for sd in (41, 42):
        n, bad = hm.hunt(12, sd)
        tot += n
        for key in sorted(bad):
            ws = sorted(bad[key], key=lambda t: sum(size(q) for q in t))
            x, y, z = ws[0]
            print('%s  seed=%d  R%d %-18s slot=%s  n=%d' % (name, sd, key[0], key[1], key[2], len(ws)), flush=True)
            print('   x =', show(x), flush=True)
            print('   y =', show(y), flush=True)
            print('   z =', show(z), flush=True)
            C = cf.Closed(law, rules)
            A = C.op(y, x); U = C.op(A, y); B = C.op(y, z); V = C.op(x, B); top = C.op(U, V)
            for nm, t in (('A=op y x', A), ('U=op A y', U), ('B=op y z', B), ('V=op x B', V), ('top', top)):
                print('   %-10s %s' % (nm, show(t) if size(t) < 90 else '<size %d>' % size(t)), flush=True)
            print('   GOT top =', show(top) if size(top) < 90 else '<%d>' % size(top), ' WANT x', flush=True)
    print('%s tested %d' % (name, tot), flush=True)
