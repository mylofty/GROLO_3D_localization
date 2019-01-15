import math
import numpy as np
from matplotlib import pyplot as plt
from triangle_extension_file import triangle_extension


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
        self.parent1 = -1
        self.parent2 = -1
        self.root1 = -1
        self.root2 = -1
        self.extra = -1
        self.query1 = -1
        self.query2 = -1



    def set_parents(self, p1, p2):
        self.parent1 = p1
        self.parent2 = p2

    def set_beacon(self):
        self.isBeacon = True
        self.z = 0
        self.state = 3
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
        assert not math.isnan(loss)
        if not math.isnan(coord[0]):
            self.set_coord(coord)

    def cal_z(self, robots):
        if self.isBeacon or self.z:
            return self.z
        for nei in self.myNeighbor:
            if robots[nei[0]].z != None:
                d1 = nei[1]
                d2 = self.measured_distance[nei[0]]
                print('calculate_z of robot[{}] using robot[{}], d1 = {}, d2 = {}'.format(self.id, nei[0], d1, d2))
                self.z = (d2**2-d1**2+2*robots[nei[0]].z*self.t-self.t**2)/(2*self.t)
                # print(self.z)
                return self.z

    def cal_2d_distances(self, robots):
        if self.z == None:
            return
        for nei in self.myNeighbor:
            if robots[nei[0]].z != None:
                tmp = (nei[1]**2-(self.z-robots[nei[0]].z)**2)**0.5
                self.d2_distances[nei[0]] = tmp
