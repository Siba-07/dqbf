from copy import deepcopy
from .utils import *

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
                currx = deepcopy(Xvar)
                depmap[y] = currx
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

def getSkolemOne(oldproj):
    skf = {}
    proj = deepcopy(oldproj)
    for y in proj:
        # if y == 9 : print(proj[y])
        skf[y] = [x for x in proj[y] if y not in x]
        for x in skf[y]:
            if -y in x:
                x.remove(-y)
            # if x == []:
    
    return skf

def getSkolemZero(oldproj):
    skf = {}
    proj = deepcopy(oldproj)
    for y in proj:
        # if y == 9 : print(proj[y])
        skf[y] = [x for x in proj[y] if -y not in x]
        for x in skf[y]:
            if y in x:
                x.remove(y)
            # if x == []:
    
    return skf
    
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
        # print(Ys)
        for y in Ys:
            f1 = []
            f2 = []
            cl = deepcopy(clauses)
            for c in cl:
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
                clauses = deepcopy(f2)
                Yvar.remove(y)
                del depmap[y]  
                unate_map[y] = 0 
                flag = 1 
            elif not unate_check(f2, f1):
                # print("here")
                clauses = deepcopy(f1)
                Yvar.remove(y)
                del depmap[y]
                unate_map[y] = 1
                flag = 1

    return unate_map, clauses    

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
