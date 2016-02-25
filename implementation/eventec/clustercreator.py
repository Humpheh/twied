import logging

from geopy.distance import vincenty


class ClusterCreator:
    def __init__(self, clsman):
        self.clsman = clsman

    def process_tweet(self, tweet):
        coord = self.clsman.get_coordinate(tweet)

        toremove = []
        candidates = []
        for t in self.clsman.unclustered:
            dist = vincenty(coord.rev(), self.clsman.get_coordinate(t).rev()).km
            time = abs(tweet['timestamp_obj'] - t['timestamp_obj'])

            if dist < self.clsman.radius and time < self.clsman.timediff:
                logging.debug("Candidate tweet %.2f km apart" % dist)
                candidates.append(t)
            elif time > self.clsman.timediff:
                toremove.append(t)

        if len(toremove) > 0:
            logging.debug("Removing %i old candidate tweets." % len(toremove))
            for x in toremove:
                self.clsman.unclustered.remove(x)

        logging.debug("Found %i candidates" % len(candidates))
        if len(candidates) >= self.clsman.mincount - 1:
            # remove candidates from unclustered
            for x in candidates:
                self.clsman.unclustered.remove(x)

            candidates.append(tweet)

            # create new cluster
            self.clsman.add_cluster(candidates, tweet)
            return True
        else:
            logging.debug("Not enough candidates to create cluster (%i)" % len(candidates))
            return False
