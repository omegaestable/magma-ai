# rules of the ACCEPTED rec13992.lean (variant3); the original, refuted rules are chk13992_gen0.py
import sys, os, json
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata')
import closedform as cf
from freemodel import normalise, catalog
from laws import parse_eq
law = normalise(parse_eq(catalog()[13992]))
rules = [([('TG', ('V',)), ('TG', ('A1', ('V',))), ('TG', ('A2', ('A1', ('V',)))), ('TG', ('A1', ('A2', ('A1', ('V',))))), ('EQ', ('U',), ('A2', ('A1', ('A2', ('A1', ('V',)))))), ('EQ', ('U',), ('A2', ('A2', ('A1', ('V',))))), ('EQ', ('U',), ('A2', ('V',)))], ('A1', ('A1', ('A2', ('A1', ('V',))))), 'free'), ([('TG', ('V',)), ('TG', ('A1', ('V',))), ('TG', ('A2', ('A1', ('V',)))), ('EQ', ('U',), ('A2', ('A2', ('A1', ('V',))))), ('EQ', ('U',), ('A2', ('V',))), ('TG', ('U',)), ('OPEQ', ('OP', ('A2', ('U',)), ('U',)), ('A1', ('A2', ('A1', ('V',)))))], ('A2', ('U',)), '010l'), ([('TG', ('V',)), ('TG', ('A1', ('V',))), ('EQ', ('U',), ('A2', ('V',))), ('TG', ('U',)), ('OPEQ', ('OP', ('A2', ('U',)), ('U',)), ('A2', ('A1', ('V',)))), ('OPEQ', ('OP', ('A2', ('U',)), ('U',)), ('A2', ('U',)))], ('A2', ('U',)), '01l'), ([('TG', ('V',)), ('EQ', ('U',), ('A2', ('V',))), ('TG', ('U',)), ('TG', ('OP', ('OP', ('A2', ('U',)), ('U',)), ('U',))), ('OPEQ', ('OP', ('A2', ('OP', ('OP', ('A2', ('U',)), ('U',)), ('U',))), ('OP', ('OP', ('A2', ('U',)), ('U',)), ('U',))), ('A1', ('V',)))], ('A2', ('U',)), '0l')]
C = cf.Closed(law, rules)
tested, fails = cf.deep_tests(C, law, int(sys.argv[1]) if len(sys.argv) > 1 else 3000, 300, 11)
print("tested", tested, "fails", len(fails))
