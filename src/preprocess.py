from copy import deepcopy
from bisect import bisect_left, bisect_right
from pysat.formula import CNF
from pysat.solvers import Solver

global_n = 100000

def parse(inputfile):
    with open(inputfile) as f:
        lines = f.readlines()
    f.close()

    Xvar = []
    Yvar = []

    dqdimacs_list = []
    depmap = {}
    dep = []
    
    for line in lines:
        if line.startswith("c"):
            continue
        if (line == "") or (line == "\n"):
            continue
        if line.startswith("p"):
            continue
        if line.startswith("a"):
            vars = line.strip("a").strip("\n").strip(" ").split(" ")[:-1]
            vars = list(map(int, list(vars)))
            Xvar.extend(vars)
            continue
        if line.startswith("e"):
            vars = line.strip("e").strip("\n").strip(" ").split(" ")[:-1]
            vars = list(map(int, list(vars)))
            for y in vars:
                depmap[y] = []
            Yvar.extend(vars)
            continue
        if line.startswith("d"):
            vars = line.strip("d").strip("\n").strip(" ").split(" ")[:-1]
            vars = list(map(int, list(vars)))
            depmap[vars[0]] = vars[1:]
            dep.extend(vars)
            Yvar.append(vars[0])
            continue
        
        clause = line.strip(" ").strip("\n").strip(" ").split(" ")[:-1]

        if len(clause) > 0:
            clause = list(map(int, list(clause)))
            dqdimacs_list.append(clause)

    if (len(Xvar) == 0) or (len(Yvar) == 0) or (len(dqdimacs_list) == 0):
        print("problem with the files")

    # for y in Yvar:
    #     if y not in depmap.keys():
    #         depmap[y] = Xvar

    dep = set(dep)
    totvar = Xvar +  Yvar
    totvar = set(totvar)
    ind = list(totvar - dep)


    return Xvar, Yvar, depmap, dqdimacs_list, ind

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

def getProjections(clauses, Xvar, Yvar, depmap):
    proj = {}
    for y in Yvar:
        desired_set = deepcopy(depmap[y])
        desired_set.append(y)

        filtered = [c if y in c or -y in c else [] for c in clauses]
        proj_y = []
       
        for c in filtered:
            if not c:
                proj_y.append([])
            else:
                proj_y.append([x for x in c if abs(x) in desired_set])

        proj[y] = proj_y
    return proj     

def getSkolemFunctions(oldproj):
    skf = {}
    proj = deepcopy(oldproj)
    for y in proj:
        # if y == 9 : print(proj[y])
        skf[y] = [x for x in proj[y] if -y in x]
        for x in skf[y]:
            if -y in x:
                x.remove(-y)
            # if x == []:
    
    return skf

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

def getJointEncoding(x):
    je = []
    modelmap = {}
    for y in x.keys():
        for k in x[y].keys():
            cors = x[y][k]
            if (len(cors) == 1):
                modelmap[cors[0].id] = cors[0]
                je.extend(cors[0].enc)
                # yset.update(set(cors[0].y_toy.keys()))
                # return je, modelmap
            
            # print(y,k)
            # for c in cors:
            #     print(c.id)
            
            # print("^^^^^^^^^^^^^^^^^^^^^")
                
            for i in range(1):
                for j in range((i+1),len(cors)):
                    # print(cors[i].id, cors[j].id, "HELLO")
                    if(cors[i].id in modelmap.keys()):
                        cor1 = modelmap[cors[i].id]
                    else:
                        cor1 = cors[i]
                        modelmap[cor1.id] = cor1
                        je.extend(cor1.enc)

                    if(cors[j].id in modelmap.keys()):
                        cor2 = modelmap[cors[j].id]
                    else:
                        cor2 = cors[j]
                        modelmap[cor2.id] = cor2
                        je.extend(cor2.enc)

                    y1 = cor1.ytoy_[y]
                    y2 = cor2.ytoy_[y]
                    je.extend([[-y1,y2],[y1,-y2]])
                   
    return je, modelmap
    
def classifyCs(x):
    # print(x)
    cx = {}
    ucx = {}
    for y in x.keys():
        cx[y] = {}
        ucx[y] = {}
        for k in x[y].keys():
            cors = x[y][k]
            for c in cors:
                if(c.corrected == 0):
                    if k in ucx[y].keys():
                        ucx[y][k].append(c)
                    else:
                        ucx[y][k] = [c] 
                else:
                    if k in cx[y].keys():
                        cx[y][k].append(c)
                    else:
                        cx[y][k] = [c]
    return cx, ucx

# def getSize(x):
#     sz = 0
#     for y in x.keys():
#         sz += len(x[y])
#     return sz

def updateCorrectionsTemp(b, modelmap, cors):
# modelmap : id -> corr
    bm = sorted(b, key=abs)
    bk = [abs(y) for y in b]
    bs = sorted(bk)
    # print(len(cors))
    for c in cors:
        # print(c.id)
        usedcor = modelmap[c.id]
        ymin = usedcor.fy
        ymax = usedcor.ly
        i1 = bisect_left(bs, ymin)
        i2 = bisect_right(bs, ymax)
        breq = bm[i1:i2]
        # print(breq)
        # print(breq, usedcor.y_toy.keys())
        for y in c.yvars.keys():
            yvar = usedcor.ytoy_[abs(y)]
            if yvar in breq:
                c.yvars[y] = y
            else:
                c.yvars[y] = -y   
    # for y in x.keys():
    #     for k in x[y].keys():
    #         cors = x[y][k]
    #         for c in cors:
    #             usedcor = modelmap[c.id]
    #             # if not temp : c.corrected = 1
    #             for y in c.yvars.keys():
    #             # c.corrected = 1
    #                 yvar = usedcor.ytoy_[abs(y)]
    #                 if yvar in b:
    #                     c.yvars[y] = y
    #                 else:
    #                     c.yvars[y] = -y
    # return

def updateCorrectionsFinal(cors):
    for c in cors:
        c.corrected = 1  

# have to change this
def checkModel(b, modelmap, cx, ucx):
# modelmap : id -> corr
    for y in cx.keys():
        for k in cx[y].keys():
            # print("HOOOO")
            # print(cx[y][k])
            cor1 = cx[y][k]
            if k in ucx[y].keys():
                cor2 = ucx[y][k]
            else:
                continue

            # if len(cor1) + len(cor2) < 2:
            #     return True
            
            c1 = cor1[0]
            c2 = cor2[0]

            usedcor = modelmap[c2.id]
            ynew = usedcor.ytoy_[abs(y)]
            if ynew not in b: ynew = -ynew
            yold = c1.yvars[y]

            if yold*ynew < 0 : return False

    return True

def getX(sx, id):
    res = []
    for i in range(len(id)):
        if id[i] == '1':
            res.append(-sx[i])
        else:
            res.append(sx[i])
    return res

# def updateSkolems(b, modelmap, skf, Xvar):
#     sx = sorted(Xvar)
#     for id in modelmap.keys():
#         x = getX(sx, id)
#         c = modelmap[id]
#         for k in c.y_toy.keys():
#             y_ = k
#             y = c.y_toy[y_]
#             if y_ in b:
#                 op = x.copy()
#                 op.append(y)
#                 skf[y].append(op)
#             else:
#                 op = x.copy()
#                 op.append(-y)
#                 skf[y].append(op)
#     return 


def correctionClauses(b, modelmap, corsofar):
    bm = sorted(b, key=abs)
    bk = [abs(y) for y in b]
    bs = sorted(bk)
    for id in modelmap.keys():
        # print(id)
        corr = modelmap[id]
        op = []
        ymin = corr.fy
        ymax = corr.ly
        i1 = bisect_left(bs, ymin)
        i2 = bisect_right(bs, ymax)
        breq = bm[i1:i2]
        for k in corr.y_toy.keys():
            y_ = k
            y = corr.y_toy[y_]
            if y_ in breq:
                op.append(y)
            else:
                op.append(-y)

        corsofar[id] = op 
    return

# def addCorrectionClauses(corsofar, Xvar):
#     sx = sorted(Xvar)
#     corrclauses = []
#     for id in corsofar.keys():
#         x = getX(sx, id)
#         for y in corsofar[id]:
#             op = x.copy()
#             op.append(y)
#             corrclauses.append(op)
#     return corrclauses

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

#
def unate_check(f1, f2):
    vars = varnames(1)
    clauses = deepcopy(f1)
    # print(vars[0])
    clauses.append([-vars[0]])
    # clauses.append(getEquiMultiClause(vars[0], f1))
    clauses.extend(getEquiMultiClause(vars[0], f2))
    res, _ = check_SAT(clauses)
    # print(clauses)
    # print(res)
    return res

def unate_test(Xvar, Yvar, clauses, depmap):
    unate_map = {}
    flag = 1
    while flag:
        flag = 0
        Ys = deepcopy(Yvar)
        print(Ys)
        for y in Ys:
            f1 = []
            f2 = []
            for c in clauses:
                c_ = c
                if y in c:
                    c_.remove(y)
                    f2.append(c_)
                elif -y in c:
                    c_.remove(-y)
                    f1.append(c_)
                else:
                    f1.append(c_)
                    f2.append(c_)
        
            if not unate_check(f1, f2):
                # print("here")
                clauses = deepcopy(f1)
                Yvar.remove(y)
                del depmap[y]  
                unate_map[y] = 0 
                flag = 1 
            elif not unate_check(f2, f1):
                # print("here")
                clauses = deepcopy(f2)
                Yvar.remove(y)
                del depmap[y]
                unate_map[y] = 1
                flag = 1
    
    return unate_map, clauses




