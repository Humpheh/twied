import json
import pycurl

from io import BytesIO
from urllib.parse import urlencode

class DBPSpotlightInterface:
    def __init__(self, url):
        self.c = pycurl.Curl()
        self.c.setopt(self.c.URL, url + "/annotate")
        self.c.setopt(pycurl.HTTPHEADER, ['accept: application/json'])

        self.post_data = {
            'text' : '',
            'confidence' : 0.2,
            'support' : 20
        }

    def req(self, text):
        self.post_data['text'] = text
        postfields = urlencode(self.post_data)
        self.c.setopt(self.c.POSTFIELDS, postfields)

        buffer = BytesIO()
        self.c.setopt(self.c.WRITEDATA, buffer)
        self.c.perform()
        return buffer.getvalue().decode('cp437')

    def destroy(self):
        self.c.close()


class DBPInterface:
    def __init__(self):
        self.c = pycurl.Curl()
        self.c.setopt(pycurl.HTTPHEADER, ['accept: application/json'])

    def extract_name(self, text):
        return text.rpartition('/')[-1]

    def req(self, name):
        self.c.setopt(self.c.URL, "http://dbpedia.org/data/" + name + ".json")

        buffer = BytesIO()
        self.c.setopt(self.c.WRITEDATA, buffer)
        self.c.perform()
        return json.loads(buffer.getvalue().decode('cp437'))['http://dbpedia.org/resource/' + name]

    def destroy(self):
        self.c.close()


class GeonamesInterface:
    def __init__(self, url, username, fuzzy = 0.8):
        self.c = pycurl.Curl()
        self.c.setopt(pycurl.HTTPHEADER, ['accept: application/json'])
        self.c.setopt(self.c.URL, url + "/search")

        self.post_data = {
            'q': '',
            'username' : username,
            'type' : 'json',
            'fuzzy' : fuzzy,
            'orderBy' : 'relevance'
        }

    def req(self, query):
        print(query)
        self.post_data['q'] = query
        postfields = urlencode(self.post_data)
        self.c.setopt(self.c.POSTFIELDS, postfields)

        buffer = BytesIO()
        self.c.setopt(self.c.WRITEDATA, buffer)
        self.c.perform()
        return json.loads(buffer.getvalue().decode('cp437'))

    def destroy(self):
        self.c.close()
