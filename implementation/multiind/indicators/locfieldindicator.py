import logging

from multiind.indicators import Indicator
from multiind.interfaces import GeonamesInterface, GADMPolyInterface, CountryPolyInterface


class LocFieldIndicator(Indicator):
    # place types which need polygon instead of points

    def __init__(self, config):
        geo_url = config.get("geonames", "url")
        geo_user = config.get("geonames", "user")
        self.polydb_url = config.get("multiindicator", "gadm_polydb_path")

        self.geonames = GeonamesInterface(geo_url, geo_user)

        self.geolimit = config.getint("geonames", "limit")
        self.weight = config.getfloat("mi_weights", "GN")

    def get_loc(self, location):
        if location is None:
            return []

        # setup db
        self.countrypoly = CountryPolyInterface(self.polydb_url)
        self.gadmpoly = GADMPolyInterface(self.polydb_url)

        res = self.geonames.req(location)

        # TODO: check if failed...
        # TODO: edit the location to conform to standards
        # TODO: limit used

        statstr = ""
        polygons = []

        count = 0

        for g in res['geonames']:
            userpoint = True

            if 'country' in g['fclName']:
                polys = self.countrypoly.get_polys(g['name'], self)
                if len(polys) > 0:
                    polygons += polys
                    userpoint = False
                    statstr += "#"

            if userpoint and any(p in g['fclName'] for p in ['state', 'region']):
                # getpolygon for the place
                polys = self.gadmpoly.get_polys(g['name'], self)
                if len(polys) > 0:
                    polygons += polys
                    userpoint = False
                    statstr += "="

            if userpoint:
                polypoint = self.point_to_poly((float(g['lng']), float(g['lat'])))
                polygons.append(polypoint)
                statstr += "."

            count += 1
            if count >= self.geolimit:
                break

        pargs = (LocFieldIndicator.__name__[:-9], len(res['geonames']), statstr)
        logging.info("%10s =  %i geonames [%s]" % pargs)

        self.countrypoly.destroy()
        self.gadmpoly.destroy()

        return polygons
