import twieds
import logging
import sys
import time
import datetime

from pymongo import MongoClient
from configparser import NoOptionError
from urllib3.exceptions import MaxRetryError
from twython import Twython

from multiind.inference import InferThread
from multiind.indicators.locfieldindicator import GeonamesException

if __name__ == "__main__":
    # setup argpase, configparse and logger
    config, args = twieds.setup_mi_args("settings/locinf.ini")
    twieds.setup_logger(args.logfile)

    # print out the arguments to the logging file
    for arg in vars(args):
        logging.info("[arg] %-8s: %s" % (arg, getattr(args, arg)))

    logging.info("Are these correct? (Any input to continue)")
    try:
        input(">")
    except KeyboardInterrupt:
        logging.info("Inference cancelled.")
        sys.exit()
    logging.info("Continuing with inference...")

    # connect to the MongoDB
    logging.info("Connecting to MongoDB...")
    client = MongoClient(args.db, args.port)

    # select the database and collection based off config
    try:
        db_n, col_n = args.coll.split(".")
        col = client[db_n][col_n]
    except NoOptionError:
        logging.critical("Cannot connect to MongoDB database and collection. Config incorrect?")
        sys.exit()

    # store the argument variables in config to pass down
    config.set("geonames", "user", args.geo)
    config.set("multiindicator", "gadm_polydb_path", args.gadmdb)
    config.set("multiindicator", "tld_csv", args.tldcsv)
    config.set("multiindicator", "workers", args.workers)

    logging.info("Using Geonames user %s." % config.get("geonames", "user"))

    field = args.field  # 'locinf.mi.test'

    query = {
        field + '.id': {'$ne': args.infid},
        field + '.alloc': {'$in': args.alc}
    }

    api_settings = config._sections['twitter']
    twitter = Twython(**api_settings)

    def tweetstr(string):
        global twitter
        logging.info("Attemting to send tweet: {0}".format(string))
        twitter.update_status(status=string)
        logging.info("Tweet sent.")


    tweetstr("%s (%s)\nInference started\n%s" % (args.infid, args.pid, datetime.datetime.utcnow()))

    inf = InferThread(col, config, test=args.test, inf_id=args.infid, tweetfunc=tweetstr, tweetint=10000, proc_id=args.pid)
    while True:
        logging.info("Starting inference...")
        try:
            inf.infer(query, field=field)
            logging.info("Inference finished successfully.")
            tweetstr("@Humpheh %s - finished successfully." % args.pid)
            break
        except MaxRetryError:
            logging.warning("Got a MaxRetryError - sleeping for 2 mins...")
            time.sleep(2 * 60)  # sleep for 5 mins
        except GeonamesException:
            logging.warning("Got a GeonamesException - sleeping for 10 mins...")
            time.sleep(10 * 60)  # sleep for 10 mins
        except Exception as e:
            logging.error("Exception caught")
            tweetstr("@Humpheh %s - exited due to a %s." % (args.pid, type(e).__name__))
            raise
