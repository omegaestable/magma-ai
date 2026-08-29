"""Tag-automaton synthesiser: seed models + CEGIS repairs, verified by symb.Model (complete)."""
import itertools, heapq, sys, json, time
from symb import Model, Var, State, pretty, subterm_of, _vars
from laws import parse_eq, show


# ---------- traced evaluation ----------
def eval_traced(m, term, env, st, trace):
    if isinstance(term, str):
        yield (st, env[term], trace)
        return
    if m.rev:
        pairs = ((s2, u, v, t2) for s1, v, t1 in eval_traced(m, term[1], env, st, trace) for s2, u, t2 in eval_traced(m, term[0], env, s1, t1))
    else:
        pairs = ((s2, u, v, t2) for s1, u, t1 in eval_traced(m, term[0], env, st, trace) for s2, v, t2 in eval_traced(m, term[1], env, s1, t1))
    for s2, u, v, t2 in pairs:
        if True:
            pending = [s2]
            for ri, (pu, pv, rhs) in enumerate(m.rules):
                nxt = []
                for s in pending:
                    for s3, b in m.match_rule(pu, pv, u, v, s):
                        if b is None:
                            nxt.append(s3)
                        else:
                            val = m.inst(rhs, b)
                            yield (s3, val, t2 + [(u, v, val, ri)])
                pending = nxt
            for s in pending:
                val = (m.default, u, v)
                yield (s, val, t2 + [(u, v, val, None)])


def verify_traced(m, law, max_fail=None, max_leaves=200000, deadline=None):
    lhs, rhs = law
    vs = sorted(set(_vars(rhs)) | {lhs})
    env = {v: Var('M', v) for v in vs}
    fails = []
    n = 0
    for st, val, tr in eval_traced(m, rhs, env, State(), []):
        n += 1
        if st.resolve(val) != st.resolve(env[lhs]):
            fails.append((st, env, val, tr))
            if max_fail and len(fails) >= max_fail:
                break
        if n >= max_leaves or (deadline is not None and (n & 255) == 0 and time.monotonic() > deadline):
            fails.append(None)
            break
    return fails, n


# ---------- spines ----------
def spines(t, v):
    if t == v:
        return [[]]
    if isinstance(t, str):
        return []
    out = []
    for p in spines(t[0], v):
        out.append([('L', t[1])] + p)
    for p in spines(t[1], v):
        out.append([('R', t[0])] + p)
    return out


# ---------- pattern generalisation ----------
def generalize(t, st, depth, keep_path=(), counter=None):
    t = st.resolve(t)
    if counter is None:
        counter = {}
    if isinstance(t, Var):
        return counter.setdefault(('v', t.id), '$v%d' % t.id)
    if depth <= 0 and not keep_path:
        return counter.setdefault(('t', t), '$t%d' % len(counter))
    if t[0] == 'G':
        return (t[0], counter.setdefault(('v', t[1].id), '$n%d' % t[1].id)) if isinstance(t[1], Var) else t
    args = []
    for i, a in enumerate(t[1:], 1):
        kp = keep_path[1:] if keep_path and keep_path[0] == i else ()
        args.append(generalize(a, st, depth - 1, kp, counter))
    return (t[0],) + tuple(args)


def paths_to(t, s, st, pre=()):
    t = st.resolve(t)
    if t == s:
        return [pre]
    if isinstance(t, Var):
        return []
    out = []
    for i, a in enumerate(t[1:], 1):
        out += paths_to(a, s, st, pre + (i,))
    return out


def _at(p, path):
    for i in path:
        p = p[i]
    return p


# ---------- seeds ----------
def generic_value(m, off):
    """Evaluate term `off` on distinct generators under m; return (state, value, env) of the generic branch."""
    vs = sorted(set(_vars(off)))
    atoms = {v: Var('N') for v in vs}
    env = {v: ('G', atoms[v]) for v in vs}
    st = State()
    for a, b in itertools.combinations(vs, 2):
        st.diseq.append((atoms[a], atoms[b]))
    for s, val in m.eval(off, env, st):
        return s, val, env
    return None


def value_to_pattern(s, val, depth, c=None):
    if c is None:
        c = {}
    t = s.resolve(val)
    if isinstance(t, tuple) and t[0] == 'G':
        return c.setdefault(('g', t[1].id), '$g%d' % t[1].id)
    if isinstance(t, Var):
        return c.setdefault(('v', t.id), '$v%d' % t.id)
    if depth <= 0:
        key = ('o', id(t))
        if key not in c:
            c[key] = '$o%d' % len(c)
        return c[key]
    return (t[0],) + tuple(value_to_pattern(s, a, depth - 1, c) for a in t[1:])


def build_model(law, spine, check_depth, square=False):
    """Stage-tag model: innermost step keyed on the off-spine term's generic shape (to check_depth),
    every other step keyed on the stage tag of the spine argument, root projects x."""
    lhs, rhs = law
    k = len(spine)
    tags = {}
    rules = []
    if square:
        rules.append(('$u', '$u', ('S', '$u')))
        tags['S'] = 1

    def spine_pat(i):
        side, off = spine[i]
        tag = 'T%d' % (i + 1)
        inner = '$x' if i == k - 1 else spine_pat(i + 1)
        return (tag, inner, '$w%d' % i) if side == 'L' else (tag, '$w%d' % i, inner)
    for i in range(k - 1, -1, -1):
        side, off = spine[i]
        if i == k - 1:
            if isinstance(off, str) or check_depth == 0:
                offpat = '$b'
            else:
                s, val, env = generic_value(Model(dict(tags), list(rules)), off)
                offpat = value_to_pattern(s, val, check_depth)
                if not isinstance(offpat, tuple):
                    offpat = '$b'
            sp = '$x'
        else:
            offpat = '$b'
            sp = spine_pat(i + 1)
        pu, pv = (sp, offpat) if side == 'L' else (offpat, sp)
        if i == 0:
            rules.append((pu, pv, '$x'))
        else:
            tag = 'T%d' % (i + 1)
            tags[tag] = 2
            rules.append((pu, pv, (tag, pu, pv)))
    return tags, rules


def root_model(law, depth, square=False):
    """Term model with root reduction: one rule = the generic shape of the RHS (to `depth`) -> x."""
    lhs, rhs = law
    tags = {}
    rules = []
    if square:
        rules.append(('$u', '$u', ('S', '$u')))
        tags['S'] = 1
    m0 = Model(dict(tags), list(rules))
    s, val, env = generic_value(m0, rhs)
    c = {}
    pat = value_to_pattern(s, val, 99 if depth is None else depth, c)
    xatom = env[lhs][1]
    xp = c.get(('g', xatom.id))
    if xp is None or not isinstance(pat, tuple):
        return None
    rules.append((pat[1], pat[2], xp))
    return tags, rules


def rec_root_model(law, square=False):
    """Self-consistent root model: the root rule matches the RHS structurally down to the first
    occurrence of every variable; every other compound off-spine subterm whose variables are all
    already bound becomes an OP check (the position must equal the model's own evaluation)."""
    lhs, rhs = law
    tags = {}
    rules = []
    if square:
        rules.append(('$u', '$u', ('S', '$u')))
        tags['S'] = 1
    bound = set()

    def go(t):
        if isinstance(t, str):
            bound.add(t)
            return '$' + t
        vs = set(_vars(t))
        if vs <= bound:
            return ('OP', go_inst(t[0]), go_inst(t[1]))
        return ('J', go(t[0]), go(t[1]))

    def go_inst(t):
        if isinstance(t, str):
            return '$' + t
        return ('OP', go_inst(t[0]), go_inst(t[1]))
    pu = go(rhs[0])
    pv = go(rhs[1])
    if lhs not in bound:
        return None
    rules.append((pu, pv, '$' + lhs))
    return tags, rules


def seed_models(law):
    lhs, rhs = law
    seeds = []
    for sq in (False, True):
        for d in (None, 4, 3, 2):
            r = root_model(law, d, sq)
            if r:
                seeds.append((('root', d, sq), Model(*r)))
    for si, sp in enumerate(spines(rhs, lhs)):
        for cd in (0, 1, 2, 3):
            for sq in (False, True):
                tags, rules = build_model(law, sp, cd, sq)
                seeds.append((('spine', si, cd, sq), Model(tags, rules)))
    return seeds


# ---------- repairs ----------
def repair_candidates(m, fail, depths=(0, 1, 2, 3, 4, 5, 6)):
    st, env, val, trace = fail
    x = st.resolve(env['x'])
    cands = []
    seen = set()

    def add(kind, rule, before):
        pu, pv, rhs = rule
        pu, pv = share_repeats(pu, pv)
        rule = (pu, pv, rhs)
        key = (json.dumps(rule, default=str), before)
        if key not in seen:
            seen.add(key)
            cands.append((kind, rule, before))
    u, v, rv, ri = trace[-1]
    pos = [(0, p) for p in paths_to(u, x, st)] + [(1, p) for p in paths_to(v, x, st)]
    for side, path in pos:
        for du in depths:
            for dv in depths:
                c = {}
                if side == 0:
                    pu = generalize(u, st, du, path, c)
                    pv = generalize(v, st, dv, (), c)
                    rhs = _at(pu, path)
                else:
                    pu = generalize(u, st, du, (), c)
                    pv = generalize(v, st, dv, path, c)
                    rhs = _at(pv, path)
                for before in {ri, 0, len(m.rules)}:
                    add('proj', (pu, pv, rhs), before)
    for (u, v, rv, ri2) in reversed(trace):
        lost = (subterm_of(u, x, st) or subterm_of(v, x, st)) and not subterm_of(rv, x, st)
        if ri2 is not None or lost:
            for du in depths:
                for dv in depths:
                    c = {}
                    pu = generalize(u, st, du, (), c)
                    pv = generalize(v, st, dv, (), c)
                    add('keep', (pu, pv, (m.default, pu, pv)), 0 if ri2 is None else ri2)
    return cands


def _complexity(rule):
    pu, pv, rhs = rule
    vs = _pvars(pu) + _pvars(pv)
    neq = len(vs) - len(set(vs))
    def depth(p):
        if isinstance(p, str):
            return 0
        if p[0] == 'AS':
            return depth(p[2])
        return 1 + max((depth(a) for a in p[1:]), default=0)
    return (depth(pu) + depth(pv), neq)


def filter_candidates(cands, max_eq=4, max_depth=9):
    out = []
    for kind, rule, before in cands:
        d, neq = _complexity(rule)
        if neq <= max_eq and d <= max_depth:
            out.append((d + neq, kind, rule, before))
    out.sort(key=lambda t: t[0])
    return [(k, r, b) for _, k, r, b in out]


def insert_rule(m, rule, before):
    rules = list(m.rules)
    idx = len(rules) if before is None else min(before, len(rules))
    rules.insert(idx, rule)
    m2 = Model(m.tags, rules, m.default)
    m2.rev = m.rev
    m2.vfirst = m.vfirst
    return m2


def model_key(m):
    return json.dumps(m.rules, sort_keys=True, default=str)


def synthesize(law, max_rules=14, time_limit=120, verbose=False, seed_time=None, max_fail=20):
    """Global best-first search over all seeds with lazy candidate verification."""
    seeds = seed_models(law)
    seen = set()
    t0 = time.monotonic()
    cnt = itertools.count()
    heap = []
    for info, m in seeds:
        key = model_key(m)
        if key in seen:
            continue
        seen.add(key)
        fails, n = verify_traced(m, law, max_fail=max_fail, max_leaves=30000, deadline=time.monotonic() + 120)
        if not fails:
            return m, info, 0
        if fails[-1] is None:
            continue
        heapq.heappush(heap, (len(fails) / n + 0.01 * len(m.rules), next(cnt), m, fails, info))
    best = None
    total = 0
    nodes = 0
    while heap and time.monotonic() - t0 < time_limit:
        score, _, m, fails, info = heapq.heappop(heap)
        if fails is None:
            fails, n = verify_traced(m, law, max_fail=max_fail, max_leaves=4000, deadline=min(t0 + time_limit, time.monotonic() + 60))
            total += 1
            if not fails:
                return m, info, total
            if fails[-1] is None:
                continue
            score = len(fails) / n + 0.01 * len(m.rules)
            if heap and heap[0][0] < score:
                heapq.heappush(heap, (score, next(cnt), m, fails, info))
                continue
        nodes += 1
        if best is None or score < best[0]:
            best = (score, m, fails, info)
        if verbose:
            print(f'  {info} node {nodes} score {score:.3f} rules {len(m.rules)} fails {len(fails)}', flush=True)
        if len(m.rules) >= max_rules:
            continue
        for f in fails[:2]:
            for kind, rule, before in directed_repairs(m, f) + filter_candidates(repair_candidates(m, f)):
                m2 = insert_rule(m, rule, before)
                key = model_key(m2)
                if key in seen:
                    continue
                seen.add(key)
                heapq.heappush(heap, (score - (2e-6 if kind == "directed" else 1e-6), next(cnt), m2, None, info))
    return None, best, total


def check_goal(m, goal):
    lhs, rhs = goal
    vs = sorted(set(_vars(rhs)) | {lhs})
    atoms = {v: Var('N') for v in vs}
    env = {v: ('G', atoms[v]) for v in vs}
    st = State()
    for a, b in itertools.combinations(vs, 2):
        st.diseq.append((atoms[a], atoms[b]))
    results = []
    for s, val in m.eval(rhs, env, st):
        results.append(s.resolve(val) != s.resolve(env[lhs]))
    return all(results), len(results)


def rules_str(m):
    return '\n'.join(f'  {_ps(pu)} ◇ {_ps(pv)} -> {_ps(r)}' for pu, pv, r in m.rules) + f'\n  default -> {m.default}(u,v)'


def _ps(p):
    if isinstance(p, str):
        return p
    if p[0] == 'AS':
        return p[1] + '@' + _ps(p[2])
    return p[0] + '(' + ','.join(_ps(a) for a in p[1:]) + ')'


# ---------- rule minimisation (fewer / shallower patterns => smaller proof trees) ----------
def _positions(p, pre=()):
    """all positions of constructor sub-patterns (deepest first)."""
    out = []
    if isinstance(p, tuple):
        for i, a in enumerate(p[1:], 1):
            out += _positions(a, pre + (i,))
        out.append(pre)
    return out


def _replace(p, path, new):
    if not path:
        return new
    return p[:path[0]] + (_replace(p[path[0]], path[1:], new),) + p[path[0] + 1:]


def _pvars(p):
    if isinstance(p, str):
        return [p]
    if p[0] == 'AS':
        return [p[1]] + _pvars(p[2])
    return [v for a in p[1:] for v in _pvars(a)]


def share_repeats(pu, pv, counter=None):
    """Replace repeated compound sub-patterns by one AS-binding plus references, so a repeated
    compound costs one equality check instead of one per variable."""
    if counter is None:
        counter = itertools.count(1)
    counts = {}

    def collect(p):
        if isinstance(p, str) or p[0] == 'AS':
            return
        counts[p] = counts.get(p, 0) + 1
        for a in p[1:]:
            collect(a)
    collect(pu)
    collect(pv)
    rep = {p for p, n in counts.items() if n >= 2}
    if not rep:
        return pu, pv
    names = {}

    def go(p):
        if isinstance(p, str) or p[0] == 'AS':
            return p
        if p in rep:
            if p in names:
                return names[p]
            nm = '$s%d' % next(counter)
            names[p] = nm
            return ('AS', nm, (p[0],) + tuple(go(a) for a in p[1:]))
        return (p[0],) + tuple(go(a) for a in p[1:])
    return go(pu), go(pv)


def minimize(m, law, deadline=None, verbose=False):
    """Greedy: delete rules, then generalise sub-patterns to fresh variables and drop repeated
    variables (equality checks), keeping every change that still verifies with 0 fails.
    Returns (model, leaves)."""
    def ok(mm):
        if deadline and time.monotonic() > deadline:
            return None
        f, n = verify_traced(mm, law, max_fail=1, deadline=(time.monotonic() + 20))
        return None if f else n
    cur = m
    best_n = ok(cur)
    if best_n is None:
        return m, None
    # 1. delete rules
    changed = True
    while changed:
        changed = False
        for i in range(len(cur.rules)):
            mm = Model(cur.tags, cur.rules[:i] + cur.rules[i + 1:], cur.default)
            mm.rev = cur.rev
            mm.vfirst = cur.vfirst
            n = ok(mm)
            if n is not None and n <= best_n:
                cur, best_n, changed = mm, n, True
                break
    # 2. generalise sub-patterns / drop equality checks
    fresh = itertools.count(1000)
    changed = True
    while changed:
        changed = False
        for i, (pu, pv, rhs) in enumerate(cur.rules):
            used = set(_pvars(rhs)) if not isinstance(rhs, str) else {rhs}
            for side in (0, 1):
                pat = (pu, pv)[side]
                for path in _positions(pat):
                    if not path and isinstance(pat, str):
                        continue
                    sub = pat
                    for i2 in path:
                        sub = sub[i2]
                    if isinstance(sub, str):
                        continue
                    if any(v in used for v in _pvars(sub)):
                        continue  # needed by the rhs
                    newpat = _replace(pat, path, '$m%d' % next(fresh))
                    rule = (newpat, pv, rhs) if side == 0 else (pu, newpat, rhs)
                    mm = Model(cur.tags, cur.rules[:i] + [rule] + cur.rules[i + 1:], cur.default)
                    mm.rev = cur.rev
                    mm.vfirst = cur.vfirst
                    mm.vfirst = cur.vfirst
                    n = ok(mm)
                    if n is not None and n <= best_n:
                        cur, best_n, changed = mm, n, True
                        break
                if changed:
                    break
            if changed:
                break
            # drop an equality check: rename a repeated occurrence of a variable not used in rhs
            allv = _pvars(pu) + _pvars(pv)
            for v in set(allv):
                if allv.count(v) > 1 and v not in used:
                    # rename the last occurrence
                    def rename_last(p, target, new, state):
                        if isinstance(p, str):
                            if p == target and not state['done']:
                                state['done'] = True
                                return new
                            return p
                        return (p[0],) + tuple(rename_last(a, target, new, state) for a in reversed(p[1:]))[::-1]
                    st = {'done': False}
                    npv = rename_last(pv, v, '$m%d' % next(fresh), st)
                    npu = pu if st['done'] else rename_last(pu, v, '$m%d' % next(fresh), st)
                    mm = Model(cur.tags, cur.rules[:i] + [(npu, npv, rhs)] + cur.rules[i + 1:], cur.default)
                    mm.rev = cur.rev
                    mm.vfirst = cur.vfirst
                    mm.vfirst = cur.vfirst
                    n = ok(mm)
                    if n is not None and n <= best_n:
                        cur, best_n, changed = mm, n, True
                        break
            if changed:
                break
    return cur, best_n


# ---------- duality ----------
def dual_pattern(p, m):
    """swap the two arguments of every binary constructor (patterns and rhs)."""
    if isinstance(p, str):
        return p
    if p[0] == 'G':
        return p
    if p[0] == 'AS':
        return ('AS', p[1], dual_pattern(p[2], m))
    args = [dual_pattern(a, m) for a in p[1:]]
    if len(args) == 2:
        args = [args[1], args[0]]
    return (p[0],) + tuple(args)


def dual_model(m):
    rules = [(dual_pattern(pv, m), dual_pattern(pu, m), dual_pattern(rhs, m)) for (pu, pv, rhs) in m.rules]
    m2 = Model(m.tags, rules, m.default)
    m2.rev = not m.rev
    m2.vfirst = not m.vfirst
    return m2


# ---------- orientation ----------
def good_orientation(law):
    """True if some spine has its innermost product with x on the LEFT or with a compound
    off-spine term (so the innermost step can be keyed without breaking injectivity)."""
    lhs, rhs = law
    for sp in spines(rhs, lhs):
        side, off = sp[-1]
        if side == 'L' or not isinstance(off, str):
            return True
    return False


def synthesize_any(law, **kw):
    """Synthesise directly when the orientation is good; otherwise on the dual law and dualise
    the model back (verified on the original).  Returns (model, info, verifications)."""
    from laws import dual as _dual
    if good_orientation(law):
        return synthesize(law, **kw)
    dl = (_dual(law[0]), _dual(law[1]))
    m, info, n = synthesize(dl, **kw)
    if m is None:
        return m, info, n
    dm = dual_model(m)
    f, _ = verify_traced(dm, law, max_fail=1, max_leaves=200000)
    if f:
        return None, ('dual model failed re-verification',), n
    return dm, ('dual',) + tuple(info), n


# ---------- directed repairs (keep only the paths that matter) ----------
def generalize_paths(t, st, paths, counter):
    """keep constructors on any of `paths` (tuples of arg indices); everything else opaque,
    keyed structurally so repeated subterms become equality checks."""
    t = st.resolve(t)
    if isinstance(t, Var):
        return counter.setdefault(('v', t.id), '$v%d' % t.id)
    if not any(paths):
        if () in paths:
            pass
    keep = any(p == () or p for p in paths) and any(True for p in paths)
    if not paths:
        return counter.setdefault(('t', t), '$t%d' % len(counter))
    if t[0] == 'G':
        return (t[0], counter.setdefault(('v', t[1].id), '$n%d' % t[1].id)) if isinstance(t[1], Var) else t
    args = []
    for i, a in enumerate(t[1:], 1):
        sub = [p[1:] for p in paths if p and p[0] == i]
        args.append(generalize_paths(a, st, sub, counter))
    return (t[0],) + tuple(args)


def directed_repairs(m, fail):
    """Candidates built from the failing trace: at the root (u,v), keep the path to x, the path(s)
    to every early-unload payload occurring in v, and the same payload's path inside u."""
    st, env, val, trace = fail
    x = st.resolve(env['x'])
    u, v, rv, ri = trace[-1]
    xpos = [(0, p) for p in paths_to(u, x, st)] + [(1, p) for p in paths_to(v, x, st)]
    if not xpos:
        return []
    payloads = []
    for (a, b, r, rj) in trace[:-1]:
        if rj is not None and not (isinstance(st.resolve(r), tuple) and st.resolve(r)[0] == m.default):
            payloads.append(st.resolve(r))
    cands = []
    for side, xp in xpos:
        pu_paths = [xp] if side == 0 else []
        pv_paths = [xp] if side == 1 else []
        for w in payloads:
            pv_paths += paths_to(v, w, st)
            pu_paths += paths_to(u, w, st)
        # variants: with and without the payload's path in u / in v
        variants = [(pu_paths, pv_paths)]
        if payloads:
            variants.append(([xp] if side == 0 else [], ([xp] if side == 1 else []) + [q for w in payloads for q in paths_to(v, w, st)]))
        for pup, pvp in variants:
            c = {}
            pu = generalize_paths(u, st, pup, c)
            pv = generalize_paths(v, st, pvp, c)
            try:
                rhs = _at(pu if side == 0 else pv, xp)
            except (IndexError, TypeError):
                continue
            if not isinstance(rhs, str):
                continue
            pu2, pv2 = share_repeats(pu, pv)
            # rhs after sharing
            def at_shared(p, path):
                for i in path:
                    while isinstance(p, tuple) and p[0] == 'AS':
                        p = p[2]
                    if not isinstance(p, tuple) or i >= len(p):
                        return None
                    p = p[i]
                while isinstance(p, tuple) and p[0] == 'AS':
                    p = p[1]
                return p
            rhs2 = at_shared(pu2 if side == 0 else pv2, xp)
            if isinstance(rhs2, str):
                for before in (len(m.rules), ri if ri is not None else 0):
                    cands.append(('directed', (pu2, pv2, rhs2), before))
    return cands


if __name__ == '__main__':
    law = parse_eq(sys.argv[1] if len(sys.argv) > 1 else 'x = (((y * y) * y) * x) * (y * z)')
    tl = float(sys.argv[2]) if len(sys.argv) > 2 else 120
    m, info, nodes = synthesize(law, verbose='-v' in sys.argv, time_limit=tl)
    if m:
        print('FOUND after', nodes, 'verifications; seed', info)
        print(rules_str(m))
    else:
        print('no model; best', info[0] if info else None, 'verifications', nodes)
        if info:
            print(rules_str(info[1]))
