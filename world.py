import json
import numpy as np
from cooordinateObject import CoordinateObject


class World:

    world = None

    def __new__(cls, mat=None):
        if cls.world is None:
            if mat is None:
                raise ValueError("Must provide 'mat' parameter on first instantiation.")
            cls.world = super().__new__(cls)
            cls.world.init_world(mat)
        return cls.world

    def init_world(self, mat):
        self.mat_world = mat  # extended map of tiles
        self.mat_resource = [[[0, 0, 0, 0] for _ in range(len(mat))] for _ in
                             range(len(mat))]  # to do ["Wood", "Wool", "Iron", "Blocks"] # smaal mat of resources
        self.jason_data = open("definitions.json")
        self.data = json.load(self.jason_data)
        self.size_tile: int = self.data['Sizes']['Tile']
        self.arr_resource = self.data['ResourceTypes']
        self.dict_all_object = {}  # contain all the object in the world
        self.people_in_cities =[]

    def build_world(self):
        rows, cols = len(self.mat_world), len(self.mat_world[0])
        new_mat_world = np.empty((rows * self.size_tile[1], cols * self.size_tile[0]), dtype=object)
        for i in range(rows):
            for j in range(cols):
                obj =  {'type':self.mat_world[i][j],'cell':[i, j]}
                new_mat_world[i * self.size_tile[1]:(i + 1) * self.size_tile[1],
                j * self.size_tile[0]:(j + 1) * self.size_tile[0]] = obj
        for i in range(len(new_mat_world)):
            for j in range(len(new_mat_world[0])):
                new_mat_world[i][j]=CoordinateObject(new_mat_world[i][j]['type'],new_mat_world[i][j]['cell'])

        self.mat_world = new_mat_world


