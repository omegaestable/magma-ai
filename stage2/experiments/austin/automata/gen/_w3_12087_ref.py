import sys, os, itertools
D = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D); sys.path.insert(0, os.path.join(D, 'gen'))
import importlib.util
spec = importlib.util.spec_from_file_location('lab', os.path.join(D, 'gen', '_w3_12087_lab.py'))
lab = importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
op, show = lab.op, lab.show
from freemodel import normalise, catalog, pvars
from laws import parse_eq
cat = catalog()
def evg(pat, s):
    if isinstance(pat, str): return s[pat]
    return op(evg(pat[0], s), evg(pat[1], s))
cands = [('g',0), ('g',1), ('g',2)]
for gid in (28770, 22818):
    lg = normalise(parse_eq(cat[gid])); vs = set(pvars(lg[1])) | {lg[0]}
    vs = sorted(vs)
    got = None
    for combo in itertools.product(cands, repeat=len(vs)):
        s = dict(zip(vs, combo))
        try:
            r = evg(lg[1], s)
            if r != s[lg[0]]: got = (s, r); break
        except RecursionError: pass
    print('goal', gid, cat[gid], '| vars', vs)
    if got:
        s, r = got
        print('   REFUTED at', {k: show(v) for k, v in s.items()}, '-> got', show(r))
    else:
        print('   NOT refuted on generator triples')
