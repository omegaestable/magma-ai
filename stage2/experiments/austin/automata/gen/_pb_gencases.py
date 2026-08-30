"""_pb_gencases.py <rec<eq>.lean> : emit the `op_cases` packing theorem for a generated skeleton.

Reads the `def op (u v : M) : M := ... termination_by` block, splits it into the `let p_k := <dite>`
prelude and the if-chain body, and prints the ∃-packed restatement of `op.eq_1` whose anonymous-constructor
proof is `⟨_, …, rfl, …, op.eq_1 u v⟩`.  Purely textual: the if-chain is copied verbatim, so the p_k in it
become the ∃-bound variables.
"""
import re
import sys


def gen(path: str) -> str:
    src = open(path, encoding='utf-8').read()
    i = src.index('def op (u v : M) : M :=')
    j = src.index('termination_by', i)
    block = src[i:j].split('\n')[1:]          # drop the `def op …` header line
    lets, body = [], []
    for line in block:
        m = re.match(r'\s*let (p\d+) := (.*)$', line)
        if m and not body:
            lets.append((m.group(1), m.group(2)))
        elif line.strip():
            body.append(line.rstrip())
    names = [n for n, _ in lets]
    out = ['theorem op_cases (u v : M) : ∃ ' + ' '.join(names) + ' : M,']
    for n, rhs in lets:
        out.append('    %s = (%s) ∧' % (n, rhs))
    out.append('    op u v = (')
    out.extend(body)
    out.append('    ) :=')
    out.append('  ⟨' + ', '.join(['_'] * len(names) + ['rfl'] * len(names)) + ', op.eq_1 u v⟩')
    return '\n'.join(out)


if __name__ == '__main__':
    print(gen(sys.argv[1]))
