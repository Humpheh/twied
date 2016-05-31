from geopy.distance import vincenty
from itertools import product
from collections import defaultdict


class GeoGrid:
    """
    Simple class which stores tweets in a grid storage system for faster
    retrieval of neighbouring tweets.

    The :func:`add_tweet` method will add a tweet to a cell based on its
    coordinate. Will store the tweet in the cell of the coordinate and the
    surrounding cells. The cell key the tweet is stored in will be the int
    value of the coordinates. The :func:`get_surrounding` method will retrieve
    the tweets within a cell, meaning tweets in surrounding cells are also
    included.

    .. note:: this class is not useful if the event radius parameter is
        too large.
    """

    def __init__(self):
        """
        Setup the geogrid.
        """
        self.areas = defaultdict(list)
        self.tests = list(product([-1, 0, 1], repeat=2))

    @staticmethod
    def get_str(coord):
        """
        Gets a string of the lat and lon integer values of the coordinate to
        for fast indexing using a dictionary.

        :Example:

        >>> g = GeoGrid()
        >>> g.get_str((50.734910, -3.533687))
        '50,-3'

        :param coord: Tuple of the (lat, lon) of the coordinate.
        :type coord: tuple/list, float
        :return: String of the key for the coordinate.

        .. note:: this function does not round the values of the coordinates.
        """
        return "%.1d,%.1d" % (coord[0], coord[1])

    def add_tweet(self, tweet):
        """
        Add a tweet dictionary to the cell of its coordinates and the
        surrounding cells. Uses the :func:`get_str` method to calculate
        the cells the tweet will be stored in.

        :param tweet: Dictionary of tweet information.
        :type tweet: dict
        """
        coord = tweet['_coord']

        for x in self.tests:
            newc = self.get_str([(coord[0] - x[0]), (coord[1] - x[1])])
            self.areas[newc].append(tweet)

    def remove_tweet(self, tweet):
        """
        Removes a tweet dictionary from all cells it is in.

        :param tweet: Dictionary of tweet information.
        :type tweet: dict

        .. note:: the tweet dictionary must be the same object as the one
            added using the :func:`add_tweet` method.
        """
        coord = tweet['_coord']

        for x in self.tests:
            newc = self.get_str([(coord[0] - x[0]), (coord[1] - x[1])])
            try:
                self.areas[newc].remove(tweet)
            except (KeyError, ValueError):
                pass

    def get_surrounding(self, tweet):
        """
        Gets the tweets within a cell based on the coordinate of the tweet.
        As tweets area stored in surrounding cells, will get the tweets
        surrounding this cell also.

        :param tweet: Dictionary of tweet information.
        :type tweet: dict
        :return: Surrounding tweet dictionaries.
        :rtype: list, dict
        """
        try:
            return self.areas[self.get_str(tweet['_coord'])]
        except KeyError:
            return []


class ClusterCreatorGrid:
    """
    Class to manage the creation of clusters from tweets. This is a
    alternative implementation of the :class:`ClusterCreator` class
    which uses a :class:`GeoGrid` for more efficient comparisons of
    nearby tweets.

    Tweets are fed in through the :func:`process_tweet` method. These
    are compared with the current unclustered tweets and a cluster is
    created if the required number of tweets were posted within a
    certain timeframe and radius.

    Class also manages a list of unclustered tweets. Tweets are added
    using the :func:`add_unclustered` method. The :func:`process_tweet`
    method will remove tweets from the unclustered set if they are added
    to a cluster or if the difference between the times are greater
    than the threshold.

    .. seealso:: :class:`ClusterCreator`, less efficient version of
        this class which examines all unclustered tweets.
    .. note:: This class will not work well for large cluster radiuses,
        instead :class:`ClusterCreator` should be used.
    """

    def __init__(self, clsman):
        """
        Create the cluster manager.

        :param clsman: The cluster managaer object.
        :type clsman: ClusterManager
        """
        self.clsman = clsman
        self.grid = GeoGrid()

    def process_tweet(self, tweet):
        """
        Take a tweet and attempt to create a new cluster.

        :param tweet: Dictionary of tweet information.
        :return: Whether a cluster has been created or not.
        """
        # Use the GeoGrid to get the tweets to search in.
        searchspace = self.grid.get_surrounding(tweet)

        # Keep a list of tweets to remove after this tweet has been processed
        toremove = []

        # Keep a list of tweets that could be part of a new cluster
        candidates = [tweet]

        for t in searchspace:
            # Check if tweets were within time and radius
            dist = vincenty(tweet['_coord'].rev(), t['_coord'].rev()).km
            time = abs(tweet[self.clsman.tsfield] - t[self.clsman.tsfield])

            if dist < self.clsman.radius and time < self.clsman.timediff:
                # Tweet is within radius and time
                candidates.append(t)
            elif time > self.clsman.timediff:
                # Tweet is older than the max age so remove from unclustered
                toremove.append(t)

        # Remove old tweets
        for x in toremove:
            self.grid.remove_tweet(x)

        # If have enough candidates to create a cluster
        if len(candidates) >= tweet['_popreq']:
            # Remove candidates from unclustered
            for x in candidates:
                self.grid.remove_tweet(x)

            # Create new cluster
            self.clsman.add_cluster(candidates, tweet)
            return True
        else:
            # Not enough candidates to create cluster
            return False

    def add_unclustered(self, tweet):
        """
        Add a tweet to the list of unclustered tweets.

        :param tweet: Dictionary of tweet information.
        """
        self.grid.add_tweet(tweet)

    def __str__(self):
        """
        String representation of the number of unclustered tweets.
        """
        return "<ClusterCreatorGrid: %i areas>" % len(self.grid.areas)