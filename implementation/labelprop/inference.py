import logging
from collections import defaultdict

from twython import Twython
from twython.exceptions import TwythonAuthError, TwythonError

from labelprop.distance import geometric_mean


class SLNetwork:
    """
    Stores information about the users and connections in a network.
    """
    def __init__(self):
        self.users = {}
        self.connections = []
        self.key_user = None
        self.limdepth = 100
        self.testing = False


class InferSL:
    """
    Implementation of the spatial label propagation method for infering the location of Twitter users.
    Generates the network around a specific user in order to locate.
    """
    def __init__(self, config, dbcollection, verbose=False):
        """
        Setup a InferSL instance.
        :param config: The configuration to be used.
        :param dbcollection: The MongoDB collection to connect with.
        :param verbose: Boolean if to output log.
        """
        # setup Twitter API interface
        api_settings = config._sections['twitter']
        self.twitter = Twython(**api_settings)
        self.db = dbcollection

        self.verbose = verbose

        self.min_mentions = config.getint("slinf", "min_mentions")
        self.req_locs = config.getint("slinf", "req_locations")
        self.max_iter = config.getint("slinf", "max_iterations")
        self.max_depth = config.getint("slinf", "max_depth")
        self.timelines = config.getint("slinf", "num_timelines")

    def log(self, message):
        """
        Logs a message to the console is verbose was true in initialisation.
        :param message: The message to log.
        """
        if self.verbose:
            logging.info(message)

    def infer(self, user_id, test=False):
        """
        Infers a location for a user with an ID.
        :param user_id: The Twitter ID of the user.
        :return: [coordinate, geodis] tuple
        """
        network = self.get_network(user_id)
        network.testing = test
        return self.get_location(network)

    def get_network(self, user_id):
        """
        Gets the network surronding a user.
        :param user_id: The Twitter ID of the user.
        :return: An SLNetwork object with the network information.
        """
        # setup the network object
        network = SLNetwork()
        network.key_user = user_id

        # gets the users' connections
        user = self.get_user(user_id)
        self.get_connections(user, network, 0)

        return network

    def get_user(self, user_id):
        """
        Gets a user profile from the Twitter API and stores their geotag tweets and mentions.
        :param user_id: The Twitter ID of the user to find.
        :return: The data for the Twitter user with that ID.
        """
        # find the user in the database
        dbusr = self.db.find_one({'user.id': int(user_id)})

        # return none if the user is private or field empty
        if dbusr is not None:
            return dbusr if 'private' not in dbusr else None

        mentions = defaultdict(int)
        geotags = []
        user = None

        max_id = None
        for i in range(self.timelines):
            try:
                # get the next part of the twitter timeline
                self.log("Downloading new Twitter profile: %s %i/%i" % (user_id, i+1, self.timelines))
                usr_tweets = self.twitter.get_user_timeline(user_id=user_id, count=200, include_rts=False, max_id=max_id)
            except TwythonAuthError:
                # if auth error, user is private, store as private entry
                self.db.insert_one({
                    'user': {'id': int(user_id)},
                    'private': True
                })
                return None
            except TwythonError as e:
                # error in getting the information (API limited?)
                logging.error(str(e))
                return None

            # search the returned tweets for geotags and mentions
            for twt in usr_tweets:
                user = twt['user']
                for m in twt['entities']['user_mentions']:
                    mentions[m['id_str']] += 1
                if twt['geo'] is not None:
                    geotags.append(twt['geo'])
                max_id = twt['id']

        # if the user is none, no tweets were returned
        if user is None:
            return None

        # store the data
        data = {
            'user': user,
            'locations': geotags,
            'mentions': mentions
        }

        self.db.insert_one(data)
        return data

    def get_connections(self, user, network, depth=0):
        """
        Recursively gets the connections around a user until at least one with enough geotags has been found.
        :param user: The user object to continue inferring from.
        :param network: An SLNetwork object containing the network.
        :param depth: The depth of the recursion (default 0)
        :return: Boolean of if the network was attempted to be extended.
        """
        # store the user in net_users
        network.users[str(user['user']['id'])] = user

        # if the user is None, then it cannot be found, so return
        if user is None:
            return False

        self.log("Processing %s (%s)" % (user['user']['screen_name'], user['user']['id']))

        # if recursive depth has been met, return
        if depth >= self.max_depth or depth > network.limdepth:
            return False

        next_connections = []

        for uid, count in user['mentions'].items():
            # if the number of mentions is less than a threshold, pass it
            if count < self.min_mentions:
                continue

            # get the mentioned user
            user2 = self.get_user(uid)

            # if cannot find the user, continue
            if user2 is None:
                continue

            self.log("Inner processing %s (%s)" % (user2['user']['screen_name'], uid))

            if str(user['user']['id']) in user2['mentions']:
                # if the other user has not mentioned the main subject enough, skip
                if user2['mentions'][str(user['user']['id'])] < self.min_mentions:
                    continue

                network.connections.append((str(user['user']['id']), str(user2['user']['id'])))
                self.log("Found connecting user: %s - %s" % (user['user']['screen_name'], user2['user']['screen_name']))

                if str(uid) not in network.users:
                    # recursively get the connections of the next user
                    next_connections.append(user2)

                    if len(user2['locations']) > 3:
                        network.limdepth = depth
                        self.log("Found candidate user %s at %i depth." % (user2['user']['screen_name'], network.limdepth))

        # continue for next users
        for usr_i in next_connections:
            self.get_connections(usr_i, network, depth+1)

        return True

    def get_location(self, netw):
        """
        Infers the location of a user from a network.
        :param netw: An SLNetwork object
        :return: [coordinate, geodis] tuple
        """
        ground_truth = {}
        for _, u in netw.users.items():
            # if there are more than the required number of locations
            if len(u.get('locations', [])) >= self.req_locs:
                # if in testing and the user is key, ignore him
                if netw.testing and str(u['user']['id']) == str(netw.key_user):
                    continue

                locc = [p['coordinates'] for p in u.get('locations')]
                ground_truth[str(u['user']['id'])] = geometric_mean(locc)

        # build a dictionary of connections between users
        ego = defaultdict(dict)
        for c in netw.connections:
            ego[c[0]][c[1]] = True
            ego[c[1]][c[0]] = True

        for i in range(self.max_iter):
            # if have found the required user, return
            if str(netw.key_user) in ground_truth:
                break

            if len(ground_truth) >= len(netw.users):
                # all users have been located
                break

            new_gt = {}

            for uid, u in netw.users.items():
                if uid in ground_truth or str(uid) not in ego:
                    continue
                egon = ego.get(str(uid)).keys()

                # if any of the connections have been located
                if any([eg in ground_truth for eg in egon]):
                    # set the grount_truth for that user
                    friend_locs = [ground_truth[eg][0] for eg in egon if eg in ground_truth]
                    new_gt[uid] = geometric_mean(friend_locs)
                    self.log("Located %s (%s)" % (u['user']['screen_name'], new_gt[uid]))

            if len(new_gt) == 0:
                # could not locate anymore users
                break

            ground_truth.update(new_gt)

        if str(netw.key_user) in ground_truth:
            self.log("Found user %s after %i iterations." % (netw.key_user, i))
            return ground_truth[str(netw.key_user)]
        else:
            return None
