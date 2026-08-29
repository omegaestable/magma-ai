"""Batch tag-automaton synthesis over the research hypotheses."""
import json, sys, time, os, traceback
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
from laws import load_rows, parse_eq
from synth import synthesize, synthesize_any, check_goal, rules_str, Model, minimize
from concrete import random_test, goal_fails

TIME = float(os.environ.get('SYN_TIME', '300'))
NODES = int(os.environ.get('SYN_NODES', '3000'))


def work(item):
    eid, eq, goals = item
    law = parse_eq(eq)
    t0 = time.time()
    out = {'eq1_id': eid, 'eq1': eq}
    try:
        m, info, nodes = synthesize_any(law, time_limit=TIME)
        out['nodes'] = nodes
        out['seconds'] = round(time.time() - t0, 1)
        if m is None:
            out['status'] = 'none'
            score, bm, fails, seed = info
            out['best_score'] = score
            out['best_rules'] = rules_str(bm)
            out['best_fails'] = len(fails)
            return out
        out['status'] = 'model'
        out['seed'] = list(info)
        mm, nleaves = minimize(m, law, deadline=time.monotonic() + 120)
        if nleaves is not None:
            m = mm
        out['leaves'] = nleaves
        out['tags'] = m.tags
        out['rules'] = m.rules
        out['rules_str'] = rules_str(m)
        bad, ex = random_test(m, law, n=50000, depth=6)
        out['random_bad'] = bad
        out['goals'] = {}
        for gid, g in goals.items():
            ref, nb = check_goal(m, parse_eq(g))
            out['goals'][gid] = {'refuted_symbolic': ref, 'refuted_concrete': goal_fails(m, parse_eq(g))}
    except Exception as e:
        out['status'] = 'error'
        out['error'] = traceback.format_exc()
    return out


if __name__ == '__main__':
    rows = load_rows()
    hyps = {}
    goals = {}
    for r in rows:
        hyps[r['eq1_id']] = r['equation1']
        goals.setdefault(r['eq1_id'], {})[r['eq2_id']] = r['equation2']
    items = [(k, v, goals[k]) for k, v in sorted(hyps.items())]
    # control
    items.insert(0, (28770, 'x = (((y * y) * y) * x) * (y * z)', {2: 'x = y'}))
    only = sys.argv[2:] if len(sys.argv) > 2 else None
    skip = set(os.environ.get('SYN_SKIP', '').split(','))
    items = [it for it in items if str(it[0]) not in skip]
    if only:
        items = [it for it in items if str(it[0]) in only]
    outpath = sys.argv[1]
    nproc = int(os.environ.get('SYN_PROCS', '8'))
    with Pool(nproc) as pool, open(outpath, 'w', encoding='utf-8') as f:
        for res in pool.imap_unordered(work, items):
            f.write(json.dumps(res, default=str) + '\n')
            f.flush()
            print(res['eq1_id'], res['status'], res.get('seconds'), res.get('nodes'), res.get('random_bad'), res.get('goals'), flush=True)
