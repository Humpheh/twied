import logging
import sys
import threading
import time

from datetime import datetime
from twython import TwythonStreamer
import twicol




class TweetThread(threading.Thread):
    """
    Thread class which handles the creation and running of the TweetStreamer.
    """
    def __init__(self, db, counter, name, trackstr, **kargs):
        super().__init__()
        self.name = "TweetThread_" + name
        self.stream = TweetStreamer(db, name, counter, **kargs)
        self.trackstr = trackstr
        self.dorun = True

    def run(self):
        @twicol.exception_repeat
        def m():
            if not self.dorun:
                return
            try:
                logging.info("Starting to track: {0}".format(self.trackstr))
                self.stream.statuses.filter(track=self.trackstr)
            except:
                e = sys.exc_info()[0]
                logging.warning("Error: {0}".format(e))
                raise e

        while self.dorun:
            m()

    def stop(self):
        logging.info("Shutting down thread...")
        self.stream.disconnect()
        self.dorun = False


class CounterThread(threading.Thread):
    """
    Thread class which logs the number of tweets recieved in intervals.
    """
    def __init__(self, api_settings, interval = 5, rep_interval = 2):
        super().__init__()
        self.name = "CountThread"
        self.lock = threading.Lock()

        self.counts = {}
        self.countsl = {}
        self.repcount = 0
        self.starttime = time.time()
        self.dorun = True

        self.interval = interval
        self.rep_interval = rep_interval
        self.api_settings = api_settings

    def add_count(self, name):
        with self.lock:
            try: self.counts[name] += 1
            except: self.counts[name] = 1

            try: self.countsl[name] += 1
            except: self.countsl[name] = 1

    def run(self):
        while self.dorun:
            time.sleep(self.interval)
            self.repcount += 1
            with self.lock:
                for k, v in self.counts.items():
                    logging.info("Collected tweets - {0}: {1}".format(k, v))
                self.counts = {}

                if self.repcount >= self.rep_interval:
                    twicol.send_tweet(self.api_settings, self.get_tweet_report())
                    self.repcount = 0
                    self.countsl = {}

    def get_tweet_report(self):
        status = "Last {0} mins - {1}\nUptime - {2}"
        st_tweets = ", ".join(['%s: %i' % (k, v) for k, v in self.countsl.items()])
        st_time = (self.interval * self.rep_interval) / 60

        uptime = time.time() - self.starttime
        m, s = divmod(uptime, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        st_uptime = "%d:%d:%02d:%02d" % (d, h, m, s)

        return status.format(str(st_time), st_tweets, st_uptime)

    def shutdown(self):
        self.dorun = False
