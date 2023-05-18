import math

class PointTriplet:
    pass

class Circle:
    pass

class Line2D:
    pass

class Point2D:
    def __init__(self, x, y, index = -1):
        self.index = index
        self.x = x
        self.y = y

    def __str__(self):
        return "({}, {}, ind = {})".format(self.x, self.y, self.index)
    
    def __eq__(self, another_point):
        return self.x == another_point.x and self.y == another_point.y
    
    def distance(self, another_point):
        return math.sqrt((self.x - another_point.x) ** 2 + (self.y - another_point.y) ** 2)
    
    def inside(self, shape: PointTriplet or Circle):
        if isinstance(shape, PointTriplet):
            pt1 = PointTriplet(self, shape.p1, shape.p2)
            pt2 = PointTriplet(self, shape.p2, shape.p3)
            pt3 = PointTriplet(self, shape.p3, shape.p1)

            return abs(pt1.area() + pt2.area() + pt3.area() - shape.area()) <= 1e-7
        
        elif isinstance(shape, Circle):
            return self.distance(shape.center) - shape.radius <= 1e-7
    
    def project(self, line: Line2D):
        if line.p2.x - line.p1.x == 0:
            return Point2D(line.p1.x, self.y)
        else:
            a = (line.p2.y - line.p1.y) / (line.p2.x - line.p1.x)
            b = line.p1.y - a * line.p1.x
            x = (a * (self.y - b) + self.x) / (a ** 2 + 1)
            y = a * x + b
            return Point2D(x, y)

    def rotate_around(self, center, theta):
        x = self.x - center.x
        y = self.y - center.y
        x_rotated = x * math.cos(theta) - y * math.sin(theta)
        y_rotated = x * math.sin(theta) + y * math.cos(theta)
        x_rotated += center.x
        y_rotated += center.y

        return Point2D(x_rotated, y_rotated, self.index)
    
    def flip_vertically(self):
        return Point2D(200 - self.x, self.y, self.index)
        
class PointTriplet:
    def __init__(self, p1, p2, p3):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
    
    def __str__(self):
        return "Triplet: {}, {}, {}".format(str(self.p1), str(self.p2), str(self.p3))
    
    def __getitem__(self, index):
        if index == 1:
            return self.p1
        elif index == 2:
            return self.p2
        elif index == 3:
            return self.p3
        else:
            return None
        
    def get_orientation(self):
        # Return orientation of the triplet
        # Method:
        #   - Get the sign of the cross product vector of p1p2 and p2p3
        #       . Negative: Counter-clockwise
        #       . Positive: Clockwise
        #       . 0       : Collinear
        tmp = (self.p2.y - self.p1.y) * (self.p3.x - self.p2.x) - (self.p2.x - self.p1.x) * (self.p3.y - self.p2.y)
        if tmp < 0:
            return -1
        elif tmp > 0:
            return 1
        else:
            return 0
    
    def is_aligned(self):
        return self.p2.x <= max(self.p1.x, self.p3.x) and self.p2.x >= min(self.p1.x, self.p3.x) and self.p2.y <= max(self.p1.y, self.p3.y) and self.p2.y >= min(self.p1.y, self.p3.y)

    def area(self):
        a = self.p1.distance(self.p2)
        b = self.p2.distance(self.p3)
        c = self.p3.distance(self.p1)
        
        s = round((a + b + c) / 2, 13)
        if (s < a or s < b or s < c):
            s += 1e-7
        return math.sqrt(s * (s - a) * (s - b) * (s - c))
    
    def get_circumcircle(self):
        edge23 = Line2D(self.p2, self.p3)
        bisector1 = edge23.get_bisector()

        edge31 = Line2D(self.p3, self.p1)
        bisector2 = edge31.get_bisector()
        
        center = bisector1.get_intersection_with(bisector2)
        radius = center.distance(self.p1)

        return Circle(center, radius)

    def get_common_vertices_with(self, another_triplet):
        vertices = [self.p1, self.p2, self.p3, another_triplet.p1, another_triplet.p2, another_triplet.p3]

        tmp = [vertex for vertex in vertices if vertices.count(vertex) == 2]
        
        common_vertices = []
        [common_vertices.append(vertex) for vertex in tmp if vertex not in common_vertices]

        return None if len(common_vertices) < 2 else common_vertices
    
class Point2Ds:
    def __init__(self, lst: list[Point2D]):
        self.lst = lst

    def __str__(self):
        return "Points: [{}]".format(", ".join([str(point) for point in self.lst]))
    
    def get_convex_hull(self):
        tmp = [Point2D(0, 0, 32), 
               Point2D(0, 200, 33), 
               Point2D(200, 200, 34), 
               Point2D(200, 0, 35)]
        
        return Point2Ds(tmp)

    def triangulate(self):
        def is_convex(p1, p2, p3, p4):
            def cross_product(p1, p2, p3):
                x1 = p1.x
                x2 = p2.x
                x3 = p3.x
                y1 = p1.y
                y2 = p2.y
                y3 = p3.y
                
                return (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)
            
            cp1 = cross_product(p1, p2, p3)
            cp2 = cross_product(p2, p3, p4)
            cp3 = cross_product(p3, p4, p1)
            cp4 = cross_product(p4, p1, p2)

            return (cp1 > 0 and cp2 > 0 and cp3 > 0 and cp4 > 0) or (cp1 < 0 and cp2 < 0 and cp3 < 0 and cp4 < 0)
        
        convex_hull = self.get_convex_hull()
        triplets = [PointTriplet(convex_hull.lst[0], convex_hull.lst[1], convex_hull.lst[3]),
                     PointTriplet(convex_hull.lst[3], convex_hull.lst[1], convex_hull.lst[2])]
        
        for point in self.lst:
            for index, triplet in enumerate(triplets):
                if point.inside(triplet):
                    triplets.append(PointTriplet(point, triplet.p1, triplet.p2))
                    triplets.append(PointTriplet(point, triplet.p2, triplet.p3))
                    triplets.append(PointTriplet(point, triplet.p3, triplet.p1))
                    del triplets[index]
                    break
        
        flag = True
        count = 0
        #optimized_triplets = []

        while flag:
            count += 1
            flag = False

            for i in range(len(triplets) - 1):
                for j in range(i + 1, len(triplets)):
                    common_vertices = triplets[i].get_common_vertices_with(triplets[j])

                    if common_vertices:
                        vertices = [triplets[i].p1, triplets[i].p2, triplets[i].p3, triplets[j].p1, triplets[j].p2, triplets[j].p3]

                        remaining_vertices = [vertex for vertex in vertices if vertex not in common_vertices]
                        
                        # print(triplets[i], triplets[j])

                        # for vertex in common_vertices:
                        #     print(vertex)
                        
                        # for vertex in remaining_vertices:
                        #     print(vertex)
                        
                        # if remaining_vertices == []:
                        #     print(i, j)
                        #     print(triplets[i], triplets[j])

                        if is_convex(common_vertices[0], remaining_vertices[0], common_vertices[1], remaining_vertices[1]):
                            #print("Convex")
                            circumcircle = triplets[j].get_circumcircle()

                            tmp = None
                            if triplets[i].p1 in remaining_vertices:
                                tmp = triplets[i].p1

                            elif triplets[i].p2 in remaining_vertices:
                                tmp = triplets[i].p2

                            elif triplets[i].p3 in remaining_vertices:
                                tmp = triplets[i].p3

                            if tmp.inside(circumcircle):
                                flipped_triplet1 = PointTriplet(remaining_vertices[0], remaining_vertices[1], common_vertices[0])
                                flipped_triplet2 = PointTriplet(remaining_vertices[0], remaining_vertices[1], common_vertices[1])
                                triplets[i] = flipped_triplet1
                                triplets[j] = flipped_triplet2

                                flag = True
        #return optimized_triplets
        return triplets

class Circle:
    def __init__(self, p, r):
        self.center = p
        self.radius = r

class Line2D:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def get_bisector(self):
        midpoint = self.get_midpoint()
        if self.p1.x == self.p2.x:
            slope = 0
            y_intercept = midpoint.y
        elif self.p1.y == self.p2.y:
            return Line2D(midpoint, Point2D(midpoint.x, -1))
        else:
            slope = -1 / ((self.p2.y - self.p1.y) / (self.p2.x - self.p1.x))
            y_intercept = midpoint.y - slope * midpoint.x
        return Line2D(midpoint, Point2D(-1, y_intercept))

    def crossed(self, another_line):
        o1 = PointTriplet(self.p1, another_line.p1, self.p2).get_orientation()
        o2 = PointTriplet(self.p1, another_line.p1, another_line.p2).get_orientation()
        o3 = PointTriplet(self.p2, another_line.p2, self.p1).get_orientation()
        o4 = PointTriplet(self.p2, another_line.p2, another_line.p1).get_orientation()

        if o1 != o2 and o3 != o4:
            return True
    
        if o1 == 0 and PointTriplet(self.p1, self.p2, another_line.p1).aligned():
            return True
    
        if o2 == 0 and PointTriplet(self.p1, another_line.p2, another_line.p1).aligned():
            return True
    
        if o3 == 0 and PointTriplet(self.p2, self.p1, another_line.p2).aligned():
            return True
    
        if o4 == 0 and PointTriplet(self.p2, another_line.p1, another_line.p2).aligned():
            return True
    
        return False

    def get_midpoint(self):
        return Point2D((self.p1.x + self.p2.x) / 2, (self.p1.y + self.p2.y) / 2)
    
    def get_intersection_with(self, another_line):
        x1 = self.p1.x
        x2 = self.p2.x
        x3 = another_line.p1.x
        x4 = another_line.p2.x
        y1 = self.p1.y
        y2 = self.p2.y
        y3 = another_line.p1.y
        y4 = another_line.p2.y

        det = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if det == 0:
            return None
        else:
            t1 = x1 * y2 - y1 * x2
            t2 = x3 * y4 - y3 * x4
            x = (t1 * (x3 - x4) - t2 * (x1 - x2)) / det
            y = (t1 * (y3 - y4) - t2 * (y1 - y2)) / det
            return Point2D(x, y)

def is_convex(p1, p2, p3, p4):
    def cross_product(p1, p2, p3):
        x1 = p1.x
        x2 = p2.x
        x3 = p3.x
        y1 = p1.y
        y2 = p2.y
        y3 = p3.y
        
        return (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)
    
    return cross_product(p1, p2, p3) * cross_product(p2, p3, p4) > 0 and cross_product(p2, p3, p4) * cross_product(p3, p4, p1) > 0
