import logging
from collections import defaultdict

from twython import Twython
from twython.exceptions import TwythonAuthError, TwythonError


class SLNetwork:
    def __init__(self):
        self.users = {}
        self.connections = []


class InferSL:
    def __init__(self, config, dbcollection):
        # setup Twitter API interface
        api_settings = config._sections['twitter']
        self.twitter = Twython(**api_settings)
        self.db = dbcollection

        self.minconnections = 4

    def infer_location(self, user_id):
        network = SLNetwork()

        user = self.get_user(user_id)
        self.get_connections(user, network, 0)

        return network

    def get_user(self, user_id):
        dbusr = self.db.find_one({'user.id': int(user_id)})

        if dbusr is not None:
            return dbusr if 'private' not in dbusr else None

        mentions = defaultdict(int)
        geotags = []
        user = None

        max_id = None
        for i in range(2):
            try:
                print("Downloading...")
                usr_tweets = self.twitter.get_user_timeline(user_id=user_id, count=200, include_rts=False, max_id=max_id)
            except TwythonAuthError:
                self.db.insert_one({
                    'user': {'id': int(user_id)},
                    'private': True
                })
                return None
            except TwythonError as e:
                logging.error(str(e))
                return None

            for twt in usr_tweets:
                user = twt['user']
                for m in twt['entities']['user_mentions']:
                    mentions[m['id_str']] += 1
                if twt['geo'] is not None:
                    geotags.append(twt['geo'])
                max_id = twt['id']

        if user is None:
            return None

        data = {
            'user': user,
            'locations': geotags,
            'mentions': mentions
        }

        self.db.insert_one(data)
        return data

    def get_connections(self, user, network, depth=0, cont=True):
        # store the user in net_users
        network.users[str(user['user']['id'])] = user

        # if the user is None, then it cannot be found, so return
        if user is None:
            return

        print("Processing", user['user']['id'], user['user']['screen_name'])

        # if recursive depth has been met, return
        if depth >= 3 or not cont:
            return

        next_continue = True
        next_connections = []

        for uid, count in user['mentions'].items():
            # if the number of mentions is less than a threshold, pass it
            if count < self.minconnections:
                continue

            # get the mentioend user
            user2 = self.get_user(uid)

            # if cannot find the user, continue
            if user2 is None:
                continue

            print("Processing", uid, user2['user']['screen_name'])

            if str(user['user']['id']) in user2['mentions']:
                # if the other user has not mentioned the main subject enough, skip
                if user2['mentions'][str(user['user']['id'])] < self.minconnections:
                    continue

                network.connections.append((str(user['user']['id']), str(user2['user']['id'])))
                print("Found connecting user:", user['user']['screen_name'], "-", user2['user']['screen_name'])

                if str(uid) not in network.users:
                    # recursively get the connections of the next user
                    next_connections.append(user2)

                    if len(user2['locations']) > 3:
                        next_continue = False

        for usr_i in next_connections:
            self.get_connections(usr_i, network, depth+1, next_continue)

