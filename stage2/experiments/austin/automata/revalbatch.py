"""revalbatch.py <out.jsonl> <secs> <workers> <eq1,eq2,...> [extra revalidate.py args]

Run revalidate.py over several laws in parallel (subprocess per law, hard timeout); results are written as
they complete (not in submission order), with the full stdout kept in <out>.log.
"""
import sys, os, json, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laws import ROOT
PY = ROOT + '/.venv/Scripts/python.exe'; HERE = os.path.dirname(os.path.abspath(__file__))

def one(eq, secs, extra):
    t0 = time.time()
    try:
        p = subprocess.run([PY, os.path.join(HERE, 'revalidate.py'), str(eq)] + extra, capture_output=True, text=True,
                           timeout=secs, env=dict(os.environ, PYTHONIOENCODING='utf-8'), encoding='utf-8', errors='replace')
        lines = [l for l in p.stdout.splitlines() if l.startswith('{')]
        rep = json.loads(lines[-1]) if lines else dict(eq=eq, error=(p.stderr[-800:] or 'no output'))
        rep['secs'] = round(time.time() - t0, 1); rep['log'] = p.stdout[-6000:] + p.stderr[-2000:]
        return rep
    except subprocess.TimeoutExpired:
        return dict(eq=eq, error='timeout', secs=round(time.time() - t0, 1))

if __name__ == '__main__':
    out = sys.argv[1]; secs = float(sys.argv[2]); workers = int(sys.argv[3])
    eqs = [int(e) for e in sys.argv[4].split(',')]
    extra = sys.argv[5:]
    with ThreadPoolExecutor(workers) as ex, open(out, 'w', encoding='utf-8') as f, open(out + '.log', 'w', encoding='utf-8') as g:
        futs = {ex.submit(one, e, secs, extra): e for e in eqs}
        for fu in as_completed(futs):
            r = fu.result()
            g.write('===== %s\n%s\n' % (r.get('eq'), r.pop('log', ''))); g.flush()
            f.write(json.dumps(r) + '\n'); f.flush()
            print(r.get('eq'), r.get('status'), 'rules', r.get('nrules_full'), '->', r.get('nrules'), 'full', r.get('full_noexist'), r.get('full_exist', ''), 'secs', r.get('secs'), r.get('error', '')[:100], flush=True)
