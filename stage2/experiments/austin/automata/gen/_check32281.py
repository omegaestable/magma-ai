"""Pre-ship gate for a 32281 certificate: banned tokens (raw text, comments included), byte cap, sorry count."""
import sys, re, pathlib
BANNED = ['macro', 'run_cmd', 'run_elab', '@[init', 'skipKernelTC',
          'notation3', 'notation', 'infixl', 'infixr', 'infix', 'prefix', 'postfix']
CAP = 19500
ok = True
for p in sys.argv[1:]:
    t = pathlib.Path(p).read_text(encoding='utf-8')
    n = len(t.encode('utf-8'))
    hits = [b for b in BANNED if b in t]
    ns = t.count('sorry')
    bad = hits or n > CAP or ns
    ok = ok and not bad
    print(('FAIL ' if bad else 'PASS ') + p, 'bytes=%d/%d' % (n, CAP),
          'sorry=%d' % ns, 'banned=%s' % (hits or 'none'))
sys.exit(0 if ok else 1)
