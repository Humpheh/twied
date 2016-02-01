import logging
import sys
from collections import defaultdict

import pymongo
import matplotlib.pyplot as plt
import networkx as nx

from pymongo import MongoClient
from configparser import NoOptionError

import twieds
from labelprop.inference import InferSL
from labelprop.distance import geometric_mean


visited_users = {}
colors = {}

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

    user_test = 15808177 #97034991#

    infersl = InferSL(config, collection)
    netw = infersl.infer_location(user_test)

    net_users, net_connections = netw.users, netw.connections

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

    max_iterations = 4

    for i in range(max_iterations):
        plt.figure(1)
        values = [float(colors.get(node, max_iterations)) / float(max_iterations+2) for node in G.nodes()]
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
                print("Located", u['user']['screen_name'], new_gt[id])
                colors[str(u['user']['screen_name'])] = i + 1

        ground_truth.update(new_gt)


    print (colors)