"""transplant.py <accepted_L.lean> <dual_skeleton.lean> <out.lean>

The dualised skeleton of an R-form law has the SAME `op` (rules of the dual L-form law) as the L-form law's
skeleton; only `inst` (flipped), `rhs` and the doc-comment differ.  So an accepted L-form certificate proves the
dual row too: take the accepted file, and replace its `def inst` line and its `theorem rhs … ` block by the
dual skeleton's.  Refuses if the two `op` definitions differ textually.
"""
import sys, re

def block(txt, start_pat, end_pat):
    i = txt.index(start_pat)
    j = txt.index(end_pat, i)
    return i, j

def op_def(txt):
    i = txt.index('def op (u v : M) : M :=')
    j = txt.index('\ndef inst', i)
    return txt[i:j]

def main():
    acc, dual, out = sys.argv[1:4]
    A = open(acc, encoding='utf-8').read()
    Dl = open(dual, encoding='utf-8').read()
    if op_def(A).strip() != op_def(Dl).strip():
        print('op definitions differ; cannot transplant'); sys.exit(1)
    # inst line
    A = re.sub(r'def inst : Magma M := \{ op := [^\n]*\}', re.search(r'def inst : Magma M := \{ op := [^\n]*\}', Dl).group(0), A, count=1)
    # rhs block: from 'theorem rhs' to the line before the next top-level 'theorem' / '/--'
    def rhs_block(t):
        i = t.index('theorem rhs')
        m = re.search(r'\n(?=(theorem |/--|def |abbrev ))', t[i + 1:])
        j = i + 1 + m.start()
        return i, j
    ai, aj = rhs_block(A); di, dj = rhs_block(Dl)
    A = A[:ai] + Dl[di:dj] + A[aj:]
    open(out, 'w', encoding='utf-8', newline='\n').write(A)
    print('written', out, len(A.encode()), 'bytes')

if __name__ == '__main__':
    main()
