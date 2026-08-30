import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qmod
qmod.UNARY = []
from qmod import terms_upto
import qcheck, q22591b, q27859
from qbig import run
p9 = terms_upto(9, 1); p7 = terms_upto(7, 1); p52 = terms_upto(5, 2)
bad = 0
bad += run('22591', q22591b.M, q22591b.LAW, ['x','y','z'], {}, [p9, p7, p7], 'x<=9, y,z<=7 (1 gen)')
bad += run('22591', q22591b.M, q22591b.LAW, ['x','y','z'], {}, [p7, p9, p7], 'y<=9, x,z<=7 (1 gen)')
bad += run('22591', q22591b.M, q22591b.LAW, ['x','y','z'], {}, [p7, p7, p9], 'z<=9, x,y<=7 (1 gen)')
bad += run('12073', __import__('q12073e').M, __import__('q12073e').LAW, ['x','y'], {'z': ('g',0)}, [p52, p52], 'x,y <= 5 (2 gen) full')
bad += run('27859', q27859.M, q27859.LAW, ['x','y'], {'z': ('g',0)}, [p52, p52], 'x,y <= 5 (2 gen) full')
print('TOTAL FAILS', bad, flush=True)
