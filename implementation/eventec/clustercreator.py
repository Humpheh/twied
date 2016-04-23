from geopy.distance import vincenty


class ClusterCreator:
    def __init__(self, clsman):
        self.clsman = clsman
        self.unclustered = []

    def process_tweet(self, tweet):
        coord = tweet['_coord']

        toremove = []
        candidates = []
        for t in self.unclustered:
            dist = vincenty(coord.rev(), t['_coord'].rev()).km
            time = abs(tweet[self.clsman.tsfield] - t[self.clsman.tsfield])

            if dist < self.clsman.radius and time < self.clsman.timediff:
                candidates.append(t)
            elif time > self.clsman.timediff:
                toremove.append(t)

        if len(toremove) > 0:
            # removing old candidate tweets
            for x in toremove:
                self.unclustered.remove(x)

        if len(candidates) >= tweet['_popreq'] - 1:
            # remove candidates from unclustered
            for x in candidates:
                self.unclustered.remove(x)

            candidates.append(tweet)

            # create new cluster
            self.clsman.add_cluster(candidates, tweet)
            return True
        else:
            # not enough candidates to create cluster
            return False

    def add_unclustered(self, tweet):
        self.unclustered.append(tweet)

    def __str__(self):
        return "<ClusterCreator: %i unclustered>" % len(self.unclustered)