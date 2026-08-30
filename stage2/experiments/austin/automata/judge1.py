"""judge1.py <lean file> <row id or eq1_id:eq2_id> [--true]  : judge one certificate text against the real judge."""
import json, sys, subprocess, os, time
sys.path.insert(0, os.path.dirname(__file__))
from laws import load_rows, ROOT
import jlock

lean = open(sys.argv[1], encoding='utf-8').read()
key = sys.argv[2]
verdict = 'true' if '--true' in sys.argv else 'false'
rows = load_rows()
row = None
for r in rows:
    if r['id'] == key or r['id'].endswith(key) or f"{r['eq1_id']}:{r['eq2_id']}" == key:
        row = r
        break
if row is None:
    a, b = key.split(':')
    row = {'id': f'custom_{a}_{b}', 'eq1_id': int(a), 'eq2_id': int(b)}
    cat = {}
    for i, line in enumerate(open(ROOT + '/vendor/stage2-official/examples/problems/eq_size5.txt', encoding='utf-8'), 1):
        cat[i] = line.strip()
    row['equation1'] = cat[int(a)]
    row['equation2'] = cat[int(b)]
here = os.path.dirname(os.path.abspath(sys.argv[1]))
inp = os.path.join(here, '_judge_in_%d.jsonl' % os.getpid())
out = os.path.join(here, '_judge_out_%d.jsonl' % os.getpid())
with open(inp, 'w', encoding='utf-8') as f:
    f.write(json.dumps({'id': row['id'], 'equation1': row['equation1'].replace('*', '◇'), 'equation2': row['equation2'].replace('*', '◇'),
                        'eq1_id': row['eq1_id'], 'eq2_id': row['eq2_id'], 'verdict': verdict, 'code': lean}, ensure_ascii=False) + '\n')
t0 = time.time()
env = jlock.judge_env()
with jlock.Slot():
    p = subprocess.run([ROOT + '/.venv/Scripts/python.exe', ROOT + '/stage2/experiments/judge_cert_text.py', '--in', inp, '--out', out],
                       capture_output=True, text=True, env=env, cwd=ROOT, encoding='utf-8', errors='replace')
print(p.stdout[-3000:], p.stderr[-3000:])
rows_out = [json.loads(l) for l in open(out, encoding='utf-8')]
for f in (inp, out):
    try: os.remove(f)
    except OSError: pass
for r in rows_out:
    print('STATUS:', r.get('status') or r.get('judge_status'), 'in', round(time.time() - t0, 1), 's')
    err = r.get('error') or r.get('detail') or r.get('judge_error') or ''
    print(str(err)[:6000])
    for k in r:
        if k not in ('code', 'equation1', 'equation2'):
            print(' ', k, '=', str(r[k])[:1500])
