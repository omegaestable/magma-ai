"""_z8485_break2.py -- is the 8485 failure specific to variant f, or generic to the whole
accessor-path rule family?

The attack of `_z8485_break.py` in general form.  A rule of this family reads z off a FIXED accessor
path and then verifies the chain  op(op(op(z0, a1 v), u), u) == a2 v.  Build x so that

  * the rule fires at the pair (z, x)  -- i.e. `P = op z x` decodes -- and
  * `x` contains NO occurrence of z at all,

so that at the top pair `(y, J x R)` no accessor path into x or y can recover z (or any w with
op(w,x) = P), and the top pair is forced free.  The trick that makes the chain terminate without
leaving `z` in `a2 x` is a fixed point:  pick  c := op(z0, X1)  (free) and
z := J c (J (J (J zz c) c) c), for which P1 c z holds, so op(c, z) = c and the whole three-step
chain collapses to c.  Then  a2 x = c  and  x = J X1 c  has no z in it.

The only per-ruleset choice is the SHAPE of X1, which must put z0 on that rule's accessor path.
"""
import sys, os, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
sys.setrecursionlimit(200000)
import closedform as cf
from freemodel import normalise, catalog
from laws import parse_eq

G = lambda i: ('g', i)
J = lambda a, b: ('J', a, b)
def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))

# X1 shapes: X1 built so that <path>(X1) = z0 for the named accessor path from a1 v.
def shapes(z0, A, Cc, D, E):
    out = {}
    out['a2a2']       = J(A, J(Cc, z0))                              # z0 = a2 (a2 X1)          [N4]
    out['a2a1a2']     = J(A, J(J(Cc, z0), E))                        # z0 = a2 (a1 (a2 X1))     [C4]
    out['a2a2a2']     = J(A, J(Cc, J(D, z0)))
    out['a2a1a1a2']   = J(A, J(J(J(Cc, z0), D), E))
    out['a1a2']       = J(A, J(z0, Cc))
    out['a2a2a1']     = J(J(A, J(Cc, z0)), E)
    out['a2a1']       = J(J(A, z0), E)
    return out

def instance(X1, z0, zz):
    c = J(z0, X1)                       # = op z0 X1 when that pair is free
    z = J(c, J(J(J(zz, c), c), c))      # P1 c z  ==>  op c z = c
    x = J(X1, c)
    return x, z, c

def occurs(t, s):
    if t == s: return True
    return t[0] == 'J' and (occurs(t[1], s) or occurs(t[2], s))

def main():
    cat = catalog(); law = normalise(parse_eq(cat[8485]))
    mn = {}
    exec(open(os.path.join(HERE, '_x8485_min.py'), encoding='utf-8').read().split("if __name__")[0], mn)
    VAR = mn['VARIANTS']
    X = cf.Extractor(law)
    sets = {'FULL(noexist)': X.rules(exist=False), 'FULL(exist)': X.rules(exist=True)}
    for k in sorted(VAR): sets['variant ' + k] = VAR[k]

    ys = [G(5), G(0), J(G(0), G(1)), J(J(G(0), G(1)), G(2)),
          J(G(1), J(G(2), G(0))), J(J(J(G(0), G(1)), G(2)), G(3))]
    gens = [(G(0), G(1), G(2), G(3), G(4)), (G(0), G(0), G(0), G(0), G(0)),
            (J(G(0), G(1)), G(1), G(2), G(3), G(4)), (G(2), J(G(0), G(1)), G(0), G(1), G(3))]

    print('%-16s %-6s %s' % ('rule set', 'rules', '  per-shape:  fired/failed  (shape name -> "F" law fails, "." holds, "-" P did not decode)'))
    for name, R in sets.items():
        line = []
        for shape_name in shapes(G(0), G(1), G(2), G(3), G(4)):
            nf = nd = ntot = 0
            worst = None
            for gg in gens:
                z0, A, Cc, D, E = gg
                X1 = shapes(z0, A, Cc, D, E)[shape_name]
                zz = G(9)
                x, z, c = instance(X1, z0, zz)
                if occurs(x, z): continue
                for y in ys:
                    C = cf.Closed(law, R)
                    try:
                        P = C.op(z, x)
                        r = C.op(y, C.op(x, C.op(C.op(P, y), y)))
                    except RecursionError:
                        continue
                    ntot += 1
                    if P != J(z, x): nd += 1              # P decoded
                    if r != x:
                        nf += 1
                        if worst is None: worst = (x, y, z)
            tag = 'F' if nf else ('.' if nd else '-')
            line.append('%s:%s%d/%d' % (shape_name, tag, nf, ntot))
        print('%-16s %-6d %s' % (name, len(R), '  '.join(line)), flush=True)

if __name__ == '__main__':
    main()
