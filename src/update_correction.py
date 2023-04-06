from bisect import bisect_left, bisect_right

def updateCorrectionsTemp(b, modelmap, cors, cs, update = False):
# modelmap : id -> corr
    bm = sorted(b, key=abs)
    bk = [abs(y) for y in b]
    bs = sorted(bk)
    for c in cors:
        usedcor = modelmap[c.id]
        ymin = usedcor.fy
        ymax = usedcor.ly
        i1 = bisect_left(bs, ymin)
        i2 = bisect_right(bs, ymax)
        breq = bm[i1:i2]
        for y in c.yvars.keys():
            yvar = usedcor.ytoy_[abs(y)]
            if yvar in breq:
                c.yvars[y] = y
            else:
                c.yvars[y] = -y
        
        if update:
            cs.depSec = {}
            
        for y in c.yvars.keys():
            y_id = c.yid[y]
            yvar = c.yvars[y]
            if y_id in cs.depSec:
                if -yvar in cs.depSec[y_id]:
                    print("ERRRORRRR ABORT")
                    exit()
                elif yvar not in cs.depSec[y_id]:
                    cs.depSec[y_id].append(yvar)
            else:
                cs.depSec[y_id] = [yvar]


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
def getx(id, dep, Xvar):
    xc = []
    sx = sorted(Xvar)
    for i in range(len(id)):
        ii = id[i]
        if sx[i] not in dep:
            continue
        if ii == '1':
            xc.append(sx[i])
        elif ii == '0':
            xc.append(-sx[i])
    return xc
        
def correctionClauses(b, modelmap, corsofar, depmap, Xvar):
    bm = sorted(b, key=abs)
    bk = [abs(y) for y in b]
    bs = sorted(bk)
    for id in modelmap.keys():
        # print(id)
        corr = modelmap[id]
        # print(id, corr.id)

        op = []
        ymin = corr.fy
        ymax = corr.ly
        i1 = bisect_left(bs, ymin)
        i2 = bisect_right(bs, ymax)
        breq = bm[i1:i2]
        for k in corr.y_toy.keys():
            y_ = k
            y = corr.y_toy[y_]
            xc = getx(corr.id, depmap[y], Xvar)
            if y_ in breq:
                op.append((y, xc))
            else:
                op.append((-y, xc))

        corsofar[id] = op 
    return