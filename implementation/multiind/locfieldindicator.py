from multiind.webinterfaces import GeonamesInterface
from multiind.dbinterfaces import GADMPolyInterface, CountryPolyInterface

class LocFieldIndicator:
    # place types which need polygon instead of points

    def __init__(self, config):
        geo_url = config.get("geonames", "url")
        geo_user = config.get("geonames", "user")
        polydb_url = config.get("multiindicator", "gadm_polydb_path")

        self.geonames = GeonamesInterface(geo_url, geo_user)
        self.gadmpoly = GADMPolyInterface(polydb_url)
        self.countrypoly = CountryPolyInterface(polydb_url)

    def get_loc(self, location):
        if location == None: return [], []

        res = self.geonames.req(location)
        print(len(res['geonames']), 'geonames results')

        # TODO: check if failed...
        # TODO: edit the location to conform to standards
        # TODO: limit used

        polygons = []
        polypoints = []

        for g in res['geonames']:
            userpoint = True

            if 'country' in g['fclName']:
                polys = self.countrypoly.get_polys(g['name'])
                if len(polys) > 0:
                    polygons += polys
                    userpoint = False

            if userpoint and any(p in g['fclName'] for p in ['state', 'region']):
                # getpolygon for the place
                polys = self.gadmpoly.get_polys(g['name'])
                if len(polys) > 0:
                    polygons += polys
                    userpoint = False

            if userpoint:
                polypoints.append((float(g['lng']), float(g['lat'])))

        return polygons, polypoints
