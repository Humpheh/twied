import logging
import operator
import sys
from pprint import pprint

import matplotlib.pyplot as plt
import networkx as nx
from pymongo import MongoClient
import pymongo
from configparser import NoOptionError

from twython import Twython
from twython.exceptions import TwythonAuthError, TwythonError
from collections import defaultdict

from labelprop.distance import geometric_mean

import twieds


visited_users = {}
colors = {}


def get_user(api, id, dbcollection):
    dbusr = dbcollection.find_one({'user.id': int(id)})

    if dbusr is not None:
        if 'private' in dbusr:
            return None
        return dbusr

    mentions = defaultdict(int)
    geotags = []
    user = None

    max_id = None
    for i in range(2):
        try:
            print("Downloading...")
            usr_tweets = api.get_user_timeline(user_id=id, count=200, include_rts=False, max_id=max_id)
        except TwythonAuthError:
            dbcollection.insert_one({
                'user': {'id': int(id)},
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

    # sorted_mentions = sorted(users.items(), key=operator.itemgetter(1), reverse=True)

    if user is None:
        return None

    data = {
        'user': user,
        'locations': geotags,
        'mentions': mentions
    }

    dbcollection.insert_one(data)
    return data


def get_connections(api, dbcollection, user, net_users, net_connections, depth=0):
    # store the user in net_users
    net_users[str(user['user']['id'])] = user

    # if the user is None, then it cannot be found, so return
    if user is None:
        return

    print("Processing", user['user']['id'], user['user']['screen_name'])

    # if recursive depth has been met, return
    if depth >= 3:
        return

    for uid, count in user['mentions'].items():
        # if the number of mentions is less than a threshold, pass it
        if count < 4:
            continue

        # get the mentioend user
        user2 = get_user(twitter, uid, dbcollection)

        # if cannot find the user, continue
        if user2 is None:
            continue

        print("Processing", uid, user2['user']['screen_name'])

        if str(user['user']['id']) in user2['mentions']:
            net_connections.append((str(user['user']['id']), str(user2['user']['id'])))
            print("Found connecting user:", user['user']['screen_name'], "-", user2['user']['screen_name'])

            if str(uid) not in net_users:
                # recursively get the connections of the next user
                get_connections(api, dbcollection, user2, net_users, net_connections, depth+1)


# must run this as a script
if __name__ == "__main__":
    config = twieds.setup("logs/labelprop.log", "settings/locinf.ini")

    # connect to the MongoDB
    logging.info("Connecting to MongoDB...")
    client = MongoClient(config.get("mongo", "address"), config.getint("mongo", "port"))
    logging.info("Connected to MongoDB")

    # select the database and collection based off config
    try:
        db = client[config.get("mongo", "database")]
        collection = db["users"]
        collection.create_index([('user.id', pymongo.ASCENDING)], unique=True)
        collection.create_index([('user.screen_name', pymongo.ASCENDING)])
    except NoOptionError:
        logging.critical("Cannot connect to MongoDB database and collection. Config incorrect?")
        sys.exit()

    api_settings = config._sections['twitter']
    twitter = Twython(**api_settings)

    user_test = 15808177

    # locs = past_users['TashaaMoss']
    # locc = [p['coordinates'] for p in locs[1]]
    # geometric_mean(locc)

    net_users = {}
    net_connections = []

    user = get_user(twitter, user_test, collection)
    get_connections(twitter, collection, user, net_users, net_connections, 0)

    colors = {}
    ground_truth = {}
    for id, u in net_users.items():
        if len(u.get('locations', [])) > 0:
            locc = [p['coordinates'] for p in u.get('locations')]
            ground_truth[str(u['user']['id'])] = geometric_mean(locc)
            colors[str(u['user']['screen_name'])] = 0

    print(ground_truth)

    G = nx.Graph()
    ego = defaultdict(list)
    for c in net_connections:
        ego[c[0]].append(c[1])
        ego[c[1]].append(c[0])
        G.add_edge(net_users[str(c[0])]['user']['screen_name'], net_users[str(c[1])]['user']['screen_name'])

    maxi = 4

    for i in range(maxi):

        plt.figure(1)
        values = [float(colors.get(node, maxi)) / float(maxi+2) for node in G.nodes()]
        nx.draw_networkx(G, cmap=plt.get_cmap('cool'), node_color=values)
        plt.show()

        new_gt = {}

        for id, u in net_users.items():
            if id in ground_truth:
                continue
            egon = ego.get(str(id))
            print([str(eg) in ground_truth for eg in egon])
            if any([eg in ground_truth for eg in egon]):
                new_gt[id] = geometric_mean([ground_truth[eg][0] for eg in egon if eg in ground_truth])
                print("Located ", u['user']['screen_name'], new_gt[id])
                colors[str(u['user']['screen_name'])] = i + 1

        ground_truth.update(new_gt)


    print (colors)