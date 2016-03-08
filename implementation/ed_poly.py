import logging
import sys

from configparser import NoOptionError
from pymongo import MongoClient

import twieds
from eventec.eventdetection import EventDetection
from polyani import plotevents_count

config = twieds.setup("logs/ed_test.log", "settings/locinf.ini", logging.DEBUG)

# connect to the MongoDB
logging.info("Connecting to MongoDB...")
client = MongoClient(config.get("mongo", "address"), config.getint("mongo", "port"))
logging.info("Connected to MongoDB")

# select the database and collection based off config
try:
    db = client[config.get("mongo", "database")]
    col = db["geotweets"]#config.get("mongo", "collection")]
except NoOptionError:
    logging.critical("Cannot connect to MongoDB database and collection. Config incorrect?")
    sys.exit()

# get the tweet cursor
logging.info("Getting tweets...")
cursor = db.tweets.find({'locinf.mi.test': {'$ne': None}})

count = 0
polys = {'twts': []}
ani = plotevents_count(polys)
for doc in cursor:
    print("%3s," % doc['user']['screen_name'],)
    if count % 10 == 0:
        print("Drawing..")
        next(ani)

    polys['twts'].append(doc)
    if len(polys['twts']) > 10:
        polys['twts'] = polys['twts'][1:]
    count += 1


