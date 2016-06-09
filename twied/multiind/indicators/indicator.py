from Polygon.Shapes import Circle
from Polygon.Utils import pointList


class Indicator:
    """
    Base class for an indicator.
    """

    def __init__(self):
        pass

    def get_weight(self, belief, overloadw=None):
        """
        Gets the weight of a polygon based on a belief for the polygon and
        the weight of this indicator.

        :param belief: Value in [0, 1] of how confident the estimation is.
        :type belief: float
        :param overloadw: *(optional)* If `None` will use normal weight, otherwise
            can override the weight of the indicator.
        :type overloadw: float
        :return: The value of the indicator
        :rtype: float
        """
        if overloadw is None:
            return self.weight * belief
        else:
            return overloadw * belief

    def point_to_poly(self, point, belief, overloadw=None):
        """
        Translates a (lat, lon) point into a circular polygon of 0.1 degree radius.

        :param point: The (lat, lon) point to get a polygon around.
        :type point: tuple
        :param belief: Value in [0, 1] of how confident the estimation is.
        :type belief: float
        :param overloadw: *(optional)* If `None` will use normal weight, otherwise
            can override the weight of the indicator.
        :type overloadw: float
        :return:
        """
        circle = Circle(0.1, point)
        return pointList(circle), self.get_weight(belief, overloadw)
