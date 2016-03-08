import logging
import time
import sys

from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing.context import TimeoutError
from configparser import NoOptionError

from pymongo import MongoClient
from pymongo.errors import CursorNotFound

import polyplotter
import twieds
import multiind.indicators as indicators
from multiind import polystacker


def add_ind(task):
    ind = task[0]
    field = task[1]

    f_field = field[:50].encode('utf8') if isinstance(field, str) else field

    start = time.clock()
    logging.debug("%10s <- Value: %-50s" % (type(ind).__name__[:-9], f_field))
    result = ind.get_loc(field)
    logging.debug("%10s -> Took %.2f seconds. (%i polys)" % (
        type(ind).__name__[:-9], (time.clock() - start), len(result))
    )
    return result


def process_tweet(twt, indis):
    logging.info("%s: Starting inference...", twt['_id'])

    app_inds = [
        (indis['ms'], twt['text']),
        (indis['lf'], twt['user']['location']),
        (indis['ws'], twt['user']['url']),
        (indis['co'], twt['user']['location']),
        (indis['tz'], twt['user']['time_zone']),
        (indis['to'], twt['user']['utc_offset']),
        # (indis['tg'], twt['geo'])
    ]

    pool = ThreadPool(6)
    polys = pool.map(add_ind, app_inds)

    logging.info("%s: Intersecting polygons for tweet...", twt['_id'])
    new_polys, max_val = polystacker.infer_location(polys)
    logging.info("%s: Polygon intersection complete.", twt['_id'])

    pool.close()
    pool.join()

    return new_polys, max_val, twt


# must run this as a script
if __name__ == "__main__":
    config = twieds.setup("logs/mi_test.log", "settings/locinf.ini")

    # setup the indicators
    logging.info("Setting up indicators...")
    inds = dict()
    inds['ms'] = indicators.MessageIndicator(config)
    inds['tz'] = indicators.TZIndicator(config)
    inds['to'] = indicators.TZOffsetIndicator(config)
    inds['lf'] = indicators.LocFieldIndicator(config)
    inds['co'] = indicators.CoordinateIndicator(config)
    inds['ws'] = indicators.WebsiteIndicator(config)
    # inds['tg'] = indicators.GeotagIndicator(config)
    logging.info("Setup indicators.")

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

    # id of the test
    testid = 2

    worker_count = config.getint("multiindicator", "workers")
    workers = ThreadPool(processes=worker_count)

    try:
        vals = eval(sys.argv[1])
        if not all(isinstance(item, int) for item in vals):
            raise
    except:
        logging.critical("Need allocation arguments as list")
        sys.exit()

    counter = 0
    waiting = []
    while True:
        # get the tweet cursor
        cursor = col.find({'geo': {'$ne': None}, 'locinf.mi.test.id': {'$ne': testid}, 'locinf.mi.test.alloc': {'$in': vals}})

        try:
            for doc in cursor:
                while len(waiting) > worker_count:
                    for i in waiting:
                        try:
                            result, maxval, tweet = i.get(timeout=0.02)
                            waiting.remove(i)

                            # process the data
                            pointarr = []
                            for c in result:
                                pointarr.append(c)

                            # store the polygon in the database
                            col.update_one({'_id': tweet['_id']}, {
                                '$set': {
                                    'locinf.mi.test.poly': str(pointarr),
                                    'locinf.mi.test.weight': maxval,
                                    'locinf.mi.test.id': testid
                                }
                            })
                            counter += 1
                            logging.info("=== Tweets processed: %5i ===" % counter)
                        except TimeoutError:
                            pass
                    time.sleep(0.1)

                logging.info("Adding new process...")
                res = workers.apply_async(process_tweet, (doc, inds))

                waiting.append(res)
            break
        except CursorNotFound:
            logging.error("Cursor not found, retrying...")
            continue

