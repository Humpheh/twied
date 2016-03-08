import sys
import logging
import argparse

from configparser import NoOptionError

from pymongo import MongoClient
import twieds

config = twieds.setup("logs/mi_alloc.log", "settings/locinf.ini")

parser = argparse.ArgumentParser(description="Allocates each tweet in a collection with a number in specified range.")
parser.add_argument('-field', help='the fieldname to store the inferred location in', required=True)
parser.add_argument('-num', type=int, help='the range [0, X] of id\'s to allocate', required=True)
parser.add_argument('-db', help='address of the database', default=config.get('mongo', 'address'))
parser.add_argument('-port', type=int, help='port of the database', default=config.get('mongo', 'port'))
parser.add_argument('-coll', help='database and collection name seperated by a dot (eg, twitter.tweets)', required=True)
args = parser.parse_args()

# connect to the MongoDB
logging.info("Connecting to MongoDB...")
client = MongoClient(args.db, args.port)
logging.info("Connected to MongoDB.")

# select the database and collection based off config
try:
    db_n, col_n = args.coll.split(".")
    col = client[db_n][col_n]
except NoOptionError:
    logging.critical("Cannot connect to MongoDB database and collection. Config incorrect?")
    sys.exit()

cursor = col.find()

if args.num < 0:
    logging.error("Number range must be >= 0.")
    sys.exit()

logging.info("Allocating to field '%s.alloc' - correct? (Any input to continue)" % args.field)
input(">")

count = 0
allocid = 0
for doc in cursor:
    # store the polygon in the database
    col.update_one({'_id': doc['_id']}, {
        '$set': {
            args.field + '.alloc': allocid
        }
    })
    allocid = (allocid + 1) % args.num
    if count % 1000 == 0:
        logging.info("Allocated %i" % count)
    count += 1

logging.info("Allocation complete.")