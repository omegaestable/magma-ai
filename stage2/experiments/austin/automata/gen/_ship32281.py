"""Strip Lean block comments (squeeze.py does not) then squeeze.  Usage: _ship32281.py <in> <out>"""
import re, sys, subprocess, pathlib
src = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
# whole-line comments: eat the leading indentation too, or the following line's indent doubles
t = re.sub(r'^[ \t]*/-.*?-/[ \t]*\n', '', src, flags=re.S | re.M)
t = re.sub(r'/-.*?-/', '', t, flags=re.S)
t = re.sub(r'\n{3,}', '\n\n', t)
tmp = pathlib.Path(sys.argv[2] + '.nc')
tmp.write_text(t, encoding='utf-8', newline='\n')
print('raw', len(src.encode()), '-> nocomment', len(t.encode()))
subprocess.run([sys.executable, 'squeeze.py', str(tmp), sys.argv[2], '--rename'], check=True)
tmp.unlink()
