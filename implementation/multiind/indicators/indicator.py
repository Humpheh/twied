from Polygon.Shapes import Circle
from Polygon.Utils import pointList


class Indicator:
    """
    Base class for an indicator.
    """

    def __init__(self):
        pass

    def get_weight(self, belief):
        return self.weight * belief

    def point_to_poly(self, point, belief):
        circle = Circle(0.25, point)
        return pointList(circle), self.get_weight(belief)
