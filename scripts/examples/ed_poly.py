#!/usr/bin/python
"""
File to build an animation.
"""
import logging
import sys
from configparser import NoOptionError
from datetime import timedelta

from pymongo import MongoClient

import twieds
from polyani import plotevents_count

config = twieds.setup("logs/ed_test.log", "settings/locinf.ini", logging.DEBUG)

# connect to the MongoDB
logging.info("Connecting to MongoDB...")
client = MongoClient(config.get("mongo", "address"), config.getint("mongo", "port"))
logging.info("Connected to MongoDB")

# select the database and collection based off config
try:
    db = client[config.get("mongo", "database")]
    col = db["inftweets"]
except NoOptionError:
    logging.critical("Cannot connect to MongoDB database and collection. Config incorrect?")
    sys.exit()

# get the tweet cursor
logging.info("Getting tweets...")
cursor = col.find()

count = 0
polys = {'twts': [], 'nexttime': None, 'done': False}
ani = plotevents_count(polys)
for doc in cursor:

    try:
        doc['locinf']['mi']['id']
    except KeyError:
        continue

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