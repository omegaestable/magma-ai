import time, json, sys
import closedform as cf, smallcheck as sc
from freemodel import normalise, catalog
from laws import parse_eq
cat = catalog()
for eq in [int(a) for a in sys.argv[1:]]:
    law = normalise(parse_eq(cat[eq])); X = cf.Extractor(law)
    t0 = time.time(); rules = X.rules(); tx = time.time() - t0
    n, f = sc.exhaustive(cf.Closed(law, rules), law, 9, 1, limit=25)
    n2, f2 = sc.exhaustive(cf.Closed(law, rules), law, 5, 2, limit=25)
    t, f3 = cf.deep_tests(cf.Closed(law, rules), law, 2000, 120, 9)
    print(json.dumps(dict(eq=eq, nrules=len(rules), extract_secs=round(tx, 1), exh9_1=len(f), exh5_2=len(f2), deep2000=len(f3), secs=round(time.time() - t0, 1))), flush=True)
