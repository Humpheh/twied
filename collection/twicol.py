import sys
import time

from pymongo import MongoClient
from twicol import *

config = setup("twicol.log", "settings.ini")

# if running as a script
if __name__ == "__main__":
    logging.info("Starting twicol...")

    # connect to the MongoDB
    logging.info("Connecting to MongoDB...")
    client = MongoClient(config.get("mongo", "address"), config.getint("mongo", "port"))
    logging.info("Connected to MongoDB")

    # select the database and collection based off config
    try:
        db = client[config.get("mongo", "database")]
        col = db[config.get("mongo", "collection")]
    except:
        logging.critical("MongoDB collection and database invalid")
        sys.exit()

    # get the twitter API settings
    try:
        api_settings = config._sections['twitter']
    except KeyError:
        logging.critical("Twitter API settings not defined in config")
        sys.exit()

    # setup thread to output counts
    count_interval = config.getint("logging", "interval", fallback=5)
    tweet_interval = config.getint("logging", "tweetintervals", fallback=2*6*60)
    count_thread = CounterThread(api_settings, count_interval, tweet_interval)
    count_thread.start()

    logging.info ("Count interval: {0}s".format(count_interval))
    logging.info ("Tweet interval: {0} counts".format(tweet_interval))

    # setup the threads for the collections
    tweet_threads = []
    col_items = config.items("collections")
    for key, string in col_items:
        tt = TweetThread(col, count_thread, key, string, **api_settings)
        tt.start()
        tweet_threads.append(tt)
        break # only support for 1 thread at the moment

    twicol.send_tweet(api_settings, "Started twicol...")

    try:
        while True:
            time.sleep(1000)
    except:
        logging.info("Exception caught...")
        pass
    finally:
        # if excepted, close all threads
        logging.info("Stopping collection:")
        for t in tweet_threads:
            t.stop()
        count_thread.shutdown()

    # wait until all threads have stopped
    for t in tweet_threads:
        t.join()
    count_thread.join()
    logging.info("Collection stopped")
