"""Generate closed-form packages (rules, Lean skeleton, checker) for every hypothesis in parallel."""
import sys, os, json, subprocess, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laws import load_rows, ROOT
PY = ROOT + '/.venv/Scripts/python.exe'; HERE = os.path.dirname(os.path.abspath(__file__))
def one(eq, secs):
    t0 = time.time()
    try:
        p = subprocess.run([PY, os.path.join(HERE, 'leangen.py'), str(eq), os.path.join(HERE, 'gen')], capture_output=True, text=True,
                           timeout=secs, env=dict(os.environ, PYTHONIOENCODING='utf-8'), encoding='utf-8', errors='replace')
        line = [l for l in p.stdout.splitlines() if l.startswith('{')]
        if line: r = json.loads(line[-1]); r['secs'] = round(time.time() - t0, 1); return r
        return dict(eq=eq, error=(p.stderr[-600:] or 'no output'), secs=round(time.time() - t0, 1))
    except subprocess.TimeoutExpired:
        return dict(eq=eq, error='timeout', secs=round(time.time() - t0, 1))
if __name__ == '__main__':
    out = sys.argv[1]; secs = float(sys.argv[2]); workers = int(sys.argv[3])
    eqs = sorted({int(r['eq1_id']) for r in load_rows()})
    if len(sys.argv) > 4: eqs = [int(e) for e in sys.argv[4].split(',')]
    with ThreadPoolExecutor(workers) as ex, open(out, 'w', encoding='utf-8') as f:
        for res in ex.map(lambda e: one(e, secs), eqs):
            f.write(json.dumps(res) + '\n'); f.flush()
            print(res.get('eq'), 'rules', res.get('nrules'), 'fails', res.get('fails_all'), 'refuted', res.get('refuted'), 'secs', res.get('secs'), res.get('error', '')[:120], flush=True)
