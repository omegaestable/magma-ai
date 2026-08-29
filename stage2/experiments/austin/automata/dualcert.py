"""dualcert.py <accepted_L.lean> <L_eq_id> <R_eq_id> <goal_eq_id> <out.lean>

Build the certificate of the R-form row (R_eq, goal) from an ACCEPTED certificate of its dual L-form law:
flip `inst` (op b a), recompute the refutation of the goal in the flipped magma (instance found with the
semantic free model — generator triples only, so every product is a free J in any correct model), keep the
file's own refutation tactic, and prove `lhs` by trying the six variable permutations of `law`.
"""
import sys, os, re, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import freemodel as fm
from freemodel import normalise, catalog, pvars
from laws import parse_eq

def lt(t):
    if t[0] == 'g': return 'g %d' % t[1]
    return 'J (%s) (%s)' % (lt(t[1]), lt(t[2]))

def main():
    acc, leq, req, goal, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    A = open(acc, encoding='utf-8').read()
    cat = catalog()
    L = normalise(parse_eq(cat[leq]))
    F = fm.Free(L)
    g = normalise(parse_eq(cat[goal])); gv = pvars(g[1])
    order = ['x'] + [v for v in gv if v != 'x']
    def evg(p, s):
        if isinstance(p, str): return s[p]
        a, b = evg(p[0], s), evg(p[1], s)
        return F.op(b, a)          # flipped magma
    inst = None
    for vals in itertools.product([('g', 0), ('g', 1), ('g', 2)], repeat=len(order)):
        s = dict(zip(order, vals))
        if s['x'] != evg(g[1], s): inst = s; break
    if inst is None:
        print('no generator instance refutes the goal in the flipped magma'); sys.exit(1)
    def lp(p):
        if isinstance(p, str): return lt(inst[p])
        return 'op (%s) (%s)' % (lp(p[1]), lp(p[0]))
    # inst
    A2 = re.sub(r'def inst : Magma M := \{ op := [^\n]*\}', 'def inst : Magma M := { op := fun a b => op b a }', A, count=1)
    assert A2 != A, 'inst line not found'
    # rhs block
    i = A2.index('theorem rhs')
    m = re.search(r'\n(?=(theorem |/--|def |abbrev |end submission))', A2[i + 1:]); j = i + 1 + m.start()
    old = A2[i:j]
    lines = old.split('\n')
    tail = [l for l in lines[1:] if l.strip() and not l.strip().startswith(('intro h', 'have := h', 'revert this', 'change ¬'))]
    newrhs = 'theorem rhs : ¬ @EquationRHS M inst := by\n  intro h\n  have := h %s\n  revert this\n  change ¬ %s = %s\n%s' % (
        ' '.join('(%s)' % lt(inst[v]) for v in order), lt(inst[g[0]]), lp(g[1]), '\n'.join(tail))
    A2 = A2[:i] + newrhs + A2[j:]
    # lhs block
    i = A2.index('theorem lhs')
    j = A2.index('end submission', i)
    perms = ' | '.join('exact (law %s).symm' % ' '.join(p) for p in itertools.permutations(['x', 'y', 'z']))
    A2 = A2[:i] + 'theorem lhs : @EquationLHS M inst := by\n  intro x y z\n  first | %s\n\n' % perms + A2[j:]
    open(out, 'w', encoding='utf-8', newline='\n').write(A2)
    print('written', out, len(A2.encode()), 'bytes; instance', {k: lt(v) for k, v in inst.items()})

if __name__ == '__main__':
    main()
