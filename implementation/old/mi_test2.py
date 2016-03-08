import logging
import sys

from configparser import NoOptionError
from pymongo import MongoClient
from Polygon import Polygon
from Polygon import Error as PolygonError

import twieds
import polyplotter

from geopy.distance import vincenty

config = twieds.setup("logs/locinf.log", "settings/locinf.ini")

# connect to the MongoDB
logging.info("Connecting to MongoDB...")
client = MongoClient(config.get("mongo", "address"), config.getint("mongo", "port"))
logging.info("Connected to MongoDB")

# select the database and collection based off config
try:
    db = client[config.get("mongo", "database")]
    col = db[config.get("mongo", "collection")]
except NoOptionError:
    logging.critical("Cannot connect to MongoDB database and collection. Config incorrect?")
    sys.exit()

# get the tweet cursor
logging.info("Getting tweets...")
cursor = db.tweets.find({'locinf.mi.test': {'$ne': None}})


distances = []
insides = []

for doc in cursor:
    print ("Proc:", doc['user']['screen_name'])
    if doc["geo"] is None:
        continue

    point = (doc["geo"]["coordinates"][1], doc["geo"]["coordinates"][0])
    poly = eval(doc["locinf"]["mi"]["test"]["poly"])

    p = Polygon()
    for i in poly:
        p.addContour(i)

    try:
        center = p.center()
    except PolygonError:
        insides.append(False)
        print("Failed centering.")
        continue

    inside = p.isInside(point[0], point[1])
    insides.append(inside)

    distance = vincenty(point, center).km
    distances.append(distance)

    print("Inside:", ('Y' if inside else 'N'), "- Distance:", distance)

    # polyplotter.polyplot(poly, [point, point, point, center])

print(insides)
print(distances)

print("Insides:", len(insides))
print("Distances:", len(distances))
print("Mean distance from polygon center:", sum(distances) / len(distances))
print("Fraction within polygon:", sum(insides) / len(insides))
