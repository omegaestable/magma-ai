"""_xt_sweep.py <eq,eq,...> [--maxsize 7] [--gens 2] [--secs 90]

Cheap, deterministic before/after metric across many laws: for each law, count the pairs (u,v) of
free-magma terms up to `maxsize` over `gens` generators on which the extracted rule system disagrees
with the SEMANTIC free model, for
    old  = closedform.Extractor(law).rules()
    new  = closedform2.Extractor(law).rules()
    new+ = closedform2.extract(law)  (with the soundness filter)
and split each count into WRONG (a rule fired and returned the wrong value -- an unsound rule) and
HOLE (no rule fired where the free model reads a value -- a missing mode).
"""
import sys, os, json, time
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'gen'))
import leangen
import freemodel as fm
import closedform as cf1
import closedform2 as cf2
from freemodel import normalise, catalog
from laws import parse_eq


def get_law(eq):
    cat = catalog(); orig = normalise(parse_eq(cat[eq]))
    dz = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
    return ('x', leangen.dual_pat(orig[1])) if dz else orig, dz


def score(law, rules, pool, F, deadline):
    C = cf2.Closed(law, rules)
    wrong = 0; hole = 0; n = 0
    for u in pool:
        if time.time() > deadline: return None, None, n
        for v in pool:
            try:
                fr = F.op(u, v)
            except Exception:
                continue
            try:
                cr = C.op(u, v)
            except RecursionError:
                continue
            n += 1
            if cr == fr: continue
            if cf2.firing_rule(C, u, v) is None: hole += 1
            else: wrong += 1
    return wrong, hole, n


def main():
    eqs = [int(x) for x in sys.argv[1].split(',')]
    ms = int(sys.argv[sys.argv.index('--maxsize') + 1]) if '--maxsize' in sys.argv else 7
    gens = int(sys.argv[sys.argv.index('--gens') + 1]) if '--gens' in sys.argv else 2
    secs = float(sys.argv[sys.argv.index('--secs') + 1]) if '--secs' in sys.argv else 90
    pool = cf2.terms_upto(ms, gens)
    for eq in eqs:
        law, dz = get_law(eq)
        F = fm.Free(law)
        t0 = time.time()
        row = dict(eq=eq, dualized=dz, pool=len(pool))
        try:
            r1 = cf1.Extractor(law).rules()
            row['old_n'] = len(r1)
            w, h, n = score(law, r1, pool, F, t0 + secs)
            row['old_wrong'], row['old_hole'] = w, h
            r2 = cf2.Extractor(law).rules()
            row['new_n'] = len(r2)
            w, h, n = score(law, r2, pool, F, t0 + 2 * secs)
            row['new_wrong'], row['new_hole'] = w, h
            r3, info = cf2.extract(law, maxsize=ms, gens=gens)
            row['snd_n'] = len(r3); row['dropped'] = info['dropped']
            w, h, n = score(law, r3, pool, F, t0 + 3 * secs)
            row['snd_wrong'], row['snd_hole'] = w, h
        except Exception as e:
            row['error'] = '%s: %s' % (type(e).__name__, e)
        row['secs'] = round(time.time() - t0, 1)
        print(json.dumps(row), flush=True)


if __name__ == '__main__':
    main()
