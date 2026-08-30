import io, os
D = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
p = os.path.join(D, 'gen', '_w3_12087_lab.py')
t = io.open(p, encoding='utf-8').read()
a = t.index('def op(u, v, depth=0):')
b = t.index('def chain(')
new = '''def B0(u, v, depth=0):
    """the free model's B0l, transplanted: V untagged (N2 decoded).  Reads the payload out of N3 and
       certifies u by recomputation.  At the root the guard is op (op y x) z = N2 -- rfl."""
    if tg(v) != 2 or tg(a2(v)) == 1: return None
    x = a1(a2(v)); z = a2(a2(v))
    if op(op(u, x, depth + 1), z, depth + 1) == a1(v): return x
    return None

def op(u, v, depth=0):
    if depth > 60: return ('J', u, v)
    X = Dec(u, v, depth)
    if X is not None:
        PROF[(u, v)] = 'D'; return X
    if P(u, v, depth):
        PROF[(u, v)] = 'T'; return ('E', u, v)
    X = B0(u, v, depth)
    if X is not None:
        PROF[(u, v)] = 'B'; return X
    PROF[(u, v)] = None
    return ('J', u, v)

'''
t = t[:a] + new + t[b:]
io.open(p, 'w', encoding='utf-8', newline='\n').write(t)
print('v9 written (B0 added, order Dec / P / B0)')
