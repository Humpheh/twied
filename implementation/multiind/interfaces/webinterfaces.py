import json
import urllib3
import logging
import time
import urllib.parse


class DBPSpotlightInterface:
    """
    Interface to access the DBpedia spotlight API.
    """
    def __init__(self, config):

        url = config.get("dbpedia", "spotlight_url")
        port = config.getint("dbpedia", "spotlight_port")
        self.page = config.get("dbpedia", "spotlight_page")

        self.post_data = {
            'text': '',
            'confidence': 0.2,
            'support': 20
        }

        self.pool = urllib3.HTTPConnectionPool(host=url, port=port, maxsize=25, headers={'accept': 'application/json'})

    def req(self, text, delay=0.5):
        self.post_data['text'] = urllib.parse.quote(text)

        r = self.pool.request('GET', self.page, fields=self.post_data)

        try:
            return json.loads(r.data.decode('utf8'))
        except ValueError:
            logging.error("Unable to decode JSON data returned from DBPSpotlightInterface, trying again in " + str(delay))
            time.sleep(delay)
            delay = delay + 0.5 if delay + 0.5 < 5 else delay
            return self.req(text, delay)

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
        self.post_data['q'] = urllib.parse.quote(query)
        r = self.pool.request('GET', "/search", fields=self.post_data)
        return json.loads(r.data.decode('utf8'))

    def destroy(self):
        self.c.close()
