"""
Run the SLP algorithm on a user.
"""
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
import polyplotter


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

    user_test = int(input("Target user ID (eg 434500083):"))

    infersl = InferSL(config, collection, verbose=True)

    input(infersl.infer(user_test))

    netw = infersl.get_network(user_test)

    net_users, net_connections = netw.users, netw.connections

    colors = {}
    ground_truth = {}
    for id, u in net_users.items():
        if len(u.get('locations', [])) > 0:
            locc = [p['coordinates'] for p in u.get('locations')]
            ground_truth[str(u['user']['id'])] = geometric_mean(locc)
            print("GT", ground_truth[str(u['user']['id'])])
            colors[str(u['user']['screen_name'])] = 0

    print(ground_truth)

    G = nx.Graph()
    ego = defaultdict(dict)
    for c in net_connections:
        ego[c[0]][c[1]] = True
        ego[c[1]][c[0]] = True
        G.add_edge(net_users[str(c[0])]['user']['screen_name'], net_users[str(c[1])]['user']['screen_name'])

    max_iterations = 4

    for i in range(max_iterations):
        plt.figure(1)
        values = [float(colors.get(node, max_iterations)) / float(max_iterations+2) for node in G.nodes()]
        nodes = nx.draw_networkx(G, cmap=plt.get_cmap('jet'), node_color=values, vmin=0, vmax=1)
        plt.show()

        # check if all users have been located
        if len(ground_truth) >= len(net_users):
            print("Located all users.")
            break

        new_gt = {}

        for id, u in net_users.items():
            if id in ground_truth:
                continue
            egon = ego.get(str(id)).keys()
            print([str(eg) in ground_truth for eg in egon])
            if any([eg in ground_truth for eg in egon]):
                print(egon)
                print([ground_truth[eg][0] for eg in egon if eg in ground_truth])
                new_gt[id] = geometric_mean([ground_truth[eg][0] for eg in egon if eg in ground_truth])
                print("Located", u['user']['screen_name'], new_gt[id])
                colors[str(u['user']['screen_name'])] = i + 1

        print(len(new_gt))
        if len(new_gt) == 0:
            print("Could not locate anymore users.")
            break

        ground_truth.update(new_gt)

    polyplotter.polyplot([], [(i[0][1], i[0][0]) for i in ground_truth.values()])


    print (colors)