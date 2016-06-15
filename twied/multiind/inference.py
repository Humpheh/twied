import logging
import datetime
import time

from enum import Enum
from . import polystacker
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing.context import TimeoutError
from pymongo.errors import CursorNotFound

from . import indicators as indicators


class Indicators(Enum):
    """
    Simple enum which stores values for each of the Indicators.
    """
    Message = 0
    TZ = 1
    TZOffset = 2
    LocField = 3
    Coordinate = 4
    Website = 5
    Geotag = 6


class InferThread:
    """
    This class manages the inference of users by creating and managing multiple threads
    of indicators. The class will setup a number of threads to simultaneously infer
    tweets. Each of these threads will in turn setup their own threads to contact each
    of the indicators.

    This class takes a MongoDB database which the tweets will be retrieved from, a config
    object which contains all of the configuration for the indicators. The class will setup
    all of the indicators in the package:

        * :class:`MessageIndicator` - uses message field to find topoynms.
        * :class:`TZIndicator` - uses the timezone the user is in.
        * :class:`TZOffsetIndicator` - uses the timezone offset the user is in.
        * :class:`LocFieldIndicator` - uses topoynms in the users location field.
        * :class:`CoordinateIndicator` - finds coordinates in the users location field.
        * :class:`WebsiteIndicator` - uses the TLD of the users website address.
        * :class:`GeotagIndicator` - uses the geotag on the users tweet.

    Each of these indicators will be contacted to return estimations of the location of the
    user. These are then 'stacked' to determine an area where the weight is the higest. This
    class will write the inferred polygon and other information back onto the tweet object
    in the MongoDB.

    .. note:: This class is not multi-core, which would need to be setup manually or
        by using multiple processes of this class pointing at different sections of the
        data.
    """

    def __init__(self, dbcol, config, inf_id=None, proc_id="default", test=False, tweetfunc=None, tweetint=1000):
        """
        Initialise the MI location inference.

        :param dbcol: The MongoDB collection to recover tweets from.
        :param config: The :class:`configparser` object containing the configuration.
        :param inf_id: The inference ID. Has no impact on the inference but is stored
            in the database alongside the inferred location to act as a tag for the
            inference task which inferred the location.
        :param proc_id: The process name, also stored alongside the inferred location.
        :param test: If `True` will not use the :class:`GeotagIndicator`.
        :type test: bool
        :param tweetfunc: A function which is called every `tweetint` number of inferred
            tweets which passes a string of the current inference status.
        :param tweetint: The number of tweets before each call of the `tweetfunc`.
        """
        # Setup the indicators
        logging.info("Setting up indicators...")
        self.inds = dict()

        self.inds[Indicators.Message] = indicators.MessageIndicator(config)
        self.inds[Indicators.TZ] = indicators.TZIndicator(config)
        self.inds[Indicators.TZOffset] = indicators.TZOffsetIndicator(config)
        self.inds[Indicators.LocField] = indicators.LocFieldIndicator(config)
        self.inds[Indicators.Coordinate] = indicators.CoordinateIndicator(config)
        self.inds[Indicators.Website] = indicators.WebsiteIndicator(config)

        # If testing, dont use geotag inference
        if not test:
            self.inds[Indicators.Geotag] = indicators.GeotagIndicator(config)
        logging.info("Setup indicators.")

        # Store variables
        self.test = test
        self.config = config
        self.dbcol = dbcol
        self.inf_id = inf_id
        self.proc_id = proc_id
        self.tweetint = tweetint
        self.tweetfunc = tweetfunc

        # Setup the workers
        self.worker_count = config.getint("multiindicator", "workers")
        self.workers = ThreadPool(processes=self.worker_count)

    def infer(self, query, field='locinf.mi'):
        """
        Starts the location inference task.

        :param query: The query used to select tweets from the MongoDB.
        :param field: The name of the field to write the inferred location
            to. For example with the field 'locinf.mi' (as default), the final
            polygon would be written to 'locinf.mi.poly'.
        """
        counter = 0
        waiting = []
        while True:
            # Get the tweet cursor
            cursor = self.dbcol.find(query)

            try:
                for doc in cursor:
                    while len(waiting) > self.worker_count:
                        for i in waiting:
                            try:
                                result, li, lp, maxval, tweet = i.get(timeout=0.02)
                                waiting.remove(i)

                                # Process the data
                                pointarr = []
                                for c in result:
                                    pointarr.append(c)

                                # Store the polygon in the database
                                self.dbcol.update_one({'_id': tweet['_id']}, {
                                    '$set': {
                                        field + '.poly': str(pointarr),
                                        field + '.weight': maxval,
                                        field + '.id': self.inf_id,
                                        field + '.pid': self.proc_id,
                                        field + '.len.inds': li,
                                        field + '.len.polys': lp,
                                        field + '.date': datetime.datetime.utcnow()
                                    }
                                })
                                counter += 1
                                logging.info("=== Tweets processed: %5i ===" % counter)

                                if counter % self.tweetint == 0 and self.tweetfunc is not None:
                                    tstr = "Infer process %s (%s)\n%i processed." % (self.inf_id, self.proc_id, counter)
                                    self.tweetfunc(tstr)

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
        """
        Processes a task. The task takes a tuple of a Indicator and a field. This
        method is used in parallel.

        :param task: The tuple of the Inidicator and the field.
        :return: The result of passing the field through the indicator.
        """
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
        """
        Process a single tweet.

        :param twt: The tweet object.
        :return: Tuple of the inferred polygons, the number of indicators with a result,
            the number of polygons returned, the maximum 'height' of the stacked polygons,
            and the tweet object.
        """
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
