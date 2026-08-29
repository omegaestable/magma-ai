import sys, os, json
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata')
import closedform as cf
from freemodel import normalise, catalog
from laws import parse_eq
law = normalise(parse_eq(catalog()[22591]))
rules = [([('TG', ('U',)), ('TG', ('A2', ('U',))), ('EQ', ('A1', ('U',)), ('A1', ('A2', ('U',)))), ('TG', ('V',)), ('TG', ('A1', ('V',))), ('EQ', ('A2', ('A2', ('U',))), ('A1', ('A1', ('V',)))), ('EQ', ('A2', ('A2', ('U',))), ('A2', ('A1', ('V',))))], ('A2', ('A2', ('U',))), 'free'), ([('TG', ('U',)), ('TG', ('A2', ('U',))), ('EQ', ('A1', ('U',)), ('A1', ('A2', ('U',)))), ('TG', ('V',)), ('OPEQ', ('OP', ('A2', ('A2', ('U',))), ('A2', ('A2', ('U',)))), ('A1', ('V',)))], ('A2', ('A2', ('U',))), 'B0s'), ([('TG', ('U',)), ('TG', ('V',)), ('TG', ('A1', ('V',))), ('EQ', ('A1', ('A1', ('V',))), ('A2', ('A1', ('V',)))), ('OPEQ', ('OP', ('A1', ('U',)), ('A1', ('A1', ('V',)))), ('A2', ('U',)))], ('A1', ('A1', ('V',))), 'A1s')]
C = cf.Closed(law, rules)
tested, fails = cf.deep_tests(C, law, int(sys.argv[1]) if len(sys.argv) > 1 else 3000, 300, 11)
print("tested", tested, "fails", len(fails))
