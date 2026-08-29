import sys, os, json, time
sys.path.insert(0, r'c:\Users\nacho\Documents\GitHub\magma-ai\stage2\experiments\austin\automata')
import closedform as cf
import revalidate as rv
from freemodel import normalise, catalog
from laws import parse_eq
import leangen

EQ = 6912
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
exec(open(r'c:\Users\nacho\Documents\GitHub\magma-ai\stage2\experiments\austin\automata\gen\chk6912.py').read().split('C = cf.Closed')[0])

U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
a1u = A1(U); a2u = A2(U)
a1a1u = A1(a1u); a2a1u = A2(a1u)
a1a2u = A1(a2u); a2a2u = A2(a2u)
a1a2a2u = A1(a2a2u); a2a2a2u = A2(a2a2u)
a2v = A2(V)

deep3 = ([
  ('TG', V), ('EQ', U, A1(V)), ('TG', U), ('TG', a1u),
  ('EQ', a1a1u, a2a1u), ('TG', a2u), ('EQ', a1a2u, a1a1u),
  ('TG', a2a2u), ('EQ', a1a2a2u, a2a2a2u),
  ('EQ', a2v, a1a1u),
], a2a2u, 'DEEP3~')

deep4 = ([
  ('TG', V), ('EQ', U, A1(V)), ('TG', U), ('TG', a2u),
  ('TG', a1a2u),
  ('EQ', a1a2u, a2a2u),
  ('EQ', a2v, a1a2u),
], a1a2u, 'DEEP4~')

# tighter deep5: require u itself compound with BOTH children compound (excludes u=J(atom,atom))
deep5 = ([
  ('TG', V), ('EQ', U, A1(V)), ('EQ', a2v, U),
  ('TG', U), ('TG', a1u), ('TG', a2u),
], ('J', V, V), 'DEEP5~')

for label, extra in [('deep3+4+5tight', [deep3,deep4,deep5])]:
    rules2 = rules[:10]+extra+rules[10:]
    print('===', label, 'nrules', len(rules2), flush=True)
    t0=time.time()
    fails = rv.run_tests(law, rules2, [3, 4, 5], 3000, 12000)
    print('NFAILS', len(fails), 'secs', time.time()-t0, flush=True)
    for f in fails[:20]:
        s, r, kind, sd = f
        print(kind, sd, {k: v for k,v in s.items()})
