import json, sys, os, collections
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
from laws import load_rows
rows = load_rows()
latest = {}
for line in open(os.path.join(here, 'certs', 'ledger.jsonl'), encoding='utf-8'):
    r = json.loads(line)
    if r['judge_status'] == 'accepted' or r['id'] not in latest:
        latest[r['id']] = r
acc = [r for r in latest.values() if r['judge_status'] == 'accepted']
print(f'accepted rows: {len(acc)} / 100 ; judged rows: {len(latest)}')
byh = collections.Counter(r['eq1_id'] for r in acc)
print('accepted per hypothesis:', dict(byh))
tot = sum(r['code_bytes'] for r in acc); print('max bytes', max((r['code_bytes'] for r in acc), default=0), 'max secs', max((r['judge_seconds'] for r in acc), default=0))
missing = collections.Counter(int(r['eq1_id']) for r in rows if r['id'] not in {a['id'] for a in acc})
print('hypotheses still open:', len(missing))
