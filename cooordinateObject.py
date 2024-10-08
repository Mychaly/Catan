class CoordinateObject:
    global_id = 0#re
    def __init__(self, tile_type, resources_coordinates):
        CoordinateObject.global_id+=1
        self.id=CoordinateObject.global_id
        self.resources_coordinates = resources_coordinates
        self.tile_type = tile_type
        self.road_id = 0
        self.settlement_id = 0  # village,city
        self.vehicle_id = 0 # car,truck,helicopter
        self.people_id = 0
