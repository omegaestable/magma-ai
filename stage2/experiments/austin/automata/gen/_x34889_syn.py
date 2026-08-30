"""Tag-automaton synthesis for law 34889 (single law, one process)."""
import sys, os, json, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
from laws import parse_eq, load_rows
from synth import synthesize_any, check_goal, rules_str, minimize
from concrete import random_test, goal_fails
from freemodel import catalog

EQ = 34889
GOALS = {22818: None, 17522: None, 30591: None}
TL = float(sys.argv[1]) if len(sys.argv) > 1 else 600.0

cat = catalog()
law = parse_eq(cat[EQ])
print('law', EQ, cat[EQ], flush=True)
t0 = time.time()
m, info, nodes = synthesize_any(law, time_limit=TL)
print('nodes', nodes, 'secs', round(time.time() - t0, 1), flush=True)
if m is None:
    score, bm, fails, seed = info
    print('STATUS none  best_score=%s best_fails=%d seed=%s' % (score, len(fails), seed))
    print(rules_str(bm))
    sys.exit(0)
print('STATUS model  seed=%s' % (list(info),))
mm, nleaves = minimize(m, law, deadline=time.monotonic() + 180)
if nleaves is not None:
    m = mm
print('leaves', nleaves)
print('tags', m.tags)
print(rules_str(m))
bad, ex = random_test(m, law, n=50000, depth=6)
print('random_bad', bad, ex)
for gid in GOALS:
    g = parse_eq(cat[gid])
    ref, nb = check_goal(m, g)
    print('goal %d: refuted_symbolic=%s refuted_concrete=%s' % (gid, ref, goal_fails(m, g)))
with open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/_x34889_model.json', 'w', encoding='utf-8') as f:
    json.dump({'eq': EQ, 'tags': m.tags, 'rules': m.rules, 'rev': getattr(m, 'rev', None),
               'default': getattr(m, 'default', None), 'seed': list(info)}, f, default=str)
print('wrote gen/_x34889_model.json')
