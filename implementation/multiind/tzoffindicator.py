from multiind.dbinterfaces import TZPolyInterface

class TZOffsetIndicator:
    def __init__(self, config):
        polydb_url = config.get("multiindicator", "gadm_polydb_path")
        self.tzpoly = TZPolyInterface(polydb_url)

    def get_loc(self, offset):
        if offset == None: return [], []

        return self.tzpoly.get_polys_offset(offset), []
