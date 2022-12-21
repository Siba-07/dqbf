from copy import deepcopy

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
                depmap[y] = Xvar
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
def getEquiMultiClause(a, f):
    clauses = []
    gc = varnames(len(f))
    for i in range(len(f)):
        clauses.append([-a,gc[i]])
        clauses += getEquiSingleClause(gc[i],f[i])
    gc = [-x for x in gc]
    clauses.append(gc + [a])
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
                # return je, modelmap
            
            for i in range(len(cors)):
                for j in range((i+1),len(cors)):
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
                    if y in ucx[y].keys():
                        ucx[y][k].append(c)
                    else:
                        ucx[y][k] = [c] 
                else:
                    if y in cx[y].keys():
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
    for c in cors:
        usedcor = modelmap[c.id]
        for y in c.yvars.keys():
            yvar = usedcor.ytoy_[abs(y)]
            if yvar in b:
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

def updateSkolems(b, modelmap, skf, Xvar):
    sx = sorted(Xvar)
    for id in modelmap.keys():
        x = getX(sx, id)
        c = modelmap[id]
        for k in c.y_toy.keys():
            y_ = k
            y = c.y_toy[y_]
            if y_ in b:
                op = x.copy()
                op.append(y)
                skf[y].append(op)
            else:
                op = x.copy()
                op.append(-y)
                skf[y].append(op)
    return 


def correctionClauses(b, modelmap, corsofar):
    for id in modelmap.keys():
        corr = modelmap[id]
        op = []
        for k in corr.y_toy.keys():
            y_ = k
            y = corr.y_toy[y_]
            if y_ in b:
                op.append(y)
            else:
                op.append(-y)

        corsofar[id] = op 
    return

def addCorrectionClauses(corsofar, Xvar):
    sx = sorted(Xvar)
    corrclauses = []
    for id in corsofar.keys():
        x = getX(sx, id)
        for y in corsofar[id]:
            op = x.copy()
            op.append(y)
            corrclauses.append(op)
    return corrclauses

def getTempClause(b, Xvar):
    clause = []
    for x in Xvar:
        if x in b:
            clause.append(-x)
        else:
            clause.append(x)
    return clause



