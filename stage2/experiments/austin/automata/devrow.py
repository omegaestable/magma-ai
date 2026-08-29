"""devrow.py <eq1_id> <eq2_id> : prepare a fast local Lean compile directory for one row
(vendor/stage2-official/.artifacts/dev_<eq1>_<eq2>/ with JudgeProblem.lean exactly as the judge renders it,
compiled to JudgeProblem.olean).  Then compile certificates with:
    D=<that dir> bash devlean2.sh cert.lean
"""
import sys, os, re, subprocess, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laws import ROOT

def eqdef(name, text):
    seen = set(); vs = []
    for v in re.findall(r'\b([a-z])\b', text):
        if v not in seen: seen.add(v); vs.append(v)
    binders = ' '.join('(%s : G)' % v for v in vs)
    return '@[reducible] def %s (G : Type _) [Magma G] : Prop := ∀ %s, %s' % (name, binders, text)

def main():
    e1, e2 = int(sys.argv[1]), int(sys.argv[2])
    cat = {}
    for i, line in enumerate(open(ROOT + '/vendor/stage2-official/examples/problems/eq_size5.txt', encoding='utf-8'), 1):
        cat[i] = line.strip().replace('*', '◇')
    d = os.path.join(ROOT, 'vendor', 'stage2-official', '.artifacts', 'dev_%d_%d' % (e1, e2))
    os.makedirs(d, exist_ok=True)
    src = 'import JudgeMagma.Magma\n\n%s\n%s\n\n-- Target type for this verify (verdict-specific, judge-controlled).\nabbrev Goal : Prop := ∃ (G : Type) (_ : Magma G), EquationLHS G ∧ ¬ EquationRHS G\n' % (
        eqdef('EquationLHS', cat[e1]), eqdef('EquationRHS', cat[e2]))
    with open(os.path.join(d, 'JudgeProblem.lean'), 'w', encoding='utf-8', newline='\n') as f: f.write(src)
    shutil.copy(os.path.join(ROOT, 'vendor', 'stage2-official', '.artifacts', 'dev5107', 'leanpath.txt'), os.path.join(d, 'leanpath.txt'))
    leanpath = open(os.path.join(d, 'leanpath.txt')).read().strip()
    env = dict(os.environ)
    env['PATH'] = os.path.expanduser('~/.elan/bin') + os.pathsep + env['PATH']
    env['LEAN_PATH'] = d + ';' + leanpath
    p = subprocess.run(['lean', '--root=' + d, '-o', os.path.join(d, 'JudgeProblem.olean'), 'JudgeProblem.lean'],
                       cwd=d, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print(p.stdout[-2000:], p.stderr[-2000:])
    print('dev dir:', d, 'olean ok:', os.path.exists(os.path.join(d, 'JudgeProblem.olean')))

if __name__ == '__main__':
    main()
