import logging

from multiind.indicators import Indicator
from multiind.interfaces import GisgraphyInterface, GADMPolyInterface
from multiind.indicators.messageindicator import MessageIndicator


class GisgraphyException(Exception):
    """
    Exception object thrown when there is an error is getting the location
    from the Gisgraphy service.
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class GISLocFieldIndicator(Indicator):
    """
    Indicator which finds toponyms in the location field and maps them to a area or point using
    the geonames gazetteer.

    This is a reimplementation of the :class:`LocFieldIndicator` class which uses the
    `Gisgraphy <http://gisgraphy.com/>_` open source gazeteer instead of the
    `Geonames <http://www.geonames.org/>_` gazeteer. In testing this service was found
    to have a less useful search feature, however was not API limited as the service
    could be hosted locally.
    """

    def __init__(self, config):
        """
        Initialise the indicator.

        :param config: The config object for the MI technique.
        """
        super().__init__()
        self.polydb_url = config.get("multiindicator", "gadm_polydb_path")

        self.geonames = GisgraphyInterface(config)

        self.geolimit = config.getint("geonames", "limit")
        self.weight = config.getfloat("mi_weights", "GN")

        self.messageindicator = MessageIndicator(config)
        self.messageindicator.weight = config.getfloat("mi_weights", "GN_3")

    def get_loc(self, location):
        if location is None:
            return []

        # setup db
        gadmpoly = GADMPolyInterface(self.polydb_url)

        polygons = self.get_polys(location, gadmpoly)

        # split by commas
        if len(polygons) == 0:
            spl = location.split(",")
            if not len(spl) == 1:
                for component in spl:
                    print(",:", component.strip())
                    polygons += self.get_polys(component.strip(), gadmpoly)

        # if still none, split by spaces
        if len(polygons) == 0:
            for component in location.split(" "):
                print(" :", component.strip())
                polygons += self.get_polys(component.strip(), gadmpoly)

        # if geonames couldn't find anything - try running it through the backup message indicator
        if len(polygons) == 0:
            polygons += self.messageindicator.get_loc(location)

        gadmpoly.destroy()

        return polygons

    def get_polys(self, location, gadmpoly):

        res = self.geonames.req(location)

        # check if failed, if have then raise an exception
        if 'response' not in res:
            raise GisgraphyException("Geonames not present in result?")

        statstr = ""
        polygons = []

        count = 0

        for g in res['response']['docs']:
            userpoint = True

            # belief in coordinate decreases by 0.1 the lower down the list from 1 to 0.5
            belief = float(g['score']) / float(res['response']['maxScore'])  #1 - (count / self.geolimit / 2)

            if any(p in g['placetype'] for p in ['Adm', 'City']):
                # getpolygon for the place
                polys = gadmpoly.get_polys(g['name'], self.get_weight(belief))
                if len(polys) > 0:
                    polygons += polys
                    userpoint = False
                    statstr += "="

            if userpoint:
                # cannot get any polys, just plot the point
                polypoint = self.point_to_poly((float(g['lng']), float(g['lat'])), belief)
                polygons.append(polypoint)
                statstr += "."

            count += 1
            if count >= self.geolimit:
                break

        pargs = (location, len(res['response']['docs']), statstr)
        logging.debug("%10s =  %i geonames [%s]" % pargs)

        return polygons
