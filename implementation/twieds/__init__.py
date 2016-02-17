import configparser
import logging
import os
import sys

def setup(logfile, settingsfile):
    setup_logger(logfile)

    config = configparser.ConfigParser()
    config.read(settingsfile)
    return config

def setup_logger(filename):
    """
    Function to setup a logger to console and file.
    :param filename: (optional) the filename to output to
                     default = collector.log, false for no file output
    """
    # setup the logger
    logformatstr = "%(asctime)s [%(threadName)-11s] %(levelname)-7s - %(message)s"
    logformat = logging.Formatter(logformatstr)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # output the logging to the stdout
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logformat)
    stream_handler.setLevel(logging.INFO)
    root_logger.addHandler(stream_handler)

    # output the logging to a file
    if not filename == False:
        file_handler = logging.FileHandler(filename)
        file_handler.setFormatter(logformat)
        file_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)

    logging.info("-----------")
    logging.info("Initialised logging for: {0} {1}".format(sys.argv[0], os.getpid()))
    logging.info("-----------")
