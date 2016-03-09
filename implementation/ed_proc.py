import logging
import sys
import pickle
import argparse

from configparser import NoOptionError
from pymongo import MongoClient

import twieds
from eventec.eventdetection import EventDetection

parser = argparse.ArgumentParser(description="Run the event detection")
parser.add_argument('output', help='the output file to write to')
args = parser.parse_args()

config = twieds.setup("logs/ed_test.log", "settings/locinf.ini", logging.INFO)

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
for doc in cursor:
    logging.info("Proc tweet %i by %s" % (count, doc['user']['screen_name']))
    tf.process_tweet(doc)
    count += 1

allc = tf.get_all_clusters()
carr = [c.as_dict() for c in allc]

pkl_file = open(args.output, 'wb')
pickle.dump(carr, pkl_file)
pkl_file.close()
