import sys
import logging

from configparser import NoOptionError

from pymongo import MongoClient
import twieds

config = twieds.setup("logs/mi_alloc.log", "settings/locinf.ini")

# connect to the MongoDB
logging.info("Connecting to MongoDB...")
client = MongoClient(config.get("mongo", "address"), config.getint("mongo", "port"))
logging.info("Connected to MongoDB.")

# select the database and collection based off config
try:
    db = client[config.get("mongo", "database")]
    col = db["geotweets"]  # config.get("mongo", "collection")]
except NoOptionError:
    logging.critical("Cannot connect to MongoDB database and collection. Config incorrect?")
    sys.exit()

cursor = col.find({'geo': {'$ne': None}})

allocid = 0
for doc in cursor:
    # store the polygon in the database
    col.update_one({'_id': doc['_id']}, {
        '$set': {
            'locinf.mi.test.alloc': allocid
        }
    })
    allocid = (allocid + 1) % 4
    print(allocid)