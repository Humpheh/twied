import sys

from .collection import *
from .counters import *


def exception_repeat(func):
    """
    Function decorator that retrys the function if it throws an exception
    after a short interval. Interval grows exponentially the more times
    the function throws an exception. Initial time is 0.5 seconds.

    :param func: The function to wrap.
    """
    def func_wrapper(timer=0.5):
        try:
            func()
        except:
            try:
                time.sleep(timer)
            except:
                return
            err = sys.exc_info()[0]
            ntimer = timer * 2 if timer <= 32 else 64
            logging.warning("Exception caught in repeat method: {0}".format(err))
            logging.warning("Waiting for {0}s before retrying...".format(ntimer))
            func_wrapper(ntimer)
    return func_wrapper

