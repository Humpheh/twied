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
                # logging.debug("Candidate tweet %.2f km apart" % dist)
                candidates.append(t)
            elif time > self.clsman.timediff:
                toremove.append(t)

        if len(toremove) > 0:
            # logging.debug("Removing %i old candidate tweets." % len(toremove))
            for x in toremove:
                self.unclustered.remove(x)

        # logging.debug("Found %i candidates" % len(candidates))
        if len(candidates) >= tweet['_popreq'] - 1:
            # remove candidates from unclustered
            for x in candidates:
                self.unclustered.remove(x)

            candidates.append(tweet)

            # create new cluster
            self.clsman.add_cluster(candidates, tweet)
            return True
        else:
            # logging.debug("Not enough candidates to create cluster (%i)" % len(candidates))
            return False

    def add_unclustered(self, tweet):
        self.unclustered.append(tweet)
        # logging.debug("Appended to unclustered (%i)" % len(self.unclustered))

    def __str__(self):
        return "<ClusterCreator: %i unclustered>" % len(self.unclustered)