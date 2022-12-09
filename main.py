import time
import argparse
import tempfile

from src.preprocess import *

from pysat.formula import CNF
from pysat.solvers import Solver

n = 10000

def solver():
    print("parsing")
    start_time = time.time()
    Xvar, Yvar, depmap, clauses = parse(args.input)

    if args.verbose:
        print("count X variables", len(Xvar))
        print("count Y variables", len(Yvar))
    
    inputfile_name = args.input.split('/')[-1][:-9]
    # cnffile_name = tempfile.gettempdir()+"/"+inputfile_name+".cnf"
    
    proj = getProjections(clauses, Xvar, Yvar, depmap)
    skf  = getSkolemFunctions(proj)
    # for y in proj.keys():
    #     print(y)
    #     print(proj[y])
    
    # print("--------")
    # for y in skf:
    #     print(y)
    #     print(skf[y])

    exp = CNF(from_clauses=clauses)
    neg = exp.negate()
    for y in Yvar:
        neg.extend(getEquiMultiClause(y,skf[y],neg.nv))
    
    while True:
        s = Solver()
        s.append_formula(neg.clauses)
        print(s.solve())
        print(s.get_model())
        break

    # TODO -  Handcraft an example




    

if __name__ ==  "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("input", help="input file")
    parser.add_argument('--verb', type=int, help="0, 1, 2", dest= 'verbose')
    
    args = parser.parse_args()
    print("Starting solver")
    solver()