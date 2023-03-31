def printmap(x):
    for i in x.keys():
        print(i)
        print("--")
        print(len(x[i]))

def printCNF(clauses, filename):
    f = open(filename,"w")
    l = len(clauses)
    mm = 0
    for c in clauses:
        for v in c:
            mm = max(mm, abs(v))
    
    f.write("p cnf {} {}".format(l,mm))

    for c in clauses:
        str = ' '.join(c)
        str += " 0"
        f.write(str)
    
    f.close()

def evaluate(ff, xx):
    # print(ff)
    for c in ff:
        flag = 0
        for x in xx:
            if x in c:
                flag = 1
                break
        if flag == 0 :
            # print(c,xx)
            return 0
    return 1       
# def getSize(x):
#     sz = 0
#     for y in x.keys():
#         sz += len(x[y])
#     return sz

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