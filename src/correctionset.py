from copy import deepcopy
from .preprocess import varnames

class Correction:
    def __init__(self, m, proj, clauses, Xvar, Yvar, core):
        # print(y)
        # print(m)
        self.m = m
        self.id = self.get_id(core)
        self.ytoy_ = {}
        self.y_toy = {}
        self.yvars = {}
        self.fy = -1
        self.ly = -1
        self.enc = self.getEncoding(clauses, Xvar, Yvar)
        self.corrected = 0
        for y in Yvar:
            self.yvars[abs(y)] = abs(y)
    
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

    def getEncoding(self, clauses , Xvar, Yvar):
        enc = []
        # print(clauses)
        for i in range(len(clauses)):
            k = clauses[i]
            flag = 0
            for x in k:
                if x in self.m:
                    flag =1
                    break  
            if not flag:
                print(k)
                enc.append([x for x in k if abs(x) not in Xvar])
        
        # print(self.m, enc)
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
        
        print(self.m,enc)
        # print(enc)
        return enc

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
        # print(y, dep, sm)
        # print(dep)
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
    def add(self,m, core):
        sm = sorted(m, key=abs)
        corr = Correction(m , self.proj, self.clauses, self.Xvar, self.Yvar, core)  
        self.allcors.append(corr)
        for y in self.depmap.keys():
            keys = self.getKey(y,sm, core)
            # print(y)
            # print(keys)
            for k in keys:
                if k in self.cs[y].keys():
                    self.cs[y][k].append(corr)
                else:
                    self.cs[y][k] = [corr]
    
    def getcs(self):
        return self.cs

    def printcs(self, cx):
        for y in cx.keys():
            # print(y)
            for k in cx[y].keys():
                # print(k)
                for c in cx[y][k]:
                    print(y, k, c, c.yvars)
        # for y in self.depmap:
        #     k = self.getKey(y, m)
        #     print("{} with key {} has {} corrections".format(y, k, len(self.cs[y][k])))

        