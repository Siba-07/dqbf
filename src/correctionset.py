from copy import deepcopy
from .preprocess import varnames

class Correction:
    def __init__(self, m, proj, clauses, y, Xvar, Yvar):
        # print(y)
        # print(m)
        self.m = m
        self.id = self.get_id()
        self.ytoy_ = {}
        self.y_toy = {}
        self.y = y
        self.enc = self.getEncoding(clauses, Xvar, Yvar)
        self.corrected = 0
        
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
        self.depmap = deepcopy(depmap)
        self.proj = deepcopy(proj) 
        self.clauses = deepcopy(clauses)
        self.Xvar = deepcopy(Xvar)
        self.Yvar = deepcopy(Yvar)
    
    def getKey(self,y,m):
    #get key from model given y
        sm = sorted(m, key=abs)
        # print(sm)
        key = ""
        dep = self.depmap[y]
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

    def add(self,m):
        for y in self.depmap:
            k = self.getKey(y,m)
            if k in self.cs.keys():
                self.cs[k].append(Correction(m, self.proj, self.clauses, y, self.Xvar, self.Yvar))
            else:
                self.cs[k] = [Correction(m, self.proj, self.clauses, y, self.Xvar, self.Yvar)]
    
    def getcs(self, m):
        corrset = {}
        for y in self.depmap:
            k = self.getKey(y,m)
            corrset[y] = self.cs[k]
        
        return corrset



        