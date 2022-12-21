import time
import argparse
import tempfile

from src.preprocess import *
from src.correctionset import CorrectionSet

from pysat.formula import CNF
from pysat.solvers import Solver
from src.debug_utils import *

n = 10000

def check_SAT(clauses):
    s = Solver()
    s.append_formula(clauses)
    res = s.solve()
    b = s.get_model()
    return res, b


def solver():
    print("parsing")
    start_time = time.time()
    Xvar, Yvar, depmap, clauses, ind = parse(args.input)
    
    if (args.verbose >= 1):
        print("Xvars : {}".format(Xvar))
        print("count of X variables", len(Xvar))
        print("Yvars : {}".format(Yvar))
        print("count of Y variables", len(Yvar))
        print("No of clauses = {}".format(len(clauses)))

        if (args.verbose >= 2):
            for y in depmap:
                print("FOR y = {}, dependancy vars are {}".format(y, depmap[y]))

    proj = getProjections(clauses, Xvar, Yvar, depmap)
    skf  = getSkolemFunctions(proj)

    if (args.verbose >=1 ):
        for y in proj.keys():
            print("No of proj[y] clauses for {} =  {}".format(y, len(proj[y])))
            if args.verbose >=2 : print("Projection function - {}".format(proj[y]))
        for y in skf.keys():
            print("No of skf[y] clauses for {} =  {}".format(y, len(skf[y])))
            if args.verbose >=2 : print("Skolem functions = {}".format(skf[y]))
    
    cs  = CorrectionSet(depmap, proj , clauses, Xvar, Yvar)
    corsofar = {}

    # initialize
    exp = CNF(from_clauses=clauses)
    neg = exp.negate(topv = currn())
    updatemaxvar(neg.nv)
    for y in Yvar:
        neg.extend(getEquiMultiClause(y,skf[y]))
    updatemaxvar(neg.nv)
    corrno = 0
    th = 1000
    tempclauses = []
    cind = 0
    ucind = 0
    while True:
        corrno += 1
        if(args.verbose >=1 ) : print("Inside loop, correction no. = {}".format(corrno))
        allclauses = deepcopy(neg.clauses)
        corrclauses = addCorrectionClauses(corsofar, Xvar) 
        allclauses.extend(corrclauses)
        allclauses.extend(tempclauses)
        res, b = check_SAT(allclauses)

        if res:
            b = cleanmodel(b, Xvar, Yvar)
            cs.add(b)
            ucind+=1
            if args.verbose >=1 : cs.printcs(b)
            if((ucind-cind) < th):
                tempclauses.append(getTempClause(b, Xvar))
                continue
            # print(cind)
            # print(ucind)
            print("ENTERING SOLVER ...")
            
            x = cs.getcs()
            cx, ucx = classifyCs(x) ########### set this dynamically #############
            # cs.printcs(ucx)
            
            gg, modelmap = getJointEncoding(ucx)
            resc , bc = check_SAT(gg)
            allcors = cs.allcors
            # for c in allcors:
            #     print(c)
            if resc:
                updateCorrectionsTemp(bc, modelmap, allcors[cind+1:ucind])
                # print(checkModel(bc, modelmap, cx))
                if checkModel(bc, modelmap, cx , ucx):
                    correctionClauses(bc, modelmap, corsofar)
                    updateCorrectionsFinal(allcors[cind+1:ucind])
                    #updateSkolems(bc, modelmap, skf, Xvar)
                else:
                    print("local correction failed")
                    gg, modelmap = getJointEncoding(x)
                    resx, bx = check_SAT(gg)
                    if resx:
                        updateCorrectionsTemp(bx, modelmap, allcors)
                        correctionClauses(bx, modelmap, corsofar)
                        updateCorrectionsFinal(allcors)
                        #updateSkolems(bx, modelmap , skf, Xvar)
                    else:
                        print("here1")
                        break
            else:
                print("here2")
                break
        else:
            x = cs.getcs()
            allcors = cs.allcors
            gg, modelmap = getJointEncoding(x)
            resx, bx = check_SAT(gg)
            if resx:
                updateCorrectionsTemp(bx, modelmap, allcors)
                correctionClauses(bx, modelmap, corsofar)
                updateCorrectionsFinal(allcors)
            else:
                print("here3")
                break

            for y in skf.keys():
                print(y)
                print(skf[y])
            print("SAT")
            return

        cind = ucind
        tempclauses = []


if __name__ ==  "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("input", help="input file")
    parser.add_argument('--verb', type=int, help="0, 1, 2", dest= 'verbose')
    
    args = parser.parse_args()
    print("Starting solver")
    solver()