import logging

from multiind.indicators import Indicator
from multiind.interfaces import GeonamesInterface, GADMPolyInterface, CountryPolyInterface
from multiind.indicators.messageindicator import MessageIndicator


class GeonamesException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class LocFieldIndicator(Indicator):
    """
    Indicator which finds toponyms in the location field and maps them to a area or point using
    the geonames gazetteer.
    """

    def __init__(self, config):
        super().__init__()
        self.polydb_url = config.get("multiindicator", "gadm_polydb_path")

        self.geonames = GeonamesInterface(config)

        self.weight = config.getfloat("mi_weights", "GN")
        self.weight_pp = config.getfloat("mi_weights", "GN_1")
        self.weight_sym = config.getfloat("mi_weights", "GN_2")

        self.messageindicator = MessageIndicator(config)
        self.messageindicator.weight = config.getfloat("mi_weights", "GN_3")

    def _get_polys(self, res, countrypoly, gadmpoly, weight):
        if 'geonames' not in res:
            raise GeonamesException("Geonames not present in result - rate limit reached?")

        statstr = ""
        polygons = []

        maxscore = None

        for g in res['geonames']:
            userpoint = True

            if maxscore is None:
                maxscore = g['score']
            belief = g['score'] / maxscore

            if 'country' in g['fclName']:
                polys = countrypoly.get_polys(g['name'], self.get_weight(belief, weight))
                if len(polys) > 0:
                    polygons += polys
                    userpoint = False
                    statstr += "#"

            if userpoint and any(p in g['fclName'] for p in ['state', 'region']):
                # getpolygon for the place
                polys = gadmpoly.get_polys(g['name'], self.get_weight(belief, weight))
                if len(polys) > 0:
                    polygons += polys
                    userpoint = False
                    statstr += "="

            if userpoint:
                # cannot get any polys, just plot the point
                polypoint = self.point_to_poly((float(g['lng']), float(g['lat'])), belief, weight)
                polygons.append(polypoint)
                statstr += "."

        pargs = (LocFieldIndicator.__name__[:-9], len(res['geonames']), statstr)
        logging.debug("%10s =  %i geonames [%s]" % pargs)

        return polygons

    def _try_split(self, location, symbol, countrypoly, gadmpoly, weight):
        polygons = []
        linesplit = location.split(symbol)
        linesplit = [x.strip() for x in linesplit if x.strip() != '']
        if len(linesplit) > 1:
            for x in linesplit:
                res = self.geonames.req(x)
                polygons += self._get_polys(res, countrypoly, gadmpoly, weight)
        return polygons

    def get_loc(self, location):
        if location is None:
            return []

        # setup db
        countrypoly = CountryPolyInterface(self.polydb_url)
        gadmpoly = GADMPolyInterface(self.polydb_url)

        # TODO: edit the location to conform to standards

        res = self.geonames.req(location)

        # check if failed, if have then raise an exception
        polygons = self._get_polys(res, countrypoly, gadmpoly, self.weight)

        if len(polygons) == 0:
            logging.debug("Trying locationfield slashes...")
            polygons += self._try_split(location, "/", countrypoly, gadmpoly, self.weight_pp)

        if len(polygons) == 0:
            logging.debug("Trying locationfield dashes...")
            polygons += self._try_split(location, "-", countrypoly, gadmpoly, self.weight_sym)

        # if geonames couldn't find anything - try running it through the backup message indicator
        if len(polygons) == 0:
            polygons += self.messageindicator.get_loc(location)

        countrypoly.destroy()
        gadmpoly.destroy()

        return polygons
