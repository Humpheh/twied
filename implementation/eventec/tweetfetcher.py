import datetime

from geopy.distance import vincenty


from .tweetcluster import TweetCluster


class ClusterCreator:
    def __init__(self, field='geo.coordinate'):
        self.unclustered = []
        self.geofield = field
        self.geofieldspl = field.split(".")

        self.radius = 100  # km
        self.mincount = 5  # tweets
        self.timediff = datetime.timedelta(minutes=30)

    def get_coordinate(self, tweet):
        cur_dict = tweet
        for x in range(len(self.geofieldspl) - 1):
            cur_dict = cur_dict.get(self.geofieldspl[x])
        return cur_dict[self.geofieldspl[-1]]

    def recieve_tweet(self, tweet):
        candidates = [tweet]
        for t in self.unclustered:
            dist = vincenty(self.get_coordinate(tweet), self.get_coordinate(t)).km
            time = abs(tweet['timestamp_obj'] - t['timestamp_obj'])

            if dist < self.radius and time < self.timediff:
                candidates.append(t)

        if len(candidates) > self.mincount:
            # create new cluster
            return TweetCluster(candidates, self.get_coordinate(tweet))
        else:
            self.unclustered.append(tweet)
            return None
