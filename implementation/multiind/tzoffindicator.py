from multiind.dbinterfaces import TZPolyInterface
from multiind.indicator import Indicator


class TZOffsetIndicator(Indicator):
    def __init__(self, config):
        self.polydb_url = config.get("multiindicator", "gadm_polydb_path")
        self.weight = config.getfloat("mi_weights", "TZ")

    def get_loc(self, offset):
        if offset is None:
            return []

        # setup db connection
        self.tzpoly = TZPolyInterface(self.polydb_url)

        result = self.tzpoly.get_polys_offset(offset, self)

        self.tzpoly.destroy()
        return result
