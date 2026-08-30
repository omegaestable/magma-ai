import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qmod
qmod.UNARY = []
from qmod import terms_upto
import q27859
from qbig import run
p11 = terms_upto(11, 1)
run('27859', q27859.M, q27859.LAW, ['x','y'], {'z': ('g',0)}, [p11, p11], 'x,y <= 11 (1 gen)')
print('DONE', flush=True)
