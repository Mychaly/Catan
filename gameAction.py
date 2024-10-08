import json
import json
from typing import List
from command import Command
from object_in_world import ObjectInWorld
from world import World


class GameAction:
    def __init__(self):
        self.world = World()
        self.last_select = [0, 0]  # the las selected tile
        # self.current_work = None  # [0][1]who work now # can be changed to list...
        # self.mount_rain = 0
        # self.place_to_rane = None
        self.complete = []
        self.place_to_grow = []
        self.total_points = 0

        self.command_map = {
            Command.SELECT: self.select,
            Command.MOVE: self.move,
            Command.WORK: self.work,
            Command.DEPOSIT: self.deposit,
            Command.TAKE_RESOURCES: self.take_resources,
            Command.BUILD: self.build,
            Command.MANUFACTURE: self.manufacture,
            Command.PEOPLE: self.people,
            Command.RESOURCE: self.resource,
            Command.RESOURCES: self.resources,
            Command.MAKE_EMPTY: self.make_empty,
            Command.RAIN: self.rain,
            Command.ROBBER: self.robber,
            Command.MAKE_ROBBER: self.make_robber,
            Command.WAIT: self.wait,
            Command.SET_POINTS: self.set_points,
        }

    def select_category(self):
        current_obj = self.world.mat_world[int(self.last_select[1]) - 1, int(self.last_select[0]) - 1]

        if current_obj.people_id != 0:
            print("SelectedCategory People")
        elif current_obj.road_id != 0:
            print("SelectedCategory Road")
        elif current_obj.settlement_id != 0:
            settlement_type = self.world.dict_all_object[current_obj.settlement_id].type
            print("SelectedCategory ", settlement_type)
        else:
            num_type = self.world.mat_world[int(self.last_select[1]) - 1, int(self.last_select[0]) - 1].tile_type
            category = self.number_to_name_tile(num_type)
            print("SelectedCategory " + category)

    def select_resource(self):

        current_obj = self.world.mat_world[self.last_select[1] - 1, self.last_select[0] - 1]
        cord_x, cord_y = current_obj.resources_coordinates  # find the resource coordinate
        resources = self.world.mat_resource[cord_x][cord_y]  # get the rosource of tile
        if current_obj.people_id != 0 and self.world.dict_all_object[current_obj.people_id].capacity[:4] != [0, 0, 0,
                                                                                                             0]:  # if the selected cell is people
            resources = self.world.dict_all_object[current_obj.people_id].capacity
        elif current_obj.vehicle_id != 0:  # if the selscted cell is vehicle
            resources = self.world.dict_all_object[current_obj.vehicle_id].capacity[:-1]
        elif current_obj.settlement_id != 0:  # if the selected cell is settlement
            resources = self.world.dict_all_object[current_obj.settlement_id].capacity[:-1]
        print("SelectedResource", resources[0], resources[1], resources[2], resources[3], sep=" ")

    ###################################
    # the function that are in the dict
    def select(self, argument):
        self.last_select[0] = int(argument[0])
        self.last_select[1] = int(argument[1])

    def add_resource(self, obj_id, index_resource, amount):

        capacity_dict = self.world.data["Capacities"]
        max_capacity = capacity_dict[self.world.dict_all_object[obj_id].type][index_resource]
        current_capacity = self.world.dict_all_object[obj_id].capacity[index_resource]
        if amount + current_capacity < max_capacity:
            self.world.dict_all_object[obj_id].capacity[index_resource] += amount
        else:
            self.world.dict_all_object[obj_id].capacity[index_resource] = max_capacity

    def resource(self, arguments):
        # ['1', 'Wood', '1', '1']
        amount = int(arguments[0])
        resource_type = arguments[1]

        # find the resource coordinate
        cord_x, cord_y = self.world.mat_world[int(arguments[3]) - 1, int(arguments[2]) - 1].resources_coordinates
        index_resource = self.world.arr_resource.index(resource_type)  # index resource in arr json

        obj_cell = self.world.mat_world[int(arguments[3]) - 1][int(arguments[2]) - 1]  # find the current object

        # add resource:
        if obj_cell.people_id != 0:  # to person
            self.world.dict_all_object[obj_cell.people_id].capacity[index_resource] += amount
        elif obj_cell.vehicle_id != 0:  # to vehicle
            self.add_resource(obj_cell.vehicle_id, index_resource, amount)
        elif obj_cell.settlement_id != 0:  # to settlement
            self.add_resource(obj_cell.settlement_id, index_resource, amount)
        else:  # to tile
            if amount == 0 and resource_type in ['Wood', 'Wool']:  # make tile ready to rain
                self.place_to_grow.append([cord_x, cord_y, index_resource, resource_type])
            self.world.mat_resource[cord_x][cord_y][index_resource] += amount  # add resource

    def number_to_name_tile(self, number):
        tiles_dic = self.world.data['Tiles']
        for key, value in tiles_dic.items():
            if int(value) == int(number):
                return key

    def get_destination_point(self, point_x, point_y, obj_size):
        # The function checks whether the target point is empty, otherwise returns an alternative point
        if self.world.mat_world[point_x][point_y].vehicle_id != 0:
            return self.world.dict_all_object[self.world.mat_world[point_x][point_y].vehicle_id].start_point[
                       1] - obj_size
        if self.world.mat_world[point_x][point_y].people_id != 0:
            return point_y - obj_size
        return point_y

    def move_vehicle(self, i_mat, j_mat):
        last_selected = self.world.mat_world[self.last_select[1] - 1][self.last_select[0] - 1]
        selected_obj = self.world.dict_all_object[last_selected.vehicle_id]
        size_obj = self.world.data['Sizes'][selected_obj.type][0]
        j_mat_world = self.get_destination_point(i_mat, j_mat, size_obj)  # get the destination point
        i_mat_world = i_mat
        start_i = selected_obj.start_point[0]
        start_j = selected_obj.start_point[1]
        for i in range(start_i, start_i + size_obj):  # remove the vehicle from the last place
            for j in range(start_j, start_j + size_obj):
                self.world.mat_world[i][j].vehicle_id = 0
        selected_obj.start_point = [i_mat_world, j_mat_world]
        for i in range(i_mat_world, i_mat_world + size_obj):  # put the vehicle on the new place
            for j in range(j_mat_world, j_mat_world + size_obj):
                self.world.mat_world[i][j].vehicle_id = selected_obj.id
        self.last_select = [j_mat_world + 1, i_mat_world + 1]

    def move_person(self, i_mat, j_mat):
        last_selected = self.world.mat_world[self.last_select[1] - 1][
            self.last_select[0] - 1]  # get the last selected cell
        size_obj = self.world.data['Sizes']['People'][0]
        j_mat_world = self.get_destination_point(i_mat, j_mat, size_obj)  # get the destination point
        i_mat_world = i_mat
        self.world.mat_world[i_mat_world][
            j_mat_world].people_id = last_selected.people_id  # put the people on the new place
        last_selected.people_id = 0  # remove the person from the last place
        if self.world.mat_world[i_mat_world][j_mat_world].settlement_id != 0:
            self.world.dict_all_object[self.world.mat_world[i_mat_world][j_mat_world].settlement_id].capacity[-1] += 1
        self.last_select = [j_mat_world + 1, i_mat_world + 1]

    def move(self, arguments):

        i_mat_world = int(arguments[1]) - 1
        j_mat_world = int(arguments[0]) - 1
        tile_name = self.number_to_name_tile(self.world.mat_world[i_mat_world][j_mat_world].tile_type)
        # if the tile type is water so return
        if tile_name == "Water":
            return
        last_selected = self.world.mat_world[self.last_select[1] - 1][self.last_select[0] - 1]
        #  move vehicle
        if last_selected.vehicle_id != 0:
            self.move_vehicle(i_mat_world, j_mat_world)
        # move people
        else:
            self.move_person(i_mat_world, j_mat_world)

    def work(self, arguments):

        i_mat_world = int(arguments[1]) - 1
        j_mat_world = int(arguments[0]) - 1
        # take the selected person from its place
        selected_person = self.world.mat_world[self.last_select[1] - 1][self.last_select[0] - 1]
        worker_id = selected_person.people_id
        selected_person.people_id = 0
        # put the person in the new place
        self.world.mat_world[i_mat_world][j_mat_world].people_id = worker_id
        i_mat_resource, j_mat_resource = self.world.mat_world[i_mat_world][j_mat_world].resources_coordinates

        # change the capacity of person
        self.world.dict_all_object[self.world.mat_world[i_mat_world][j_mat_world].people_id].capacity = \
        self.world.mat_resource[i_mat_resource][j_mat_resource]

        # after the person finish to work
        self.world.mat_resource[i_mat_resource][j_mat_resource] = [0, 0, 0, 0]

        # change the last select to the new place of the person
        self.last_select = [int(arguments[0]), int(arguments[1])]

    def deposit(self, arguments):
        cord_i = int(arguments[1]) - 1
        cord_j = int(arguments[0]) - 1
        last_selected = self.world.mat_world[self.last_select[1] - 1][self.last_select[0] - 1]
        destination = self.world.mat_world[cord_i][cord_j]
        src_resource = dest_resource = max_capacity = None
        #  source capacity
        if last_selected.vehicle_id != 0:
            src_resource = self.world.dict_all_object[last_selected.vehicle_id].capacity
        elif last_selected.settlement_id != 0:
            src_resource = self.world.dict_all_object[last_selected.settlement_id].capacity
        else:
            i, j = last_selected.resources_coordinates
            src_resource = self.world.mat_resource[i][j]
        #  destination capacity:
        if destination.vehicle_id != 0:  # vehicle
            dest_resource = self.world.dict_all_object[destination.vehicle_id].capacity
            max_capacity = self.world.data['Capacities'][self.world.dict_all_object[destination.vehicle_id].type]

        else:  # settlement
            dest_resource = self.world.dict_all_object[destination.settlement_id].capacity
            max_capacity = self.world.data['Capacities'][self.world.dict_all_object[destination.settlement_id].type]

        # take the resources from the source capacity and put the in the dest capacity
        for i in range(len(src_resource) - 1):
            max_amount = max_capacity[i] - dest_resource[i]
            amount_to_take = max_amount if int(src_resource[i]) > int(max_amount) else src_resource[i]
            src_resource[i] = int(src_resource[i]) - int(amount_to_take)  # take resource
            dest_resource[i] = int(dest_resource[i]) + int(amount_to_take)  # add resource

    def take_resources(self, arguments):
        # self.move(arguments,world)

        cord_i = int(arguments[1]) - 1
        cord_j = int(arguments[0]) - 1
        src_cell = self.world.mat_world[cord_i][cord_j]
        src_resource = self.world.dict_all_object[src_cell.settlement_id].capacity  # source

        dest_cell = self.world.mat_world[self.last_select[1] - 1][self.last_select[0] - 1]
        dest_resource = self.world.dict_all_object[dest_cell.vehicle_id].capacity  # destination
        vehicle_type = self.world.dict_all_object[dest_cell.vehicle_id].type

        max_capacity = self.world.data['Capacities'][vehicle_type]

        # take the resources from the source capacity and put the in the dest capacity
        for i in range(len(src_resource) - 1):
            max_amount = int(max_capacity[i]) - int(dest_resource[i])
            amount_to_take = max_amount if int(src_resource[i]) > int(max_amount) else src_resource[i]
            src_resource[i] = int(src_resource[i]) - int(amount_to_take)  # take resource
            dest_resource[i] = int(dest_resource[i]) + int(amount_to_take)  # add resource

    def build(self, arguments):
        obj_to_buid = arguments[0]
        cord_i = int(arguments[2]) - 1
        cord_j = int(arguments[1]) - 1
        command_type = arguments[-1]
        obj_size = self.world.data["Sizes"][obj_to_buid]
        # check if the place to build on is ground
        for i in range(cord_i, cord_i + int(obj_size[0])):
            for j in range(cord_j, cord_j + int(obj_size[1])):
                if self.world.mat_world[cord_i][cord_j].tile_type != "1":
                    return
        if command_type == "input" and obj_to_buid in ['Village', 'City'] and self.is_attached_road(obj_size[0],cord_i,cord_j) == False:
            return
        else:
            if obj_to_buid in ['Village', 'City']:
                if obj_to_buid == 'City':
                    self.set_points([2])
                else:
                    self.set_points([1])
                build = ObjectInWorld(obj_to_buid, [cord_i, cord_j])
                self.world.dict_all_object[build.id] = build
                for i in range(cord_i, cord_i + obj_size[0]):
                    for j in range(cord_j, cord_j + obj_size[1]):
                        self.world.mat_world[i][j].settlement_id = build.id

            else:
                build = ObjectInWorld(obj_to_buid)
                self.world.dict_all_object[build.id] = build
                for i in range(cord_i, cord_i + obj_size[0]):
                    for j in range(cord_j, cord_j + obj_size[1]):
                        self.world.mat_world[i][j].road_id = build.id


    def is_attached_road(self, size, i, j):
        road_size = int(self.world.data["Sizes"]["Road"][0])
        if i > 0:
            for index in range(j + road_size - 1, j + size - road_size + 1):
                if self.world.mat_world[i - 1][index].road_id != 0:
                    return True
        if i < len(self.world.mat_world) - 1:
            for index in range(j + road_size - 1, j + size - road_size + 1):
                if self.world.mat_world[i + 1][index].road_id != 0:
                    return True
        if j > 0:
            for index in range(i + road_size - 1, i + size - road_size + 1):
                if self.world.mat_world[index][j - 1].road_id != 0:
                    return True
        if j < len(self.world.mat_world) - 1:
            for index in range(i + road_size - 1, i + size - road_size + 1):
                if self.world.mat_world[index][j + 1].road_id != 0:
                    return True
        return False

    def manufacture(self, arguments):  # create vehicle
        command_type = arguments[-1]
        vehicle_type = arguments[0]
        cord_i, cord_j = int(arguments[2]) - 1, int(arguments[1]) - 1
        cell = self.world.mat_world[cord_i][cord_j]
        size_vehicle = self.world.data['Sizes'][vehicle_type]

        # check if tile_type is valid
        for i in range(cord_i, cord_i + size_vehicle[0]):
            for j in range(cord_j, cord_j + size_vehicle[0]):
                if self.world.mat_world[i][j].tile_type != '1':  # is ground
                    return

        if command_type == 'input':
            necessary_resource = self.world.data['Costs'][vehicle_type]
            existing_resource = self.world.dict_all_object[cell.settlement_id].capacity

            # if there are not enough resources for creating vehicle
            if not all(int(x) <= int(y) for x, y in zip(necessary_resource,existing_resource)):
                return
            # decrease the resources
            self.world.dict_all_object[cell.settlement_id].capacity = [int(x) - int(y) for x, y in zip(existing_resource, necessary_resource)]


        # create the specific vehicle
        new_vehicle = ObjectInWorld(vehicle_type, [cord_i, cord_j])
        self.world.dict_all_object[new_vehicle.id] = new_vehicle

        # update the cell to point the object
        for i in range(cord_i, cord_i + size_vehicle[0]):
            for j in range(cord_j, cord_j + size_vehicle[0]):
                self.world.mat_world[i][j].vehicle_id = new_vehicle.id

    def people(self, arguments ):

        i_mat_world = int(arguments[2]) - 1
        j_mat_world = int(arguments[1]) - 1
        amount = int(arguments[0])
        obj_cell = self.world.mat_world[i_mat_world][j_mat_world]
        index_resource_people = self.world.arr_resource.index("People")  # index of people in arr json

        # add people to settlement
        if int(obj_cell.settlement_id) != 0:
            capacity_dict = self.world.data["Capacities"]
            max_capacity = capacity_dict[self.world.dict_all_object[obj_cell.settlement_id].type][index_resource_people]
            current_capacity = self.world.dict_all_object[obj_cell.settlement_id].capacity[index_resource_people]
            if current_capacity + amount > max_capacity:
                amount = max_capacity - current_capacity
            self.world.dict_all_object[obj_cell.settlement_id].capacity[index_resource_people] += amount  # add people
            for _ in range(amount):
                new_people = ObjectInWorld("People")
                self.world.people_in_cities.append(new_people)

        else:
            new_people = ObjectInWorld("People", [i_mat_world, j_mat_world])
            self.world.mat_world[i_mat_world][j_mat_world].people_id = new_people.id
            self.world.dict_all_object[new_people.id] = new_people

    def resources(self, arguments):
        cord_i, cord_j = int(arguments[5]) - 1, int(arguments[4]) - 1
        resources = arguments[:4]
        cell = self.world.mat_world[cord_i][cord_j]
        if int(cell.vehicle_id) != 0:
            self.world.dict_all_object[cell.vehicle_id].capacity = resources + [
                self.world.dict_all_object[cell.vehicle_id].capacity[-2]]
        elif int(cell.settlement_id) != 0:
            self.world.dict_all_object[cell.settlement_id].capacity = resources + [
                self.world.dict_all_object[cell.settlement_id].capacity[-2]]
        else:
            self.world.mat_resource[cell.resources_coordinates[0]][cell.resources_coordinates[1]] = resources

    def make_empty(self, arguments ):
        # Add logic for make empty
        pass

    def rain(self, arguments):
        # go over the places if the rain amount enough - grow
        while self.place_to_grow:
            place = self.place_to_grow.pop()
            if int(arguments[0]) >= int(self.world.data["Rains"][place[3]]):
                self.world.mat_resource[place[0]][place[1]][place[2]] = 1

    def set_points(self, arguments):
        new_point = self.total_points + int(arguments[0])
        self.total_points = new_point if new_point <= 100 else 100

    def robber(self, arguments):
        # Add logic for robber
        pass

    def make_robber(self, arguments):
        # Add logic for make robber
        pass

    def wait(self, argument):
        pass

    def village_count(self):
        print("VillageCount ", ObjectInWorld.dict_count['Village'])

    def city_count(self):
        print("CityCount ", ObjectInWorld.dict_count['City'])

    def car_count(self):
        print("CarCount ", ObjectInWorld.dict_count['Car'])

    def truck_count(self):
        print("TruckCount ", ObjectInWorld.dict_count['Truck'])

    def helicopter_count(self):
        print("HelicopterCount ", ObjectInWorld.dict_count['Helicopter'])

    def road_count(self):
        print("RoadCount ", ObjectInWorld.dict_count['Road'])

    def select_people(self):
        current_tile = self.world.mat_world[self.last_select[1] - 1][self.last_select[0] - 1]
        if current_tile.settlement_id != 0:
            print('SelectedPeople', self.world.dict_all_object[current_tile.settlement_id].capacity[-1])
        elif current_tile.people_id != 0:
            print('SelectedPeople', 1)
        else:
            print('SelectedPeople', 0)

    def select_car(self):
        current_tile = self.world.mat_world[self.last_select[1] - 1][self.last_select[0] - 1]
        if current_tile.vehicle_id != '0' and self.world.dict_all_object[current_tile.vehicle_id].type == 'Car':
            print('SelectedCar', 1)
        else:
            print('SelectedCar', 0)

    def select_truck(self):
        current_tile = self.world.mat_world[self.last_select[1] - 1][self.last_select[0] - 1]
        if current_tile.vehicle_id != '0' and self.world.dict_all_object[current_tile.vehicle_id].type == 'Truck':
            print('SelectedTruck', 1)
        else:
            print('SelectedTruck', 0)

    def select_helicopter(self):
        current_tile = self.world.mat_world[self.last_select[1] - 1][self.last_select[0] - 1]
        if current_tile.vehicle_id != '0' and self.world.dict_all_object[current_tile.vehicle_id].type == 'Helicopter':
            print('SelectedHelicopter', 1)
        else:
            print('SelectedHelicopter', 0)

    def select_complete(self):
        print("SelectedComplete", False)

    def selected_coordinates(self):
        print('SelectedCoordinates', self.last_select[0], self.last_select[1])
        # selected_tile = world.mat_world[self.last_select[1] - 1][self.last_select[0] - 1].resources_coordinates
        # print('SelectedCoordinates',selected_tile[1],selected_tile[0])

    def points(self):
        print('Points', self.total_points)

    def execute_command(self, command: Command):
        if command.name in self.command_map:
            func = self.command_map[command.name]
            return func(command.arguments)
        else:
            raise ValueError(f"Unknown command: {command.name}")

    def execute_asserts(self, one_assert):
        case = one_assert
        switcher = {
            'SelectedResource': self.select_resource,
            'SelectedCategory': self.select_category,
            'SelectedPeople': self.select_people,
            'SelectedCar': self.select_car,
            'SelectedTruck': self.select_truck,
            'SelectedHelicopter': self.select_helicopter,
            'SelectedComplete': self.select_complete,
            'SelectedCoordinates': self.selected_coordinates,
            'VillageCount': self.village_count,
            'CityCount': self.city_count,
            'RoadCount': self.road_count,
            'CarCount': self.car_count,
            'TruckCount': self.truck_count,
            'HelicopterCount': self.helicopter_count,
            'Points': self.points,

        }
        switcher.get(case, "unKnown assert")()
