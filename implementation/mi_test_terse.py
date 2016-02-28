import logging
import sys
import time

from configparser import NoOptionError
from urllib3.exceptions import MaxRetryError

from pymongo import MongoClient

import twieds
from multiind.inference import InferThread
from multiind.indicators.locfieldindicator import GeonamesException
from multiprocessing import Process


# must run this as a script
def inf_thread(testid, vals, geonames=None):
    config = twieds.setup("logs/mi_test.log", "settings/locinf.ini")

    # connect to the MongoDB
    logging.info("Connecting to MongoDB...")
    client = MongoClient(config.get("mongo", "address"), config.getint("mongo", "port"))

    # select the database and collection based off config
    try:
        col = client[config.get("mongo", "database")]["geotweets"]  # config.get("mongo", "collection")]
    except NoOptionError:
        logging.critical("Cannot connect to MongoDB database and collection. Config incorrect?")
        sys.exit()

    if geonames is not None:
        config.set("geonames", "user", geonames)
    logging.info("Using Geonames user %s." % config.get("geonames", "user"))

    field = 'locinf.mi.test'

    query = {
        'geo': {'$ne': None},
        field + '.id': {'$ne': testid},
        field + '.alloc': {'$in': vals}
    }

    inf = InferThread(col, config, test=True, inf_id=testid)
    inf.infer(query, field=field)


if __name__ == "__main__":
    while True:
        # id of the test
        tid = 20160225
        tasks = [(tid, [0, 1], "humph"), (tid, [2, 3], "humpheh")]

        try:
            procs = []
            for i in tasks:
                p = Process(target=inf_thread, args=i)
                p.start()
                procs.append(p)

            for p in procs:
                p.join()

            # break if everything went correctly
            break
        except MaxRetryError:
            logging.warning("Got a MaxRetryError - sleeping for 2 mins...")
            time.sleep(2 * 60)  # sleep for 5 mins
        except GeonamesException:
            logging.warning("Got a GeonamesException - sleeping for 10 mins...")
            time.sleep(10 * 60)  # sleep for 10 mins
