from pysat.formula import CNF
from pysat.solvers import Solver
from copy import deepcopy

global_n = 100000

def updatemaxvar(n):
    global global_n
    global_n = max(global_n, n)

def varnames(n):
    global global_n
    nv = global_n
    vnames = [*range(nv,nv+n)]
    global_n = nv + n
    return vnames

def currn():
    return global_n


#a is a literal and f is a list
def getEquiSingleClause(a, f):
    clauses = [[-x,a] for x in f]
    clauses.append(f + [-a])
    return clauses

#a is a literal and f is list of lists
def getEquiMultiClause(a, f):
    # if a ==9 : print(a,f)
    clauses = []
    gc = varnames(len(f))
    for i in range(len(f)):
        clauses.append([-a,gc[i]])
        singleclause = getEquiSingleClause(gc[i],f[i])
        clauses += singleclause
    gc = [-x for x in gc]
    clauses.append(gc + [a])
    # if a == 9 : print(clauses)
    return clauses

def cleanmodel(m, Xvar, Yvar):
    clean = [x for x in m if abs(x) in Xvar]
    return clean

def process_model(b, assume, Xvar, Yvar, proj, cs, ucs, clauses, functionclauses, skf):
    b = cleanmodel(b, Xvar, Yvar)
    # print(b)

    core  = get_unsat_core(ucs, assume, b, clauses, Xvar, functionclauses)
    stable_y, stable_eval = get_stable_y(proj, skf, b)
    cs.add(b, core, stable_y, stable_eval)
    return core

def incremental_SAT(s, ucs, assume, orig_clauses, dc, dsk_y, n, Xvar, Yvar, functionclauses, proj, cs, skf):
    # s = Solver(name='g4', incr = True)
    # s.append_formula(allclauses)
    s.append_formula(functionclauses)
    #for handling UNSAT cores in incremental way
   
    # exp.extend(dc)
    ucs.append_formula(functionclauses)

    for i in range(n):
        # print(i)
        res = s.solve(assumptions=assume)
        if not res:
            return i
        b = s.get_model()
        core = process_model(b, assume, Xvar, Yvar, proj, cs, ucs, orig_clauses, functionclauses, skf)
        tc = getTempClause(core)
        if len(tc) != 0:
            s.add_clause(tc)
    return n

def check_SAT(clauses):
    s = Solver()
    s.append_formula(clauses)
    res = s.solve()
    b = s.get_model()
    return res, b

def getSigma(b, Xvar):
    sig = []
    for x in Xvar:
        if x in b:
            sig.append(x)
        else:
            sig.append(-x)
    return sig

def get_unsat_core(s, assume, b, phi, Xvar, psi):
    # exp = CNF(from_clauses=phi)
    # exp.extend(psi)
    # res, _ = check_SAT(exp)

    # if not res:
    #     print(" ERROR IN FUNCTION !!!!!!")
    #     exit()
    
    sig = getSigma(b, Xvar)
    curr_assume = deepcopy(assume)
    sig.extend(curr_assume)

    # print("sig = ",sig)

    res = s.solve(assumptions=sig)
    # print(res)
    if not res:
        core = s.get_core()
    # print(core)
    return core

def getX(sx, id):
    res = []
    for i in range(len(id)):
        if id[i] == '1':
            res.append(-sx[i])
        else:
            res.append(sx[i])
    return res

def getorigX(sx, id):
    res = []
    # print(len(sx))
    # print(sx)
    for i in range(len(id)):
        if id[i] == '1':
            res.append(sx[i])
        else:
            res.append(-sx[i])
    return res

def addDefaultSkolemClauses(skf):
    def_clauses = []
    vnames = varnames(len(skf.keys()))
    ind = 0
    dsk_y = {}
    for y in skf.keys():
        cc = getEquiMultiClause(y, skf[y])
        cd = getEquiMultiClause(vnames[ind], cc)
        def_clauses.extend(cd)
        dsk_y[y] = vnames[ind] 
        ind += 1

    return def_clauses, dsk_y

def addFunctionClauses(corsofar, ids, Xvar, skf, dsk_y):
    sx = sorted(Xvar)
    xclauses = []
    n = len(corsofar.keys())*len(skf.keys())
    vnames = varnames(n)
    ind = 0

    lcname = varnames(1)
    lcname = lcname[0]

    yvs = {}
    for y in skf.keys():
        yvs[y] = []

    for id in ids:
        for y,xg in corsofar[id]:
            x = [-v for  v in xg]
            var = vnames[ind]
            ind+=1
            xc = x.copy()
            xc.extend([var,lcname])
            xclauses.append(xc)
            xx = xg.copy()

            for xv in  xx:
                xclauses.append([-var,xv, lcname])
            
            xclauses.append([-var,y, lcname])

            yvs[abs(y)].append(var)
    
    for y in skf.keys():
        vs = yvs[y].copy()
        vs.append(dsk_y[y])
        vs.append(lcname)
        xclauses.append(vs)

    return xclauses, lcname

def getAssumption(lcs):
    ass = [l for l in lcs[:-1]]
    ass.append(-lcs[-1])
    return ass

def getTempClause(core):
    clause = [-x for x in core]
    return clause

def evaluate(y, f, m):
    flag = 0
    for c in f[abs(y)]:
        cflag = 0
        for x in c:
            if (x in m) or (x == y):
                cflag = 1
                break
        if not cflag:
            flag = 1
            break
    if flag:
        return 0
    else:
        return 1

def get_stable_y(proj, skf, m):
    stable_y = []
    stable_eval = {}
    
    for y in proj:
        eval1 = evaluate(y, proj, m)
        eval2 = evaluate(-y, proj, m)

        if eval1 == 1 or eval2 == 1:
            stable_y.append(y)
            eval_y = evaluate(y, skf, m)
            stable_eval[y] = eval_y
    
    return stable_y, stable_eval
