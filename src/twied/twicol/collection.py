import logging
import twied.twicol

from threading import Thread
from twython import TwythonStreamer
from datetime import datetime


class TweetStreamer(TwythonStreamer, Thread):
    """
    Threaded class which handles callbacks from the twython streamer and
    stores tweets in a MongoDB database.
    """

    def __init__(self, name, trackstr, db=None, callbacks=None, **kwargs):
        """
        Creates the TweetStreamer. This streamer collects tweets from the
        Twitter API and stores them in a MongoDB. Can also callback to functions.

        :param name: An indentifier for the collection.
        :type name: str
        :param trackstr: Search string for the twitter API.
        :type trackstr: str
        :param db: The MongoDB collection to put the tweet in. If this
            parameter is left as `None`, no database will be written to,
            instead only the `on_add` function will be called *(optional)*.
        :param callbacks: Functions called when a tweet is recieved.
            Can also be a list of functions which will all be called.
            Will pass three arguments (name, data, insert_id) being the
            collection name, tweet data and mongo insert id respectively
            into the function *(optional)*.
        :param **kwargs: Settings for the Twitter API. Suggested example
            arguments:

                * `app_key`
                * `app_secret`
                * `oauth_token`
                * `oauth_token_secret`

            (for more information see the :class:`twython.TwythonStreamer`
            documentation)

        :Example:

        Following example is the usage of the :class:`TweetStreamer` that
        prints out the ID of each tweet when it is recieved. As the db is None
        no storage of the tweets is performed. `api_settings` is a dictionary
        of the Twitter API settings.

        >>> def test(name, data, insertid):
        >>>     print("Inserted with ID: %s" % insertid)
        >>>
        >>> ts = TweetStreamer("test", "twitter", db=None, callbacks=test, **api_settings)
        >>> ts.start()

        """
        Thread.__init__(self)
        TwythonStreamer.__init__(self, **kwargs)
        self.db = db
        self.name = name
        self.trackstr = trackstr
        self.running = True

        if not type(callbacks) == list:
            self.callbacks = [callbacks]
        else:
            self.callbacks = callbacks

    def run(self):
        """
        Main thread loop.
        """
        self.running = True

        @twied.twicol.exception_repeat
        def ex_run():
            if not self.running:
                return
            try:
                logging.info("Starting to track: %s" % self.trackstr)
                self.statuses.filter(track=self.trackstr)
            except Exception as e:
                logging.warning("Exception in collection: %s" % e)
                raise e

        # Run the thread
        while self.running:
            ex_run()

    def stop(self):
        """
        Stop the tweet collection.
        """
        logging.info("Shutting down thread...")
        self.disconnect()
        self.running = False

    def on_success(self, data):
        """
        Function called when a tweet was successfully recieved from the API.

        :param data: The tweet data.
        """
        if 'text' not in data:
            logging.warning("Recieved tweet without text")
            return

        # Save the name of the collection task alongside the tweet data
        data['collection'] = self.name

        # Calculate a timestamp object from the data
        ts_float = float(data['timestamp_ms'])
        data['timestamp_obj'] = datetime.utcfromtimestamp(ts_float/1000)

        # Insert the tweet into the database
        insertid = None
        if self.db is not None:
            insertid = self.db.insert_one(data).inserted_id

        # Call the callback functions if exists
        if self.callbacks is not None:
            for f in self.callbacks:
                f(self.name, data, insertid)

    def on_error(self, status_code, data):
        """
        Called on error with recieving tweet.
        """
        logging.warning("Error recieving tweet: {0}".format(status_code))

    def on_timeout(self):
        """
        Called on timeout of the streaming API.
        """
        logging.error("Streaming request timed out")
