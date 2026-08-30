"""Wave-3 (W3-6) re-validation of the inherited 12234 rule set.

The session-7 handover flags this model as needing re-validation, and two inherited models
have been proved FALSE today.  This runs the full W3-6 standard:
  rv.run_tests(law, rules, [3,4,5], 3000, 12000)   -- exhaustive small terms + deep + fuzz
                                                      + closure fuzz + critical fuzz
  cf.deep_tests at 20,000 on 5 seeds
  smallcheck semantic vs --closed
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import closedform as cf
import revalidate as rv
import leangen
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 12234
cat = catalog()
orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
print('law', EQ, cat[EQ], 'dualized' if dualized else 'L-form')
print('normalised', law)

# the rule set shipped in gen/chk12234.py / gen/rec12234.lean
rules = [([('TG', ('V',)), ('TG', ('A1', ('V',))), ('TG', ('A1', ('A1', ('V',)))), ('EQ', ('U',), ('A2', ('A1', ('V',)))), ('TG', ('A2', ('V',))), ('EQ', ('A2', ('A1', ('A1', ('V',)))), ('A1', ('A2', ('V',)))), ('EQ', ('U',), ('A2', ('A2', ('V',))))], ('A2', ('A1', ('A1', ('V',)))), 'free'), ([('TG', ('V',)), ('TG', ('A1', ('V',))), ('TG', ('A1', ('A1', ('V',)))), ('EQ', ('U',), ('A2', ('A1', ('V',)))), ('OPEQ', ('OP', ('A2', ('A1', ('A1', ('V',)))), ('U',)), ('A2', ('V',)))], ('A2', ('A1', ('A1', ('V',)))), 'B1l'), ([('TG', ('V',)), ('TG', ('A1', ('V',))), ('EQ', ('U',), ('A2', ('A1', ('V',)))), ('TG', ('A2', ('V',))), ('EQ', ('U',), ('A2', ('A2', ('V',)))), ('TG', ('A1', ('A2', ('V',)))), ('TG', ('A1', ('A1', ('A2', ('V',))))), ('OPEQ', ('OP', ('A2', ('A1', ('A1', ('A2', ('V',))))), ('A1', ('A2', ('V',)))), ('A1', ('A1', ('V',))))], ('A1', ('A2', ('V',))), 'B00l'), ([('TG', ('V',)), ('TG', ('A1', ('V',))), ('EQ', ('U',), ('A2', ('A1', ('V',)))), ('TG', ('U',)), ('TG', ('A1', ('U',))), ('OPEQ', ('OP', ('A2', ('A1', ('U',))), ('U',)), ('A2', ('V',))), ('TG', ('A2', ('A1', ('U',)))), ('TG', ('A1', ('A2', ('A1', ('U',))))), ('OPEQ', ('OP', ('A2', ('A1', ('A2', ('A1', ('U',))))), ('A2', ('A1', ('U',)))), ('A1', ('A1', ('V',))))], ('A2', ('A1', ('U',))), 'B00l,B1l'), ([('TG', ('V',)), ('TG', ('A2', ('V',))), ('EQ', ('U',), ('A2', ('A2', ('V',)))), ('TG', ('U',)), ('TG', ('A1', ('U',))), ('OPEQ', ('OP', ('A2', ('A1', ('U',))), ('U',)), ('A1', ('V',))), ('TG', ('A2', ('A1', ('U',)))), ('EQ', ('A1', ('A2', ('V',))), ('A2', ('A2', ('A1', ('U',)))))], ('A1', ('A2', ('V',))), 'B0l'), ([('TG', ('V',)), ('TG', ('A2', ('V',))), ('EQ', ('U',), ('A2', ('A2', ('V',)))), ('TG', ('U',)), ('TG', ('A1', ('U',))), ('OPEQ', ('OP', ('A2', ('A1', ('U',))), ('U',)), ('A1', ('V',))), ('TG', ('A1', ('A2', ('V',)))), ('TG', ('A1', ('A1', ('A2', ('V',))))), ('OPEQ', ('OP', ('A2', ('A1', ('A1', ('A2', ('V',))))), ('A1', ('A2', ('V',)))), ('A2', ('A1', ('U',))))], ('A1', ('A2', ('V',))), 'B0l,B00l')]

print('rules:', len(rules))

fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
print('run_tests fails:', len(fails))
kinds = {}
for (s, r, kind, sd) in fails:
    kinds[kind] = kinds.get(kind, 0) + 1
print('  by kind:', kinds)
for (s, r, kind, sd) in fails[:8]:
    print('  FAIL[%s seed=%s] assignment=%s got=%s' % (kind, sd, s, r))

tot = 0
for sd in (11, 12, 13, 14, 15):
    C = cf.Closed(law, rules)
    t, f = cf.deep_tests(C, law, 20000, 600, sd)
    tot += t
    print('deep_tests seed=%d tested=%d fails=%d' % (sd, t, len(f)))
    for (s, r) in f[:3]:
        print('   ', s, '->', r)
print('deep total tested', tot)
