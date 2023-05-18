import numpy as np
import math

import cv2
import PIL.Image as Image
import matplotlib.pyplot as plt

import openpyxl
import json

from threading import Thread
from multiprocessing import Process, Manager
import time

from config import *
from utils import *


wb = openpyxl.load_workbook(FACE_LANDMARKS_PATH)

faces_vertices = []
for index in wb.sheetnames:
    face_landmarks = wb[index]
    face_vertices = [Point2D(face_landmarks['A' + str(i + 1)].value, face_landmarks['B' + str(i + 1)].value, i) for i in range(NUM_FACE_LANDMARKS)]
    faces_vertices.append(face_vertices)

with open(STANDARD_INDEX_TRIPLETS_PATH, 'r') as f:
    standard_index_triplets = json.load(f)

faces_triplets = []
for face_vertices in faces_vertices:
    ps = Point2Ds(face_vertices)
    face_triplets = []

    for indices in standard_index_triplets:
        points = []
        for index in indices:
            for point in ps.lst:
                if point.index == index:
                    points.append(point)
                    break

        face_triplets.append(
            PointTriplet(
                points[0].rotate_around(Point2D(100, 100), math.pi).flip_vertically(),
                points[1].rotate_around(Point2D(100, 100), math.pi).flip_vertically(),
                points[2].rotate_around(Point2D(100, 100), math.pi).flip_vertically()
            )
        )

    faces_triplets.append(face_triplets)

fig, axes = plt.subplots(1, 4)

for i, face_triplets in enumerate(faces_triplets):
    for triplet in face_triplets:
        axes[i].plot([triplet.p1.x, triplet.p2.x], [triplet.p1.y, triplet.p2.y])
        axes[i].plot([triplet.p2.x, triplet.p3.x], [triplet.p2.y, triplet.p3.y])
        axes[i].plot([triplet.p3.x, triplet.p1.x], [triplet.p3.y, triplet.p1.y])

plt.show()

def get_transformation_matrix(triplet1, triplet2):
    y = [[triplet2.p1.x, triplet2.p2.x, triplet2.p3.x],
         [triplet2.p1.y, triplet2.p2.y, triplet2.p3.y],
         [1, 1, 1]]
    
    x = [[triplet1.p1.x, triplet1.p2.x, triplet1.p3.x],
         [triplet1.p1.y, triplet1.p2.y, triplet1.p3.y],
         [1, 1, 1]]

    y = np.array(y)
    x = np.array(x)

    t = np.matmul(y, np.linalg.inv(x))
    return t

def normalize(c):
    c = np.where(c < 0, 0, c)
    c = np.where(c > 199, 199, c)
    
    return c.astype(int)

def region_warp(start_img, end_img, intermediate_triplets, transformation_matrices, r, start_of_region):
    region = np.zeros((200, 200))

    tms = np.zeros((200, 200, 3, 3))
    ips = np.zeros((200, 200, 3, 1))
    for i in range(200):
        for j in range(200):
            for k, triplet in enumerate(intermediate_triplets):
                if Point2D(i + start_of_region, j).inside(triplet):
                    tms[i, j] = transformation_matrices[k]
                    ips[i, j] = np.array([[i + start_of_region], [j], [1]])
    
    sps = np.matmul(np.linalg.inv(np.identity(3) + r * (tms.reshape(40000, 3, 3) - np.identity(3))).reshape(200, 200, 3, 3), ips)
    eps = np.matmul(tms, sps)

    sx = normalize(sps[:, :, 0, 0])
    sy = normalize(sps[:, :, 1, 0])
    ex = normalize(eps[:, :, 0, 0])
    ey = normalize(eps[:, :, 1, 0])

    region = (1 - r) * start_img[sx, sy] + r * end_img[ex, ey]
            
    return region

class RegionWarpThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.args = args
        self.kwargs = kwargs
        self.result = None

    def run(self):
        self.result = region_warp(*self.args, **self.kwargs)

def get_transition_frames(start_img, end_img, start_triplets, end_triplets, num_frame):
    frames = []
    for frame_no in range(num_frame):
        print("At frame number: ", frame_no)
        if frame_no == 0:
            continue
        
        r = frame_no / num_frame
        transformation_matrices = [get_transformation_matrix(start_triplets[i], end_triplets[i]) for i in range(len(start_triplets))]

        intermediate_triplets = []
        for i in range(len(start_triplets)):
            tm = transformation_matrices[i]
            
            st = start_triplets[i]
            indices = [st.p1.index, st.p2.index, st.p3.index]
            st = np.array([[st.p1.x, st.p2.x, st.p3.x],
                           [st.p1.y, st.p2.y, st.p3.y],
                           [1, 1, 1]])
            
            
            it = (1 - r) * st + r * np.matmul(tm, st)
            it = PointTriplet(Point2D(it[0][0], it[1][0], indices[0]),
                              Point2D(it[0][1], it[1][1], indices[1]),
                              Point2D(it[0][2], it[1][2], indices[2]))
            intermediate_triplets.append(it)
        
        # region_workers = []
        # for region_no in range(1):
        #     region_workers.append(RegionWarpThread(start_img, end_img, intermediate_triplets, transformation_matrices, r, region_no * 200))
        # for region_worker in region_workers:
        #     region_worker.start()
        
        # for region_worker in region_workers:
        #     region_worker.join()

        # frame = np.vstack([worker.result for worker in region_workers])

        frame = region_warp(start_img, end_img, intermediate_triplets, transformation_matrices, r, 0)

        frames.append(frame)
    frames = [start_img for _ in range(1)] + frames + [end_img for _ in range(1)]
    return frames

class GetTransitionFramesThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.args = args
        self.kwargs = kwargs
        self.result = None

    def run(self):
        self.result = get_transition_frames(*self.args, **self.kwargs)

class GetTransitionFramesProcess(Process):
    def __init__(self, transtion_frames, *args, **kwargs):
        super().__init__()
        self.args = args
        self.kwargs = kwargs

        self.transition_frames = transition_frames

    def run(self):
        pass

faces = [cv2.imread(DATA_PATH + "{}.png".format(i + 1), cv2.IMREAD_GRAYSCALE) for i in range(NUM_FACES)]
transition_chain = [face for face in faces] + [faces[0]]
triplets_chain = [face_triplets for face_triplets in faces_triplets] + [faces_triplets[0]]

start_timer = time.time()
transition_workers = []
for i in range(len(transition_chain) - 1):
    transition_workers.append(GetTransitionFramesThread(transition_chain[i], transition_chain[i + 1], triplets_chain[i], triplets_chain[i + 1], 3))

for worker in transition_workers:
    worker.start()

for worker in transition_workers:
    worker.join()

transition_frames = []
for worker in transition_workers:
    transition_frames += worker.result

end_timer = time.time()
print("Execution time: ", end_timer - start_timer)

transition_gif = [Image.fromarray(frame) for frame in transition_frames]

transition_gif[0].save(RESULT_PATH + 'result1.gif', format = 'GIF', append_images = transition_gif[1:], save_all = True, duration = 300, loop = 0)


    