from Polygon.Shapes import Circle
from Polygon.Utils import pointList


class Indicator:
    """
    Base class for an indicator.
    """

    def __init__(self):
        pass

    def get_weight(self, belief, overloadw=None):
        if overloadw is None:
            return self.weight * belief
        else:
            return overloadw * belief

    def point_to_poly(self, point, belief, overloadw=None):
        circle = Circle(0.1, point)
        return pointList(circle), self.get_weight(belief, overloadw)
