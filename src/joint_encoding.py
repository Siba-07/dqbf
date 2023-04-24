def getJointEncoding(x, useConst = False):
    je = []
    modelmap = {}
    for y in x.keys():
        for k in x[y].keys():
            cors = x[y][k]

            if (len(cors) == 1):
                modelmap[cors[0].id] = cors[0]
                je.extend(cors[0].enc)
                if len(cors[0].st_y) != 0 : je.extend(cors[0].st_y)
                if useConst :
                    je.extend(cors[0].constClause)
                
            for i in range(1):
                for j in range((i+1),len(cors)):
                    # print(cors[i].id, cors[j].id, "HELLO")
                    if(cors[i].id in modelmap.keys()):
                        cor1 = modelmap[cors[i].id]
                    else:
                        cor1 = cors[i]
                        modelmap[cor1.id] = cor1
                        je.extend(cor1.enc)
                        if len(cor1.st_y) != 0 : je.extend(cor1.st_y)
                        if useConst :
                            je.extend(cor1.constClause)

                    if(cors[j].id in modelmap.keys()):
                        cor2 = modelmap[cors[j].id]
                    else:
                        cor2 = cors[j]
                        modelmap[cor2.id] = cor2
                        je.extend(cor2.enc)
                        if len(cor2.st_y) != 0 : je.extend(cor2.st_y)
                        if useConst :
                            je.extend(cor2.constClause)

                    y1 = cor1.ytoy_[y]
                    y2 = cor2.ytoy_[y]
                    je.extend([[-y1,y2],[y1,-y2]])
    # print(modelmap.keys())  
    return je, modelmap