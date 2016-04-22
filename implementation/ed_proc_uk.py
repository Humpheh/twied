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

config = twieds.setup(None, "settings/locinf.ini", logging.INFO)

# connect to the MongoDB
logging.info("Connecting to MongoDB...")
client = MongoClient(config.get("mongo", "address"), config.getint("mongo", "port"))
logging.info("Connected to MongoDB")

# select the database and collection based off config
try:
    db = client["twitter"]  # config.get("mongo", "database")]
    col = db["ptweets"]  # ["geotweets"]#config.get("mongo", "collection")]
except NoOptionError:
    logging.critical("Cannot connect to MongoDB database and collection. Config incorrect?")
    sys.exit()

with open('D:/ds/code/workbooks/ukpoly.pkl', 'rb') as file:
    mp = pickle.load(file)

# get the tweet cursor
logging.info("Getting tweets...")
cursor = col.find(no_cursor_timeout=True).sort('timestamp', 1)#{'locinf.mi.test': {'$ne': None}})

count = 0
tf = EventDetection('centre', 'timestamp')#'geo.coordinates')
try:
    for doc in cursor:
        if doc['centre'] is None or not mp.isInside(doc['centre'][0], doc['centre'][1]):
            continue

        tf.process_tweet(doc)
        count += 1

        if count % 100 == 0:
            logging.info("Proc tweet %i by %s" % (count, doc['timestamp']))#doc['user']['screen_name']))
            logging.info(tf)

        #if count > 500000:
        #    break
except Exception as e:
    print(e)
    pass

print("Saving clusters...")
allc = tf.get_all_clusters()
carr = [c.as_dict() for c in allc]

pkl_file = open(args.output, 'wb')
pickle.dump(carr, pkl_file)
pkl_file.close()

cursor.close()