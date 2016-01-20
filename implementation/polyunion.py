from shapely.geometry import Polygon
from shapely.geometry.linestring import LineString
from shapely.geometry.multilinestring import MultiLineString
from shapely.geometry.collection import GeometryCollection
from shapely.geometry.point import Point
from shapely.geometry.multipolygon import MultiPolygon
from itertools import combinations
import random
import collections

poly_holder_counter = 0

class PolyHolder:
    def __init__(self, poly, wei):
        global poly_holder_counter

        if type(poly) is list or type(poly) is tuple:
            self.polygon = Polygon(poly)
        else:
            self.polygon = poly
        self.weight = wei

        self.id = hash(poly_holder_counter)
        poly_holder_counter += 1

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id


def is_poly(poly):
    print ('Test:', type(poly))
    return not type(poly) in [MultiLineString, LineString, Point]


def shapely_tocoords(poly):
    if type(poly) in [GeometryCollection, MultiPolygon]:
        polyarr = []
        for p in poly:
            if not is_poly(p):
                polyarr += p.exterior.coords
        return polyarr

    if not is_poly(poly):
        return []

    return [poly.exterior.coords]


def get_top(polys):
    shapes = []
    for i in range(len(polys)):
        shapes.append(PolyHolder(polys[i], 0.5))

    print (len(shapes))
    overlap = True


    while overlap:
        overlap = False
        print("Comboing...")
        combos = combinations(shapes, 2)
        print("Combo.", len(shapes))
        topval = 0
        last = None
        for pair in combos:
            if last and pair[0] != last:
                print (last.weight, topval)
                if last.weight < topval:
                    shapes.remove(last)
                    print ("Removing", last)

            last = pair[0]
            topval = max([topval, pair[0].weight, pair[1].weight])
            if pair[0].polygon.intersects(pair[1].polygon) and not pair[0].polygon.touches(pair[1].polygon):
                print ('Intersecting...')

                polyplotter.polyplot(polygons=[pair[1].polygon.exterior.coords, pair[0].polygon.exterior.coords], points=[])

                totweight = pair[0].weight + pair[1].weight
                intersect = pair[0].polygon.intersection(pair[1].polygon)
              #  if isinstance(intersect, Polygon) or (isinstance(intersect, collections.Iterable) and len(intersect) > 0):#all(isinstance(n, Polygon) for n in intersect)):
                newpoly = PolyHolder(intersect, totweight)
                shapes.append(newpoly)
                topval = max([topval, totweight])

                if pair[0].polygon.contains(pair[1].polygon):
                    print (list(pair[0].polygon.exterior.coords), list(pair[1].polygon.centroid.coords))
                    pair[0].polygon = Polygon(list(pair[0].polygon.exterior.coords) + list(pair[1].polygon.centroid.coords) + [list(pair[0].polygon.exterior.coords)[-1]])
                if pair[1].polygon.contains(pair[0].polygon):
                    pair[1].polygon = Polygon(list(pair[1].polygon.exterior.coords) + list(pair[0].polygon.centroid.coords))

                print ('Difference...')
                d0 = pair[0].polygon.symmetric_difference(pair[1].polygon)

                #if d0 != pair[0].polygon and (not isinstance(d0, collections.Iterable) or all(isinstance(n, Polygon) for n in d0)):
                shapes.append(PolyHolder(d0, pair[0].weight))

                polyplotter.polyplot(polygons=[i.exterior.coords for i in d0], points=[])

                print ('Removing...')
                shapes.remove(pair[0])
                shapes.remove(pair[1])
                overlap = True
                print ('Done...')
                break

    print ("Scoring...")
    top_score = 0
    top = []
    for i in shapes:
        print(type(i.polygon))
        if top == [] or i.weight > top_score:
            coords = shapely_tocoords(i.polygon)
            if coords == []:
                continue

            top = coords
            top_score = i.weight
        elif i.weight == top_score:
            top += shapely_tocoords(i.polygon)
        print (top)
    print(len(top))

    return top


#polys = [
#    ([(1,1), (1,3), (3,3), (3,1)], random.random()),
#    ([(2,2), (2,4), (4,4), (4,2)], random.random())
#]
#print (get_top(polys))

if __name__ == "__main__":
    import polyplotter
    from pprint import pprint

    from polyexample import dict
    dict = [Polygon(d) for d in dict]

    #dict = [[(30, 30), (60, 30), (60, -30), (30, -30)], [(40, 20), (50, 20), (50, -20), (40, -20)]]
    polyplotter.polyplot(polygons=dict, points=[])
    new = get_top(dict)
    pprint(new)
    polyplotter.polyplot(polygons=new, points=[])
