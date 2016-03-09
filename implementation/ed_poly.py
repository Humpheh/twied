import logging
import sys

from configparser import NoOptionError
from pymongo import MongoClient

import twieds
from eventec.eventdetection import EventDetection
from polyani import plotevents_count
from datetime import datetime, timedelta

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
polys = {'twts': [], 'nexttime': None, 'done': False}
ani = plotevents_count(polys)
for doc in cursor:
    if polys['nexttime'] is None:
        polys['nexttime'] = doc['timestamp_obj'] + timedelta(hours=1)
    else:
        while doc['timestamp_obj'] > polys['nexttime']:
            print("Drawing", polys['nexttime'])
            next(ani)

            polys['nexttime'] = polys['nexttime'] + timedelta(hours=1)
            polys['twts'] = []

    print("%3s," % doc['user']['screen_name'],)
    polys['twts'].append(doc)
    count += 1

polys['done'] = True
next(ani)