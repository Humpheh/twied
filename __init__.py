import configparser
import logging
import __main__

from twicol.threads import *
from twicol.tweet import *

def setup_logger(filename = 'collector.log'):
    """
    Function to setup a logger to console and file.
    :param filename: (optional) the filename to output to
                     default = collector.log, false for no file output
    """
    # setup the logger
    logformatstr = "%(asctime)s [%(threadName)s] %(levelname)s - %(message)s"
    logformat = logging.Formatter(logformatstr)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # output the logging to the stdout
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logformat)
    root_logger.addHandler(stream_handler)

    # output the logging to a file
    if not filename == False:
        file_handler = logging.FileHandler(filename)
        file_handler.setFormatter(logformat)
        root_logger.addHandler(file_handler)

    logging.info("-----------")
    logging.info("Initialised logging for: {0}".format(__main__.__file__))
    logging.info("-----------")


def exception_repeat(func):
    """
    Function decorator that retrys the function if it throws an exception
    after a short interval. Interval grows exponentially the more times
    the function throws an exception. Initial time is 0.5 seconds.
    """
    def func_wrapper(timer = 0.5):
        try:
            func()
        except:
            try:
                time.sleep(timer)
            except:
                return
            err = sys.exc_info()[0]
            ntimer = timer * 2 if timer <= 32 else 64
            logging.warning ("Exception caught in repeat method: {0}".format(err))
            logging.warning ("Waiting for {0}s before retrying...".format(ntimer))
            func_wrapper(ntimer)
    return func_wrapper


# setup configparser
config = configparser.ConfigParser()
config.read("settings.ini")
