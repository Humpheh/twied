"""
Run the SLP algorithm on a user.
"""
import logging
import sys
from collections import defaultdict
from configparser import NoOptionError

import matplotlib.pyplot as plt
import networkx as nx
import pymongo
from mpl_toolkits.basemap import Basemap
from pymongo import MongoClient

from labelprop.distance import geometric_mean
from labelprop.inference import InferSL
from scripts.examples import twieds

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

    #input(infersl.infer(user_test))

    netw = infersl.get_network(user_test, hidegeo=True)

    net_users, net_connections = netw.users, netw.connections

    colors = {}
    ground_truth = {}
    true_users = {}
    target_user = {}
    for id, u in net_users.items():
        if len(u.get('locations', [])) > 0:
            locc = [p['coordinates'] for p in u.get('locations')]
            ground_truth[str(u['user']['id'])] = geometric_mean(locc)
            print("GT", ground_truth[str(u['user']['id'])])
            true_users[u['user']['id']] = str(u['user']['screen_name'])
            colors[str(u['user']['screen_name'])] = 0

        if u['user']['id'] == user_test:
            target_user[u['user']['id']] = str(u['user']['screen_name'])

    plt.ion()

    G = nx.Graph()
    ego = defaultdict(dict)
    for c in net_connections:
        ego[c[0]][c[1]] = True
        ego[c[1]][c[0]] = True
        G.add_edge(net_users[str(c[0])]['user']['screen_name'], net_users[str(c[1])]['user']['screen_name'])

    pos = nx.spring_layout(G)

    max_iterations = 10

    for i in range(max_iterations):
        #plt.figure(1)

        values = [float(colors.get(node, max_iterations)) / float(max_iterations+5) for node in G.nodes()]
        plt.clf()
        nodes = nx.draw_networkx(G, pos, cmap=plt.get_cmap('jet'), node_color=values, vmin=0, vmax=1)
        plt.show()

        input(">")
        logging.info("Iteration %i" % i)

        # check if all users have been located
        if len(ground_truth) >= len(net_users):
            logging.info("Located all users.")
            break

        new_gt = {}

        for id, u in net_users.items():
            if id in ground_truth:
                continue
            egon = ego.get(str(id)).keys()
            #print([str(eg) in ground_truth for eg in egon])
            if any([eg in ground_truth for eg in egon]):
                #print(egon)
                #print([ground_truth[eg][0] for eg in egon if eg in ground_truth])
                new_gt[id] = geometric_mean([ground_truth[eg][0] for eg in egon if eg in ground_truth])
                logging.info("Located %-17s (%-17s)" % (u['user']['screen_name'], new_gt[id]))
                colors[str(u['user']['screen_name'])] = i + 1

        if len(new_gt) == 0:
            logging.info("Could not locate anymore users.")
            break

        ground_truth.update(new_gt)

    plt.ioff()
    plt.figure(2)
    logging.info("Plotting points on maps...")

    m = Basemap(projection='robin', lon_0=0, resolution='l')
    m.drawcoastlines()
    m.drawmapboundary()

    geolabel = []
    targetlabel = []
    xs, ys = [], []
    for k, i in ground_truth.items():
        x, y = m(i[0][1], i[0][0])
        xs.append(x)
        ys.append(y)

        if int(k) in true_users.keys():
            print("GT: ", k)
            geolabel.append([true_users[int(k)], x, y])
        if int(k) in target_user.keys():
            print("TG: ", k)
            targetlabel.append([target_user[int(k)], x, y])

    m.scatter(xs, ys)

    for label, x, y in geolabel:
        plt.annotate(label,
            xy = (x, y), xytext = (-20, 20),
            textcoords = 'offset points', ha = 'right', va = 'bottom',
            bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
            arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))

    for label, x, y in targetlabel:
        plt.annotate(label,
            xy = (x, y), xytext = (20, -20),
            textcoords = 'offset points', ha = 'left', va = 'top',
            bbox = dict(boxstyle = 'round,pad=0.5', fc = 'blue', alpha = 0.5),
            arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))

    plt.show()
