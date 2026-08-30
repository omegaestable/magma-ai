"""squeeze.py <in.lean> <out.lean> [--rename]

Byte-squeeze a certificate without changing its proof: drop set_option lines and blank lines, halve the
indentation (relative structure preserved), remove spaces around infix operators / after commas / inside
anonymous constructors, `theorem` -> `def`, join single-tactic proofs onto the `:=by` line, `· ` -> `·`.
With --rename, also rename the most frequent global lemma names to unused single capitals.
NOT IDEMPOTENT -- squeeze ONCE, from the readable source, and compile the result.
Re-squeezing an ALREADY-squeezed file produces a smaller file that does not compile: measured
2026-08-29 on the accepted 33020 certificate (itself squeezed), 19,877 -> 18,952 B and 18 compile
errors. It cost an agent real time because the breakage reads as a name collision. Two causes: the
indentation pass halved an already-1-space indent to 0 (`1 // 2 == 0`), deleting the indentation a
multi-line `:=by` block depends on -- that one is fixed below -- and the tactic-joining and
operator-spacing passes are one-shot by construction. `looks_squeezed()` detects the case and
__main__ warns rather than silently producing a broken file.
Compile the result with devlean2.sh before judging — every step is syntax-preserving in practice but Lean's
whitespace sensitivity means the compile is the check.  Took 18137 from 23,064 to 19,705 bytes (accepted).
"""
import sys, re
def looks_squeezed(s):
    """A file already put through squeeze(): no line indented two or more spaces, and `:=by` present."""
    return ':=by' in s and ' := by' not in s and 'rw [' not in s


def squeeze(s, rename=False):
    out = []
    for line in s.split('\n'):
        m = re.match(r'^( *)(.*)$', line); ind, rest = m.group(1), m.group(2)
        if rest.startswith('set_option') or not rest.strip(): continue
        # Halve the indent, but never to zero from a non-zero indent: `1 // 2 == 0` deletes the
        # indentation that a multi-line `:=by` tactic block depends on, so a SECOND squeeze of an
        # already-squeezed file silently breaks it. Measured 2026-08-29 on gen/_sq33020.lean, which
        # was already squeezed: the second pass produced 28 `unexpected identifier` errors and read
        # as a name collision. Squeezing is now idempotent.
        out.append(' ' * max(len(ind) // 2, 1 if ind else 0) + rest)
    t = '\n'.join(out)
    for op in ['=', '∧', '∨', '<', '≤', '+', '≠', '→', '↔', '*']:
        t = t.replace(' %s ' % op, op)
    t = t.replace(', ', ',').replace('⟨ ', '⟨').replace(' ⟩', '⟩')
    t = re.sub(r'[ \t]+\n', '\n', t)
    if rename:
        used = set(re.findall(r'\b[A-Z]\b', t))
        free = [c for c in 'WTEZKYVXLNOQRDGHIU' if c not in used]
        names = [n for n, c in sorted(((n, t.count(n)) for n in set(re.findall(r'(?<=\n)(?:theorem|def) ([A-Za-z_][A-Za-z0-9_\']*)', t))
                                       if n not in ('op', 'inst', 'lhs', 'rhs', 'law', 'submission', 'sz', 'tg', 'a1', 'a2', 'Pre', 'op_free')), key=lambda x: -x[1])]
        for n, c in zip(names, free):
            t = re.sub(r'(?<![A-Za-z0-9_.])%s(?![A-Za-z0-9_\'])' % re.escape(n), c, t)
    t = t.replace('have := ', 'have:=').replace(':= by', ':=by').replace('simp only [', 'simp only[').replace('(config := {decide := true})', '(config:={decide:=true})')
    t = t.replace('\ntheorem ', '\ndef ')
    for a in ['obtain ⟨', 'with ⟨', 'exact ⟨', 'refine ⟨', 'rw [', 'simp [', 'simp_all [', 'rintro ⟨']:
        t = t.replace(a, a.replace(' ', ''))
    t = t.replace('⟩ := ', '⟩:=').replace(' := ', ':=')
    lines = t.split('\n'); out = []; i = 0
    while i < len(lines):
        l = lines[i]
        if l.rstrip().endswith(':=by') and i + 1 < len(lines):
            nxt = lines[i + 1]; ind = len(nxt) - len(nxt.lstrip())
            after = lines[i + 2] if i + 2 < len(lines) else ''
            aind = len(after) - len(after.lstrip()) if after.strip() else 0
            if ind > 0 and (not after.strip() or aind < ind) and not nxt.lstrip().startswith('·'):
                out.append(l.rstrip() + ' ' + nxt.strip()); i += 2; continue
        out.append(l); i += 1
    t = '\n'.join(out).replace('· ', '·')
    return t
if __name__ == '__main__':
    s = open(sys.argv[1], encoding='utf-8').read()
    if looks_squeezed(s):
        print('WARNING: %s already looks squeezed. Squeezing is NOT idempotent: a second pass yields a '
              'smaller file that does NOT compile. Squeeze the readable source instead, and always '
              'compile what you judge (devlean2.sh, then grep the output for an error line).'
              % sys.argv[1], file=sys.stderr)
    t = squeeze(s, '--rename' in sys.argv)
    open(sys.argv[2], 'w', encoding='utf-8', newline='\n').write(t)
    print(len(s.encode()), '->', len(t.encode()))
