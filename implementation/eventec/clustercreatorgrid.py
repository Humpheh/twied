from geopy.distance import vincenty


class GeoGrid:
    def __init__(self):
        self.areas = {}
        self.tests = [
            (1,  1), (0,  1), (-1,  1),
            (1,  0), (0,  0), (-1,  0),
            (1, -1), (0, -1), (-1, -1)
        ]

    def get_str(self, coord):
        return "%.1d,%.1d" % (coord[0], coord[1])

    def add_tweet(self, tweet):
        coord = tweet['_coord']

        for x in self.tests:
            newc = self.get_str([(coord[0] - x[0]), (coord[1] - x[1])])
            try:
                self.areas[newc].append(tweet)
            except:
                self.areas[newc] = [tweet]

    def remove_tweet(self, tweet):
        coord = tweet['_coord']

        for x in self.tests:
            newc = self.get_str([(coord[0] - x[0]), (coord[1] - x[1])])
            try:
                self.areas[newc].remove(tweet)
            except:
                pass

    def get_surrounding(self, tweet):
        try:
            return self.areas[self.get_str(tweet['_coord'])]
        except:
            return []


class ClusterCreator:
    def __init__(self, clsman):
        self.clsman = clsman
        self.grid = GeoGrid()

    def process_tweet(self, tweet):
        coord = tweet['_coord']

        searchspace = self.grid.get_surrounding(tweet)

        toremove = []
        candidates = []
        for t in searchspace:
            dist = vincenty(coord.rev(), t['_coord'].rev()).km
            time = abs(tweet[self.clsman.tsfield] - t[self.clsman.tsfield])

            if dist < self.clsman.radius and time < self.clsman.timediff:
                # candidate tweet is close enough
                candidates.append(t)
            elif time > self.clsman.timediff:
                toremove.append(t)

        if len(toremove) > 0:
            # remove old candidate tweets
            for x in toremove:
                self.grid.remove_tweet(x)

        if len(candidates) >= tweet['_popreq'] - 1:
            # remove candidates from unclustered
            for x in candidates:
                self.grid.remove_tweet(x)

            candidates.append(tweet)

            # create new cluster
            self.clsman.add_cluster(candidates, tweet)
            return True
        else:
            # not enough candidates to create cluster
            return False

    def add_unclustered(self, tweet):
        # Appended to unclustered
        self.grid.add_tweet(tweet)

    def __str__(self):
        return "<ClusterCreator: %i areas>" % len(self.grid.areas)