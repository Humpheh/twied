import logging

from ..interfaces import DBPInterface, DBPSpotlightInterface, GADMPolyInterface
from . import Indicator


class MessageIndicator(Indicator):
    """
    Indicator which finds place names in tweet text using DBpedia spotlight and
    maps them to a area or point location.
    """

    def __init__(self, config):
        super().__init__()
        self.polydb_url = config.get("multiindicator", "gadm_polydb_path")

        self.dbps = DBPSpotlightInterface(config)
        self.dbpi = DBPInterface()

        self.weight = config.getfloat("mi_weights", "SP")

    def get_loc(self, message):
        if not message:
            return []

        # setup db connection
        gadmpoly = GADMPolyInterface(self.polydb_url)

        j = self.dbps.req(message)

        if j is None:
            return []

        statstr = ""
        polygons = []

        if 'Resources' in j:
            for resource in j['Resources']:
                # check that it is a place and not something useless
                if 'Schema:Place' in resource['@types']:
                    r_url = resource['@URI']
                    name = self.dbpi.extract_name(r_url)
                    datareq = self.dbpi.req(name)

                    if datareq is None:
                        continue
                    # TODO: check if http://dbpedia.org/ontology/wikiPageRedirects exists

                    # get the polygons and weigh them
                    similarity = float(resource['@similarityScore'])
                    polys = gadmpoly.get_polys(name.replace('_', ' '), self.get_weight(similarity))

                    if not len(polys) == 0:
                        polygons += polys
                        statstr += '#'
                    else:
                        try:
                            lat, lon = datareq['http://www.georss.org/georss/point'][0]['value'].split(" ")
                            pos = (float(lon), float(lat))
                            polygons.append(self.point_to_poly(pos, similarity))
                            statstr += '.'
                        except KeyError:
                            try:
                                lat = datareq['http://dbpedia.org/property/sourceLatD'][0]['value']
                                lon = datareq['http://dbpedia.org/property/sourceLongD'][0]['value']
                                pos = (float(lon), float(lat))
                                polygons.append(self.point_to_poly(pos, similarity))
                                statstr += '.'
                            except KeyError:
                                logging.warning("No georss/sourceD field on 'place': %s" % name)
                                statstr += '!'
                                # TODO: try latd or longd
                else:
                    statstr += ' '

            pargs = (MessageIndicator.__name__[:-9], len(j['Resources']), statstr)
            logging.debug("%10s =  %i resources [%s]" % pargs)
        else:
            pargs = (MessageIndicator.__name__[:-9])
            logging.warning("%10s =  0 resources in response" % pargs)

        gadmpoly.destroy()

        return polygons
