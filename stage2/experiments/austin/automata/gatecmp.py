"""gatecmp.py <eq> : extract with the current extractor, validate under GATE=msr and GATE=lex; JSON line."""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog
from laws import parse_eq
eq = int(sys.argv[1]); cat = catalog(); orig = normalise(parse_eq(cat[eq]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
t0 = time.time(); X = cf.Extractor(law); rules = X.rules(); tx = round(time.time() - t0, 1)
out = dict(eq=eq, nrules=len(rules), extract_secs=tx)
for g in ('msr', 'lex'):
    cf.GATE = g; t1 = time.time()
    fails = rv.run_tests(law, rules, [3, 4], 1500, 6000, secs=90)
    kinds = {}
    for s, r, kind, sd in fails: kinds[kind] = kinds.get(kind, 0) + 1
    out[g] = dict(fails=len(fails), kinds=kinds, secs=round(time.time() - t1, 1))
print(json.dumps(out), flush=True)
