import cv2
import numpy as np


class Graphic:

    def __init__(self, graphic_mat):
        self.graphic_matrix = graphic_mat
        self.dict_images = {1: 'tile_ground',
                            2: 'tile_water',
                            3: 'tile_forest',
                            4: 'tile_field',
                            5: 'tile_iron_mine',
                            6: 'tile_blocks_mine'}
        self.game_matrix = None
        self.total_height = 0
        self.total_width = 0

    def show_matrix(self):

        # יצירת מטריצה של ניתובים
        images = []
        for row in self.graphic_matrix:
            image_row = []
            for cell in row:
                # טען את התמונה מקובץ (לדוגמה, image0.jpg, image1.jpg, image2.jpg וכן הלאה)
                image = cv2.imread(f'images/TILES/{self.dict_images[int(cell.tile_type)]}.png')
                image_row.append(image)
            images.append(image_row)

        # יצירת חלונית גרפית עבור התמונות
        window_name = 'Matrix of Images'# שם של החלון
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

        # כיוונון החלונית כדי להציג את כל התמונות במערך
        num_rows = len(images)
        num_cols = len(images[0])
        max_height = max(image.shape[0] for row in images for image in row)
        max_width = max(image.shape[1] for row in images for image in row)
        total_height = max_height * num_rows
        total_width = max_width * num_cols
        display_matrix = np.zeros((total_height, total_width, 3), dtype=np.uint8)

        # הצגת התמונות בחלונית
        for i, row in enumerate(images):
            for j, image in enumerate(row):
                start_h = i * max_height
                start_w = j * max_width
                end_h = start_h + image.shape[0]#גובה של התונה
                end_w = start_w + image.shape[1]
                display_matrix[start_h:end_h, start_w:end_w, :] = image # אתחול של הניתוב

        self.game_matrix = display_matrix
        self.total_height = total_height
        self.total_width = total_width
        self.draw_lines()

        cv2.imshow(window_name, self.game_matrix)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def draw_lines(self):
        for row in range(0, len((self.game_matrix)), len(self.game_matrix) // len(self.graphic_matrix)):
            cv2.line(self.game_matrix, (0, row), (len((self.game_matrix[0])) - 1, row), (255, 255, 255), 1)
            if row % 5 == 0:
                cv2.line(self.game_matrix, (0, row), (len((self.game_matrix[0])) - 1, row), (255, 0, 0), 3)

        for column in range(0, len((self.game_matrix[0])), len(self.game_matrix[0]) // len(self.graphic_matrix[0])):
            cv2.line(self.game_matrix, (column, 0), (column, len((self.game_matrix)) - 1), (255, 255, 255), 1)
            if column % 5 == 0:
                cv2.line(self.game_matrix, (column, 0), (column, len((self.game_matrix)) - 1), (255, 0, 0), 3)