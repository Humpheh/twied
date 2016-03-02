import twieds
import logging
import sys

from pymongo import MongoClient
from configparser import NoOptionError

from multiind.inference import InferThread

if __name__ == "__main__":
    # setup argpase, configparse and logger
    config, args = twieds.setup_mi_args("settings/locinf.ini")
    twieds.setup_logger(args.logfile)

    print(args)

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
        'geo': {'$ne': None},
        field + '.id': {'$ne': args.testid},
        field + '.alloc': {'$in': args.alc}
    }

    inf = InferThread(col, config, test=True, inf_id=args.testid)
    inf.infer(query, field=field)