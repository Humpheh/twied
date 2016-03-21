import datetime
import logging

from geopy.distance import vincenty


class ClusterManager:
    def __init__(self, field, tsfield):
        self.clusters = []
        self.oldclusters = []
        self.geofield = field
        self.geofieldspl = field.split(".")
        self.tsfield = tsfield

        #self.radius = 10  # km
        #self.mincount = 15  # tweets #5
        #self.timediff = datetime.timedelta(minutes=60)
        #self.maxage = datetime.timedelta(hours=1)#24)

        self.radius = 10  # km
        self.mincount = 15  # tweets #5
        self.timediff = datetime.timedelta(minutes=30)
        self.maxage = datetime.timedelta(minutes=30)#24)

        self.lasttime = datetime.datetime.utcnow()

    def __iter__(self):
        return iter(self.clusters)

    def __str__(self):
        return "<ClusterManager: %i clusters>" % len(self.clusters)

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

    def get_all_clusters(self):
        return self.oldclusters + self.clusters

    def __str__(self):
        return "<ClusterManager: %i clusters, %i old clusters>" % (len(self.clusters), len(self.oldclusters))


class Coordinate:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def __iter__(self):
        for elem in [self.lat, self.lon]:
            yield elem

    def __getitem__(self, item):
        return [self.lat, self.lon][item]

    def get(self):
        return [self.lat, self.lon]

    def rev(self):
        return [self.lon, self.lat]


class TweetCluster:
    def __init__(self, tweets, centre, clsman):
        self._tweets = sorted(tweets, key=lambda x: x[clsman.tsfield])
        self.centres = [centre['_coord']]
        self.clsman = clsman
        self.oldest = self._tweets[-1][clsman.tsfield]

    def merge(self, cluster):
        self._tweets += cluster._tweets
        self.centres += cluster.centres
        self.oldest = max([self.oldest, cluster.oldest])

    def in_cluster(self, tweet):
        for c in self.centres:
            if vincenty(tweet['_coord'].rev(), c.rev()).km < self.clsman.radius:
                return True
        return False

    def add_tweet(self, tweet):
        self._tweets.append(tweet)
        self.oldest = max([self.oldest, tweet[self.clsman.tsfield]])

    def get_points(self):
        return [x['_coord'] for x in self._tweets]

    def as_dict(self):
        return {
            'tweets': [{
                    'id': t['tweetid'],#'id_str'],
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
