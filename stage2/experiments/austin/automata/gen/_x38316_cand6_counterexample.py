"""Deterministic counterexample for the five-rule 38316/cand6 model.

This is deliberately a single-instance regression check.  It loads the exact
rule list used to emit v38316.lean and v38316b.lean, evaluates the dual L-form
chain, and asserts that only R5 fires (at ``a``) before the law fails.

Run from the repository root with:

    python -B stage2/experiments/austin/automata/gen/_x38316_cand6_counterexample.py
"""

from __future__ import annotations

import os
import sys


HERE = os.path.dirname(os.path.abspath(__file__))
AUTOMATA = os.path.dirname(HERE)
sys.path.insert(0, AUTOMATA)

import closedform as cf  # noqa: E402
import leangen  # noqa: E402
from freemodel import catalog, normalise, size  # noqa: E402
from laws import parse_eq  # noqa: E402


def J(left, right):
    return ("J", left, right)


def g(index):
    return ("g", index)


def a1(term):
    return term[1] if term[0] == "J" else term


def a2(term):
    return term[2] if term[0] == "J" else term


def tg(term):
    return 2 if term[0] == "J" else 1


namespace = {}
with open(os.path.join(HERE, "_x38316_rules_cand6.py"), encoding="utf-8") as handle:
    exec(handle.read(), namespace)
rules = namespace["rules"]
tags = [rule[2] for rule in rules]
expected_tags = [
    "V0-W1-q0",
    "V0-W1-q1",
    "V0-W2",
    "V0-W3-q1",
    "V1-s-W1q0",
]
assert tags == expected_tags, (tags, expected_tags)

original = normalise(parse_eq(catalog()[38316]))
law = ("x", leangen.dual_pat(original[1]))
C = cf.Closed(law, rules)

# The complete P1--op blocks are identical, so this exact cand6 execution
# refutes both staged row candidates rather than only one RHS wrapper.
def operation_block(filename):
    with open(os.path.join(HERE, filename), encoding="utf-8") as handle:
        source = handle.read()
    return source[source.index("def P1") : source.index("theorem rhs")]


assert operation_block("v38316.lean") == operation_block("v38316b.lean")

G = g(0)
U = J(G, J(J(G, J(G, G)), G))
z = U
y = g(1)
x = J(J(J(U, J(G, G)), U), G)

a = C.op(z, x)
b = C.op(y, a)
c = C.op(b, y)
d = C.op(x, c)
top = C.op(y, d)
pairs = [(z, x), (y, a), (b, y), (x, c), (y, d)]
values = [a, b, c, d, top]


def firing_index(u, v):
    for index, (conditions, result, _tag) in enumerate(C.rules):
        if C.check(conditions, u, v) and C.ev(result, u, v) is not None:
            return index
    return -1


pattern = [firing_index(u, v) for u, v in pairs]
free = [value == J(u, v) for value, (u, v) in zip(values, pairs)]
adig_left = tg(a2(x)) == 2 and a2(a2(x)) == z
adig_right = a2(x) == a1(z)

assert [size(x), size(y), size(z)] == [25, 1, 9]
assert pattern == [4, -1, -1, -1, -1]
assert [size(value) for value in values] == [23, 25, 27, 53, 55]
assert a == a1(x)
assert free == [False, True, True, True, True]
assert not adig_left and adig_right
assert top != x

print("rules:", tags)
print("sizes x,y,z:", [size(x), size(y), size(z)])
for name, index, value, is_free in zip("abcdt", pattern, values, free):
    tag = tags[index] if index >= 0 else "free"
    print(f"{name}: {tag}, size {size(value)}, free={is_free}")
print("Adig-left:", adig_left)
print("Adig-right:", adig_right)
print("top == x:", top == x)
print("COUNTEREXAMPLE CONFIRMED for v38316.lean and v38316b.lean")
