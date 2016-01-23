import logging

from multiind.indicators import Indicator
from multiind.interfaces import GeonamesInterface, GADMPolyInterface, CountryPolyInterface


class LocFieldIndicator(Indicator):
    """
    Indicator which finds toponyms in the location field and maps them to a area or point using
    the geonames gazetteer.
    """

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
        countrypoly = CountryPolyInterface(self.polydb_url)
        gadmpoly = GADMPolyInterface(self.polydb_url)

        res = self.geonames.req(location)

        # TODO: check if failed...
        # TODO: edit the location to conform to standards
        # TODO: limit used

        statstr = ""
        polygons = []

        count = 0

        for g in res['geonames']:
            userpoint = True

            # belief in coordinate decreases by 0.1 the lower down the list from 1 to 0.5
            belief = 1 - (count / self.geolimit / 2)

            if 'country' in g['fclName']:
                polys = countrypoly.get_polys(g['name'], self.get_weight(belief))
                if len(polys) > 0:
                    polygons += polys
                    userpoint = False
                    statstr += "#"

            if userpoint and any(p in g['fclName'] for p in ['state', 'region']):
                # getpolygon for the place
                polys = gadmpoly.get_polys(g['name'], self.get_weight(belief))
                if len(polys) > 0:
                    polygons += polys
                    userpoint = False
                    statstr += "="

            if userpoint:
                polypoint = self.point_to_poly((float(g['lng']), float(g['lat'])), belief)
                polygons.append(polypoint)
                statstr += "."

            count += 1
            if count >= self.geolimit:
                break

        pargs = (LocFieldIndicator.__name__[:-9], len(res['geonames']), statstr)
        logging.info("%10s =  %i geonames [%s]" % pargs)

        countrypoly.destroy()
        gadmpoly.destroy()

        return polygons
