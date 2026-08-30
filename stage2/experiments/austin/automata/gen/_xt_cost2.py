"""_xt_cost2.py <eq> [--deep 400] [--fuzz 1200]

Where the revalidate.py 2,400 s timeout actually goes.  Prints
  * extraction seconds at cap2 = 1, 8, 64, 256, 1024 (the knob the handover blamed),
  * validation seconds of `revalidate.run_tests` for prefixes of the extracted rule list of size
    k = 10, 20, 40, 80, all  --  the quantity revalidate's minimiser pays ONCE PER RULE.
The minimiser's total is about nrules x run_tests(nrules), i.e. QUADRATIC in the rule count.
"""
import sys, os, json, time
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'gen'))
import leangen
from freemodel import normalise, catalog
from laws import parse_eq
import closedform as cf1
import closedform2 as cf2
import revalidate as rv


def get_law(eq):
    cat = catalog(); orig = normalise(parse_eq(cat[eq]))
    dz = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
    return ('x', leangen.dual_pat(orig[1])) if dz else orig


def main():
    eq = int(sys.argv[1])
    N = int(sys.argv[sys.argv.index('--deep') + 1]) if '--deep' in sys.argv else 400
    NF = int(sys.argv[sys.argv.index('--fuzz') + 1]) if '--fuzz' in sys.argv else 1200
    law = get_law(eq)
    print('== extraction cost vs cap2 (eq %d)' % eq)
    for mod, name in ((cf1, 'closedform'), (cf2, 'closedform2')):
        for cap in (1, 8, 64, 256, 1024):
            t0 = time.time(); r = mod.Extractor(law).rules(cap2=cap)
            print('   %-12s cap2=%-5d nrules=%-4d extract=%.2fs' % (name, cap, len(r), time.time() - t0), flush=True)
    print('== validation cost vs rule count (run_tests, 1 seed, deep=%d fuzz=%d)' % (N, NF))
    rv.cf = cf1
    full = cf1.Extractor(law).rules()
    for k in (10, 20, 40, 80, len(full)):
        if k > len(full): continue
        sub = full[:k]
        t0 = time.time()
        f = rv.run_tests(law, sub, [eq * 7 + 3], N, NF)
        print('   nrules=%-4d run_tests=%.1fs   (minimiser pays this ~%d times => ~%.0fs)'
              % (k, time.time() - t0, k, k * (time.time() - t0)), flush=True)


if __name__ == '__main__':
    main()
