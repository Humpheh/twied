from Polygon.Shapes import Circle
from Polygon.Utils import pointList


class Indicator:
    def __init__(self):
        pass

    def point_to_poly(self, point):
        circle = Circle(0.25, point)
        return pointList(circle)
