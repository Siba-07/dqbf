from pysat.formula import CNF
from pysat.solvers import Solver

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
        # if a==9 : print(f[i])
        # if a==9 : print(singleclause)
        # if a == 9 : print("----")
        clauses += singleclause
    gc = [-x for x in gc]
    clauses.append(gc + [a])
    # if a == 9 : print(clauses)
    return clauses

def cleanmodel(m, Xvar, Yvar):
    clean = [x for x in m if abs(x) in Xvar]
    return clean

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

def get_unsat_core(b, phi, Xvar, psi):
    exp = CNF(from_clauses=phi)
    exp.extend(psi)
    res, _ = check_SAT(exp)

    if not res:
        print(" ERROR IN FUNCTION !!!!!!")
        exit()
    
    sig = getSigma(b, Xvar)
    # print("sig = ",sig)

    s = Solver()
    s.append_formula(exp)
    res = s.solve(assumptions=sig)
    if not res:
        core = s.get_core()
    
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
    for i in range(len(id)):
        if id[i] == '1':
            res.append(sx[i])
        else:
            res.append(-sx[i])
    return res

def addFunctionClauses(corsofar, Xvar, skf):
    sx = sorted(Xvar)
    xclauses = []
    n = len(corsofar.keys())
    vnames = varnames(n)
    ind = 0
    for id in corsofar.keys():
        x = getX(sx, id)
        var = vnames[ind]
        ind+=1
        xc = x.copy()
        xc.append(var)
        xclauses.append(xc)

        xx = getorigX(sx, id)

        for x in xx:
            xclauses.append([-var,x])

        for y in corsofar[id]:
            xclauses.append([-var,y])
    
    for y in skf.keys():
        cc = getEquiMultiClause(y,skf[y])
        # if y ==9 : print(y, cc)
        for c in cc:
            vs = vnames.copy()
            vs.extend(c)
            xclauses.append(vs)
    return xclauses

def getTempClause(core):
    clause = [-x for x in core]
    return clause