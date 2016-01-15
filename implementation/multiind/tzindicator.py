from multiind.dbinterfaces import TZPolyInterface

class TZIndicator:
    def __init__(self, config):
        polydb_url = config.get("multiindicator", "gadm_polydb_path")
        self.tzpoly = TZPolyInterface(polydb_url)

    def get_loc(self, tz):
        if tz == None: return [], []

        # Check if falls in america
        if 'Pacific Time (US & Canada)' in tz:
            return self.tzpoly.get_polys_america('PST'), []
        elif 'Eastern Time (US & Canada)' in tz:
            return self.tzpoly.get_polys_america('EST'), []
        elif 'Central Time (US & Canada)' in tz:
            return self.tzpoly.get_polys_america('CST'), []

        # Format timezone a little better
        tz = re.sub(r'\([^)]*\)', '', name)
        tz = name.strip()
        tz = name.replace(' ', '_')

        return self.tzpoly.get_polys(tz), []
