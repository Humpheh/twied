import logging
import time
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing.context import TimeoutError
from multiprocessing import Pool

from pymongo import MongoClient

import polyplotter
import twieds
import multiind.indicators as indicators
from multiind import polystacker


def add_ind(task):
    ind = task[0]
    field = task[1]

    f_field = field[:50].encode('utf8') if isinstance(field, str) else field

    start = time.clock()
    logging.info("%10s <- Value: %-50s" % (type(ind).__name__[:-9], f_field))
    result = ind.get_loc(field)
    logging.info("%10s -> Took %.2f seconds. (%i polys)" % (
        type(ind).__name__[:-9], (time.clock() - start), len(result))
    )
    return result


def process_tweet(tweet, indis):
    #tweet, indis = data

    logging.info("Processing tweet %s", tweet['_id'])

    app_inds = [
        (indis['ms'], tweet['text']),
        (indis['lf'], tweet['user']['location']),
        (indis['ws'], tweet['user']['url']),
        (indis['co'], tweet['user']['location']),
        (indis['tz'], tweet['user']['time_zone']),
        (indis['to'], tweet['user']['utc_offset'])
    ]

    pool = ThreadPool(6)
    polys = pool.map(add_ind, app_inds)

    logging.info('Intersecting polygons...')
    new_polys, maxval = polystacker.infer_location(polys)
    logging.info('Polygon intersection complete.')

    # polyplotter.polyplot(polygons=new_polys, points=[])

    pool.close()
    pool.join()

    return new_polys, maxval, tweet


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
    logging.info("Setup indicators.")

    # connect to the mongodb
    logging.info("Connecting to database...")
    client = MongoClient()
    db = client.twitter
    logging.info("Connected to database.")

    # get the tweet cursor
    cursor = db.tweets.find()

    worker_count = 1
    workers = ThreadPool(processes=worker_count)

    waiting = []
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
                    db.tweets.update_one({'_id': tweet['_id']}, {
                        '$set': {
                            'locinf.mi.poly': str(pointarr),
                            'locinf.mi.weight': maxval
                        }
                    })
                except TimeoutError:
                    pass
            time.sleep(0.1)

        logging.info("Adding new process...")
        res = workers.apply_async(process_tweet, (doc, inds))

        waiting.append(res)

