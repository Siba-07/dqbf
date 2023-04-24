import time
import argparse

from src.preprocess import *
from src.update_correction import *
from src.joint_encoding import *
from src.utils import *
from src.correctionset import CorrectionSet
from src.debug_utils import *

from pysat.formula import CNF
from pysat.solvers import Solver
from src.debug_utils import *

n = 10000

import time

def tryCorrection(csx, corsofar, Xvar, depmap, cind, ucind, cs, local = True):
    allcors = cs.allcors
    st = time.time()
    gg, modelmap = getJointEncoding(csx, local)
    # printCNF(gg, "local_correction_"+str(lc))
    jt = time.time()
    if args.verbose >= 3 : print("Time for getting local encoding = {}".format(jt - st))
    resc , bc = check_SAT(gg)
    # print(resc)
    if not resc:
        # print("idhar")
        return False
    
    satt = time.time()

    if args.verbose >= 3 : print("Time for SAT call = {}".format(satt - jt))

    glob = not local
    updateCorrectionsTemp(bc, modelmap, allcors[cind:ucind], cs, glob)
    if args.verbose >= 3 : print("Time for updateCorrtemp call = {}".format(time.time() - satt))
    cmt = time.time()
    correctionClauses(bc, modelmap, corsofar, depmap, Xvar)
    if args.verbose >= 3 : print("Time for correctionclauses call = {}".format(time.time() - cmt))
    cct = time.time()
    updateCorrectionsFinal(allcors[cind:ucind])
    if args.verbose >= 3 : print("Time for updatecorrectionfinal call = {}".format(time.time() - cct))
    # print("HOLA", len(corsofar.keys()))
    if args.verbose >= 3 : print("Time elapsed for correction = {}".format(time.time() - st)) 

    return True

def solver():
    print("parsing")
    start_time = time.time()
    Xvar, Yvar, depmap, clauses, ind = parse(args.input)

    unate_map, clauses = unate_test(Xvar, Yvar, clauses, depmap)

    # print(unate_map)
    # print(args.input, len(unate_map.keys()))
    # fname = args.input.split('/')
    # # print(fname)
    # fname = fname[2]
    # # print(fname)
    # ufilename = fname + "_unate"
    # # print(ufilename)    
    # # printCNF(clauses, ufilename)
    # exit()
    # m = [1, 2, -3, 4, 5, -6, 7, 8, -9, -10, 11, -12,-13, -14, 15, 16, -17, -18, -19, 20, -21, 22, -23, -24, -25,-26]
    # for c in clauses:
    #     flag = 0
    #     for mx in m:
    #         flag = 0
    #         if mx in c:
    #             flag = 1
    #             break
    #     if not flag:
    #         print(c)
    #         print("ERROR")
    #         exit()
    # exit()
    # print(clauses[0])
    if len(Yvar) == 0:
        print("UNATE SOLVED")
        print(unate_map)
        exit()

    
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
    skf  = getSkolemOne(proj)
    skf2 = getSkolemZero(proj)
    
    cs  = CorrectionSet(depmap, proj , clauses, Xvar, Yvar)
    corsofar = {}

    # initialize
    exp = CNF(from_clauses=clauses)
    neg = exp.negate(topv = currn())
    updatemaxvar(neg.nv + 1)
    default_clauses, dsk_y = addDefaultSkolemClauses(skf)

    th = 500
    cind = 0
    ucind = 0
    gc = 0
    lc = 0

    lcs = []

    ## initialize
    # print(default_clauses)
    s = Solver(name='g4', incr = True)
    ucs = Solver()
    exp = CNF(from_clauses = clauses)
    # exp.extend(functionclauses)
    ucs.append_formula(exp)


    allclauses = deepcopy(neg.clauses)
    allclauses.extend(default_clauses)
    ucs.append_formula(default_clauses)
    s.append_formula(allclauses)
    last_iter_global = False

    while True:
        lc = 0
        if last_iter_global:
            functionclauses, lc_var  = addFunctionClauses(corsofar, corsofar.keys(), Xvar, skf, dsk_y)
            newclause = [[l] for l in lcs]
            s.append_formula(newclause)
            lcs = [lc_var]
        else:
            req_ids = [c.id for c in cs.allcors[cind:ucind]]
            functionclauses, lc_var  = addFunctionClauses(corsofar, req_ids, Xvar, skf, dsk_y)
            # print(functionclauses)

            lcs.append(lc_var)

        cind = ucind
        last_iter_global = False
        # print(lcs)
        assume = getAssumption(lcs)
        incre_start = time.time()
        i = incremental_SAT(s, ucs, assume, clauses, default_clauses, dsk_y, th, Xvar, Yvar, functionclauses, proj, cs, skf)
        incre_end = time.time()

        if args.verbose >= 3 : print("Time for IncrementSAT call = {}".format(incre_end - incre_start))

        ucind = ucind + i

        if cind == ucind:
            # print(len(corsofar.keys()))
            # for id in corsofar.keys():
            #     print(id, corsofar[id])
            sanity_check(corsofar, clauses, allclauses, Xvar, Yvar, depmap)
            print("SAT")
            return

        print("ENTERING SOLVER ...")
        x = cs.getcs()
        cx, ucx = classifyCs(x) ########### set this dynamically ############
        reslocal = tryCorrection(ucx, corsofar, Xvar, depmap, cind, ucind, cs, True)
        # cs.printcs(ucx)
        # for k in cs.depSec.keys():
        #     print(k, cs.depSec[k])
        if not reslocal:
            print("Local correction failed")
            last_iter_global = True
            # cs.printcs(x)
            resglobal = tryCorrection(x, corsofar, Xvar, depmap, 0, ucind, cs, False)
            # for k in cs.depSec.keys():
            #     print(k, cs.depSec[k])
            if resglobal:
                gc += 1
            else:
                print("UNSAT: Global Correction Failed")
                break
        else:
            lc += 1
        print("Total Local corrections = {}, Global corrections = {}".format(lc, gc))


if __name__ ==  "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("input", help="input file")
    parser.add_argument('--verb', type=int, help="0, 1, 2, 3", dest= 'verbose')
    
    args = parser.parse_args()
    print("Starting solver")
    solver()