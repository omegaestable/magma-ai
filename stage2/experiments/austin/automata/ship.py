"""ship.py: turn judge-accepted research certificates into (a) fixture lines for
stage2/fixtures/judge_verified_certs.jsonl and (b) DISTILLED_CERTS entries (Python source)
keyed by the solver's own canonical_eq_text.  Writes ship_fixture.jsonl and ship_certs.py
next to the certs directory; nothing in the repo is modified.
"""
import json, sys, os, importlib.util, time
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
from laws import load_rows, ROOT

spec = importlib.util.spec_from_file_location('solver_mod', ROOT + '/stage2/solver/solver.py')
solver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(solver)

certdir = os.path.join(here, '..', 'certs')
rows = {r['id']: r for r in load_rows()}
latest = {}
for line in open(os.path.join(certdir, 'ledger.jsonl'), encoding='utf-8'):
    r = json.loads(line)
    if r['judge_status'] == 'accepted':
        latest[r['id']] = r
fixture_lines = []
entries = []
seen_keys = set()
for rid, rec in sorted(latest.items()):
    row = rows[rid]
    code = open(os.path.join(certdir, rid + '.lean'), encoding='utf-8').read()
    name = f"aus_e{row['eq1_id']}_e{row['eq2_id']}"
    route = f"false:distilled:{name}"
    fixture_lines.append({'id': rid, 'route': route, 'verdict': 'false', 'cert_shape': 'false_infinite_automaton',
                          'code': code, 'judge_status': 'accepted', 'judge_seconds': rec['judge_seconds'],
                          'verified_on': rec['when'][:10], 'equation1': row['equation1'].replace('*', '◇'),
                          'equation2': row['equation2'].replace('*', '◇'), 'eq1_id': row['eq1_id'], 'eq2_id': row['eq2_id']})
    e1 = solver.parse_equation(row['equation1'].replace('*', '◇'))
    e2 = solver.parse_equation(row['equation2'].replace('*', '◇'))
    key = (solver.canonical_eq_text(e1), solver.canonical_eq_text(e2))
    assert key not in seen_keys, key
    seen_keys.add(key)
    entries.append((key, name, code))
with open(os.path.join(certdir, 'ship_fixture.jsonl'), 'w', encoding='utf-8') as f:
    for fl in fixture_lines:
        f.write(json.dumps(fl, ensure_ascii=False) + '\n')
with open(os.path.join(certdir, 'ship_certs.py'), 'w', encoding='utf-8') as f:
    for (k1, k2), name, code in entries:
        f.write(f'    ({k1!r}, {k2!r}): ("false", {name!r}, {code!r}),\n')
total = sum(len(c.encode()) for _, _, c in entries)
print(f'{len(entries)} entries, {total} bytes of Lean; fixture lines {len(fixture_lines)}')
