"""verify_certs.py [--only <row,row,...>] [--workers N]

Re-judge every certs/<row>.lean against the REAL judge and write the verdicts to verify_certs.json.
It does NOT touch certs/ledger.jsonl -- run `append_ledger.py` for that, which appends and never
replaces (rail 16: a tool that REPLACES a pin file costs the pins it does not know about).
This is the orchestrator's gate: an agent's claim of acceptance is not evidence, the judge is.
Runs `workers` judge processes at a time (each takes a jlock slot; keep workers <= JUDGE_SLOTS).
"""
import sys, os, json, glob, subprocess, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from laws import load_rows, ROOT
import jlock

def judge_one(rid, path, rows):
    row = rows[rid]
    inp = os.path.join(HERE, '_vc_in_%s.jsonl' % rid[-4:])
    out = os.path.join(HERE, '_vc_out_%s.jsonl' % rid[-4:])
    code = open(path, encoding='utf-8').read()
    with open(inp, 'w', encoding='utf-8') as f:
        f.write(json.dumps({'id': rid, 'equation1': row['equation1'].replace('*', '◇'),
                            'equation2': row['equation2'].replace('*', '◇'), 'eq1_id': row['eq1_id'],
                            'eq2_id': row['eq2_id'], 'verdict': 'false', 'code': code}, ensure_ascii=False) + '\n')
    env = jlock.judge_env()
    t0 = time.time()
    with jlock.Slot():
        subprocess.run([ROOT + '/.venv/Scripts/python.exe', ROOT + '/stage2/experiments/judge_cert_text.py',
                        '--in', inp, '--out', out], capture_output=True, text=True, env=env, cwd=ROOT,
                       encoding='utf-8', errors='replace')
    rec = None
    try:
        for l in open(out, encoding='utf-8'):
            rec = json.loads(l)
    except OSError:
        pass
    for f in (inp, out):
        try: os.remove(f)
        except OSError: pass
    st = (rec or {}).get('judge_status', 'NO_OUTPUT')
    return dict(id=rid, eq1_id=row['eq1_id'], eq2_id=row['eq2_id'], judge_status=st,
                judge_seconds=(rec or {}).get('judge_seconds', round(time.time() - t0, 1)),
                code_bytes=len(code.encode()), errors=[], when=time.strftime('%Y-%m-%d %H:%M'))

def main():
    rows = {r['id']: r for r in load_rows()}
    only = None
    if '--only' in sys.argv:
        only = set(sys.argv[sys.argv.index('--only') + 1].split(','))
    workers = int(sys.argv[sys.argv.index('--workers') + 1]) if '--workers' in sys.argv else 3
    files = sorted(glob.glob(os.path.join(HERE, 'certs', '*.lean')))
    tasks = [(os.path.basename(p)[:-5], p) for p in files]
    if only:
        tasks = [t for t in tasks if t[0] in only or t[0][-4:] in only]
    print('judging', len(tasks), 'certificates with', workers, 'workers', flush=True)
    from concurrent.futures import ThreadPoolExecutor, as_completed
    res = []
    with ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(judge_one, rid, p, rows): rid for rid, p in tasks}
        for f in as_completed(futs):
            r = f.result(); res.append(r)
            print(('  OK ' if r['judge_status'] == 'accepted' else '  ** '), r['id'], r['judge_status'],
                  r['code_bytes'], 'B', r['judge_seconds'], 's', flush=True)
    bad = [r for r in res if r['judge_status'] != 'accepted']
    print('accepted %d / %d' % (len(res) - len(bad), len(res)))
    if bad:
        print('NOT ACCEPTED:', [(r['id'], r['judge_status']) for r in bad])
    json.dump(res, open(os.path.join(HERE, 'verify_certs.json'), 'w'), indent=1)

if __name__ == '__main__':
    main()
