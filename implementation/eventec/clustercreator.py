from geopy.distance import vincenty


class ClusterCreator:
    """
    Class to manage the creation of clusters from tweets.

    Tweets are fed in through the :func:`process_tweet` method. These
    are compared with the current unclustered tweets and a cluster is
    created if the required number of tweets were posted within a
    certain timeframe and radius.

    Class also manages a list of unclustered tweets. Tweets are added
    using the :func:`add_unclustered` method. The :func:`process_tweet`
    method will remove tweets from the unclustered set if they are added
    to a cluster or if the difference between the times are greater
    than the threshold.

    .. seealso:: :class:`ClusterCreatorGrid`, more efficient version of
        this class which only examines surrounding tweets using a grid data
        structure.
    """

    def __init__(self, clsman):
        """
        Create the cluster manager.

        :param clsman: The cluster managaer object.
        :type clsman: ClusterManager
        """
        self.clsman = clsman
        self.unclustered = []

    def process_tweet(self, tweet):
        """
        Take a tweet and attempt to create a new cluster.

        :param tweet: Dictionary of tweet information.
        :return: Whether a cluster has been created or not.
        """
        # Keep a list of tweets to remove after this tweet has been processed
        toremove = []

        # Keep a list of tweets that could be part of a new cluster
        candidates = [tweet]

        for t in self.unclustered:
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
            self.unclustered.remove(x)

        # If have enough candidates to create a cluster
        if len(candidates) >= tweet['_popreq']:
            # Remove candidates from unclustered
            for x in candidates:
                self.unclustered.remove(x)

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
        self.unclustered.append(tweet)

    def __str__(self):
        """
        String representation of the number of unclustered tweets.
        """
        return "<ClusterCreator: %i unclustered>" % len(self.unclustered)
