
import numpy as np
# from matplotlib import pyplot as plt
from triangle_extension_file_more_parents import triangle_extension


class Robot(object):
    def __init__(self, id):
        self.id = id
        self.isBeacon = False
        self.isFinalPos = False
        self.coord = []  # robot's coord [x, y]
        # self.neighborsCoord = []  # neighbor's coord [x, y]

        self.nei_id = []
        self.myNeighbor = []  # this is construct like [id, distance], it has been sorted, 3D
        # measured_distance is a map,  key is neighbor's id, value is neighbor's distance, it was changed by self.t!!!
        self.measured_distance = {}
        # calculate Z
        self.t = 2           # robot move in Z, up and down ,to calculate pos.z
        self.d2_distances = {}
        self.z = None

        # triangle extension
        self.state = 0
        self.parent1 = []
        self.parent2 = []
        self.root1 = []
        self.root2 = []
        self.query1 = []
        self.query2 = []

    def add_parents(self, p1, p2):
        self.parent1.append(p1)
        self.parent2.append(p2)

    def add_roots(self, r1, r2):
        self.root1.append(r1)
        self.root2.append(r2)

    def is_child_of_id(self, other):
        for p in self.parent1:
            if p==other:
                return True
        for p in self.parent2:
            if p==other:
                return True
        return False

    def has_same_root(self, other):
        for i in range(len(self.root1)):
            for j in range(len(other.root1)):
                if self.root1[i]==other.root1[j] and self.root2[i]==other.root2[j] or \
                    self.root1[i]==other.root2[j] and self.root2[i]==other.root1[j]:
                    return True
        return False

    def has_same_root_but_not_parents(self, other):
        for i in range(len(self.root1)):
            for j in range(len(other.root1)):
                if self.root1[i]==other.root1[j] and self.root2[i]==other.root2[j] or \
                    self.root1[i]==other.root2[j] and self.root2[i]==other.root1[j]:
                    if other.id!=self.parent1[i] and other.id!=self.parent2[i]:
                        return True
        return False

    def set_beacon(self):
        self.isBeacon = True
        self.state = 3
        self.z = 0
        self.root1 = self.root2 = self.id

    def get_coord(self):
        return self.coord

    def set_coord(self, coord):
        self.coord = coord

    def distance_to(self, rid):
        for nei in self.myNeighbor:
            if nei[0]==rid:
                return nei[1]

    def triangle_extension(self, probot):
        triangle_extension(self, probot)

    def run(self, psolver, neighbors, dists):
        if(self.isBeacon == True):
            return
        if neighbors is None or neighbors == []:
            return
        coord, loss = psolver.solver(self.coord, neighbors, dists)
        print('loss is ', loss)
        self.set_coord(coord)

    def cal_z(self, robots):
        if self.isBeacon or self.z:
            return self.z
        for nei in self.myNeighbor:
            if robots[nei[0]].z != None:
                d1 = nei[1]
                d2 = self.measured_distance[nei[0]]
                self.z = (d2**2-d1**2-self.t**2)/(2*self.t) + robots[nei[0]].z # +2*robots[nei[0]].z*self.t
                print('calculate_z of robot[{}] using robot[{}], d1 = {}, d2 = {}, z = {}'
                      .format(self.id, nei[0], d1, d2, self.z))
                return self.z

    def cal_2d_distances(self, robots):
        if self.z == None:
            return
        for nei in self.myNeighbor:
            if robots[nei[0]].z != None:
                tmp = (nei[1]**2-(self.z-robots[nei[0]].z)**2)**0.5
                self.d2_distances[nei[0]] = tmp


