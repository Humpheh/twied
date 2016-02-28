import logging
import sys

from configparser import NoOptionError
from pymongo import MongoClient

import twieds
from eventec.eventdetection import EventDetection
from polyplotter import plotevents

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
tf = EventDetection('geo.coordinates')
ani = plotevents(tf)
for doc in cursor:
    print("Proc tweet by", doc['user']['screen_name'])
    tf.process_tweet(doc)

    if count % 10 == 0:
        next(ani)

    #a = "p" if count % 1000 == 0 else ""# input(">")
    count += 1

    #if a == "p":
    #    plotevents(tf)

