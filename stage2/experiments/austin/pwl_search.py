"""Piecewise-linear ordered magmas over Z as infinite countermodels.

op(x, y) = if COND(x, y) then a1*x + b1*y + c1 else a2*x + b2*y + c2

COND ranges over a fixed list of omega-friendly predicates (order, sign,
equality, parity). eq1 is checked on a window W^k (early exit), eq2 must fail
at some window point. Everything found is omega-provable in Lean (linear
arithmetic with if/mod-by-literal), i.e. the `hard2_0027` certificate shape.

usage: python pwl_search.py rows.jsonl [window] [out.json]
"""
from __future__ import annotations
import json, sys, itertools, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from austin_z3 import parse, variables  # noqa: E402

CONDS = {
    'x<y': lambda x, y: x < y,
    'x<=y': lambda x, y: x <= y,
    'x=y': lambda x, y: x == y,
    'x<0': lambda x, y: x < 0,
    'y<0': lambda x, y: y < 0,
    'x=0': lambda x, y: x == 0,
    'y=0': lambda x, y: y == 0,
    'x%2=0': lambda x, y: x % 2 == 0,
    'y%2=0': lambda x, y: y % 2 == 0,
    'x%2=y%2': lambda x, y: x % 2 == y % 2,
    'x%3=0': lambda x, y: x % 3 == 0,
    'y%3=0': lambda x, y: y % 3 == 0,
    'x<y+1': lambda x, y: x < y + 1,
    'x+y<0': lambda x, y: x + y < 0,
    'x+y=0': lambda x, y: x + y == 0,
    'x%3=y%3': lambda x, y: x % 3 == y % 3,
}
COEF = (-1, 0, 1, 2)
CONST = (-2, -1, 0, 1, 2)
LINS = [(a, b, c) for a in COEF for b in COEF for c in CONST]


def compile_eq(text):
    l, r = parse(text)
    vs = variables(l, variables(r, []))
    names = {v: f'v{i}' for i, v in enumerate(vs)}
    def render(t):
        if t[0] == 'v':
            return names[t[1]]
        return f'op({render(t[1])}, {render(t[2])})'
    src = f"lambda op, {', '.join(names.values())}: {render(l)} == {render(r)}"
    return eval(src), len(vs)


def search_one(args):
    row_id, eq1_text, eq2_texts, window = args
    check1, k1 = compile_eq(eq1_text)
    checks2 = [(t, *compile_eq(t)) for t in eq2_texts]
    W = range(-window, window + 1)
    pts1 = list(itertools.product(W, repeat=k1))
    # order points so that cheap contradictions come first: small values first
    pts1.sort(key=lambda p: sum(abs(v) for v in p))
    found = []
    t0 = time.time()
    for cname, cond in CONDS.items():
        for (a1, b1, c1) in LINS:
            for (a2, b2, c2) in LINS:
                if (a1, b1, c1) == (a2, b2, c2):
                    continue
                def op(x, y, _c=cond, _a1=a1, _b1=b1, _c1=c1, _a2=a2, _b2=b2, _c2=c2):
                    return _a1 * x + _b1 * y + _c1 if _c(x, y) else _a2 * x + _b2 * y + _c2
                ok = True
                for p in pts1:
                    if not check1(op, *p):
                        ok = False
                        break
                if not ok:
                    continue
                # eq1 holds on the window: which eq2s fail?
                refuted = []
                for (t2, check2, k2) in checks2:
                    for p in itertools.product(W, repeat=k2):
                        if not check2(op, *p):
                            refuted.append((t2, p))
                            break
                found.append({'cond': cname, 'then': (a1, b1, c1), 'else': (a2, b2, c2),
                              'refutes': refuted})
                if len(found) >= 40:
                    return row_id, found, round(time.time() - t0, 1)
    # also the unconditional linear forms
    for (a1, b1, c1) in LINS:
        def op(x, y, _a1=a1, _b1=b1, _c1=c1):
            return _a1 * x + _b1 * y + _c1
        if all(check1(op, *p) for p in pts1):
            refuted = []
            for (t2, check2, k2) in checks2:
                for p in itertools.product(W, repeat=k2):
                    if not check2(op, *p):
                        refuted.append((t2, p)); break
            found.append({'cond': None, 'then': (a1, b1, c1), 'else': None, 'refutes': refuted})
    return row_id, found, round(time.time() - t0, 1)


def main():
    rows = [json.loads(l) for l in open(sys.argv[1], encoding='utf-8') if l.strip()]
    window = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    out = sys.argv[3] if len(sys.argv) > 3 else None
    # group by eq1
    groups = {}
    for r in rows:
        groups.setdefault(r['equation1'], {'ids': [], 'eq2': []})
        groups[r['equation1']]['ids'].append(r['id'])
        if r['equation2'] not in groups[r['equation1']]['eq2']:
            groups[r['equation1']]['eq2'].append(r['equation2'])
    jobs = [(g['ids'][0], e1, g['eq2'], window) for e1, g in groups.items()]
    results = []
    with ProcessPoolExecutor(14) as ex:
        for row_id, found, secs in ex.map(search_one, jobs):
            models = [f for f in found if f['refutes']]
            print(f"{row_id}: eq1-models {len(found)}, refuting some eq2: {len(models)}  ({secs}s)", flush=True)
            for f in models[:3]:
                print('    ', f, flush=True)
            results.append({'id': row_id, 'found': found})
    if out:
        json.dump(results, open(out, 'w'), indent=1)


if __name__ == '__main__':
    main()
