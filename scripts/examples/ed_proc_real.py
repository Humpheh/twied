"""
Script for running the event detection on the processed tweets.
"""
import argparse
import logging
import pickle
import sys
from configparser import NoOptionError

from pymongo import MongoClient

from eventec.eventdetection import EventDetection
from scripts.examples import twieds

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
    db = client["twitter"]
    col = db["ptweets"]
except NoOptionError:
    logging.critical("Cannot connect to MongoDB database and collection. Config incorrect?")
    sys.exit()

# get the tweet cursor
logging.info("Getting tweets...")
cursor = col.find({'realgeo': {'$ne': None}}, no_cursor_timeout=True).sort('timestamp', 1)

count = 0
tf = EventDetection('realgeo.coordinates', 'timestamp', popmaploc='D:\ds\population\glds15ag.asc')
try:
    for doc in cursor:
        centre = doc['realgeo']['coordinates']
        doc['realgeo']['coordinates'] = [centre[1], centre[0]]

        tf.process_tweet(doc)
        count += 1

        if count % 100 == 0:
            logging.info("Proc tweet %i by %s" % (count, doc['timestamp']))
            logging.info(tf)

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