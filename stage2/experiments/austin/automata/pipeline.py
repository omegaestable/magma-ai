"""pipeline.py <batch.jsonl> <outdir>: for every model in the batch, render one certificate per
research row sharing that hypothesis, judge them all with the real judge, and append to the ledger.

Certificates go to <outdir>/<row id>.lean ; judge results to <outdir>/judged.jsonl ;
ledger (one line per row, latest status) to <outdir>/ledger.jsonl.
"""
import json, sys, os, subprocess, time, re
sys.path.insert(0, os.path.dirname(__file__))
from laws import load_rows, parse_eq, ROOT, load_catalog, dual_id
from symb import Model
from render2 import render
from synth import minimize, dual_model, verify_traced


def to_tuple(x):
    if isinstance(x, list):
        return tuple(to_tuple(a) for a in x)
    return x


def best_order(m, law):
    """minimise under both evaluation orders; return (model, leaves) with the fewer leaves."""
    best = None
    for rev, vf in ((False, False), (True, True), (False, True), (True, False)):
        mm = Model(m.tags, list(m.rules), m.default)
        mm.rev = rev
        mm.vfirst = vf
        f, n = verify_traced(mm, law, max_fail=1, deadline=time.monotonic() + 60)
        if f:
            continue
        mm2, n2 = minimize(mm, law, deadline=time.monotonic() + 120)
        if n2 is None:
            mm2, n2 = mm, n
        if best is None or n2 < best[1]:
            best = (mm2, n2)
    return best if best else (m, None)


def load_models(path):
    models = {}
    for line in open(path, encoding='utf-8'):
        r = json.loads(line)
        if r.get('status') != 'model' or r.get('random_bad', 1) != 0:
            continue
        rules = [to_tuple(x) for x in r['rules']]
        m = Model(r['tags'], rules)
        law = parse_eq(r['eq1'])
        m, n = best_order(m, law)
        print('model', r['eq1_id'], 'leaves', n, 'rules', len(m.rules), 'rev', m.rev, flush=True)
        models[int(r['eq1_id'])] = (m, r)
    # duals
    cat = load_catalog()
    hyps = {int(row['eq1_id']): row['equation1'] for row in load_rows()}
    for eid in list(models):
        if eid not in hyps:
            continue
        d = dual_id(hyps[eid], cat)
        if d in hyps and d not in models:
            dm = dual_model(models[eid][0])
            law = parse_eq(hyps[d])
            f, n = verify_traced(dm, law, max_fail=1)
            if f:
                print('dual', d, 'of', eid, 'FAILS verification', flush=True)
                continue
            dm, n2 = best_order(dm, law)
            print('dual model', d, 'of', eid, 'leaves', n2, 'rules', len(dm.rules), 'rev', dm.rev, flush=True)
            models[d] = (dm, {'eq1_id': d, 'eq1': hyps[d], 'dual_of': eid})
    return models


def main():
    batch, outdir = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    os.makedirs(outdir, exist_ok=True)
    only = set(sys.argv[3:])
    rows = load_rows()
    models = load_models(batch)
    ledger_path = os.path.join(outdir, 'ledger.jsonl')
    done = {}
    if os.path.exists(ledger_path):
        for line in open(ledger_path, encoding='utf-8'):
            r = json.loads(line)
            done[r['id']] = r
    todo = []
    for row in rows:
        eid = int(row['eq1_id'])
        if eid not in models:
            continue
        if only and row['id'] not in only and str(eid) not in only:
            continue
        if done.get(row['id'], {}).get('judge_status') == 'accepted':
            continue
        m, info = models[eid]
        law = parse_eq(row['equation1'])
        goal = parse_eq(row['equation2'])
        try:
            text, em = render(m, law, goal)
        except Exception as e:
            print(row['id'], 'RENDER ERROR', e, flush=True)
            continue
        nbytes = len(text.encode('utf-8'))
        path = os.path.join(outdir, row['id'] + '.lean')
        open(path, 'w', encoding='utf-8').write(text)
        print(row['id'], eid, row['eq2_id'], 'leaves', em.nleaves, 'bytes', nbytes, flush=True)
        if nbytes > 19500:
            print('  TOO LARGE, skipping judge', flush=True)
            continue
        todo.append({'id': row['id'], 'equation1': row['equation1'].replace('*', '◇'),
                     'equation2': row['equation2'].replace('*', '◇'), 'eq1_id': row['eq1_id'],
                     'eq2_id': row['eq2_id'], 'verdict': 'false', 'code': text})
    if not todo:
        print('nothing to judge')
        return
    inp = os.path.join(outdir, '_in.jsonl')
    out = os.path.join(outdir, '_out.jsonl')
    with open(inp, 'w', encoding='utf-8') as f:
        for t in todo:
            f.write(json.dumps(t, ensure_ascii=False) + '\n')
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    t0 = time.time()
    p = subprocess.run([ROOT + '/.venv/Scripts/python.exe', ROOT + '/stage2/experiments/judge_cert_text.py', '--in', inp, '--out', out],
                       capture_output=True, text=True, env=env, cwd=ROOT, encoding='utf-8', errors='replace')
    print(p.stdout[-2000:])
    if not os.path.exists(out):
        print('judge produced no output:', p.stderr[-2000:])
        return
    with open(os.path.join(outdir, 'judged.jsonl'), 'a', encoding='utf-8') as jf, open(ledger_path, 'a', encoding='utf-8') as lf:
        for line in open(out, encoding='utf-8'):
            r = json.loads(line)
            jf.write(line)
            msg = r.get('judge_message', '')
            errs = [l for l in msg.splitlines() if 'error' in l]
            rec = {'id': r['id'], 'eq1_id': r['eq1_id'], 'eq2_id': r['eq2_id'], 'judge_status': r.get('judge_status'),
                   'judge_seconds': r.get('judge_seconds'), 'code_bytes': r.get('code_bytes'), 'errors': errs[:5], 'when': time.strftime('%Y-%m-%d %H:%M')}
            lf.write(json.dumps(rec) + '\n')
            print(r['id'], r.get('judge_status'), r.get('judge_seconds'), r.get('code_bytes'), errs[:2], flush=True)


if __name__ == '__main__':
    main()
