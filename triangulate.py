from utils import *
from config import *

import openpyxl
import json

wb = openpyxl.load_workbook(STANDARD_FACE_LANDMARK_PATH)
standard_face_landmarks = wb['standard']

standard_face_vertices = [Point2D(standard_face_landmarks['A' + str(i + 1)].value,
                                  standard_face_landmarks['B' + str(i + 1)].value,
                                  i) for i in range(NUM_FACE_LANDMARKS - 4)]

standard_face_vertices = Point2Ds(standard_face_vertices)
standard_triplets = standard_face_vertices.triangulate()

standard_index_triplets = [[triplet[1].index, triplet[2].index, triplet[3].index] for triplet in standard_triplets]

with open(STANDARD_INDEX_TRIPLETS_PATH, 'w') as f:
    json.dump(standard_index_triplets, f)



