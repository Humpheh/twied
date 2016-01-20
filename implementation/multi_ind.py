import logging
from multiprocessing.dummy import Pool as ThreadPool

from pymongo import MongoClient

from multiind import (
    messageindicator, tzindicator, tzoffindicator,
    locfieldindicator, coordinateindicator, websiteindicator
)
import twieds
import polyplotter
import polyunion2
import time

config = twieds.setup("logs/locinf.log", "settings/locinf.ini")

# setup the indicators
logging.info("Setting up indicators...")
ms_ind = messageindicator.MessageIndicator(config)
tz_ind = tzindicator.TZIndicator(config)
to_ind = tzoffindicator.TZOffsetIndicator(config)
lf_ind = locfieldindicator.LocFieldIndicator(config)
co_ind = coordinateindicator.CoordinateIndicator(config)
ws_ind = websiteindicator.WebsiteIndicator(config)
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
    logging.info("%10s -> Took %.2f seconds. (%i poly, %i point)" % (
        type(ind).__name__[:-9], (time.clock() - start),
        len(result[0]), len(result[1])
    ))
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

    res = pool.map(add_ind, indicators)

    polys = []
    points = []
    for i in res:
        polys += i[0]
        points += i[1]

    print ([type(p) for p in polys])

    logging.info('Intersecting polygons...')
    new_polys = polyunion2.get_top(polys)
    logging.info('Polygon intersection complete. %i highest areas' % len(new_polys))

    for i in new_polys:
        print(i)

    ply = []
    for p in new_polys:
        for c in range(len(p.polygon)):
            ply.append(p.polygon[c])
    polyplotter.polyplot(polygons=ply, points=[])
    #polyplotter.d_polyplot(polyold=polys, polynew=new_polys)

pool.close()
pool.join()
