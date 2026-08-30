"""Search a quotient model for an assignment refuting a row's goal equation (eq2)."""
import sys, os, json, itertools, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import qmod
from qmod import E, show, terms_upto, pvars
from laws import parse_eq, load_rows
from freemodel import catalog, normalise


def refute(M, goal, pool, limit=1):
    """goal is a (lhs, rhs) pattern pair; find s with ev(lhs) != ev(rhs)."""
    vs = []
    for p in goal:
        pvars(p, vs) if not isinstance(p, str) else (vs.append(p) if p not in vs else None)
    vs = []
    for p in goal:
        if isinstance(p, str):
            if p not in vs:
                vs.append(p)
        else:
            pvars(p, vs)
    out = []

    def ev(p, s):
        if isinstance(p, str):
            return s[p]
        return M.op(ev(p[0], s), ev(p[1], s))
    for vals in itertools.product(pool, repeat=len(vs)):
        s = dict(zip(vs, vals))
        try:
            if ev(goal[0], s) != ev(goal[1], s):
                out.append((s, ev(goal[0], s), ev(goal[1], s)))
                if len(out) >= limit:
                    return vs, out
        except RecursionError:
            continue
    return vs, out


def main(eq1, Mf, unary=()):
    qmod.UNARY = list(unary)
    cat = catalog()
    rows = [r for r in load_rows() if int(r['eq1_id']) == eq1]
    pool = terms_upto(5, 2)
    for r in rows:
        goal = parse_eq(cat[int(r['eq2_id'])])
        M = Mf()
        vs, out = refute(M, goal, pool)
        if out:
            s, a, b = out[0]
            print('%s  eq2=%s  %s' % (r['id'], r['eq2_id'], cat[int(r['eq2_id'])]))
            print('    REFUTED by ' + '  '.join('%s=%s' % (k, show(v)) for k, v in sorted(s.items())))
            print('    lhs=%s   rhs=%s' % (show(a), show(b)))
        else:
            print('%s  eq2=%s  NOT REFUTED on pool of %d' % (r['id'], r['eq2_id'], len(pool)))
