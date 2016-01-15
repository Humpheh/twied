import json

from multiind.webinterfaces import DBPInterface, DBPSpotlightInterface
from multiind.dbinterfaces import GADMPolyInterface

class MessageIndicator:
    def __init__(self, config):
        spotlight_url = config.get("multiindicator", "dbpedia_spotlight_url")
        polydb_url = config.get("multiindicator", "gadm_polydb_path")

        self.dbps = DBPSpotlightInterface(spotlight_url)
        self.dbpi = DBPInterface()
        self.gadmpoly = GADMPolyInterface(polydb_url)

    def get_loc(self, message):
        if message == None: return [], []

        j = json.loads(self.dbps.req(message))

        polygons = []
        polypoints = []

        for resource in j['Resources']:
            print ("RESOURCE:", resource['@URI'])
            if 'Schema:Place' in resource['@types']:
                r_url = resource['@URI']
                name = self.dbpi.extract_name(r_url)
                datareq = self.dbpi.req(name)
                # TODO: check if http://dbpedia.org/ontology/wikiPageRedirects exists

                polys = self.gadmpoly.get_polys(name.replace('_', ' '))

                if not len(polys) == 0:
                    polygons += polys
                    print ("Added polygons:", len(polys))
                else:
                    try:
                        lon, lat = datareq['http://www.georss.org/georss/point'][0]['value'].split(" ")
                        pos = (float(lat), float(lon))
                        print ("Added point:", pos)
                        polypoints.append(pos)
                    except:
                        print ("WARNING: No georss field on 'place'...")
                        # TODO: try latd or longd
            else:
                print ("Not Schema:Place...")

        return polygons, polypoints
