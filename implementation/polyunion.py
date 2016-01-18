from shapely.geometry import Polygon
from itertools import combinations
import random


def get_top(polys):
    shapes = []
    for i in range(len(polys)):
        shapes.append((Polygon(polys[i][0]), random.random()))

    print (len(shapes))
    overlap = True

    while overlap:
        overlap = False
        for pair in combinations(shapes, 2):
            if pair[0][0].intersects(pair[1][0]):
                totweight = pair[0][1] + pair[1][1]
                intersect = pair[0][0].intersection(pair[1][0])
                shapes.append((intersect, totweight))

                d0 = pair[0][0].difference(pair[0][0])
                d1 = pair[1][0].difference(pair[1][0])

                if d0 != pair[0][0]:
                    shapes.append((d0, pair[0][1]))
                if d1 != pair[1][0]:
                    shapes.append((d1, pair[1][1]))

                shapes.remove(pair[0])
                shapes.remove(pair[1])
                overlap = True
                break

    top = []
    for i in shapes:
        if top == [] or i[1] > top[0][1]:
            top = [i]
        elif i[1] == top[0][1]:
            top.append(i)

    return top


polys = [
    ([(1,1), (1,3), (3,3), (3,1)], random.random()),
    ([(2,2), (2,4), (4,4), (4,2)], random.random())
]
print (get_top(polys))
