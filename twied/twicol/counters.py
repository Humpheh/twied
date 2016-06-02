import time
import threading


class CounterThread(threading.Thread):
    """
    Threaded class which calls a callback at specified interval.
    Used with the :class:`TweetStreamer` class to gain a callback
    of the number of tweets collected in the previous interval.

    :Example:

    Below is an example usage of this class with the :class:`TweetThread`
    class.

    >>> def log(count):
    >>>     print("Last 5 seconds: %i tweets" % count)
    >>>
    >>> counter = CounterThread(5, log)
    >>> ts = TweetStreamer("test", "twitter", db=None, callbacks=counter, **api_settings)
    >>> ts.start()
    >>> counter.start()

    .. seealso:: :class:`TweetThread` shows the usage of the collection thread.
    """

    def __init__(self, interval_s, callbacks):
        """
        Initialise the counter.

        :param interval_s: The number of seconds between calling
            the callback function.
        :param callbacks: The function to call every `interval_s`
            seconds. Can also be a list of functions. The function
            should take a single parameter which is the number of
            tweets recieved in the last interval.
        """
        super().__init__()
        self.name = "CountThread"

        self.starttime = time.time()
        self.interval_s = interval_s
        self.dorun = True

        self.count = 0

        if not type(callbacks) == list:
            self.callbacks = [callbacks]
        else:
            self.callbacks = callbacks

    def __call__(self, name, data, insert_id):
        """
        Function to be passed to the :class:`TweetStreamer` as a
        callback. The parameters are ignored here.
        """
        self.count += 1

    def run(self):
        """
        Run the counter thread.
        """
        while self.dorun:
            time.sleep(self.interval_s)

            for f in self.callbacks:
                f(self.count)
            self.count = 0

    def stop(self):
        """
        Stop the counter thread at the next count. Note that this
        may be a delayed finish as it will stop at the next time
        the call back function is checked.
        """
        self.dorun = False
