import json
import urllib3
import logging
import re
import time
import sys

try:
    # UCS-4
    highpoints = re.compile(u'([\U00002600-\U000027BF])|([\U0001f300-\U0001f64F])|([\U0001f680-\U0001f6FF])')
except re.error:
    # UCS-2
    highpoints = re.compile(u'([\u2600-\u27BF])|([\uD83C][\uDF00-\uDFFF])'
                            u'|([\uD83D][\uDC00-\uDE4F])|([\uD83D][\uDE80-\uDEFF])')


def filter_emoji(text):
    """
    Filters out emoji characters in a string.

    :param text: The string to filter.
    :return: The text string without the emoji characters.
    """
    return highpoints.sub('', text)


def req_using_pool(pool, page, data):
    """
    Function to perform a `GET` request on a thread pool with a certain page
    and get data.

    :param pool: The pool to perform the request on.
    :param page: The page to contact.
    :param data: The get data in the request.
    :return: The result of the request.
    """
    return pool.request('GET', page, data)


class GeonamesDecodeException(Exception):
    """
    Exception for when Geonames returns a result which cannot be decoded.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class DBPSpotlightException(Exception):
    """
    Exception for twhen there is an issue with DBPediaSpotlight.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class DBPSpotlightInterface:
    """
    Interface to access the DBpedia spotlight API.
    """
    def __init__(self, config):
        """
        Initialise the DBPediaSpotlight interface.

        :param config: The :class:`configparser` object.
        """
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
        """
        Request the result for some text on DBPediaSpotlight.

        :param text: The text to request information for.
        :param delay: The number of seconds before retrying if no result is returned. Will
            double each failure to a maximum of 30 seconds before throwing an exception.
        :return: The JSON result from the service.
        """
        self.post_data['text'] = filter_emoji(text)
        r = req_using_pool(self.pool, self.page, self.post_data)

        try:
            return json.loads(r.data.decode('utf8'))
        except ValueError:
            logging.error("Unable to decode JSON data for %s returned from DBPSpotlightInterface, "
                          "Trying again in %i seconds" % (text.encode('utf8'), delay))
            time.sleep(delay)
            delay = delay * 2

            if delay > 30:
                raise DBPSpotlightException("Max number of retries for DBPSpotlightInterface reached.")
            return self.req(text, delay)

    def destroy(self):
        """
        Close the inferace and destroy the pool.
        """
        self.pool.close()


class DBPInterface:
    """
    Interface for access to the DBPedia API.
    """
    def __init__(self):
        self.pool = urllib3.HTTPConnectionPool(host="dbpedia.org", maxsize=25, headers={'accept': 'application/json'})

    def extract_name(self, text):
        """
        Extracts the name of the page from a DBPedia URL. (the last field)
        :param text: The DBPedia URL.
        :return: The name of the page.
        """
        return text.rpartition('/')[-1]

    def req(self, name):
        """
        Request the information from the DBPedia page with the name.

        :param name: The name of the DBPedia page.
        :return: The JSON result of the page.
        """
        r = req_using_pool(self.pool, "/data/" + name + ".json", {})
        try:
            js = json.loads(r.data.decode('utf8'))
            return js['http://dbpedia.org/resource/' + name]
        except ValueError:
            return None

    def destroy(self):
        """
        Close the inferace and destroy the pool.
        """
        self.pool.close()


class GeonamesInterface:
    """
    Interface for access to the Geonames API.
    """
    def __init__(self, config):
        """
        Initialise the Geonames interface.

        :param config: The :class:`configparser` object.
        """
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
        """
        Request the result from the API.

        :param query: The string to search.
        :return: The JSON result from the API.
        """
        self.post_data['q'] = filter_emoji(query)
        for i in range(5):
            try:
                r = req_using_pool(self.pool, "/search", self.post_data)
                return json.loads(r.data.decode('utf8'))
            except ValueError:
                logging.error("Value error in getting Geonames request. (Sleeping for %i second...)" % i)
                time.sleep(i)
        raise GeonamesDecodeException("Unable to decode geonames request after 5 attempts.")

    def destroy(self):
        """
        Close the inferace and destroy the pool.
        """
        self.pool.close()


class GisgraphyInterface:
    """
    Interface for access to the Gisgraphy API.
    """
    def __init__(self, config):
        """
        Initialise the Gisgraphy interface.

        :param config: The :class:`configparser` object.
        """
        url = "localhost"

        self.post_data = {
            'q': '',
            'format': 'json',
            'suggest': 'true'
        }
        self.pool = urllib3.HTTPConnectionPool(host=url, port=8080, maxsize=25, headers={'accept': 'application/json'})

    def req(self, query):
        """
        Request the result from the API.

        :param query: The string to search.
        :return: The JSON result from the API.
        """
        self.post_data['q'] = query
        r = req_using_pool(self.pool, "/fulltext", self.post_data)
        return json.loads(r.data.decode('utf8'))

    def destroy(self):
        """
        Close the inferace and destroy the pool.
        """
        self.pool.close()
