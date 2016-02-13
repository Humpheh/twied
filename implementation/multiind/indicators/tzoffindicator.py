from multiind.indicators import Indicator
from multiind.interfaces import TZPolyInterface


class TZOffsetIndicator(Indicator):
    """
    Indicator which gets an area for the UTC offset the user is in.
    """

    def __init__(self, config):
        self.polydb_url = config.get("multiindicator", "gadm_polydb_path")
        self.weight = config.getfloat("mi_weights", "TZ")
        self.history = {}

    def get_loc(self, offset):
        if offset is None:
            return []

        if offset in self.history:
            return self.history[offset]

        # setup db connection
        tzpoly = TZPolyInterface(self.polydb_url)
        result = tzpoly.get_polys_offset(offset, self.get_weight(1))
        tzpoly.destroy()

        self.history[offset] = result

        return result
