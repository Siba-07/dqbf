from bisect import bisect_left, bisect_right

def updateCorrectionsTemp(b, modelmap, cors):
# modelmap : id -> corr
    bm = sorted(b, key=abs)
    bk = [abs(y) for y in b]
    bs = sorted(bk)
    # print(len(cors))
    for c in cors:
        # print(c.id)
        usedcor = modelmap[c.id]
        ymin = usedcor.fy
        ymax = usedcor.ly
        i1 = bisect_left(bs, ymin)
        i2 = bisect_right(bs, ymax)
        breq = bm[i1:i2]
        # print(breq)
        # print(breq, usedcor.y_toy.keys())
        for y in c.yvars.keys():
            yvar = usedcor.ytoy_[abs(y)]
            if yvar in breq:
                c.yvars[y] = y
            else:
                c.yvars[y] = -y   

def updateCorrectionsFinal(cors):
    for c in cors:
        c.corrected = 1  

# have to change this
def checkModel(b, modelmap, cx, ucx):
# modelmap : id -> corr
    for y in cx.keys():
        for k in cx[y].keys():
            # print("HOOOO")
            # print(cx[y][k])
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

def correctionClauses(b, modelmap, corsofar):
    bm = sorted(b, key=abs)
    bk = [abs(y) for y in b]
    bs = sorted(bk)
    for id in modelmap.keys():
        # print(id)
        corr = modelmap[id]
        op = []
        ymin = corr.fy
        ymax = corr.ly
        i1 = bisect_left(bs, ymin)
        i2 = bisect_right(bs, ymax)
        breq = bm[i1:i2]
        for k in corr.y_toy.keys():
            y_ = k
            y = corr.y_toy[y_]
            if y_ in breq:
                op.append(y)
            else:
                op.append(-y)

        corsofar[id] = op 
    return