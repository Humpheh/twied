from .clustermanager import ClusterManager
from .clustercreator import ClusterCreator
from .clusterupdater import ClusterUpdater


class EventDetection:
    def __init__(self, field='geo.coordinate'):
        self.c_manager = ClusterManager(field=field)
        self.c_creator = ClusterCreator(self.c_manager)
        self.c_updater = ClusterUpdater(self.c_manager)

    def process_tweet(self, tweet):
        self.c_manager.lasttime = tweet['timestamp_obj']
        # attempt to create new cluster
        created = self.c_creator.process_tweet(tweet)

        # if none created, update existing
        updated = False
        if not created:
            updated = self.c_updater.process_tweet(tweet)

        if not updated and not created:
            self.c_manager.add_unclustered(tweet)

        # update and merge clusters
        if updated or created:
            self.c_updater.update_clusters(tweet)
        self.c_updater.update_oldclusters(tweet)

    def get_clusters(self):
        return self.c_manager.clusters

    def get_unclustered(self):
        return self.c_manager.unclustered

    def get_unclustered_points(self):
        return [self.c_manager.get_coordinate(x) for x in self.get_unclustered()]

    def get_all_clusters(self):
        return self.c_manager.get_all_clusters()