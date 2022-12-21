import time
import argparse
import tempfile

from src.preprocess import *
from src.correctionset import CorrectionSet

from pysat.formula import CNF
from pysat.solvers import Solver
from src.debug_utils import *

n = 10000

import time

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
    th = 100
    tempclauses = []
    cind = 0
    ucind = 0
    corrclauses = []
    tc = []
    while True:
        corrno += 1
        # if(args.verbose >=1 ) : print("Inside loop, correction no. = {}".format(corrno))
        if cind == ucind : 
            allclauses = deepcopy(neg.clauses)
            # gk = time.time()
            corrclauses = addCorrectionClauses(corsofar, Xvar)
            # if args.verbose >=3 : print("Time taken to add correction clauses = {}".format(time.time() - gk)) 
            allclauses.extend(corrclauses)
        # print(allclauses)
        if len(tc) != 0: 
            # print(tc)
            allclauses.append(tc)
        # print(allclauses)
        res, b = check_SAT(allclauses)
        # print(res)
        if res:
            b = cleanmodel(b, Xvar, Yvar)
            at = time.time()
            cs.add(b)
            #if args.verbose >= 3: print("Time taken to add correction ={}".format(time.time()- at))
            ucind+=1
            # if args.verbose >=1 : cs.printcs()
            if((ucind-cind) < th):
                tc = getTempClause(b, Xvar)
                continue
            # print(cind)
            # print(ucind)
            print("ENTERING SOLVER ...")
            
            x = cs.getcs()
            cx, ucx = classifyCs(x) ########### set this dynamically #############
            # cs.printcs(ucx)
            st = time.time()
            gg, modelmap = getJointEncoding(ucx)
            jt = time.time()
            if args.verbose >= 3 : print("Time for getting local encoding = {}".format(jt - st))
            resc , bc = check_SAT(gg)
            satt = time.time()
            if args.verbose >= 3 : print("Time for SAT call = {}".format(satt - jt))
            allcors = cs.allcors
            # for c in allcors:
            #     print(c)
            if resc:
                updateCorrectionsTemp(bc, modelmap, allcors[cind+1:ucind])
                if args.verbose >= 3 : print("Time for updateCorrtemp call = {}".format(time.time() - satt))

                # print(checkModel(bc, modelmap, cx))
                ct = time.time()
                if checkModel(bc, modelmap, cx , ucx):
                    if args.verbose >= 3 : print("Time for checking model ={}".format(time.time() - ct))
                    cmt = time.time()
                    correctionClauses(bc, modelmap, corsofar)
                    if args.verbose >= 3 : print("Time for correctionclauses call = {}".format(time.time() - cmt))
                    cct = time.time()
                    updateCorrectionsFinal(allcors[cind+1:ucind])
                    if args.verbose >= 3 : print("Time for updatecorrectionfinal call = {}".format(time.time() - cct))

                    #updateSkolems(bc, modelmap, skf, Xvar)
                    if args.verbose >= 3 : print("Time elapsed for local correction = {}".format(time.time() - st)) 
                else:
                    print("local correction failed")
                    lt = time.time()
                    if args.verbose >= 3 : print("Time elapsed for local correction = {}".format(lt - st)) 
                    gg, modelmap = getJointEncoding(x)
                    jt = time.time()
                    if args.verbose >= 3 : print("Time for getting global encoding = {}".format(jt - lt))
                    resx, bx = check_SAT(gg)
                    if args.verbose >= 3 : print("Time for global SAT call = {}".format(time.time() - jt))

                    if resx:
                        updateCorrectionsTemp(bx, modelmap, allcors)
                        correctionClauses(bx, modelmap, corsofar)
                        updateCorrectionsFinal(allcors)
                        if args.verbose >= 3 : print("Time elapsed for global correction = {}".format(time.time() - lt)) 
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
    parser.add_argument('--verb', type=int, help="0, 1, 2, 3", dest= 'verbose')
    
    args = parser.parse_args()
    print("Starting solver")
    solver()