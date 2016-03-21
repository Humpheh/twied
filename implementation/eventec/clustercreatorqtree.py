import logging

import pyqtree
from geopy.distance import vincenty


class ClusterCreator:
    def __init__(self, clsman):
        self.clsman = clsman
        self.unclustered = {}
        self.spindex = pyqtree.Index(bbox=[-180, -90, 180, 90])
        self.remcount = 0

    def process_tweet(self, tweet):
        coord = self.clsman.get_coordinate(tweet)

        bbox = [tweet['_coord'][0]-1, tweet['_coord'][1]-1, tweet['_coord'][0]+1, tweet['_coord'][1]+1]
        matches = self.spindex.intersect(bbox)

        candidates = []
        for x in matches:
            t = self.unclustered[x]

            if t['inactive']:
                continue

            dist = vincenty(coord.rev(), self.clsman.get_coordinate(t).rev()).km
            time = abs(tweet[self.clsman.tsfield] - t[self.clsman.tsfield])

            if dist < self.clsman.radius and time < self.clsman.timediff:
                logging.debug("Candidate tweet %.2f km apart" % dist)
                candidates.append(t)
            elif time > self.clsman.timediff:
                t['inactive'] = True
                self.remcount += 1

        if self.remcount > 500:
            self.remcount = 0
            logging.info("Removing inactive...")
            self.spindex = pyqtree.Index(bbox=[-180, -90, 180, 90])

            oldunclustered = self.unclustered
            self.unclustered = {}
            for t in oldunclustered.values():
                if not t['inactive']:
                    self.add_unclustered(t)

        logging.debug("Found %i candidates" % len(candidates))
        if len(candidates) >= self.clsman.mincount - 1:
            # remove candidates from unclustered
            for x in candidates:
                x['inactive'] = True
                self.remcount += 1

            candidates.append(tweet)

            # create new cluster
            self.clsman.add_cluster(candidates, tweet)
            return True
        else:
            logging.debug("Not enough candidates to create cluster (%i)" % len(candidates))
            return False


    def add_unclustered(self, tweet):
        bbox = [tweet['_coord'][0]-0.5, tweet['_coord'][1]-0.5, tweet['_coord'][0]+0.5, tweet['_coord'][1]+0.5]
        tweet['inactive'] = False
        self.unclustered[str(tweet['_id'])] = tweet
        self.spindex.insert(item=str(tweet['_id']), bbox=bbox)
        logging.debug("Appended to unclustered")

    def __str__(self):
        count = self.spindex.intersect([-180, -90, 180, 90])

        return "<ClusterCreator: %i>" % len(count)
