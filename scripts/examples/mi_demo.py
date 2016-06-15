import logging
import sys
import time
from configparser import NoOptionError
from multiprocessing.dummy import Pool as ThreadPool

from bson import objectid
from pymongo import MongoClient

import multiind.indicators as indicators
from multiind import polystacker
from scripts.examples import polyplotter, twieds


def add_ind(task):
    ind = task[0]
    field = task[1]

    f_field = field[:50].encode('utf8') if isinstance(field, str) else field

    start = time.clock()
    logging.info("%10s <- Value: %-50s" % (type(ind).__name__[:-9], f_field))
    result = ind.get_loc(field)
    logging.info("%10s -> Took %.2f seconds. (returned: %i polys)" % (
        type(ind).__name__[:-9], (time.clock() - start), len(result))
    )
    return result


def process_tweet(twt, indis):
    logging.info("Processing tweet %s", twt['_id'])

    app_inds = [
        (indis['ms'], twt['text']),
        (indis['lf'], twt['user']['location']),
        (indis['ws'], twt['user']['url']),
        (indis['co'], twt['user']['location']),
        (indis['tz'], twt['user']['time_zone']),
        (indis['to'], twt['user']['utc_offset']),
        (indis['tg'], twt['geo'])
    ]

    pool = ThreadPool(6)
    polys = pool.map(add_ind, app_inds)

    start = time.clock()
    logging.info('Intersecting polygons...')
    new_polys, max_val = polystacker.infer_location(polys, demo=True)
    logging.info('Polygon intersection complete. Took %.2f seconds.' % (time.clock() - start))

    pointarr = []
    for c in new_polys:
        pointarr.append(c)
    polyplotter.polyplot(pointarr, [])

    pool.close()
    pool.join()

    return new_polys, max_val, twt


# must run this as a script
if __name__ == "__main__":
    config = twieds.setup("logs/locinf.log", "settings/locinf.ini")

    # setup the indicators
    logging.info("Setting up indicators...")
    inds = dict()
    inds['ms'] = indicators.MessageIndicator(config)
    inds['tz'] = indicators.TZIndicator(config)
    inds['to'] = indicators.TZOffsetIndicator(config)
    inds['lf'] = indicators.LocFieldIndicator(config)
    inds['co'] = indicators.CoordinateIndicator(config)
    inds['ws'] = indicators.WebsiteIndicator(config)
    inds['tg'] = indicators.GeotagIndicator(config)
    logging.info("Setup indicators.")

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

    tid = input("Specific ID? >")

    # get the tweet cursor
    if tid is None or tid == "":
        cursor = db.tweets.find()
    else:
        cursor = db.tweets.find({'_id': objectid.ObjectId(tid)})

    waiting = []
    for doc in cursor:
        result, maxval, tweet = process_tweet(doc, inds)
        if input("Next? > ") == 'q':
            sys.exit()

        """# process the data

        # store the polygon in the database
        db.tweets.update_one({'_id': tweet['_id']}, {
            '$set': {
                'locinf.mi.poly': str(pointarr),
                'locinf.mi.weight': maxval
            }
        })"""

