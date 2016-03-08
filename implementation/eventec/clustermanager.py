import datetime
import logging

from geopy.distance import vincenty


class ClusterManager:
    def __init__(self, field):
        self.clusters = []
        self.oldclusters = []
        self.unclustered = []
        self.geofield = field
        self.geofieldspl = field.split(".")

        self.radius = 10  # km
        self.mincount = 5  # tweets
        self.timediff = datetime.timedelta(minutes=60)
        self.maxage = datetime.timedelta(hours=24)

        self.lasttime = datetime.datetime.utcnow()

    def __iter__(self):
        return iter(self.clusters)

    def __str__(self):
        return "ClusterManager: %i clusters" % len(self.clusters)

    def get_coordinate(self, tweet):
        cur_dict = tweet
        for x in range(len(self.geofieldspl) - 1):
            cur_dict = cur_dict.get(self.geofieldspl[x])
        coord = cur_dict[self.geofieldspl[-1]]
        return Coordinate(coord[1], coord[0])

    def add_cluster(self, tweets, maintweet):
        """
        Creates a new cluster and saves it. The first tweet in the list of tweets will be
        used as the center for the cluster.
        :param tweets: The tweets within the cluster.
        :return:
        """
        newcls = TweetCluster(tweets, maintweet, self)
        logging.debug("Created cluster %s" % id(newcls))
        self.clusters.append(newcls)
        return newcls

    def remove_cluster(self, cluster):
        try:
            self.clusters.remove(cluster)
            self.oldclusters.append(cluster)
            return True
        except ValueError:
            return False

    def merge_clusters(self, c1, c2):
        logging.debug("Merging clusters %s + %s" % (id(c1), id(c2)))
        c1.merge(c2)
        self.clusters.remove(c2)

    def add_unclustered(self, tweet):
        self.unclustered.append(tweet)
        logging.debug("Appended to unclustered (%i)" % len(self.unclustered))


class Coordinate:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def __iter__(self):
        for elem in [self.lat, self.lon]:
            yield elem

    def __getitem__(self, item):
        return [self.lat, self.lon][item]

    def rev(self):
        return [self.lon, self.lat]


class TweetCluster:
    def __init__(self, tweets, centre, clsman):
        self._tweets = sorted(tweets, key=lambda x: x['timestamp_obj'])
        self.centres = [clsman.get_coordinate(centre)]
        self.clsman = clsman
        print([x['timestamp_obj'] for x in self._tweets])
        self.oldest = self._tweets[-1]['timestamp_obj']

    def merge(self, cluster):
        self._tweets += cluster._tweets
        self.centres += cluster.centres
        self.oldest = max([self.oldest, cluster.oldest])

    def in_cluster(self, tweet):
        for c in self.centres:
            if vincenty(self.clsman.get_coordinate(tweet).rev(), c.rev()).km < self.clsman.radius:
                return True
        return False

    def add_tweet(self, tweet):
        self._tweets.append(tweet)
        self.oldest = max([self.oldest, tweet['timestamp_obj']])

    def get_points(self):
        return [self.clsman.get_coordinate(x) for x in self._tweets]
