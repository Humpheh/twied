import re

from . import Indicator


class CoordinateIndicator(Indicator):
    """
    Indicator for users with coordinates in their location field.
    """

    regex = r"(-?\d{1,2}\.\d{6})\s?,\s?(-?\d{1,2}\.\d{6})"

    def __init__(self, config):
        """
        Initialise the indicator.

        :param config: The config object for the MI technique.
        """
        super().__init__()
        self.prog = re.compile(CoordinateIndicator.regex)
        self.weight = config.getfloat("mi_weights", "COD")

    def get_loc(self, string):
        """
        Returns a point polygon if the users location field contains coordinates
        in it.

        :param string: The users location field.
        :return: Array of polygons.
        """
        if not string:
            return []

        search = self.prog.search(string)

        # See if the string matches the coordinate
        if search is not None:
            split = re.split(r'[\s,]+', search.group(0))
            poly = self.point_to_poly((float(split[0]), float(split[1])), 1)  # 1 belief
            return [poly]
        return []
