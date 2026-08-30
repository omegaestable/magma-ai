"""nf_failed_21865_21866_22591.py -- the measured obstructions for the three identity laws the
normal-form construction does NOT cover.  Run it to reproduce every instance quoted in the report.

Summary
-------
21865  x = (y*(z*x)) * (x*(x*z))
21866  x = (y*(z*x)) * (x*(x*w))
    Substituting every variable by x gives  x = (x*(x*x)) * (x*(x*x)) : EVERY element is a square.
    So a model with a single square constant S has x = S for all x -- the 12073/27859 family
    (all squares collapse to one point) is structurally unavailable for these two laws.
    The natural replacement is a unary tag P with
        T : op u (J u q) = P u        (the encoding  x*(x*w)  when  x*w  is free)
        D : op u (P a)   = a          (the root decode)
        Z : op u (P u)   = P u        (needed when  w = J x c  makes  x*w  already a  P x)
    and it is refuted by:  y = z = g0, x = P g0, w = g0  (21866)
                           y = z = g0, x = P g0          (21865)
    Both evaluate the law's right-hand side to P (P g0) instead of x = P g0.  The reason is
    structural, not a missing rule: with x = P g0 the LEFT factor A = op y (op z x) evaluates to
    x itself, so the root product is op x (P x) -- which rule Z must send to P x and rule D must
    send to x.  Two law instances demand different values of the SAME pair.

22591  x = (y*(y*x)) * ((x*x)*z)
    THEOREM: 22591 together with "all squares are equal" forces the magma to be trivial.
        y := S, x := S :  S = (S*(S*S)) * ((S*S)*z) = (S*S)*(S*z) = S*(S*z)
                          so  (*)  S*(S*z) = S   for every z.
        y := S         :  x = (S*(S*x)) * ((x*x)*z) = S * (S*z)   [left factor = S by (*),
                          and (x*x)*z = S*z]  = S  by (*).   So x = S for every x.
    So square collapse is unavailable here too, for a different reason than 21865/21866.
    The tag replacement  (Sq: op a a = P a;  L: op (P a) z = P a;  D: op u (P a) = a)  is refuted
    by:  y = g0, x = g0, z = P g0 -- then x*x = P g0 = z, so ((x*x)*z) = op (P g0) (P g0) is a
    pair with u = v, which Sq must send to P (P g0) and L must send to P g0.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import nfcore as nf

def J(a, b): return ('J', a, b)
def P(a): return ('E', a)

def build(rule):
    memo = {}
    def op(u, v):
        k = (u, v)
        r = memo.get(k)
        if r is not None: return r
        r = rule(op, u, v)
        if r is None: r = J(u, v)
        memo[k] = r
        return r
    return op

def rule_2186(op, u, v):
    if v[0] == 'E':
        return v if v[1] == u else v[1]          # Z then D
    if v[0] == 'J' and v[1] == u: return P(u)    # T
    return None

def rule_22591(op, u, v):
    if u == v: return P(u)                       # Sq
    if u[0] == 'E': return u                     # L
    if v[0] == 'E': return v[1]                  # D
    return None

KILLERS = [
    (21866, rule_2186,  {'y': ('g', 0), 'z': ('g', 0), 'x': P(('g', 0)), 'w': ('g', 0)}),
    (21865, rule_2186,  {'y': ('g', 0), 'z': ('g', 0), 'x': P(('g', 0))}),
    (22591, rule_22591, {'y': ('g', 0), 'x': ('g', 0), 'z': P(('g', 0))}),
]

if __name__ == '__main__':
    for eq, rule, s in KILLERS:
        law = nf.get_law(eq)
        op = build(rule)
        ev = nf.evaluator(op)
        got = ev(law[1], s)
        print('%d  %s' % (eq, nf.catalog()[eq]))
        print('   assignment %s' % {k: nf.show(v) for k, v in s.items()})
        print('   RHS -> %s ,  x = %s   =>  %s' % (nf.show(got), nf.show(s['x']),
                                                   'HOLDS' if got == s['x'] else 'REFUTED'))
        for ms, g in ((5, 1), (6, 1)):
            pool = nf.carrier_upto(ms, g, use_S=False)
            n, f = nf.exhaustive(op, law, pool, limit=3)
            print('   exhaustive carrier<=%d g%d (no S): %d assignments, %d fails' % (ms, g, n, len(f)))
