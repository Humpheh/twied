import json
import urllib3
import logging
import re
import time


try:
    # UCS-4
    highpoints = re.compile(u'([\U00002600-\U000027BF])|([\U0001f300-\U0001f64F])|([\U0001f680-\U0001f6FF])')
except re.error:
    # UCS-2
    highpoints = re.compile(u'([\u2600-\u27BF])|([\uD83C][\uDF00-\uDFFF])|([\uD83D][\uDC00-\uDE4F])|([\uD83D][\uDE80-\uDEFF])')


def filter_emoji(text):
    return highpoints.sub('', text)  #u'\u25FD', text)


def req_using_pool(pool, page, data):
    return pool.request('GET', page, data)


class DBPSpotlightException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


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
        self.post_data['text'] = filter_emoji(text)
        r = req_using_pool(self.pool, self.page, self.post_data)

        try:
            return json.loads(r.data.decode('utf8'))
        except ValueError:
            logging.error("Unable to decode JSON data returned from DBPSpotlightInterface, trying again in " + str(delay))
            time.sleep(delay)
            delay = delay * 2

            if delay > 30:
                raise DBPSpotlightException("Max number of retries for DBPSpotlightInterface reached.")

            return self.req(text, delay)

    def destroy(self):
        self.pool.close()


class DBPInterface:
    def __init__(self):
        self.pool = urllib3.HTTPConnectionPool(host="dbpedia.org", maxsize=25, headers={'accept': 'application/json'})

    def extract_name(self, text):
        return text.rpartition('/')[-1]

    def req(self, name):
        r = req_using_pool(self.pool, "/data/" + name + ".json", {})
        return json.loads(r.data.decode('utf8'))['http://dbpedia.org/resource/' + name]

    def destroy(self):
        self.pool.close()


class GeonamesInterface:
    def __init__(self, config):
        url = config.get("geonames", "url")
        username = config.get("geonames", "user")
        fuzzy = config.get("geonames", "fuzzy")
        geolimit = config.getint("geonames", "limit")

        self.post_data = {
            'q': '',
            'username': username,
            'type': 'json',
            'fuzzy': fuzzy,
            'orderBy': 'relevance',
            'style': 'FULL',
            'maxRows': geolimit
        }
        self.pool = urllib3.HTTPConnectionPool(host=url, maxsize=25, headers={'accept': 'application/json'})

    def req(self, query):
        self.post_data['q'] = filter_emoji(query)
        r = req_using_pool(self.pool, "/search", self.post_data)
        return json.loads(r.data.decode('utf8'))

    def destroy(self):
        self.pool.close()


class GisgraphyInterface:
    def __init__(self, config):
        url = "localhost"

        self.post_data = {
            'q': '',
            'format': 'json',
            'suggest': 'true'
        }
        self.pool = urllib3.HTTPConnectionPool(host=url, port=8080, maxsize=25, headers={'accept': 'application/json'})

    def req(self, query):
        self.post_data['q'] = query
        r = req_using_pool(self.pool, "/fulltext", self.post_data)
        return json.loads(r.data.decode('utf8'))

    def destroy(self):
        self.pool.close()
