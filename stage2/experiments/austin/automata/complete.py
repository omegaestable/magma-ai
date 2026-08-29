"""Exact critical-pair completion: repeatedly add the failing branch's root product (resolved,
with whole-subterm sharing) as a projection rule; then minimise."""
import sys, time, itertools
from symb import Model, describe_fail, pretty
from laws import parse_eq
from synth import (verify_traced, rules_str, generalize, paths_to, _at, share_repeats,
                   root_model, minimize, subterm_of, insert_rule, model_key, _complexity)

def exact_rule(m, fail):
    st, env, val, trace = fail
    x = st.resolve(env['x'])
    u, v, rv, ri = trace[-1]
    pos = [(0, p) for p in paths_to(u, x, st)] + [(1, p) for p in paths_to(v, x, st)]
    if not pos:
        return None
    side, path = min(pos, key=lambda sp: len(sp[1]))
    c = {}
    pu = generalize(u, st, 99, path if side == 0 else (), c)
    pv = generalize(v, st, 99, path if side == 1 else (), c)
    rhs = _at(pu if side == 0 else pv, path)
    pu2, pv2 = share_repeats(pu, pv)
    # rhs var must survive sharing: recompute rhs from the shared pattern by path
    def at_shared(p, path):
        for i in path:
            if isinstance(p, tuple) and p[0] == 'AS':
                p = p[2]
            p = p[i]
        while isinstance(p, tuple) and p[0] == 'AS':
            p = p[1]
        return p
    rhs2 = at_shared(pu2 if side == 0 else pv2, path)
    if not isinstance(rhs2, str):
        return None
    return (pu2, pv2, rhs2), ri

def complete(law, m, max_rules=40, time_limit=600, verbose=True):
    t0 = time.time(); seen = {model_key(m)}
    while len(m.rules) < max_rules and time.time() - t0 < time_limit:
        fails, n = verify_traced(m, law, max_fail=30, max_leaves=100000)
        if not fails:
            return m, n
        if fails[-1] is None:
            fails = fails[:-1]
            if not fails: return None, None
        # pick the fail with the smallest resolved root product (least nested)
        best = None
        for f in fails:
            r = exact_rule(m, f)
            if r is None: continue
            size = len(str(r[0]))
            if best is None or size < best[0]: best = (size, r, f)
        if best is None:
            print('no projectable fail; first fail:', describe_fail(fails[0][:3])[:200]); return None, None
        (rule, ri) = best[1]
        m2 = insert_rule(m, rule, len(m.rules))
        if model_key(m2) in seen:
            m2 = insert_rule(m, rule, 0)
        seen.add(model_key(m2)); m = m2
        if verbose:
            print(f'  +rule {len(m.rules)} (fails {len(fails)}, leaves {n}, cx {_complexity(rule)}): {rules_str(Model(m.tags,[rule])).splitlines()[0][:160]}', flush=True)
    return None, None

if __name__ == '__main__':
    law = parse_eq(sys.argv[1]); tl = float(sys.argv[2]) if len(sys.argv) > 2 else 600
    tags, rules = root_model(law, None, False); m = Model(tags, rules)
    m2, n = complete(law, m, time_limit=tl)
    if m2:
        print('COMPLETE with', len(m2.rules), 'rules, leaves', n)
        mm, n2 = minimize(m2, law, deadline=time.monotonic() + 300)
        print('minimised leaves', n2, 'rules', len(mm.rules)); print(rules_str(mm))
    else:
        print('did not complete')
