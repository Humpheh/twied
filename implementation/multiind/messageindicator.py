import json
import logging

from multiind.webinterfaces import DBPInterface, DBPSpotlightInterface
from multiind.dbinterfaces import GADMPolyInterface
from multiind.indicator import Indicator


class MessageIndicator(Indicator):
    def __init__(self, config):
        spotlight_url = config.get("multiindicator", "dbpedia_spotlight_url")
        self.polydb_url = config.get("multiindicator", "gadm_polydb_path")

        self.dbps = DBPSpotlightInterface(spotlight_url)
        self.dbpi = DBPInterface()

    def get_loc(self, message):
        if not message:
            return []

        # setup db connection
        self.gadmpoly = GADMPolyInterface(self.polydb_url)

        j = json.loads(self.dbps.req(message))

        statstr = ""
        polygons = []

        for resource in j['Resources']:
            if 'Schema:Place' in resource['@types']:
                r_url = resource['@URI']
                name = self.dbpi.extract_name(r_url)
                datareq = self.dbpi.req(name)
                # TODO: check if http://dbpedia.org/ontology/wikiPageRedirects exists

                polys = self.gadmpoly.get_polys(name.replace('_', ' '))

                if not len(polys) == 0:
                    polygons += polys
                    statstr += '#'
                else:
                    try:
                        lon, lat = datareq['http://www.georss.org/georss/point'][0]['value'].split(" ")
                        pos = (float(lat), float(lon))
                        polygons.append(self.point_to_poly(pos))
                        statstr += '.'
                    except:
                        logging.warning ("No georss field on 'place': %s" % (name))
                        statstr += '!'
                        # TODO: try latd or longd
            else:
                statstr += ' '

        pargs = (MessageIndicator.__name__[:-9], len(j['Resources']), statstr)
        logging.info ("%10s =  %i resources [%s]" % pargs)

        self.gadmpoly.destroy()

        return polygons
