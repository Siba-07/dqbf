import time
import argparse
import tempfile

from src.preprocess import *
from src.correctionset import CorrectionSet

from pysat.formula import CNF
from pysat.solvers import Solver

n = 10000

def solver():
    print("parsing")
    start_time = time.time()
    Xvar, Yvar, depmap, clauses, ind = parse(args.input)
    
    # print(Xvar)
    # print(Yvar)
    # print(clauses)

    # for x in depmap.keys():
    #     print(x)
    #     print(depmap[x])
    

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

    
    
    cs  = CorrectionSet(depmap, proj , clauses, Xvar, Yvar)
    corsofar = {}

    exp = CNF(from_clauses=clauses)
    neg = exp.negate(topv = currn())
    for y in Yvar:
        neg.extend(getEquiMultiClause(y,skf[y]))
    
    updatemaxvar(neg.nv)


    while True:
        allclauses = deepcopy(neg.clauses)
        corrclauses = addCorrectionClauses(corsofar, Xvar) 
        allclauses.extend(corrclauses)
        # print(allclauses)
        s = Solver()
        s.append_formula(allclauses)
        res = s.solve()
        if res:
            b = cleanmodel(s.get_model(), Xvar, Yvar)
            print(b)
            cs.add(b)
            x = cs.getcs(b)
            cx, ucx = classifyCs(x)
            
            gg, modelmap = getJointEncoding(ucx)
            
            sc = Solver()
            sc.append_formula(gg)
            resc = sc.solve()
            if resc:
                bc = sc.get_model()
                updateCorrections(bc, modelmap, ucx)
                # print(checkModel(bc, modelmap, cx))
                if checkModel(bc, modelmap, cx):
                    correctionClauses(bc, modelmap, corsofar)
                    #updateSkolems(bc, modelmap, skf, Xvar)
                else:
                    gg, modelmap = getJointEncoding(x)
                    sx = Solver()
                    sx.append_formula(gg)
                    resx = sx.solve()
                    if resx:
                        bx = sx.get_model()
                        updateCorrections(bx, modelmap, x)
                        correctionClauses( bx, modelmap, corsofar)
                        #updateSkolems(bx, modelmap , skf, Xvar)
                    else:
                        break
            else:
                break
        else:
            for y in skf.keys():
                print(y)
                print(skf[y])
            print("SAT")
            return

if __name__ ==  "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("input", help="input file")
    parser.add_argument('--verb', type=int, help="0, 1, 2", dest= 'verbose')
    
    args = parser.parse_args()
    print("Starting solver")
    solver()