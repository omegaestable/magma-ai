import sys, os, json
sys.path.insert(0, 'c:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata')
import closedform as cf
from freemodel import normalise, catalog
from laws import parse_eq
law = normalise(parse_eq(catalog()[8485]))
rules = [([('TG', ('V',)), ('TG', ('A2', ('V',))), ('TG', ('A1', ('A2', ('V',)))), ('TG', ('A1', ('A1', ('A2', ('V',))))), ('EQ', ('A1', ('V',)), ('A2', ('A1', ('A1', ('A2', ('V',)))))), ('EQ', ('U',), ('A2', ('A1', ('A2', ('V',))))), ('EQ', ('U',), ('A2', ('A2', ('V',))))], ('A1', ('V',)), 'free'), ([('TG', ('V',)), ('TG', ('A1', ('V',))), ('TG', ('A2', ('A1', ('V',)))), ('TG', ('A1', ('A2', ('A1', ('V',))))), ('OPEQ', ('OP', ('OP', ('OP', ('A2', ('A1', ('A2', ('A1', ('V',))))), ('A1', ('V',))), ('U',)), ('U',)), ('A2', ('V',)))], ('A1', ('V',)), 'zP@x212'), ([('TG', ('V',)), ('TG', ('U',)), ('TG', ('A2', ('U',))), ('TG', ('A2', ('A2', ('U',)))), ('OPEQ', ('OP', ('OP', ('OP', ('A1', ('A2', ('A2', ('U',)))), ('A1', ('V',))), ('U',)), ('U',)), ('A2', ('V',)))], ('A1', ('V',)), 'zP@u22'), ([('TG', ('V',)), ('TG', ('U',)), ('TG', ('A2', ('U',))), ('TG', ('A2', ('A2', ('U',)))), ('TG', ('A1', ('A2', ('A2', ('U',))))), ('OPEQ', ('OP', ('OP', ('OP', ('A1', ('A1', ('A2', ('A2', ('U',))))), ('A1', ('V',))), ('U',)), ('U',)), ('A2', ('V',)))], ('A1', ('V',)), 'zP@u221')]
C = cf.Closed(law, rules)
tested, fails = cf.deep_tests(C, law, int(sys.argv[1]) if len(sys.argv) > 1 else 3000, 300, 11)
print("tested", tested, "fails", len(fails))
