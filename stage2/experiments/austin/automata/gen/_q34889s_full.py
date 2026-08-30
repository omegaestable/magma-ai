import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qmod, qcheck
from q34889s import M, LAW
qcheck.check(M, LAW, ['x', 'z'], ['y'], sizes=((9, 1), (7, 2), (5, 3)), big=(11, 1, 5),
             deepN=20000, seeds=(3, 4, 5, 6, 7), fuzzN=12000)
