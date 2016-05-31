from .clustermanager import ClusterManager
from .clustercreatorgrid import ClusterCreatorGrid
from .clustercreator import ClusterCreator
from .clusterupdater import ClusterUpdater
from .popcount import PopMap

import datetime


class EventDetection:
    """
    Main entry point for the Event Detection implementation.

    This method is based of that proposed in *M.Walther and M. Kaisser,
    "Geo-spatial event detection in the twitter stream"* which focuses
    on clustering tweets temporally and spatially.

    The technique monitors the most recent tweets and clusters those
    issued geographically close to each other in a given timeframe.
    Three modules manage the clusters:

    * :class:`ClusterCreator` - checks the most recent tweets and creates
        new clusters where more than a threshold  number of tweets were
        issued within a set time frame and within a set radius.
    * :class:`ClusterUpdater` - adds new tweets to clusters if they are
        within the area of an existing cluster. This module also merges
        clusters that are overlapping. Clusters are deleted after they
        have reached a maximum amount of time with no new tweets being
        added to them.
    * :class:`ClusterManager` - manages the clusters.

    This class manages the creation, updation and deletion of event clusters
    by passing the tweets to each of the modules and deciding on what should
    happen.

    :Usage:

    After the object is initialised, tweets should be fed to the class
    in ascending datetime order to the :func:`process_tweet` method.
    The order is required as the classes will compare times based off
    the newest tweet, removing tweets or events older than a certain
    age.

    >>> ed = EventDetection()
    >>> for t in tweets:
    >>>     ed.process_tweet(t)

    Active clusters can be retrieved at any time using the :func:`get_clusters`
    method. Other methods also exist for getting expired events, which are
    clusters that did not add a new tweet for a period of time.

    The removal of clusters will only be performed once a new tweet has
    arrived. Each cluster returned from these methods is a :class:`EventCluster`
    object. A dictionary of the clusters can be retrieved using the :func:`as_dict()`
    method on the cluster object.

    >>> clusters = ed.get_all_clusters()
    >>> cdicts = [c.as_dict() for c in clusters]

    .. seemore: :class:`EventCluster` contains more details about the fields
        in each cluster.
    """

    def __init__(self, field='geo.coordinate', tsfield='timestamp_obj', gridded=True,
                 popfunc=None, popmaploc=None, mincnt=10, mdcnt=30,
                 cluster_radius=10, cluster_timediff=datetime.timedelta(minutes=30),
                 cluster_maxage=datetime.timedelta(hours=6)):
        """
        Initialises and sets up the event detection class.

        Either the `popfunc` value or the `popmaploc` field must be set. If there
        is no `popmaploc` value, then the `popfunc` will be used to calculate
        the required number of tweets to start an event at a position. Otherwise
        the function using a :class:`PopMap` will be used.

        .. seealso:: :class:`PopMap` which describes the function for determining
            the number of required tweets.

        :param field: The field in the tweet dictionary where the coordinates
            are stored. *(default 'geo.coordinate')*

            Can be passed a dot delimited string of the location of the
            location of the coordinate in the tweet dictionary.
        :type field: str
        :param tsfield: The field in the tweet dictionary where the timestamp
            field is stored. (This field cannot be dot delimited).
            *(default 'timestamp_obj')*
        :type tsfield: str
        :param gridded: Whether or not to use the :class:`ClusterCreatorGrid`
            or the less performant :class:`ClusterCreator`. See documentation
            for these classes for reasons to use either. *(default `True`)*
        :type gridded: bool
        :param popfunc: *(Optional)* Function which takes a two parameters: lon and lat,
            and returns a single integer value for the number of required
            tweets to start an event at that coordinate. If this function is
            not set, then the population map will be assumed and the `popmaploc`
            string must be set.

            Simple example for a static value:

            >>> popfunc = lambda lat, lon: 25
        :type popfunc: lambda
        :param popmaploc: *(Optional)* The location of the population grid
            to be used for the population map function. This only works for
            the UK grid. If this value is not set then the `popfunc` value
            must be set.

            If the popmap still needs to be used with a different function,
            this can be setup seperately using the `popfunc` parameter
            and passed in.
        :type popmaploc: str
        :param mincnt: If the `popmaploc` value is set this is the minimum
            number of tweets required to start an event in the lowest populated
            areas. *(default 10)*
        :type mincnt: int
        :param mdcnt: If the `popmaploc` value is set this is the median
            number of tweets required to start an event in the median
            populated areas. *(default 30)*
        :type mdcnt: int
        :param cluster_radius: Maximum radius of the events (km). *(default 10km)*
        :type cluster_radius: float
        :param cluster_timediff: Maximum time difference between all tweets
            to create a cluster. *(default 30 minutes)*
        :type cluster_timediff: datetime.timedelta
        :param cluster_maxage: Maximum age of a cluster since the last new tweet
            before it is deleted. *(default 6 hours)*
        :type cluster_maxage: datetime.timedelta
        """
        self.tsfield = tsfield

        # Setup the cluster manager and updater modules.
        self.c_manager = ClusterManager(field=field, tsfield=tsfield, radius=cluster_radius,
                                        timediff=cluster_timediff, maxage=cluster_maxage)
        self.c_updater = ClusterUpdater(self.c_manager)

        # Setup the cluster creator selected from the gridded parameter
        if gridded:
            self.c_creator = ClusterCreatorGrid(self.c_manager)
        else:
            self.c_creator = ClusterCreator(self.c_manager)

        # Setup the population function
        if popfunc is None and popmaploc is not None:
            # Setup the population map
            popmap = PopMap(popmaploc)
            ppfnc = popmap.get_reqfunc_uk(mdcnt, mincnt)  # (5, 3 for geo)

            self.popfunc = lambda lt, ln: ppfnc(popmap.get_population(ln, lt))
        elif popfunc is not None and popmaploc is None:
            self.popfunc = popfunc
        else:
            raise TypeError("Incorrect setup of Event Detection class: "
                            "popfunc and popmaploc cannot both be null or set.")

    def process_tweet(self, tweet):
        """
        Process a tweet through the event detection.

        Tweets should be fed into this method in ascending datetime
        order. If there is an error in retrieving the coordinate or
        population of the tweet a silent error will be thrown and the
        method will return `False`.

        :param tweet: Dictionary of tweet information.
        :type tweet: dict
        :return: Whether the tweet was processed correctly.
        :rtype: bool
        """
        # Try to get the coordinate, if fails, pass the tweet
        try:
            coord = self.c_manager.get_coordinate(tweet)
            tweet['_coord'] = coord

            tweet['_popreq'] = self.popfunc(coord.lon, coord.lat)
        except (KeyError, TypeError):
            # Could not get coordinate or population
            return False
        except Exception as e:
            # Unknown error was thrown
            print(e)
            raise e

        # Update the manager with the time of the latest tweet
        self.c_manager.lasttime = tweet[self.tsfield]

        # Attempt to create new cluster
        created = self.c_creator.process_tweet(tweet)

        # If none created, update existing
        updated = False
        if not created:
            updated = self.c_updater.process_tweet(tweet)

        # If tweet was not added to a cluster, add to unclustered
        if not updated and not created:
            self.c_creator.add_unclustered(tweet)

        # Update and merge clusters
        if created:
            self.c_updater.update_clusters(tweet)
        self.c_updater.update_oldclusters(tweet)

        return True

    def get_clusters(self):
        """
        Gets the list of current active clusters from the :class:`ClusterManager`.
        """
        return self.c_manager.clusters

    def get_unclustered(self):
        """
        Gets the list of current unclustered tweets from the :class:`ClusterCreator`.

        .. warning:: only the non-gridded :class:`ClusterCreator` class supports
            getting the list of unclustered tweets. It is not possible to get this
            list when using the :class:`ClusterCreatorGrid` class.

            Will raise an exception if this method is used with the wrong class.

        :returns: List of unclustered tweets.
        """
        if type(self.c_creator) == ClusterCreatorGrid:
            raise TypeError("List of unclustered tweets cannot be retrieved using the "
                            "grid version of ClusterCreator")
        else:
            return self.c_creator.unclustered

    def get_unclustered_points(self):
        return [self.c_manager.get_coordinate(x) for x in self.get_unclustered()]

    def get_all_clusters(self):
        """
        Gets the list of current active clusters and old clusters appended
        together from the :class:`ClusterManager`.
        """
        return self.c_manager.get_all_clusters()

    def __str__(self):
        """
        Returns a string of the status from each of the three modules.
        """
        return str(self.c_manager) + " " + str(self.c_creator) + " " + str(self.c_updater)

