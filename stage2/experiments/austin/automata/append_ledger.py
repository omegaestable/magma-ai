"""append_ledger.py [verify_certs.json]  : append newly ACCEPTED rows to certs/ledger.jsonl.

`verify_certs.py` judges and writes `verify_certs.json`; it does NOT touch the ledger (its docstring
used to claim it did). This is the append step, deliberately separate and deliberately append-only:
`judge_rows.py --write-fixture` REPLACING the fixture cost 102 pins once (CLAUDE.md rail 16), and the
ledger is the same shape of file. Rows already accepted in the ledger are skipped, so re-running is safe.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, 'certs', 'ledger.jsonl')
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'verify_certs.json')

have = set()
for line in open(LEDGER, encoding='utf-8'):
    line = line.strip()
    if line and json.loads(line).get('judge_status') == 'accepted':
        have.add(json.loads(line)['id'])

new = [r for r in json.load(open(src, encoding='utf-8'))
       if r.get('judge_status') == 'accepted' and r['id'] not in have]
with open(LEDGER, 'a', encoding='utf-8') as f:
    for r in sorted(new, key=lambda r: r['id']):
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(f'appended {len(new)} accepted rows; ledger now has {len(have | {r["id"] for r in new})} accepted')
