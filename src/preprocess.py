from copy import deepcopy

def parse(inputfile):
    with open(inputfile) as f:
        lines = f.readlines()
    f.close()

    Xvar = []
    Yvar = []

    dqdimacs_list = []
    depmap = {}
    
    for line in lines:
        if line.startswith("c"):
            continue
        if (line == "") or (line == "\n"):
            continue
        if line.startswith("p"):
            continue
        if line.startswith("a"):
            Xvar += line.strip("a").strip("\n").strip(" ").split(" ")[:-1]
            continue
        if line.startswith("e"):
            Yvar += line.strip("e").strip("\n").strip(" ").split(" ")[:-1]
            continue
        if line.startswith("d"):
            vars = line.strip("d").strip("\n").strip(" ").split(" ")[:-1]
            vars = list(map(int, list(vars)))
            depmap[vars[0]] = vars[1:]
            Yvar.append(vars[0])
            continue
        
        clause = line.strip(" ").strip("\n").strip(" ").split(" ")[:-1]

        if len(clause) > 0:
            clause = list(map(int, list(clause)))
            dqdimacs_list.append(clause)

    if (len(Xvar) == 0) or (len(Yvar) == 0) or (len(dqdimacs_list) == 0):
        print("problem with the files")
    
    Xvar = list(map(int, list(Xvar)))
    Yvar = list(map(int, list(Yvar)))

    # for y in Yvar:
    #     depmap[y] = Xvar

    return Xvar, Yvar, depmap, dqdimacs_list

def getProjections(clauses, Xvar, Yvar, depmap):
    proj = {}
    for y in Yvar:
        if y in depmap.keys():
            desired_set = deepcopy(depmap[y])
        else:
            desired_set = deepcopy(Xvar)
        
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
        skf[y] = [x for x in proj[y] if -y in x]
        for x in skf[y]:
            if -y in x:
                x.remove(-y)
    return skf

#a is a literal and f is a list
def getEquiSingleClause(a, f):
    clauses = [[-x,a] for x in f]
    clauses.append(f + [-a])
    return clauses

#a is a literal and f is list of lists
def getEquiMultiClause(a, f, n):
    clauses = []
    for i in range(len(f)):
        clauses.append([-a,n+i])
        clauses += getEquiSingleClause(n+i,f[i])
    gc = [*range(-n-len(f),-n)]
    clauses.append(gc + [a])
    return clauses
    