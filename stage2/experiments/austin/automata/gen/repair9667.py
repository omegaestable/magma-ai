"""repair9667.py : the generator's rule set for law 9667 is FALSE (gen/hole9667.py has the instance); this is the repair.

Law 9667: x = y * ((z * y) * (x * (y * y))).  Free model: op u v = J u v unless v encodes some x by u.
 R1 (free)   v = J (J z u) (J x (J u u))                                  -> x
 R2 (shipped) v = J w (J x (J u u)), u = J (J _ q) _, w = op q u           -> x     [recovers z as u.1.2]
The shipped R2 recovers z through the R1-shape of `op z u` (u.1 = J z' z); when `op z u` itself fired R2,
u.1 = op q z, which need not be free (hole9667.py: u.1 = g0).  Every rule carries u = v.2.2.1, i.e. after
`op z y` fires, y = J _ (J _ (J z z)) and z = y.2.2.1 is recovered through a provably free occurrence:
 R2' v = J w (J x (J u u)), J?u & J?u.2 & J?u.2.2, w = op (u.2.2.1) u   -> x
Proof sketch that the repaired model satisfies the law for ALL x, y, z (each product of T(x,y,z) in turn):
 y*y free (any rule needs u = v.2.2.1, a proper subterm of v = u); x*(J y y) free (R1: y = J _ x and y.2 = J x x,
 size; R2': y = op z0 x is either J z0 x, then x = J x x, or a proper subterm of x while x = y.2.1); P*(J x (J y y))
 with P = op z y free (any rule needs y = J P P, but P is J z y or a proper subterm of y that is a generator while
 tg P = 2); y*(J P (J x (J y y))): P = J z y -> R1 fires -> x; else op z y fired, so y = J _ (J _ (J z z)),
 z = y.2.2.1 and R2' fires with w = op z y = P -> x.
Run:  python gen/repair9667.py [N]   (N deep tests per seed, default 40000; seeds 11..14; fuzz 20000 x 2)
"""
import sys, os, time, shutil, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import closedform as cf
import fuzz as fz
import leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

law = normalise(parse_eq(catalog()[9667]))
U, V = ('U',), ('V',)
R1 = ([('TG', V), ('TG', ('A1', V)), ('EQ', U, ('A2', ('A1', V))), ('TG', ('A2', V)), ('TG', ('A2', ('A2', V))),
       ('EQ', U, ('A1', ('A2', ('A2', V)))), ('EQ', U, ('A2', ('A2', ('A2', V))))], ('A1', ('A2', V)), 'free')
R2 = ([('TG', V), ('TG', ('A2', V)), ('TG', ('A2', ('A2', V))), ('EQ', U, ('A1', ('A2', ('A2', V)))),
       ('EQ', U, ('A2', ('A2', ('A2', V)))), ('TG', U), ('TG', ('A2', U)), ('TG', ('A2', ('A2', U))),
       ('OPEQ', ('OP', ('A1', ('A2', ('A2', U))), U), ('A1', V))], ('A1', ('A2', V)), 'B0l2')
RULES = [R1, R2]

def g(n): return ('g', n)
def J(a, b): return ('J', a, b)

def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 40000
    for r in RULES: print(cf.show_rule(r))
    C = cf.Closed(law, RULES)
    # the hand instance of hole9667.py
    c, q, d = g(1), g(2), g(0)
    z = J(J(c, q), J(d, J(q, q))); y = J(d, J(J(z, z), J(z, z))); x = g(1)
    s = {'x': x, 'y': y, 'z': z}
    print('hand instance: op z y =', C.op(z, y) == J(z, z), '(fired); law holds:', C.evp(law[1], s) == s[law[0]])
    # a level-3 variant: z itself built so that op q z fires R2'
    q2 = J(g(3), J(J(g(4), g(5)), J(g(4), g(5))))          # q2 = J _ (J _ (J a a)) with a = J g4 g5 ... any shape
    a = J(g(4), g(5)); q3 = J(g(3), J(g(6), J(a, a)))       # op a q3 : needs q3 = J w (J x (J a a)) with w = op (a.2.2.1) a
    print('probe q3:', C.op(a, q3) == J(a, q3))
    tot = nf = 0; t0 = time.time()
    for seed in (11, 12, 13, 14):
        C = cf.Closed(law, RULES)
        tested, fails = cf.deep_tests(C, law, N, 600, seed)
        tot += tested; nf += len(fails)
        for s2, l in fails[:2]:
            print('  FAIL seed', seed, {k: size(v) for k, v in s2.items()})
    print('deep tests', tot, 'fails', nf, 'secs', round(time.time() - t0, 1), 'fired', C.fired)
    ft = ff = 0; t0 = time.time()
    for seed in (7, 8):
        C = cf.Closed(law, RULES)
        tested, fails = fz.fuzz(C, law, RULES, 20000, seed=seed)
        ft += tested; ff += len(fails)
        for s2, l in fails[:2]:
            print('  FUZZ FAIL seed', seed, {k: size(v) for k, v in s2.items()})
    print('fuzz', ft, 'fails', ff, 'secs', round(time.time() - t0, 1), 'fired', C.fired)
    if nf or ff:
        print('NOT REPAIRED'); return
    if '--emit' in sys.argv:
        for nm in ('rec9667.lean', 'rules9667.txt', 'chk9667.py'):
            src = os.path.join(HERE, nm); dst = os.path.join(HERE, nm.replace('9667', '9667_gen0'))
            if os.path.exists(src) and not os.path.exists(dst): shutil.copy(src, dst)
        res = leangen.emit(9667, HERE, rules_override=RULES)
        print(res)
        with open(os.path.join(HERE, 'rules9667.txt'), 'r+', encoding='utf-8') as f:
            body = f.read(); f.seek(0)
            f.write('(REPAIRED rule set, gen/repair9667.py; the original generator output, refuted by gen/hole9667.py, is rules9667_gen0.txt)\n' + body)

if __name__ == '__main__':
    main()
