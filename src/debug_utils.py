def printmap(x):
    for i in x.keys():
        print(i)
        print("--")
        print(len(x[i]))

def printCNF(clauses, filename):
    filename = str("unatefiles/"+ filename)
    f = open(filename,"w")
    l = len(clauses)
    mm = 0
    for c in clauses:
        for v in c:
            mm = max(mm, abs(v))
    
    f.write("p cnf {} {}".format(l,mm))
    
    for c in clauses:
        # x = [str(cx) for cx in c]
        st = ' '.join(str(x) for x in c)
        st += " 0\n"
        f.write(st)
    
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

 # if (args.verbose >=1 ):
    #     # for y in proj.keys():
    #     #     print("No of proj[y] clauses for {} =  {}".format(y, len(proj[y])))
    #     #     if args.verbose >=2 : print("Projection function - {}".format(proj[y]))
    # for y in skf.keys():
    #     # if y != 9 : continue
    #     print("No of skf[y] clauses for {} =  {}".format(y, len(skf[y])))
    #     if args.verbose >=2 : print("Skolem functions = {}".format(skf[y]))