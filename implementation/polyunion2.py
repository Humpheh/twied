from Polygon import Polygon
import Polygon.Utils
from itertools import combinations
import polyplotter

poly_holder_counter = 0


class PolyHolder:
    def __init__(self, poly, wei):
        global poly_holder_counter

        if type(poly) is list or type(poly) is tuple:
            self.polygon = Polygon.Polygon(Polygon.Utils.reducePoints(poly, 100))
        else:
            self.polygon = poly
        self.weight = wei

        self.id = hash(poly_holder_counter)
        poly_holder_counter += 1

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id


def polys2points(polys):
    ply = []
    for p in polys:
        for c in range(len(p)):
            ply.append(p[c])
    return ply


def split_contours(poly):
    shapes = []
    for x in range(len(poly)):
        shapes.append(PolyHolder(poly[x], 0.5))
    return shapes


def get_top(polys):
    shapes = []
    for i in range(len(polys)):
        shapes.append(PolyHolder(polys[i], 0.5))#split_contours(polys[i])
    print(shapes)

    polyplotter.polyplot(polygons=polys2points([p.polygon for p in shapes]), points=[])


    print(len(shapes))
    overlap = True

    while overlap:
        overlap = False
        combos = combinations(shapes, 2)

        print("Combos =", len(shapes))

        topval = 0
        last = None
        for pair in combos:
            if last and pair[0] != last:
                print(last.weight, topval)
                if last.weight < topval:
                    shapes.remove(last)
                    print("Removing", last)

            last = pair[0]
            topval = max([topval, pair[0].weight, pair[1].weight])
            if pair[0].polygon.overlaps(pair[1].polygon):
                print('Intersecting...')

                #polyplotter.polyplot(polygons=polys2points([pair[1].polygon, pair[0].polygon]), points=[])

                totweight = pair[0].weight + pair[1].weight
                intersect = pair[0].polygon & pair[1].polygon

                shapes.append(PolyHolder(intersect, totweight))#split_contours(intersect)
                topval = max([topval, totweight])

                print('Difference...', topval)
                d0 = pair[0].polygon ^ pair[1].polygon
                shapes.append(PolyHolder(d0, pair[0].weight))
                #shapes += split_contours(d0)

               # polyplotter.polyplot(polygons=polys2points([d0, intersect]), points=[])

                print('Removing...')
                shapes.remove(pair[0])
                shapes.remove(pair[1])
                overlap = True
                print('Done...')
                break

    print("Scoring...")
    top_score = 0
    top = []
    for i in shapes:
        print(type(i.polygon))
        if top == [] or i.weight > top_score:
            top = [i]
            top_score = i.weight
        elif i.weight == top_score:
            top += i

    print(len(top))

    return top

if __name__ == "__main__":
    from pprint import pprint
    #from polyexample import dict as d
    d = [[(30, 30), (60, 30), (60, -30), (30, -30)], [(40, 20), (50, 20), (50, -20), (40, -20)]]



    t = get_top(d)
    pprint(t)

    #polyplotter.polyplot(polygons=[Polygon.Utils.pointList(p.polygon) for p in t], points=[])

    p = Polygon.Polygon(d[0]) - Polygon.Polygon(d[1])

    pprint(Polygon.Utils.tileBSP(p))

    print(p)
    print(p.boundingBox())
    print(Polygon.Utils.pointList(p))

    polyplotter.polyplot(polygons=[Polygon.Utils.pointList(p)], points=[])