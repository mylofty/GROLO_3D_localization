# _*_ coding=utf-8 _*_
from robotClass import *
from scipy.optimize import fsolve
import os
import math
from D3_TE import from_3D_to_2D
from config import *
from GridentDescentPy import PositionSolver
import tensorflow as tf
from dv_distance_file import dv_distance
robot_Num = 0
beacon_Num = 0

def cmp_by_value(lhs):
    return lhs[1]


def create_network_topology():
    '''
    load the random nodes, create the robots object, assign  Isbeacon,
    robots can not get the points' information. just for compare in picture!
    :return:
    '''
    global beacon_Num
    global robot_Num
    beaconlist = np.loadtxt(os.path.join(folder, beacon_node_filename))
    points = np.loadtxt(os.path.join(folder, random_node_filename))
    robot_Num = points.shape[0]

    robots = [Robot(id=x) for x in range(robot_Num)]
    Beacon = np.array((beaconlist[0:len(beaconlist) - 1]), dtype=int)
    beacon_Num = len(beaconlist) - 1
    communication_distance = beaconlist[-1]
    for index in Beacon:
        robots[index].set_beacon()
    for i in range(robot_Num):
        for j in range(i+1, robot_Num):
            np.random.seed(12345)
            tempDistance = np.sqrt( (points[i][0] - points[j][0])**2 + (points[i][1] - points[j][1])**2
                                    + (points[i][2] - points[j][2])**2)
            # tempDistance = tempDistance + tempDistance * (np.random.random() * 0.02 - 0.01)  # 是否加噪声
            if tempDistance < communication_distance:
                robots[i].myNeighbor.append([j, tempDistance])
                robots[j].myNeighbor.append([i, tempDistance])
    for r in robots:
        r.myNeighbor = sorted(r.myNeighbor, key=cmp_by_value)

        r.nei_id = []
        for nei in r.myNeighbor:
            rid = r.id
            nid = nei[0]
            r.nei_id.append(nid)
            r.measured_distance[nid] = np.sqrt((points[rid][0]-points[nid][0])**2 +
                    (points[rid][1]-points[nid][1])**2 +
                    (points[rid][2]+r.t-points[nid][2])**2 )
    return points, robots


def setInitial_by_dvdistance(robots):
    '''
    assign every robot the initial position by dv-distance
    :param robots:
    :return:
    '''
    # you can also use initPos.py dv_distance() to create the dv_list
    coordlist = dv_distance()
    dv_list = np.loadtxt(os.path.join(folder, dv_distance_result))
    for index in range(len(dv_list)):
        robots[index].set_coord([dv_list[index][0], dv_list[index][1]])
        print('robot[{}] '.format(index), dv_list[index])



def localization_gradient_descent(robots, psolver, epochs=2):
    robot_num = len(robots)
    for epoch in range(epochs+1):
        print("epoch %d:------------------------------------------------" % epoch)
        for rid in range(robot_num):
            nei_dis = [value for value in robots[rid].d2_distances.values()]
            nei_pos = [robots[key].get_coord() for key in robots[rid].d2_distances.keys()]
            print('localization_ontime robot', rid)
            robots[rid].run(psolver, neighbors=nei_pos, dists=nei_dis)
            print("robots[%d].coord: " % rid, robots[rid].get_coord())
    # write to file gradient_descent_result.npy
    gd_list = []
    for r in robots:
        print('r[{}].get_coord()= {}, r.z ={}'.format(r.id, r.get_coord(), r.z), type(r.get_coord()), type(r.z))
        print('r[{}] coord is {}'.format(r.id, list(r.get_coord())+[r.z]))
        gd_list.append(np.array(list(r.get_coord())+[r.z]))
    np.savetxt(os.path.join(folder, gradient_descent_result), gd_list)



def localizatiion_GROLO(robots, localization_Nodes):
    cal_nodes = 0
    for index in range(len(robots)):
        if robots[index].isBeacon == False:
            robots[index].isFinalPos = False
        else:
            robots[index].isFinalPos = True
    print('real_position: localizationNodes is ', localization_Nodes)
    while cal_nodes < localization_Nodes:
        for index in range(len(robots)):
            if robots[index].isBeacon == True:
                continue
            if robots[index].isFinalPos == True:
                continue
            print('index %d come to calculate, cal_nodes is %d  '% (index, cal_nodes))
            p1 = robots[index].parent1
            p2 = robots[index].parent2
            if(p1 != -1 and p2 != -1 and robots[p1].isFinalPos == True and robots[p2].isFinalPos == True):
                ix, iy = robots[index].get_coord()
                p1x, p1y = robots[p1].get_coord()
                p2x, p2y = robots[p2].get_coord()
                dis1 = robots[index].d2_distances[p1]
                dis2 = robots[index].d2_distances[p2]
                def my_solve(paramter):
                    x, y = paramter[0], paramter[1]
                    return [
                        (x - p1x) ** 2 + (y - p1y) ** 2 - dis1 ** 2,
                        (x - p2x) ** 2 + (y - p2y) ** 2 - dis2 ** 2]
                sol = np.real(fsolve(my_solve, np.array([ix, iy]), xtol=1e-3))
                print('fsolve index ',index,sol)
                robots[index].set_coord([sol[0], sol[1]])
                robots[index].isFinalPos = True
                cal_nodes = cal_nodes + 1
    # write to file GROLO_result.npy
    grolo_list = []
    for r in robots:
        grolo_list.append(np.array(list(r.get_coord())+[r.z]))
    np.savetxt(os.path.join(folder, GROLO_result), grolo_list)


def main():
    sess = tf.Session()
    psolver = PositionSolver(sess, 50, 0.02)
    points, robots = create_network_topology()
    setInitial_by_dvdistance(robots)
    parentList, distanceList, zList, flexiblecount = from_3D_to_2D(robots)
    for index in range(len(points)):
        print('robot[{}] real_z : estimate_z : {} - {} = {}'.format(index, points[index][2], zList[index], points[index][2]- zList[index]))
    localization_gradient_descent(robots, psolver,  epochs=15)
    localizatiion_GROLO(robots, robot_Num - flexiblecount - beacon_Num)


if __name__ == '__main__':
    main()






