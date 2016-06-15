import time

from twied.twicol import TweetStreamer, CounterThread
from pymongo import MongoClient

# Save the Twitter API settings
api_settings = {
    'app_key': 'wYH9n6G9fqaNxYwt50UNUcxT0',
    'app_secret': 'MU6g9yi2HGDrAbBma2syPpOvFOcWFxAUIiKmeySX8Ayf80lr53',
    'oauth_token': '3950691015-SNgK3NmghSzdjLcJDbBAwQq3xyMait0bVQ6HVvV',
    'oauth_token_secret': 'x0KOBasjEHqsSvLAZ3h6sqClPWtt15TcM78W8LXBJ1BLv',
}

search_str = "twitter"

# Connect to the MongoDB and the correct collection
client = MongoClient()
collection = client['test']['coltest1']

# Setup the counter thread to output status count ever 5 secs
counter = CounterThread(5, lambda count: print("Recieved %i tweets in last 5 seconds" % count))

# Setup the tweet streamer to listen to tweets with 'twitter' in them
ts = TweetStreamer("test", search_str, db=collection, callbacks=counter, **api_settings)

# Start the threads
ts.start()
counter.start()

try:
    # Wait
    while True:
        time.sleep(1000)
except Exception:
    print("Exception caught...")
    pass
finally:
    # If excepted, close all threads
    print("Stopping collection.")
    counter.stop()
    ts.stop()