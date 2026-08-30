"""Emit a Lean file asserting  op A B = <the python model's value>  for a systematic sample of pairs.
If Lean proves every line, the Lean `op` and the python model agree on that sample.
Usage:  python qfaith.py <12073|27859|22591> <n_pairs> > out.lean   (appended to the skeleton)
"""
import sys, os, random, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qmod
qmod.UNARY = []
from qmod import terms_upto, E

MODS = {'12073': ('q12073e', True), '27859': ('q27859', True), '22591': ('q22591b', False)}


def lean(t):
    if t[0] == 'g':
        return '(g %d)' % t[1]
    if t[0] == 'E':
        return 'E'
    return '(J %s %s)' % (lean(t[1]), lean(t[2]))


def main():
    name = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    modname, has_e = MODS[name]
    mod = __import__(modname)
    M = mod.M()
    pool = [t for t in terms_upto(int(os.environ.get('QP','7')), 2) if has_e or t != E]
    random.seed(7)
    pairs = []
    small = [t for t in pool if qmod.sz(t) <= 5]
    # every pair of terms of size <= 3, then a random sample of the rest
    tiny = [t for t in pool if qmod.sz(t) <= 3]
    for a, b in itertools.product(tiny, tiny):
        pairs.append((a, b))
    while len(pairs) < len(tiny) ** 2 + n:
        pairs.append((random.choice(small), random.choice(pool)))
    out = []
    for i, (a, b) in enumerate(pairs):
        out.append('theorem F%d : op %s %s = %s := by simp (config := {decide := true}) [op.eq_1, sz, msr, tg, a1, a2]'
                   % (i, lean(a), lean(b), lean(M.op(a, b))))
    print('\n'.join(out))
    print('-- %d pairs' % len(pairs), file=sys.stderr)


if __name__ == '__main__':
    main()
