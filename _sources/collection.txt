:mod:`twied.twicol` --- Twitter Collection
==========================================

.. automodule:: twied.twicol
   :members:
   :undoc-members:

Collection
----------

.. automodule:: twied.twicol.collection
   :members:
   :undoc-members:

Counter
-------

.. automodule:: twied.twicol.counters
   :members:
   :undoc-members:

Example
-------

Below is an example file using the collection class to collect tweets which
contain the word 'Twitter'. This script saves these tweets in a MongoDB database
in the database 'test' and the collection 'coltest1'. A :class:`CounterThread` is also
created which ouputs the number of tweets collected in the previous 5 seconds.

.. note:: The API settings here have been altered so they are not valid. These would
    need to be created for your own app from the `Twitter API <https://apps.twitter.com/>`_.

.. code-block:: python

    import time

    from twied.twicol import TweetStreamer, CounterThread
    from pymongo import MongoClient

    # Save the Twitter API settings
    api_settings = {
        'app_key': 'wYHFS6G9fqVNxYwt53UNUcxT0',
        'app_secret': 'MU3r4yi2HGDrAbBma2syPpOvFOcWFxaUIiKmeySX8Ard80lr53',
        'oauth_token': '3950426785-SNgK3NmghSzdjLcJGRTAwQq3xyMait0bVQ6HVvV',
        'oauth_token_secret': 'x0FASasjEHqsSvLAZ3h6sqClPWtt54TcM78W8PLOJ1BLv',
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