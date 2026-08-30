"""_x38565_emit.py -- emit the repaired 3-rule skeleton for law 38565 (SET A: free, B101l, B1l).
The shipped gen/rec38565.lean used the softdropped B1s|rd:B101~ rule, which fires spuriously
(seed-991 deep failure); B1l (op(u.1,u) == v.2) is the right rule and the minimiser had dropped it."""
import sys, os, pickle
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import closedform as cf, revalidate as rv, leangen

EQ = 38565
with open(os.path.join(HERE, '_x38565_full.pkl'), 'rb') as f:
    full = pickle.load(f)
rules = [full[i] for i in (0, 1, 6, 10)]
for r in rules:
    print(cf.show_rule(r))
out = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/rep38565'
print(leangen.emit(EQ, out, rules_override=rules))
