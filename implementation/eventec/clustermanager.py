import datetime
import logging

from geopy.distance import vincenty


class ClusterManager:
    def __init__(self, field):
        self.clusters = []
        self.geofield = field
        self.geofieldspl = field.split(".")

        self.radius = 100  # km
        self.mincount = 5  # tweets
        self.timediff = datetime.timedelta(minutes=30)

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

    def merge_clusters(self, c1, c2):
        logging.debug("Merging clusters %s + %s" % (id(c1), id(c2)))
        c1.merge(c2)
        self.clusters.remove(c2)


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
        self.tweets = tweets
        self.centres = [clsman.get_coordinate(centre)]
        self.clsman = clsman

    def merge(self, cluster):
        self.tweets += cluster.tweets
        self.centres += cluster.centres

    def in_cluster(self, tweet):
        for c in self.centres:
            if vincenty(self.clsman.get_coordinate(tweet).rev(), c.rev()).km < self.clsman.radius:
                return True
        return False

    def add_tweet(self, tweet):
        self.tweets.append(tweet)

    def get_points(self):
        return [self.clsman.get_coordinate(x) for x in self.tweets]
