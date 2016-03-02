from enum import Enum
import multiind.indicators as indicators
from multiind import polystacker
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing.context import TimeoutError
import logging
import time
from pymongo.errors import CursorNotFound


class Indicators(Enum):
    Message = 0
    TZ = 1
    TZOffset = 2
    LocField = 3
    Coordinate = 4
    Website = 5
    Geotag = 6


class InferThread:
    def __init__(self, dbcol, config, inf_id=None, test=False):
        # setup the indicators
        logging.info("Setting up indicators...")
        self.inds = dict()

        self.inds[Indicators.Message] = indicators.MessageIndicator(config)
        self.inds[Indicators.TZ] = indicators.TZIndicator(config)
        self.inds[Indicators.TZOffset] = indicators.TZOffsetIndicator(config)
        self.inds[Indicators.LocField] = indicators.LocFieldIndicator(config)
        self.inds[Indicators.Coordinate] = indicators.CoordinateIndicator(config)
        self.inds[Indicators.Website] = indicators.WebsiteIndicator(config)

        # if testing, dont use geotag inference
        if not test:
            self.inds[Indicators.Geotag] = indicators.GeotagIndicator(config)
        logging.info("Setup indicators.")

        # store variables
        self.test = test
        self.config = config
        self.dbcol = dbcol
        self.inf_id = inf_id

        # setup the workers
        self.worker_count = config.getint("multiindicator", "workers")
        self.workers = ThreadPool(processes=self.worker_count)

    def infer(self, query, field='locinf.mi'):
        counter = 0
        waiting = []
        while True:
            # get the tweet cursor
            cursor = self.dbcol.find(query)

            try:
                for doc in cursor:
                    while len(waiting) > self.worker_count:
                        for i in waiting:
                            try:
                                result, li, lp, maxval, tweet = i.get(timeout=0.02)
                                waiting.remove(i)

                                # process the data
                                pointarr = []
                                for c in result:
                                    pointarr.append(c)

                                # store the polygon in the database
                                self.dbcol.update_one({'_id': tweet['_id']}, {
                                    '$set': {
                                        field + '.poly': str(pointarr),
                                        field + '.weight': maxval,
                                        field + '.id': self.inf_id,
                                        field + '.len.inds': li,
                                        field + '.len.polys': lp
                                    }
                                })
                                counter += 1
                                logging.info("=== Tweets processed: %5i ===" % counter)
                            except TimeoutError:
                                pass
                        time.sleep(0.1)

                    logging.info("Adding new process...")
                    res = self.workers.apply_async(self.process_tweet, (doc,))

                    waiting.append(res)
                break
            except CursorNotFound:
                logging.error("Cursor not found, retrying...")
                continue

    def add_ind(self, task):
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

    def process_tweet(self, twt):
        logging.info("%s: Starting inference...", twt['_id'])

        app_inds = [
            (self.inds[Indicators.Message], twt['text']),
            (self.inds[Indicators.LocField], twt['user']['location']),
            (self.inds[Indicators.Website], twt['user']['url']),
            (self.inds[Indicators.Coordinate], twt['user']['location']),
            (self.inds[Indicators.TZ], twt['user']['time_zone']),
            (self.inds[Indicators.TZOffset], twt['user']['utc_offset']),
        ]
        if not self.test:
            app_inds.append((self.inds[Indicators.Geotag], twt['geo']))

        pool = ThreadPool(6)
        polys = pool.map(self.add_ind, app_inds)

        # count inds and polys
        leninds = sum([p != [] for p in polys])
        lenpolys = sum([len(polys) for p in polys])

        logging.info("%s: Intersecting polygons for tweet...", twt['_id'])
        new_polys, max_val = polystacker.infer_location(polys)
        logging.info("%s: Polygon intersection complete.", twt['_id'])

        pool.close()
        pool.join()

        return new_polys, leninds, lenpolys, max_val, twt
