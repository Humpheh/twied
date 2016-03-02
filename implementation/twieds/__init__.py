import configparser
import logging
import os
import sys
import argparse


def setup(logfile, settingsfile, printlevel=logging.INFO):
    setup_logger(logfile, printlevel)

    config = configparser.ConfigParser()
    config.read(settingsfile)
    return config


def setup_logger(filename, printlevel=logging.INFO):
    """
    Function to setup a logger to console and file.
    :param filename: the filename to output to, false for no file output
    """
    # setup the logger
    logformatstr = "%(asctime)s [%(threadName)-11s] %(levelname)-7s - %(message)s"
    logformat = logging.Formatter(logformatstr)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # output the logging to the stdout
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logformat)
    stream_handler.setLevel(printlevel)
    root_logger.addHandler(stream_handler)

    # output the logging to a file
    if not filename == False:
        file_handler = logging.FileHandler(filename)
        file_handler.setFormatter(logformat)
        file_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)

    logging.info("-----------")
    logging.info("Initialised logging for: {0} {1} {2}".format(filename, sys.argv[0], os.getpid()))
    logging.info("-----------")


def setup_mi_args(settingsfile):
    config = configparser.ConfigParser()
    config.read(settingsfile)

    parser = argparse.ArgumentParser(description="Run a Multi-Indicator location inference thread")

    parser.add_argument(
        '-infid', help='the id of the inference to store with the inferred location',
        required=True
    )
    parser.add_argument(
        '-field', help='the fieldname to store the inferred location in',
        required=True
    )
    parser.add_argument(
        '-test', type=bool, nargs='?', help='if true, will ignore the geotag on the tweet object',
        default=False
    )
    parser.add_argument(
        '-logfile', help='the logfile to output to',
        default="logs/mi_test.log"
    )
    parser.add_argument(
        '-geo', help='geonames username to use for inference',
        default=config.get('geonames', 'user')
    )
    parser.add_argument(
        '-alc', nargs='+', type=int, help='the allocation ids to infer for'
    )
    parser.add_argument(
        '-db', help='address of the database',
        default=config.get('mongo', 'address')
    )
    parser.add_argument(
        '-port', type=int, help='port of the database',
        default=config.get('mongo', 'port')
    )
    parser.add_argument(
        '-coll', help='database and collection name seperated by a dot (eg, twitter.tweets)',
        default=config.get('mongo', 'database') + "." + config.get('mongo', 'collection')
    )
    parser.add_argument(
        '-workers', help='the number of simulatenous threads to run',
        default=config.get('multiindicator', 'workers')
    )
    parser.add_argument(
        '-gadmdb', help='the gadm polydb path',
        default=config.get('multiindicator', 'gadm_polydb_path')
    )
    parser.add_argument(
        '-tldcsv', help='the tld csv file',
        default=config.get('multiindicator', 'tld_csv')
    )

    return config, parser.parse_args()
