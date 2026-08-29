"""tfuzz6878.py [N] : shape-targeted fuzz of the repaired 6878 rules — random instances where a = z*x, b = x*y
and c = a*b are forced to be decoded in every combination, with leaves drawn from a growing pool (so payloads
are themselves R-shaped terms) and random variable identifications."""
import sys, random, time
sys.path.insert(0, 'C:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf
from freemodel import size, rand_term
sys.path.insert(0, 'C:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
from rep6878 import law, rules, show, which

def J(a, b): return ('J', a, b)
def enc(C, x, y, z):
    """the encoding of x by y with witness z, evaluated in the model: y * ((z*x) * (x*y))"""
    return C.op(y, C.op(C.op(z, x), C.op(x, y)))

def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    random.seed(7)
    C = cf.Closed(law, rules)
    pool = [('g', i) for i in range(4)]
    fails = 0; tested = 0; t0 = time.time(); fired = {}
    def pick():
        return random.choice(pool) if random.random() < 0.8 else rand_term(random.choice([1, 2]))
    while tested < N:
        mode = random.randrange(6)
        z = pick()
        if mode == 0:            # a decoded: x encodes x'' by z  (x = z*((z'*x'')*(x''*z)))
            xpp = pick(); zp = pick()
            x = C.op(z, C.op(C.op(zp, xpp), C.op(xpp, z)))
            if x[0] != 'J' or x[1] != z: continue
            y = pick()
        elif mode == 1:          # b decoded: y encodes y'' by x
            x = pick(); ypp = pick(); zp = pick()
            y = C.op(x, C.op(C.op(zp, ypp), C.op(ypp, x)))
            if y[0] != 'J' or y[1] != x: continue
        elif mode == 2:          # a and b decoded
            xpp = pick(); zp = pick()
            x = C.op(z, C.op(C.op(zp, xpp), C.op(xpp, z)))
            if x[0] != 'J' or x[1] != z: continue
            ypp = pick(); zq = pick()
            y = C.op(x, C.op(C.op(zq, ypp), C.op(ypp, x)))
            if y[0] != 'J' or y[1] != x: continue
        elif mode == 3:          # c decoded, a free: b = enc(c', a), y = enc(b, x)
            x = pick()
            a = C.op(z, x)
            if a[0] != 'J' or a[1] != z: continue
            cp = pick(); zp = pick()
            b = C.op(a, C.op(C.op(zp, cp), C.op(cp, a)))
            if b[0] != 'J' or b[1] != a: continue
            zq = pick()
            y = C.op(x, C.op(C.op(zq, b), C.op(b, x)))
            if y[0] != 'J' or y[1] != x: continue
        elif mode == 4:          # c decoded, a decoded
            xpp = pick(); zp = pick()
            x = C.op(z, C.op(C.op(zp, xpp), C.op(xpp, z)))
            if x[0] != 'J' or x[1] != z: continue
            a = C.op(z, x)
            cp = pick(); zr = pick()
            b = C.op(a, C.op(C.op(zr, cp), C.op(cp, a)))
            if b[0] != 'J' or b[1] != a: continue
            zq = pick()
            y = C.op(x, C.op(C.op(zq, b), C.op(b, x)))
            if y[0] != 'J' or y[1] != x: continue
        else:                    # random identification on top of a random shape
            x = pick(); y = pick()
            r = random.random()
            if r < 0.3: z = x
            elif r < 0.6: z = y
            elif r < 0.8: y = x
        if max(size(x), size(y), size(z)) > 150: continue
        s = {'x': x, 'y': y, 'z': z}
        t = C.evp(law[1], s)
        tested += 1
        w = C.op(y, C.op(C.op(z, x), C.op(x, y)))
        k = which(C, y, w); fired[k] = fired.get(k, 0) + 1
        if t != x:
            fails += 1
            if fails <= 3:
                print('FAIL mode', mode); [print('   %s = %s' % (kk, show(s[kk]))) for kk in ('x', 'y', 'z')]; print('   T =', show(t))
        for v in (x, y, z):
            if size(v) <= 60 and len(pool) < 600: pool.append(v)
    print('tested', tested, 'fails', fails, 'outer rule fired', fired, 'secs', round(time.time() - t0, 1))

if __name__ == '__main__':
    main()
