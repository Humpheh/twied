import datetime
import logging

from geopy.distance import vincenty


class ClusterManager:
    """
    Class to manage detected clusters. Stores current active clusters
    along with expired clusters.
    """

    def __init__(self, field, tsfield, radius=10, timediff=datetime.timedelta(minutes=30),
                 maxage=datetime.timedelta(hours=6)):
        """
        Creates a cluster manager.

        :param field: The field in the tweet dictionary where the coordinates
            are stored.

            Can be passed a dot delimited string of the location of the
            location of the coordinate in the tweet dictionary.
        :type field: str
        :param tsfield: The field in the tweet dictionary where the timestamp
            field is stored. (This field cannot be dot delimited).
        :type tsfield: str
        :param radius: Maximum radius of the events (km). *(default 10km)*
        :type radius: float
        :param timediff: Maximum time difference between all tweets to create a
            cluster. *(default 30 minutes)*
        :type timediff: datetime.timedelta
        :param maxage: Maximum age of a cluster since the last new tweet before it
            is deleted. *(default 6 hours)*
        :type maxage: datetime.timedelta
        """
        self.clusters = []
        self.oldclusters = []
        self.geofield = field
        self.geofieldspl = field.split(".")
        self.tsfield = tsfield

        # Store the settings for the cluster
        self.radius = radius  # km
        self.timediff = timediff
        self.maxage = maxage

        self.lasttime = datetime.datetime.utcnow()

    def __iter__(self):
        """
        Returns iteration of current active clusters.

        :return: Current active clusters.
        """
        return iter(self.clusters)

    def __str__(self):
        """
        String representation of the ClusterManager with the number of current clusters.

        :return: String of the number of active clusters.
        """
        return "<ClusterManager: %i clusters, %i old clusters>" % (len(self.clusters), len(self.oldclusters))

    def get_coordinate(self, tweet):
        """
        Gets a :class:`Coordinate` object from a tweet which stores the values of the
        lat and long coordinates. Uses the field passed in during initialisation of this
        class to find the coordinate field in the tweet object.

        :param tweet: Dictionary of tweet information.
        :type tweet: dict
        :return: Coordinate object.
        :rtype: :class:`Coordinate`
        """
        # Traverses the tweet dictionary to the correct field
        cur_dict = tweet
        for x in range(len(self.geofieldspl) - 1):
            cur_dict = cur_dict.get(self.geofieldspl[x])

        coord = cur_dict[self.geofieldspl[-1]]
        return Coordinate(coord[1], coord[0])

    def add_cluster(self, tweets, maintweet):
        """
        Creates a new cluster and saves it. The `maintweet` parameter will be
        used as the center for the cluster.

        :param tweets: Tweets within the cluster.
        :param maintweet: Tweet which created the cluster.
        :return: The created cluster object.
        :rtype: :class:`TweetCluster`
        """
        newcls = TweetCluster(tweets, maintweet, self)
        logging.debug("Created cluster %s" % id(newcls))
        self.clusters.append(newcls)
        return newcls

    def remove_cluster(self, cluster):
        """
        Removes a cluster from the current active list and adds it to the
        list of old clusters.

        :param cluster: The :class:`TweetCluster` object to remove from the active list.
        :return: Whether the cluster was removed or not. If not in active set will
            return `False`.
        :rtype: bool
        """
        try:
            # Remove the cluster from the active and add to old
            self.clusters.remove(cluster)
            self.oldclusters.append(cluster)
            return True
        except ValueError:
            return False

    def merge_clusters(self, c1, c2):
        """
        Merges two clusters together. Will add of the information from
        `c1` to `c2` and then remove c2 from the active clusters.

        :param c1: First cluster to merge.
        :type c1: :class:`TweetCluster`
        :param c2: Second cluster to merge.
        :type c2: :class:`TweetCluster`
        """
        # Merging clusters
        c1.merge(c2)
        self.clusters.remove(c2)

    def get_all_clusters(self):
        """
        Gets a list of all clusters that have been created, including ones
        that have reached the maximum age.

        :return: List of clusters.
        :rtype: list
        """
        return self.oldclusters + self.clusters


class Coordinate:
    """
    Object to store the lat and lon coordinates and provides some methods
    to quickly access or reverse the list depending on the needs.
    """

    def __init__(self, lat, lon):
        """
        Create a new object.

        :param lat: The latitude of the coordinate.
        :type lat: float
        :param lon: The longitude of the coordinate.
        :type lon: float
        """
        self.lat = lat
        self.lon = lon
        self.arr = [self.lat, self.lon]
        self.arr_r = [self.lon, self.lat]

    def __iter__(self):
        """
        Iterates over the coordinate.
        """
        for elem in self.arr:
            yield elem

    def __getitem__(self, item):
        """
        Gets the lat (0) or lon (1).

        :param item: Index of the coodinate.
        :return: Coordinate value.
        """
        return self.arr[item]

    def get(self):
        """
        Gets the coordinates in the form lat, lon.

        :return: List of the lat, lon.
        """
        return self.arr

    def rev(self):
        """
        Gets the reverse form of the coordinates in lon, lat.

        :return: List of the lon, lat.
        """
        return self.arr_r


class TweetCluster:
    """
    Holds information about a tweet cluster including the list of tweets within
    it, the centres of the cluster, the required population that initialised the
    cluster and the latest tweet within it.

    This class is used by the other modules in the event detection and provides
    methods to merge the cluster or check if a tweet should be within. Also allows
    for new tweets to be added to the cluster.

    .. note:: as clusters can be merged there can be multiple centres of the
        cluster.
    """

    def __init__(self, tweets, centre, clsman):
        """
        Creates a new :class:`TweetCluster`.

        :param tweets: List of tweets within the cluster.
        :type tweets: list, dict
        :param centre: Tweet which represents the centre of the cluster.
        :type centre: dict
        :param clsman: The :class:`ClusterManager` object.
        :type clsman: :class:`ClusterManager`
        """
        # Store the tweets in order they were posted
        self._tweets = sorted(tweets, key=lambda x: x[clsman.tsfield])
        self.centres = [centre['_coord']]
        self.popreq = centre['_popreq']
        self.clsman = clsman

        # Save the latest tweet
        self.latest = self._tweets[-1][clsman.tsfield]

    def merge(self, cluster):
        """
        Merge two clusters by appending both of the tweets and cluster
        centres together.

        :param cluster: The other cluster to merge into this one.
        :type cluster: :class:`TweetCluster`
        """
        self._tweets += cluster._tweets
        self.centres += cluster.centres
        self.latest = max([self.latest, cluster.latest])

    def in_cluster(self, tweet):
        """
        Checks if a tweet was posted within the radius of the cluster. Will
        check for all the centres of the cluster.

        :param tweet: The tweet dictionary to test.
        :type tweet: dict
        :return: Boolean of if the tweet was posted within the required radius.
        :rtype: bool
        """
        for c in self.centres:
            # Check if tweet was posted within the maximum distance.
            if vincenty(tweet['_coord'].rev(), c.rev()).km < self.clsman.radius:
                return True
        return False

    def add_tweet(self, tweet):
        """
        Add a tweet to the cluster. Will also update the value for the latest
        tweet.

        :param tweet: Dictionary of tweet information.
        :type tweet: dict

        .. note:: this method does not test if the tweet should be within the
            cluster and will add it regardless. The :func:`in_cluster` method
            should be used first to ensure that the tweet is within the cluster
            radius.
        """
        self._tweets.append(tweet)
        self.latest = max([self.latest, tweet[self.clsman.tsfield]])

    def get_points(self):
        """
        Gets a list of the coordinates of all the tweets in the cluster.

        :return: List of :class:`Coordinate` objects for all of the locations
            of the tweets.
        :rtype: list, :class:`Coordinate`
        """
        return [x['_coord'] for x in self._tweets]

    def as_dict(self):
        """
        Returns the information from the tweet cluster in a dicationary format.
        This is then used when saving the cluster information.

        The returned dictionary includes:
            * `tweets` - list of all tweets within the cluster, including each of
                their tweet_id's, the time of posting and the coordinate of the
                tweets posting location.
            * `centres` - list of centres in the cluster
            * `times` - the start and finish times of the tweets posted in the
                cluster.

        :return: Cluster dictionary.
        """
        return {
            'tweets': [{
                    'id': t['tweetid'],
                    'time': t[self.clsman.tsfield],
                    'coordinate': t['_coord'].get()
                } for t in self._tweets
            ],
            'centres': [s.get() for s in self.centres],
            'times': {
                'start': min([t[self.clsman.tsfield] for t in self._tweets]),
                'finish': max([t[self.clsman.tsfield] for t in self._tweets])
            }
        }
