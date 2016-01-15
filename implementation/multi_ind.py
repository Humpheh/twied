import sys

lastudllen = 0
def update_line(*args, set=False):
    global lastudllen
    newstr = "".join(str(i) for i in args)
    count = lastudllen - len(newstr)
    sys.stdout.write("\r" + newstr + (" " * count if count > 0 else ""))
    sys.stdout.flush()
    lastudllen = len(newstr)
    if set: print ('')

def set_line():
    print ('')

# get tweets (without geotag)

# get tweet message polygons

import logging

from pymongo import MongoClient

from multiind import messageindicator, tzindicator, tzoffindicator, locfieldindicator, coordinateindicator, websiteindicator
import twieds
import polyplotter
import time

config = twieds.setup("logs/locinf.log", "settings/locinf.ini")

# setup the indicators
logging.info("Setting up indicators...")
ms_ind = messageindicator.MessageIndicator(config)
tz_ind = tzindicator.TZIndicator(config)
to_ind = tzoffindicator.TZOffsetIndicator(config)
lf_ind = locfieldindicator.LocFieldIndicator(config)
co_ind = coordinateindicator.CoordinateIndicator(config)
ws_ind = websiteindicator.WebsiteIndicator(config)
logging.info("Setup indicators.")

# connect to the mongodb
logging.info("Connecting to database...")
client = MongoClient()
db = client.twitter
logging.info("Connected to database.")

# get the tweet cursor
cursor = db.tweets.find()

def add_ind(ind, field, res):
    start = time.clock()
    logging.info ("[%-20s] -> %-50s" % (type(ind).__name__, field))
    result = ind.get_loc(field)
    res.append(result)
    timetaken = time.clock() - start
    pargs = (type(ind).__name__, timetaken, len(result[0]), len(result[1]))
    logging.info ("[%-20s] -> Took %.2f seconds. (%i poly, %i point)" % pargs)


for doc in cursor:
    res = []
    add_ind(ws_ind, doc['user']['url'], res)
    add_ind(lf_ind, doc['user']['location'], res)
    add_ind(co_ind, doc['user']['location'], res)
    add_ind(tz_ind, doc['user']['time_zone'], res)
    add_ind(to_ind, doc['user']['utc_offset'], res)
    add_ind(ms_ind, doc['text'], res)

    polys = []
    points = []
    for i in res:
        polys += i[0]
        points += i[1]

    polyplotter.polyplot(polygons=polys, points=points)
