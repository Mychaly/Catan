class ObjectInWorld:
    global_id = 0
    dict_count = {"Road": 0,
                  "Village": 0,
                  "City": 0,
                  "Car": 0,
                  "Truck": 0,
                  "Helicopter": 0,
                  "People": 0
                  }

    def __init__(self, type, start_point=None):
        ObjectInWorld.global_id += 1
        self.id = ObjectInWorld.global_id
        self.type = type
        self.capacity = [0, 0, 0, 0, 0]
        self.start_point = start_point
        ObjectInWorld.dict_count[type] += 1
