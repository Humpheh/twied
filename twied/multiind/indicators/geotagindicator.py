from multiind.indicators import Indicator


class GeotagIndicator(Indicator):
    """
    Indicator which returns a single point if the tweet has a geotag on it.
    """

    def __init__(self, config):
        """
        Initialise the indicator.

        :param config: The config object for the MI technique.
        """
        super().__init__()
        self.weight = config.getfloat("mi_weights", "TAG")

    def get_loc(self, geofield):
        """
        Returns a polygon around the location in the geotag if it exists.

        :param geofield: The users 'geotag' field on the tweet object.
        :return: Array of single polygon around the coordinate of the user.
        """
        if geofield is not None and geofield["type"] is not None and geofield["type"] == "Point":
            return [self.point_to_poly((geofield['coordinates'][1], geofield['coordinates'][0]), 1)]
        return []