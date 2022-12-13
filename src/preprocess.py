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
            Xvar += line.strip("a").strip("\n").strip(" ").split(" ")[:-1]
            continue
        if line.startswith("e"):
            Yvar += line.strip("e").strip("\n").strip(" ").split(" ")[:-1]
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
    
    Xvar = list(map(int, list(Xvar)))
    Yvar = list(map(int, list(Yvar)))

    for y in Yvar:
        if y not in depmap.keys():
            depmap[y] = Xvar

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
    for k in x.keys():
        cors = x[k]

        if (len(cors) == 1):
            modelmap[cors[0].id] = cors[0]
            je.extend(cors[0].enc)
            return je, modelmap
        
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

                y1 = cor1.ytoy_[k]
                y2 = cor2.ytoy_[k]
                je.extend([[-y1,y2],[y1,-y2]])
    
    return je, modelmap
    
def classifyCs(x):
    cx = {}
    ucx = {}
    for y in x.keys():
        for c in x[y]:
            if(c.corrected == 0):
                if y in ucx.keys():
                    ucx[y].append(c)
                else:
                    ucx[y] = [c] 
            else:
                if y in cx.keys():
                    cx[y].append(c)
                else:
                    cx[y] = [c]
    return cx, ucx

def updateCorrections(b, modelmap, x):
# modelmap : id -> corr
    for k in x.keys():
        cors = x[k]
        for c in cors:
            usedcor = modelmap[c.id]
            yvar = usedcor.ytoy_[abs(c.y)]
            if yvar in b:
                c.y = abs(c.y)
            else:
                c.y = -abs(c.y)
    return
            


def checkModel(b, modelmap, x):
# modelmap : id -> corr
    for k in x.keys():
        cors = x[k]
        for c in cors:
            usedcor = modelmap[c.id]
            yvar = usedcor.ytoy_[abs(usedcor.y)]
            if yvar*c.y < 0: 
                return False
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





