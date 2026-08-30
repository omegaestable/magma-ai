"""The validated 4-rule 23357 model, as a rules-module (`law`, `rules`) for the hunter / descent tools."""
import sys, importlib.util
D = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D)
_spec = importlib.util.spec_from_file_location('_w3_23357_sets2', D + '/gen/_w3_23357_sets2.py')
_S = importlib.util.module_from_spec(_spec)
_argv = list(sys.argv); sys.argv = [sys.argv[0]]
_spec.loader.exec_module(_S)
sys.argv = _argv
law = _S.law
rules = _S.SETS['f4']
