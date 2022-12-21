from copy import deepcopy
from .preprocess import varnames

class Correction:
    def __init__(self, m, proj, clauses, Xvar, Yvar):
        # print(y)
        # print(m)
        self.m = m
        self.id = self.get_id()
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

    def get_id(self):
        sm = sorted(self.m, key=abs)
        id = ""
        for x in self.m:
            if x > 0 :
                id += "1"
            else:
                id += "0"

        return id

    def getEncoding(self, clauses , Xvar, Yvar):
        enc = []
        for i in range(len(clauses)):
            k = clauses[i]
            flag = 0
            for x in k:
                if x in self.m:
                    flag =1
                    break  
            if not flag:
                enc.append([x for x in k if abs(x) not in Xvar])
        
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
    
    def getKey(self,y,sm):
    #get key from model given y
        # print(sm)
        key = ""
        dep = self.depmap[y]
        # print(y, dep, sm)
        # print(dep)
        for x in sm:
            if abs(x) in dep:
                if x > 0:
                    key += "1"
                else:
                    key += "0"
            else:
                key += "#"
        return key

    #new idea for each y maintain a dictionary, and then maintain a list of corrections and then 
    def add(self,m):
        sm = sorted(m, key=abs)
        corr = Correction(m , self.proj, self.clauses, self.Xvar, self.Yvar)  
        self.allcors.append(corr)
        for y in self.depmap.keys():
            k = self.getKey(y,sm)
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
                    print(y, k, c)
        # for y in self.depmap:
        #     k = self.getKey(y, m)
        #     print("{} with key {} has {} corrections".format(y, k, len(self.cs[y][k])))

        