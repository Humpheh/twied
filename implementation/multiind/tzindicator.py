from multiind.dbinterfaces import TZPolyInterface
from multiind.indicator import Indicator
import re


class TZIndicator(Indicator):
    def __init__(self, config):
        self.polydb_url = config.get("multiindicator", "gadm_polydb_path")

    def get_loc(self, tz):
        if tz is None:
            return []

        # setup db connection
        self.tzpoly = TZPolyInterface(self.polydb_url)

        # Check if falls in america
        if 'Pacific Time (US & Canada)' in tz:
            return self.tzpoly.get_polys_america('PST')
        elif 'Eastern Time (US & Canada)' in tz:
            return self.tzpoly.get_polys_america('EST')
        elif 'Central Time (US & Canada)' in tz:
            return self.tzpoly.get_polys_america('CST')

        # Format timezone a little better
        tz = re.sub(r'\([^)]*\)', '', tz).strip().replace(' ', '_')

        result = self.tzpoly.get_polys(tz)

        self.tzpoly.destroy()
        return result
