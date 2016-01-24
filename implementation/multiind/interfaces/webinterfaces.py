import json
import urllib3
import logging


class DBPSpotlightInterface:
    """
    Interface to access the DBpedia spotlight API.
    """
    def __init__(self, config):

        url = config.get("multiindicator", "dbpedia_spotlight_url")
        port = config.getint("multiindicator", "dbpedia_spotlight_port")
        self.page = config.get("multiindicator", "dbpedia_spotlight_page")

        self.post_data = {
            'text': '',
            'confidence': 0.2,
            'support': 20
        }

        self.pool = urllib3.HTTPConnectionPool(host=url, port=port, maxsize=25, headers={'accept': 'application/json'})

    def req(self, text):
        self.post_data['text'] = text

        r = self.pool.request('GET', self.page, fields=self.post_data)

        try:
            return json.loads(r.data.decode('utf8'))
        except ValueError:
            logging.error("Unable to decode JSON data returned from DBPSpotlightInterface")
            return {}

    def destroy(self):
        self.c.close()


class DBPInterface:
    def __init__(self):
        self.pool = urllib3.HTTPConnectionPool(host="dbpedia.org", maxsize=25, headers={'accept': 'application/json'})

    def extract_name(self, text):
        return text.rpartition('/')[-1]

    def req(self, name):
        r = self.pool.request('GET', "/data/" + name + ".json")
        return json.loads(r.data.decode('utf8'))['http://dbpedia.org/resource/' + name]

    def destroy(self):
        self.c.close()


class GeonamesInterface:
    def __init__(self, config):
        url = config.get("geonames", "url")
        username = config.get("geonames", "user")
        fuzzy = config.get("geonames", "fuzzy")

        self.post_data = {
            'q': '',
            'username': username,
            'type': 'json',
            'fuzzy': fuzzy,
            'orderBy': 'relevance'
        }
        self.pool = urllib3.HTTPConnectionPool(host=url, maxsize=25, headers={'accept': 'application/json'})

    def req(self, query):
        self.post_data['q'] = query
        r = self.pool.request('GET', "/search", fields=self.post_data)
        return json.loads(r.data.decode('utf8'))

    def destroy(self):
        self.c.close()
