"""Row-id diff of an audit against the 2026-08-27 official baseline."""
import json
import sys
base = json.load(open(sys.argv[1], encoding='utf-8'))['sets']
new = json.load(open(sys.argv[2], encoding='utf-8'))['sets']
for name in sorted(new):
    if name not in base:
        print(f'{name}: no baseline')
        continue
    b = {r['id']: r for r in base[name]['rows']}
    n = {r['id']: r for r in new[name]['rows']}
    common = sorted(set(b) & set(n))
    lost = [i for i in common if b[i]['status'] == 'solved' and n[i]['status'] != 'solved']
    gained = [i for i in common if b[i]['status'] != 'solved' and n[i]['status'] == 'solved']
    flips = [i for i in common if b[i].get('verdict') and n[i].get('verdict')
             and b[i]['verdict'] != n[i]['verdict']]
    routes = [(i, b[i].get('route'), n[i].get('route')) for i in common
              if b[i].get('route') and n[i].get('route') and b[i]['route'] != n[i]['route']]
    bytes_ch = [(i, b[i].get('code_bytes'), n[i].get('code_bytes')) for i in common
                if b[i].get('code_bytes') and n[i].get('code_bytes')
                and b[i]['code_bytes'] != n[i]['code_bytes']]
    crash = [i for i in n if n[i]['status'] == 'crash']
    oracle = [i for i in n if n[i].get('oracle') not in (None, 'ok')]
    print(f'{name}: common {len(common)} | lost {len(lost)} | gained {len(gained)} | '
          f'verdict flips {len(flips)} | route changes {len(routes)} | '
          f'byte changes {len(bytes_ch)} | crashes {len(crash)} | oracle!=ok {len(oracle)}')
    for tag, xs in (('LOST', lost), ('GAINED', gained), ('FLIP', flips),
                    ('CRASH', crash), ('ORACLE', oracle)):
        for i in xs[:20]:
            print(f'  {tag} {i} {b.get(i,{}).get("route")} -> {n[i].get("route")} {n[i].get("error","")}')
    for i, o, w in routes[:25]:
        print(f'  ROUTE {i}: {o} -> {w}')
    if len(routes) > 25:
        print(f'  ... {len(routes)-25} more route changes')
    print(f'  bytes changed on {len(bytes_ch)} rows; sample {bytes_ch[:5]}')
