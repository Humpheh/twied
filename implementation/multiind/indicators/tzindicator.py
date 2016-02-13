import re

from multiind.indicators import Indicator
from multiind.interfaces import TZPolyInterface


class TZIndicator(Indicator):
    """
    Indicator which gets an area for the timezone the user is in.
    """

    def __init__(self, config):
        self.polydb_url = config.get("multiindicator", "gadm_polydb_path")
        self.weight = config.getfloat("mi_weights", "TZ")
        self.history = {}

    def get_loc(self, tz):
        if tz is None:
            return []

        if tz in self.history:
            return self.history[tz]

        # setup db connection
        tzpoly = TZPolyInterface(self.polydb_url)

        # Check if falls in america
        if 'Pacific Time (US & Canada)' in tz:
            result = tzpoly.get_polys_america('PST', self.get_weight(1))
        elif 'Eastern Time (US & Canada)' in tz:
            result = tzpoly.get_polys_america('EST', self.get_weight(1))
        elif 'Central Time (US & Canada)' in tz:
            result = tzpoly.get_polys_america('CST', self.get_weight(1))
        else:
            # Format timezone a little better
            tz = re.sub(r'\([^)]*\)', '', tz).strip().replace(' ', '_')

            result = tzpoly.get_polys(tz, self.get_weight(1))

        self.history[tz] = result

        tzpoly.destroy()
        return result
