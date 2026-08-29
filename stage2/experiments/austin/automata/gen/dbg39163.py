import sys
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata')
sys.argv = ['x', 'r5', '5', '0']
exec(open('C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata\\gen\\coin39163.py', encoding='utf-8').read().split('# --- targeted coincidence search ---')[0])
C = cf.Closed(law, rules)
w = g(0); t = g(1)
y = J(w, w)
z = J(w, J(J(t, w), J(w, w)))
x = J(z, y)
D = J(y, z)
print("msr(z, x) =", cf.msr(z, x), " msr(y, D) =", cf.msr(y, D))
print("op z x =", show(C.op(z, x)))
conds, res, tag = R5
for c in conds:
    if c[0] == 'TG':
        tv = C.ev(c[1], y, D); print('TG', cf.show_expr(c[1]), '->', show(tv) if tv else None)
    else:
        a = C.ev(c[1], y, D); b = C.ev(c[2], y, D)
        print(c[0], cf.show_expr(c[1]), show(a) if a else None, '|', cf.show_expr(c[2]), show(b) if b else None, '| eq', a == b)
print("check:", C.check(conds, y, D))
print("op y D =", show(C.op(y, D)), " fired:", C.fired)
