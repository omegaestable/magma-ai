"""Run freemodel.py over every hypothesis of the research set in parallel (subprocess per law, hard timeout)."""
import sys, os, json, subprocess, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laws import load_rows, ROOT
PY = ROOT + '/.venv/Scripts/python.exe'
HERE = os.path.dirname(os.path.abspath(__file__))
def one(eq, N, secs):
    t0 = time.time()
    try:
        p = subprocess.run([PY, os.path.join(HERE, 'freetest2.py'), str(eq), str(N), str(secs)], capture_output=True, text=True,
                           timeout=secs + 120, env=dict(os.environ, PYTHONIOENCODING='utf-8'), encoding='utf-8', errors='replace')
        line = [l for l in p.stdout.splitlines() if l.startswith('{')]
        if line: return json.loads(line[-1])
        return dict(eq=eq, error=(p.stderr[-800:] or 'no output'), secs=round(time.time() - t0, 1))
    except subprocess.TimeoutExpired:
        return dict(eq=eq, error='timeout', secs=round(time.time() - t0, 1))
if __name__ == '__main__':
    out = sys.argv[1]; N = int(sys.argv[2]); secs = float(sys.argv[3]); workers = int(sys.argv[4]) if len(sys.argv) > 4 else 14
    eqs = sorted({int(r['eq1_id']) for r in load_rows()})
    if len(sys.argv) > 5: eqs = [int(e) for e in sys.argv[5].split(',')]
    with ThreadPoolExecutor(workers) as ex, open(out, 'w', encoding='utf-8') as f:
        for res in ex.map(lambda e: one(e, N, secs), eqs):
            f.write(json.dumps(res) + '\n'); f.flush()
            print(res.get('eq'), 'fails', res.get('fails'), 'conf', res.get('conflicts'), 'cuts', res.get('cuts'), 'rbail', res.get('rbail'), 'tested', res.get('tested'), 'secs', res.get('secs'), res.get('error', '')[:100], flush=True)
