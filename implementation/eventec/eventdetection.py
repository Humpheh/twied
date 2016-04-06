from .clustermanager import ClusterManager
from .clustercreatorgrid import ClusterCreator
from .clusterupdater import ClusterUpdater
from .popcount import PopMap


class EventDetection:
    def __init__(self, field='geo.coordinate', tsfield='timestamp_obj'):
        self.tsfield = tsfield

        self.c_manager = ClusterManager(field=field, tsfield=tsfield)
        self.c_creator = ClusterCreator(self.c_manager)
        self.c_updater = ClusterUpdater(self.c_manager)

        self.popmap = PopMap('D:\ds\population\glds15ag.asc')
        self.popfunc = self.popmap.get_reqfunc_uk(30, 5)

    def process_tweet(self, tweet):
        # try to get the coordinate, if fails - pass
        try:
            coord = self.c_manager.get_coordinate(tweet)
            tweet['_coord'] = coord
            tweet['_popreq'] = self.popfunc(coord.lon, coord.lat)
        except (KeyError, TypeError):
            return

        self.c_manager.lasttime = tweet[self.tsfield]
        # attempt to create new cluster
        created = self.c_creator.process_tweet(tweet)

        # if none created, update existing
        updated = False
        if not created:
            updated = self.c_updater.process_tweet(tweet)

        if not updated and not created:
            self.c_creator.add_unclustered(tweet)

        # update and merge clusters
        if created:
            self.c_updater.update_clusters(tweet)
        self.c_updater.update_oldclusters(tweet)

    def get_clusters(self):
        return self.c_manager.clusters

    def get_unclustered(self):
        return self.c_creator.unclustered

    def get_unclustered_points(self):
        return [self.c_manager.get_coordinate(x) for x in self.get_unclustered()]

    def get_all_clusters(self):
        return self.c_manager.get_all_clusters()

    def __str__(self):
        return str(self.c_manager) + " " + str(self.c_creator) + " " + str(self.c_updater)