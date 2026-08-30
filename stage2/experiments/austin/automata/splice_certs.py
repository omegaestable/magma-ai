"""splice_certs.py [--out <path>] : splice certs/ship_certs.py into solver.py's DISTILLED_CERTS.

Drops every existing `aus_e*` entry and inserts the current `ship_certs.py` lines at the top of the
table, so re-running is idempotent and a re-judged certificate replaces its predecessor rather than
sitting beside it. Also rewrites the research block of stage2/fixtures/judge_verified_certs.jsonl from
certs/ship_fixture.jsonl, keeping every NON-research pin untouched (rail 16: a pin file that is replaced
loses the pins the writer did not know about; only the `false:distilled:aus_e*` routes are ours).

  python splice_certs.py                     # edit the repo in place
  python splice_certs.py --out /tmp/s.py     # dry run: solver only, fixture untouched
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
SOLVER = os.path.join(ROOT, 'stage2', 'solver', 'solver.py')
FIXTURE = os.path.join(ROOT, 'stage2', 'fixtures', 'judge_verified_certs.jsonl')
SHIP_CERTS = os.path.join(HERE, 'certs', 'ship_certs.py')
SHIP_FIXTURE = os.path.join(HERE, 'certs', 'ship_fixture.jsonl')
HEAD = 'DISTILLED_CERTS: dict[tuple[str, str], tuple[str, str, str]] = {\n'

def main():
    dry = '--out' in sys.argv
    out = sys.argv[sys.argv.index('--out') + 1] if dry else SOLVER
    src = open(SOLVER, encoding='utf-8').read()
    if HEAD not in src:
        raise SystemExit('DISTILLED_CERTS header not found; the table declaration changed')
    start = src.index(HEAD) + len(HEAD)
    end = src.index('\n}\n', start) + 1
    body = src[start:end]
    kept = [ln for ln in body.split('\n') if "'aus_e" not in ln and '"aus_e' not in ln]
    new = open(SHIP_CERTS, encoding='utf-8').read()
    if not new.endswith('\n'):
        new += '\n'
    merged = src[:start] + new + '\n'.join(kept).lstrip('\n') + src[end:]
    dropped = len(body.split('\n')) - len(kept)
    added = sum(1 for ln in new.split('\n') if ln.strip())
    open(out, 'w', encoding='utf-8', newline='\n').write(merged)
    print(f'{out}: dropped {dropped} old aus_e entries, inserted {added}; '
          f'{len(src.encode()):,} -> {len(merged.encode()):,} source bytes')

    if dry:
        print('dry run: fixture not touched')
        return
    lines = [ln for ln in open(FIXTURE, encoding='utf-8').read().split('\n')
             if ln.strip() and 'false:distilled:aus_e' not in ln]
    ship = [ln for ln in open(SHIP_FIXTURE, encoding='utf-8').read().split('\n') if ln.strip()]
    open(FIXTURE, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines + ship) + '\n')
    print(f'{FIXTURE}: {len(lines)} non-research pins kept + {len(ship)} research pins = '
          f'{len(lines) + len(ship)}')

if __name__ == '__main__':
    main()
