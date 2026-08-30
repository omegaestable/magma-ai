"""_pb_common.py <rec<eq>.lean> : what may a one-unfold digest assert?

Parses every `def Pk (u v : M) : Prop := c1 ∧ c2 ∧ …` of a generated skeleton, prints the conjuncts
shared by ALL rules (the digest's precondition), the per-rule results of the if-chain, and, for each
conjunct, how many rules carry it (so a near-common conjunct can be split off as a two-case digest).
"""
import re
import sys
from collections import Counter


def main(path: str) -> None:
    src = open(path, encoding='utf-8').read()
    defs = re.findall(r'^def (P\d+) \(u v : M\) : Prop := (.*)$', src, re.M)
    sets = {}
    for name, body in defs:
        sets[name] = set(c.strip() for c in body.split('∧'))
    print('%d rules' % len(sets))
    cnt = Counter(c for s in sets.values() for c in s)
    common = set.intersection(*sets.values()) if sets else set()
    print('\nCOMMON to all %d rules (safe digest precondition):' % len(sets))
    for c in sorted(common):
        print('   ', c)
    print('\nnear-common (count / %d):' % len(sets))
    for c, n in cnt.most_common(12):
        if c not in common:
            print('   %3d  %s' % (n, c))
    i = src.index('def op (u v : M) : M :=')
    j = src.index('termination_by', i)
    res = re.findall(r'then ([^\n]*?)$', src[i:j], re.M)
    print('\nresults of the if-chain (dedup):')
    for r in sorted(set(x for x in res if not x.startswith('op '))):
        print('   ', r)


if __name__ == '__main__':
    main(sys.argv[1])
