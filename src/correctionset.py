from copy import deepcopy
from .preprocess import varnames

class Correction:
    def __init__(self, m, proj, clauses, Xvar, Yvar, core, stable_y, stable_eval, depmap, cs):
        self.m = m
        self.depmap = depmap
        self.id = self.get_id(core)
        self.yid = self.get_yid(self.id, Yvar)
        self.ytoy_ = {}
        self.y_toy = {}
        self.yvars = {}
        self.fy = -1
        self.ly = -1
        self.enc = self.getEncoding(clauses, Xvar, Yvar, cs)
        self.corrected = 0
        self.st_y = []

        for y in Yvar:
            self.yvars[abs(y)] = abs(y)
            if y in stable_y:
                self.yvars[abs(y)] = stable_eval[y]

        self.constClause = self.getConstClause(Yvar, cs)

    def __str__(self) -> str:
        return self.id

    def get_id(self, core):
        sm = sorted(self.m, key=abs)
        id = ""
        for x in self.m:
            if x > 0 :
                if x in core:
                    id += "1"
                else:
                    id += "*"
            else:
                if x in core:
                    id += "0"
                else:
                    id += "*"

        return id

    def getPrimId(self, sm, id, dep):
        id = deepcopy(id)
        id = list(id)
        for i in range(len(sm)):
            if sm[i] not in dep:
                id[i] = '*'
        
        id = ''.join(id)
        return id         
    
    def get_yid(self, id, Yvar):
        yid = {}
        sm = sorted(self.m, key = abs)
        sm = [abs(x) for x in sm]
        for y in Yvar:
            yid[y] = self.getPrimId(sm, id, self.depmap[y])
        
        return yid

    def getConstClause(self, Yvar,  cs):
        cc = []
        for y in Yvar:
            y_id = self.yid[y]
            yname = self.ytoy_[y]

            if y_id in cs.depSec.keys():
                if y in cs.depSec[y_id]:
                    cc.append([yname])
                elif -y in cs.depSec[y_id]:
                    cc.append([-yname])
        return cc


    def getEncoding (self, clauses , Xvar, Yvar, cs):
        enc = []
        st_y = []
        # print(clauses)
        for y in Yvar:
            k = self.yid[y]
            if k in cs.depPrim.keys():
                if y in cs.depPrim[k]:
                    st_y.append(y)
                    self.yvars[abs(y)] = y
                elif -y in cs.depPrim[k]:
                    st_y.append(-y)
                    self.yvars[abs(y)] = -y
        
        for i in range(len(clauses)):
            k = clauses[i]
            flag = 0
            for x in k:
                if (x in self.m) or (x in st_y):
                    flag = 1
                    break  
            if not flag:
                enc.append([x for x in k if (abs(x) not in Xvar) and (abs(x) not in st_y)])
        
        newnames = varnames(len(Yvar))
        self.fy  = min(newnames)
        self.ly = max(newnames)
        
        for i in range(len(newnames)):
            self.ytoy_[Yvar[i]] = newnames[i]
            self.y_toy[newnames[i]] = Yvar[i]
        
        for i in range(len(enc)):
            for j in range(len(enc[i])):
                k = enc[i][j]
                if k > 0:
                    enc[i][j] = self.ytoy_[abs(k)]
                else:
                    enc[i][j] = -self.ytoy_[abs(k)]
        

        self.st_y = [[self.getSign(y)*self.ytoy_[abs(y)]] for y in st_y]
        return enc
    
    def getSign(self,x):
        if x>=0:
            return 1
        else :
            return -1
        
class CorrectionSet:
    def __init__(self, depmap, proj, clauses, Xvar, Yvar):
        self.cs = {}
        # self.ucx = {}
        self.allcors = []
        for y in Yvar:
            self.cs[y] = {}
        
        self.depmap = deepcopy(depmap)
        self.proj = deepcopy(proj) 
        self.clauses = deepcopy(clauses)
        self.Xvar = deepcopy(Xvar)
        self.Yvar = deepcopy(Yvar)

        self.depPrim = {}
        self.depSec =  {}

    
    def addx(self,keys, x):
        for i in range(len(keys)):
            if x > 0:
                keys[i] += "1"
            else:
                keys[i] += "0"
        return keys

    def getKey(self,y,sm, core):
    #get key from model given y
        # print(sm)
        keys = [""]
        dep = self.depmap[y]
        for x in sm:
            if abs(x) in dep:
                if x in core: 
                    keys = self.addx(keys, x)  
                else:
                    k2 = deepcopy(keys)
                    k2 = self.addx(k2, x)
                    keys = self.addx(keys, -x)
                    keys.extend(k2)
            else:
                for i in range(len(keys)):
                    keys[i] += "#"
        return keys       

        
    #new idea for each y maintain a dictionary, and then maintain a list of corrections and then 
    def add(self,m, core, stable_y, stable_eval):
        sm = sorted(m, key=abs)
        corr = Correction(m , self.proj, self.clauses, self.Xvar, self.Yvar, core, stable_y, stable_eval, self.depmap, self)  
        self.allcors.append(corr)
        # print(stable_y, stable_eval)
        for y in stable_eval:
            y_id = corr.yid[y]
            if y_id in self.depPrim:
                if -stable_eval[y] in self.depPrim[y_id]:
                    print("ERRRORRRR ABORT")
                    exit()
                else:
                    self.depPrim[y_id].append(stable_eval[y])
            else:
                self.depPrim[y_id] = [stable_eval[y]]
        
        for y in self.depmap.keys():    
            keys = self.getKey(y,sm, core)
            for k in keys:
                if k in self.cs[y].keys():
                    self.cs[y][k].append(corr)
                else:
                    self.cs[y][k] = [corr]
        
    
    def getcs(self):
        return self.cs

    def printcs(self, cx):
        for y in cx.keys():
            print(y)
            for k in cx[y].keys():
                # print(len(cx[y][k]))
                for c in cx[y][k]:
                    print(y, k, c, c.yvars, c.yid)
        # for y in self.depmap:
        #     k = self.getKey(y, m)
        #     print("{} with key {} has {} corrections".format(y, k, len(self.cs[y][k])))

        