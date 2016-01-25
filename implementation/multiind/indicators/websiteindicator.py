import logging
import csv
import re

from multiind.indicators import Indicator
from multiind.interfaces import CountryPolyInterface


class WebsiteIndicator(Indicator):
    """
    Indicator which detects the TLD of the website in the users profile and maps it to an area.
    Note: domains such as .com, .net and .org are ignored, and only country domains are detected.
    """

    tld_regex = r"[^\s\/](?:\.([a-z]{2,3}))?(?:\s|\/|$)"

    def __init__(self, config):
        csv_loc = config.get("multiindicator", "tld_csv")
        polydb_url = config.get("multiindicator", "gadm_polydb_path")

        self.weight = config.getfloat("mi_weights", "WS_1")

        self.cpi = CountryPolyInterface(polydb_url)

        # load the tlds from the csv, and get and store the polygons
        self.codes = {}
        with open(csv_loc, newline='') as csvfile:
            tldreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in tldreader:
                countries = self.cpi.get_polys(row[1], self.get_weight(1))
                self.codes[row[0]] = (row[1], countries)

        self.tldre = re.compile(self.tld_regex)

    def get_loc(self, website):
        if website is None:
            return []

        # search the field for all websites
        tlds = self.tldre.findall(website)
        polys = []
        for t in tlds:
            # find the polys from the prebuilt dictionary
            td = t.strip()
            logging.info("TLD found: %s exists = %s" % (td, (td in self.codes)))
            if td in self.codes:
                polys += self.codes[td][1]

        return polys
