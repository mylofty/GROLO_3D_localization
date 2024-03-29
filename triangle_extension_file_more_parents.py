import numpy as np

Collinear = 0.5
# triangle extension for Robot r


def triangle_extension(r, probot) :
    if r.state==0:
        # print("now get case 0")

        for j in range(len(r.myNeighbor)) :
            for k in range(j+1, len(r.myNeighbor)) :
                nei1 = probot[r.myNeighbor[j][0]]
                nei2 = probot[r.myNeighbor[k][0]]
                dis1 = r.myNeighbor[j][1]
                dis2 = r.myNeighbor[k][1]

                if nei1.state!=0 and nei2.state!=0 and (nei1.is_child_of_id(nei2.id) or nei2.is_child_of_id(nei1.id)) :
                    # are they located on one line ?
                    # if (r.locationx-nei1.locationx)*(r.locationy-nei2.locationy)!=(r.locationy-nei1.locationy)*(r.locationx-nei2.locationx) :
                    # print(nei1.id, nei2.id)

                    dis3 = nei1.distance_to(nei2.id) or nei2.distance_to(nei1.id)
                    if not(abs(dis3-dis1-dis2)<Collinear or abs(dis1-dis2-dis3)< Collinear or abs(dis2-dis1-dis3)< Collinear):
                        r.add_parents(nei1.id, nei2.id)

                        r1 = nei1.root1
                        if nei1.root2 != nei1.root1:
                            r2 = nei1.root2
                        elif nei2.root1 != nei1.root1:
                            r2 = nei2.root1
                        else:
                            r2 = nei2.root2
                        r.add_roots(r1, r2)

                        r.state = 1


                elif nei1.state==3 and nei2.state==3 :
                    # are they located on one line?
                    # if (r.locationx-nei1.locationx)*(r.locationy-nei2.locationy)!=(r.locationy-nei1.locationy)*(r.locationx-nei2.locationx):

                    dis3 = np.sqrt(np.sum(np.square(np.array([nei1.get_coord()[0], nei1.get_coord()[1]]) -
                                                    np.array([nei2.get_coord()[0], nei2.get_coord()[1]]))))

                    if not(abs(dis3-dis1-dis2)<Collinear or abs(dis1-dis2-dis3)<Collinear or abs(dis2-dis1-dis3)<Collinear):
                        r.add_parents(nei1.id, nei2.id)
                        r.add_roots(nei1.id, nei2.id)

                        r.state = 1


                elif nei1.state == 2 and nei2.state == 3 or nei1.state == 3 and nei2.state == 2:   # some problem,delete it!!
                    dis3 = np.sqrt(np.sum(np.square(np.array([nei1.get_coord()[0], nei1.get_coord()[1]]) -
                                                    np.array([nei2.get_coord()[0], nei2.get_coord()[1]]))))
                    print('dis3 is', dis3, nei1.distance_to(nei2.id), nei2.distance_to(nei1.id))
                    if not(abs(dis3-dis1-dis2) < Collinear or abs(dis1-dis2-dis3) < Collinear or abs(dis2-dis1-dis3)<Collinear):
                        r.add_parents(nei1.id, nei2.id)

                        if nei1.state == 2:
                            r.add_roots(nei1.root1, nei2.id)
                        else:
                            r.add_roots(nei1.id, nei2.root1)

                        r.state = 1


    elif r.state == 1 :
        # print("now get case 1")
        flag0 = True
        for j in range(len(r.myNeighbor)) :
            if not flag0 :
                break
            nei1 = probot[r.myNeighbor[j][0]]
            if nei1.state==2 :
                if nei1.is_child_of_id(r.id) :
                    r.state = 2
                    break
                elif r.has_same_root_but_not_parents(nei1):
                    r.state = 2
                    break
                else:
                    for i in range(len(r.parent1)):
                        p1 = probot[r.parent1[i]]
                        p2 = probot[r.parent2[i]]
                        for k in range(len(p1.myNeighbor)) :
                            if p1.myNeighbor[k][0]==nei1.id :
                                flag0 = False
                                r.state = 2
                                break
                        if flag0 :
                            for k in range(len(p2.myNeighbor)) :
                                if p2.myNeighbor[k][0]==nei1.id :
                                    flag0 = False
                                    r.state = 2
                                    break

            if nei1.state==3 :
                for i in range(len(r.root1)):
                    if nei1.id!=r.root1[i] and nei1.id!=r.root2[i] :
                        p1 = probot[r.parent1[i]]
                        p2 = probot[r.parent2[i]]
                        for k in range(len(p1.myNeighbor)) :
                            if p1.myNeighbor[k][0]==nei1.id :
                                r.state = 2
                                flag0 = False
                                break
                        if flag0:
                            for k in range(len(p2.myNeighbor)) :
                                if p2.myNeighbor[k][0]==nei1.id :
                                    r.state = 2
                                    flag0 = False
                                    break

            if nei1.state==1 and not r.has_same_root(nei1) :
                for query in nei1.query1:
                    if query==r.id :
                        for k in range(len(r.myNeighbor)) :
                            if nei1.is_child_of_id(r.myNeighbor[k][0]) :
                                r.state = 2
                                flag0 = False
                                break
                else:
                    for k in range(len(r.myNeighbor)) :
                        if nei1.is_child_of_id(r.myNeighbor[k][0]):
                            r.query1.append(nei1.id)
                            flag0 = False
                            break

    elif r.state==2:
        # print("now get case 2")
        pass

    elif r.state==3:
        # print("now get case 3")
        pass
