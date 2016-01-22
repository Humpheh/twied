import logging
import time
from multiprocessing.dummy import Pool as ThreadPool

from pymongo import MongoClient

import polyplotter
import twieds
import multiind.indicators as indicators
from multiind import polystacker

config = twieds.setup("logs/locinf.log", "settings/locinf.ini")

# setup the indicators
logging.info("Setting up indicators...")
ms_ind = indicators.MessageIndicator(config)
tz_ind = indicators.TZIndicator(config)
to_ind = indicators.TZOffsetIndicator(config)
lf_ind = indicators.LocFieldIndicator(config)
co_ind = indicators.CoordinateIndicator(config)
ws_ind = indicators.WebsiteIndicator(config)
logging.info("Setup indicators.")

# connect to the mongodb
logging.info("Connecting to database...")
client = MongoClient()
db = client.twitter
logging.info("Connected to database.")

# get the tweet cursor
cursor = db.tweets.find()


def add_ind(task):
    ind = task[0]
    field = task[1]

    start = time.clock()
    logging.info("%10s <- Value: %-50s" % (type(ind).__name__[:-9], field))
    result = ind.get_loc(field)
    logging.info("%10s -> Took %.2f seconds. (%i polys)" % (
        type(ind).__name__[:-9], (time.clock() - start), len(result))
    )
    return result


# loc field and ms_ind first

pool = ThreadPool(4)

for doc in cursor:

    logging.info("Processing tweet %s", doc['_id'])

    indicators = [
        (ms_ind, doc['text']),
        (lf_ind, doc['user']['location']),
        (ws_ind, doc['user']['url']),
        (co_ind, doc['user']['location']),
        (tz_ind, doc['user']['time_zone']),
        (to_ind, doc['user']['utc_offset'])
    ]

    polys = pool.map(add_ind, indicators)

    from pprint import pprint
    #polyplotter.d_polyplot(polyold=polys, polynew=new_polys)
    pprint ([type(p) for p in polys])

    logging.info('Intersecting polygons...')
    new_polys = polystacker.infer_location(polys)
    logging.info('Polygon intersection complete. X highest areas')
    polyplotter.polyplot(polygons=new_polys, points=[])

pool.close()
pool.join()
