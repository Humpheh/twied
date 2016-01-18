import csv
import re

from multiind.dbinterfaces import CountryPolyInterface

class WebsiteIndicator:

    tld_regex = r"[^\s\/](?:\.([a-z]{2,3}))?(?:\s|\/|$)" #r"[^.]*\.[^.]{2,3}(?:\.([a-z]{2,3}))?(?:\s|\/|$)"

    def __init__(self, config):
        csv_loc = config.get("multiindicator", "tld_csv")
        polydb_url = config.get("multiindicator", "gadm_polydb_path")

        self.cpi = CountryPolyInterface(polydb_url)

        # load the tlds from the csv, and get and store the polygons
        self.codes = {}
        with open(csv_loc, newline='') as csvfile:
            tldreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in tldreader:
                countries = self.cpi.get_polys(row[1])
                self.codes[row[0]] = (row[1], countries)

        self.tldre = re.compile(self.tld_regex)

    def get_loc(self, website):
        if website == None: return [], []

        tlds = self.tldre.findall(website)
        print (website)
        polys = []
        for t in tlds:
            td = t.strip()
            print ("TLD found:", td, 'exists ->', (td in self.codes))
            if td in self.codes:
                polys += self.codes[td][1]

        return polys, []
