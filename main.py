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

def solver():
    print("parsing")
    start_time = time.time()
    Xvar, Yvar, depmap, clauses, ind = parse(args.input)

    unate_map, clauses = unate_test(Xvar, Yvar, clauses, depmap)
    print(unate_map)
    if len(Yvar) == 0:
        print("UNATE SOLVED")
        print(unate_map)
    #check SAT
    # res, b = check_SAT(clauses)
    # print(res)
    # print(b)
    # dflag = 0
    # for c in clauses:
    #     flag = 0
    #     for x in c:
    #         if x < 0 :
    #             flag = 1
    #     if not flag:
    #         print(c)
    #         dflag = 1 
    
    # print(dflag)
    
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

    # if (args.verbose >=1 ):
    #     # for y in proj.keys():
    #     #     print("No of proj[y] clauses for {} =  {}".format(y, len(proj[y])))
    #     #     if args.verbose >=2 : print("Projection function - {}".format(proj[y]))
    #     for y in skf.keys():
    #         # if y != 9 : continue
    #         print("No of skf[y] clauses for {} =  {}".format(y, len(skf[y])))
    #         if args.verbose >=2 : print("Skolem functions = {}".format(skf[y]))
    
    cs  = CorrectionSet(depmap, proj , clauses, Xvar, Yvar)
    corsofar = {}

    # initialize
    exp = CNF(from_clauses=clauses)
    neg = exp.negate(topv = currn())
    updatemaxvar(neg.nv + 1)
    # print(neg.nv)
    # for y in Yvar:
    #     clause = getEquiMultiClause(y,skf[y])
    #     neg.extend(clause)
    # updatemaxvar(neg.nv + 1)
    corrno = 0
    th = 10
    tempclauses = []
    cind = 0
    ucind = 0
    corrclauses = []
    tc = []
    gc = 0
    lc = 0
    while True:
        corrno += 1
        # if(args.verbose >=1 ) : print("Inside loop, correction no. = {}".format(corrno))
        if cind == ucind : 
            allclauses = deepcopy(neg.clauses)
            # print(allclauses)
            # gk = time.time()
            functionclauses  = addFunctionClauses(corsofar, Xvar, skf)
            # if(args.verbose >= 1) : print(functionclauses)
            #corrclauses = addCorrectionClauses(corsofar, Xvar)
            # if args.verbose >=3 : print("Time taken to add correction clauses = {}".format(time.time() - gk)) 
            allclauses.extend(functionclauses)
        # print(allclauses)
        if len(tc) != 0: 
            # print(tc)
            allclauses.append(tc)
        # print(allclauses)
        res, b = check_SAT(allclauses)
        # print(res)
        if res:
            b = cleanmodel(b, Xvar, Yvar)
            # print(b)
            core  = get_unsat_core(b, clauses, Xvar, functionclauses)
            # print(core)
            at = time.time()
            cs.add(b, core)
            #if args.verbose >= 3: print("Time taken to add correction ={}".format(time.time()- at))
            ucind+=1
            # if args.verbose >=1 : cs.printcs()
            if((ucind-cind) < th):
                tc = getTempClause(core)
                continue
            # print(cind)
            # print(ucind)
            print("ENTERING SOLVER ...")
            # print("ucind",ucind)

            x = cs.getcs()
            cx, ucx = classifyCs(x) ########### set this dynamically #############
            cs.printcs(ucx)
            # cs.printcs(x)
            # print("-------")
            # cs.printcs(ucx)



            # print("Done")
            st = time.time()
            gg, modelmap = getJointEncoding(ucx)
            jt = time.time()
            if args.verbose >= 3 : print("Time for getting local encoding = {}".format(jt - st))
            resc , bc = check_SAT(gg)
            # print(gg)
            # print("-------")
            # print(bc)
            # break
            satt = time.time()
            if args.verbose >= 3 : print("Time for SAT call = {}".format(satt - jt))
            allcors = cs.allcors
            # for c in allcors:
            #     print(c)
            if resc:
                # for c in allcors[cind+1:ucind]:
                #     print(c.id)
                
                updateCorrectionsTemp(bc, modelmap, allcors[cind:ucind])
                if args.verbose >= 3 : print("Time for updateCorrtemp call = {}".format(time.time() - satt))

                # print(checkModel(bc, modelmap, cx))
                ct = time.time()
                if checkModel(bc, modelmap, cx , ucx):
                    cs.printcs(ucx)
                    if args.verbose >= 3 : print("Time for checking model ={}".format(time.time() - ct))
                    cmt = time.time()
                    correctionClauses(bc, modelmap, corsofar)
                    if args.verbose >= 3 : print("Time for correctionclauses call = {}".format(time.time() - cmt))
                    cct = time.time()
                    updateCorrectionsFinal(allcors[cind:ucind])
                    if args.verbose >= 3 : print("Time for updatecorrectionfinal call = {}".format(time.time() - cct))

                    #updateSkolems(bc, modelmap, skf, Xvar)
                    lc += 1
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
                        gc += 1

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
            # cs.printcs(x)
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

            for id in corsofar.keys():
                print(id, corsofar[id])
            print("SAT")
            return

        cind = ucind
        tempclauses = []

    print("Total Local corrections = {}, Global corrections = {}".format(lc, gc))


if __name__ ==  "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("input", help="input file")
    parser.add_argument('--verb', type=int, help="0, 1, 2, 3", dest= 'verbose')
    
    args = parser.parse_args()
    print("Starting solver")
    solver()