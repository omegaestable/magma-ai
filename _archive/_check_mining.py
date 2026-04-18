import json
d = json.load(open('results/v26c_magma_mining.json', encoding='utf-8'))
sc = d['set_cover']
for i, m in enumerate(sc):
    nc = [x for x in m['caught_ids'] if x.startswith('normal')]
    h3 = [x for x in m['caught_ids'] if x.startswith('hard3')]
    h2 = [x for x in m['caught_ids'] if x.startswith('hard2')]
    tbl = str(m['table'])
    print(f"#{i+1} {tbl} (size={m['size']}): N={len(nc)} H3={len(h3)} H2={len(h2)} flags={m['false_flags']}")
    if nc: print(f"  normal: {nc}")
    if h3: print(f"  hard3: {h3}")
    if h2: print(f"  hard2: {h2}")

# Also check: spine theorem catchable?
print("\n--- Normal FP detail ---")
for fp in d['normal_fp_detail']:
    print(f"{fp['id']}: 2-elem={fp['n_catchers_2elem']}, 3-elem={fp['n_catchers_3elem']}, best={fp['best']}")
