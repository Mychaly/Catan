import cv2
import numpy as np
import random

class GameObject:
    def __init__(self, obj_type, x, y):
        self.type = obj_type
        self.x = x
        self.y = y
        self.is_moving = False
        self.target_x = None
        self.target_y = None
        self.image = None

    def move_to_random_location(self, world_width, world_height):
        self.target_x = random.randint(0, world_width - 1)
        self.target_y = random.randint(0, world_height - 1)
        self.is_moving = True

    def update_position(self):
        if self.is_moving:
            if self.x < self.target_x:
                self.x += 1
            elif self.x > self.target_x:
                self.x -= 1

            if self.y < self.target_y:
                self.y += 1
            elif self.y > self.target_y:
                self.y -= 1

            if self.x == self.target_x and self.y == self.target_y:
                self.is_moving = False

class Graphic:
    def __init__(self, graphic_mat, world_width, world_height):
        self.graphic_matrix = graphic_mat
        self.dict_images = {
            'tile_ground': cv2.imread('images/TILES/tile_ground.png'),
            'tile_water': cv2.imread('images/TILES/tile_water.png'),
            'tile_forest': cv2.imread('images/TILES/tile_forest.png'),
            'tile_field': cv2.imread('images/TILES/tile_field.png'),
            'tile_iron_mine': cv2.imread('images/TILES/tile_iron_mine.png'),
            'tile_blocks_mine': cv2.imread('images/TILES/tile_blocks_mine.png'),
            'person': cv2.imread('images/Objects/person.png'),
            'car': cv2.imread('images/Objects/car.png'),
            'truck': cv2.imread('images/Objects/truck.png'),
            'helicopter': cv2.imread('images/Objects/helicopter.png')
        }
        self.world_width = world_width
        self.world_height = world_height
        self.game_objects = self.create_game_objects()
        self.game_matrix = None
        self.total_height = 0
        self.total_width = 0

    def create_game_objects(self):
        game_objects = []

        # Example: Adding people, cars, trucks, and helicopters at random positions
        num_people = 5
        num_cars = 3
        num_trucks = 1
        num_helicopters = 2

        for _ in range(num_people):
            x = random.randint(0, self.world_width - 1)
            y = random.randint(0, self.world_height - 1)
            game_objects.append(GameObject('person', x, y))

        for _ in range(num_cars):
            x = random.randint(0, self.world_width - 1)
            y = random.randint(0, self.world_height - 1)
            game_objects.append(GameObject('car', x, y))

        for _ in range(num_trucks):
            x = random.randint(0, self.world_width - 1)
            y = random.randint(0, self.world_height - 1)
            game_objects.append(GameObject('truck', x, y))

        for _ in range(num_helicopters):
            x = random.randint(0, self.world_width - 1)
            y = random.randint(0, self.world_height - 1)
            game_objects.append(GameObject('helicopter', x, y))

        return game_objects

    def show_matrix(self):
        while True:
            self.update_game_objects()
            self.draw_game()
            cv2.imshow('Game Window', self.game_matrix)

            if cv2.waitKey(100) & 0xFF == ord('q'):  # Press 'q' to exit
                break

        cv2.destroyAllWindows()

    def update_game_objects(self):
        for obj in self.game_objects:
            if not obj.is_moving:
                obj.move_to_random_location(self.world_width, self.world_height)
            obj.update_position()

    def draw_game(self):
        images = self.load_images()
        self.create_display_matrix(images)
        self.draw_lines()

    def load_images(self):
        images = []
        for row in self.graphic_matrix:
            image_row = []
            for cell in row:
                if 'tile_type' in cell:
                    image = self.dict_images[self.dict_images[int(cell['tile_type'])]]
                elif 'type' in cell:
                    image = self.dict_images[cell['type']]
                else:
                    image = np.zeros((50, 50, 3), dtype=np.uint8)  # Placeholder if no type found
                image_row.append(image)
            images.append(image_row)
        return images

    def create_display_matrix(self, images):
        num_rows = len(images)
        num_cols = len(images[0])
        max_height = max(image.shape[0] for row in images for image in row)
        max_width = max(image.shape[1] for row in images for image in row)
        total_height = max_height * num_rows
        total_width = max_width * num_cols
        self.game_matrix = np.zeros((total_height, total_width, 3), dtype=np.uint8)

        for i, row in enumerate(images):
            for j, image in enumerate(row):
                start_h = i * max_height
                start_w = j * max_width
                end_h = start_h + image.shape[0]
                end_w = start_w + image.shape[1]
                self.game_matrix[start_h:end_h, start_w:end_w, :] = image

        self.total_height = total_height
        self.total_width = total_width

    def draw_lines(self):
        for row in range(0, len(self.game_matrix), len(self.game_matrix) // len(self.graphic_matrix)):
            cv2.line(self.game_matrix, (0, row), (self.total_width - 1, row), (255, 255, 255), 1)
            if row % 5 == 0:
                cv2.line(self.game_matrix, (0, row), (self.total_width - 1, row), (255, 0, 0), 3)

        for column in range(0, len(self.game_matrix[0]), len(self.game_matrix[0]) // len(self.graphic_matrix[0])):
            cv2.line(self.game_matrix, (column, 0), (column, self.total_height - 1), (255, 255, 255), 1)
            if column % 5 == 0:
                cv2.line(self.game_matrix, (column, 0), (column, self.total_height - 1), (255, 0, 0), 3)

# Example usage
if __name__ == "__main__":
    graphic_matrix = [
        [{'tile_type': 1}, {'tile_type': 2}, {'tile_type': 3}],
        [{'tile_type': 4}, {'tile_type': 5}, {'tile_type': 6}]
    ]

    # Assuming your world width and height are based on graphic_matrix dimensions
    world_width = len(graphic_matrix[0])
    world_height = len(graphic_matrix)

    graphic = Graphic(graphic_matrix, world_width, world_height)
    graphic.show_matrix()
