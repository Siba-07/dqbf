from copy import deepcopy

class Correction:
    def __init__(self, m):
        self.m = m
        self.encoding = self.getEncoding(m)
    
    def getEncoding(self):
        
        return
    


class CorrectionSet:
    def __init__(self, depmap):
        self.cs = {}
        self.depmap = deepcopy(depmap) 
    
    def getKey(self,y,m):
    #get key from model given y
        sm = sorted(m, key=abs)
        key = ""
        dep = self.depmap[y]
        for x in sm:
            if x in dep:
                if x > 0:
                    key += "1"
                else:
                    key += "0"
            else:
                key += "#"
        return key

    def add(self,m):
        for y in self.depmap:
            k = self.getKey(self.depmap[y],m)
            if k in self.cs.keys():
                self.cs[k].append(m)
            else:
                self.cs[k] = [m]
    
    def getcs(self, m):
        corrset = []
        for y in self.depmap:
            k = self.getKey(self.depmap[y],m)
            corrset += self.cs[k]
        
        return corrset



        