import tkinter as tk
from tkinter import ttk
import pprint

import time
from multiprocessing.dummy import Pool as ThreadPool
import logging
import twieds
from pymongo import MongoClient
from configparser import NoOptionError
from bson.objectid import ObjectId
import sys
import datetime
import random

import polyplotter
import twieds
import multiind.indicators as indicators
from multiind import polystacker


class Application(tk.Frame):
    def __init__(self, inferfunc, inds, master=None):
        self.inferfunc = inferfunc
        self.inds = inds

        tk.Frame.__init__(self, master, padx=5, pady=5)
        self.pack(expand=True, fill=tk.BOTH)

        self.frame1 = tk.Frame(self)
        self.frame1.pack(fill=tk.X)

        self.lab1 = tk.Label(self.frame1, text="Tweet ID:", padx=5, width=6)
        self.lab1.pack(side=tk.LEFT, anchor=tk.N)

        self.tweetid = tk.Entry(self.frame1, width=30)
        self.tweetid.pack(fill=tk.X)

        self.frame2 = tk.Frame(self, pady=5)
        self.frame2.pack(fill=tk.X)

        self.action = tk.Button(self.frame2, height=1)
        self.action["text"] = "Get Tweet"
        self.action["command"] = self.get_tweet
        self.action.pack(side=tk.LEFT, anchor=tk.N)

        self.actionR = tk.Button(self.frame2, height=1)
        self.actionR["text"] = "Random Tweet"
        self.actionR["command"] = self.get_random
        self.actionR.pack(side=tk.LEFT, anchor=tk.N)

        self.actionDo = tk.Button(self.frame2, height=1)
        self.actionDo["text"] = "Infer Tweet"
        self.actionDo["command"] = self.infer_tweet
        self.actionDo.pack(side=tk.RIGHT, anchor=tk.N)

        self.tweetval = tk.Text(self, height=10, width=40)
        self.tweetval.pack(fill=tk.BOTH, expand=True)

        self.output = tk.Label(self, text="-", pady=4)
        self.output.pack(side=tk.LEFT, anchor=tk.SW)

        """self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Hello World\n(click me)"
        self.hi_there["command"] = self.say_hi
        self.hi_there.pack(side="top")

        self.QUIT = tk.Button(self, text="QUIT", fg="red",
                                            command=root.destroy)
        self.QUIT.pack(side="bottom")"""

    def get_tweet(self):
        try:
            id = ObjectId(self.tweetid.get())
            cursor = db.tweets.find({'_id': id})
            for doc in cursor:
                logging.info("Got tweet: %s" % doc['_id'])

                fordoc = pprint.pformat(doc, indent=4).encode('utf-8')

                self.tweetval.delete(1.0, tk.END)
                self.tweetval.insert(1.0, fordoc)
                self.output['text'] = "Got tweet successfully."
                break
        except Exception as e:
            self.output['text'] = "ERROR in loading doc: " + str(type(e).__name__)
            raise e

    def get_random(self):
        try:
            count = 5000
            doc = db.tweets.find()[random.randrange(count)]
            logging.info("Got tweet: %s" % doc['_id'])

            fordoc = pprint.pformat(doc, indent=4).encode('utf-8')

            self.tweetval.delete(1.0, tk.END)
            self.tweetval.insert(1.0, fordoc)
            self.output['text'] = "Got tweet successfully."
        except Exception as e:
            self.output['text'] = "ERROR in loading random doc: " + str(type(e).__name__)
            raise e

    def infer_tweet(self):
        try:
            doc = eval(self.tweetval.get(1.0, tk.END))

            self.inferfunc(self, doc, self.inds)
        except Exception as e:
            self.output['text'] = "ERROR in parsing doc: " + str(type(e).__name__)
            raise e

config = twieds.setup("logs/locinf.log", "settings/locinf.ini")

def add_ind(task):
    ind = task[0]
    field = task[1]

    f_field = field[:50].encode('utf8') if isinstance(field, str) else field

    start = time.clock()
    logging.info("%10s <- Value: %-50s" % (type(ind).__name__[:-9], f_field))
    result = ind.get_loc(field)
    logging.info("%10s -> Took %.2f seconds. (returned: %i polys)" % (
        type(ind).__name__[:-9], (time.clock() - start), len(result))
    )
    return result


def process_tweet(tkwin, twt, indis):
    global root
    logging.info("Processing tweet %s", twt['_id'])

    app_inds = [
        (indis['ms'], twt['text']),
        (indis['lf'], twt['user']['location']),
        (indis['ws'], twt['user']['url']),
        (indis['co'], twt['user']['location']),
        (indis['tz'], twt['user']['time_zone']),
        (indis['to'], twt['user']['utc_offset']),
        # (indis['tg'], twt['geo'])
    ]

    t = tk.Toplevel(tkwin)
    t.wm_title("Details")

    tree = ttk.Treeview(t, columns=('text', 'polys', 'weight'))
    tree.pack(fill=tk.BOTH, expand=True)

    tree.column('text', anchor='w')
    tree.heading('text', text='Text')

    tree.column('polys', width=10, anchor='w')
    tree.heading('polys', text='Polys')

    tree.column('weight', width=10, anchor='w')
    tree.heading('weight', text='Weight')

    # infer polys
    pool = ThreadPool(6)
    polys = pool.map(add_ind, app_inds)

    for x in range(len(app_inds)):
        inddet = app_inds[x]
        txt = inddet[1] if inddet[1] is not None else ""
        tree.insert('', 'end', text=type(inddet[0]).__name__,
                    values='"'+str(txt)+'" '+str(len(polys[x]))+" "+str(inddet[0].get_weight(1)))

    start = time.clock()
    logging.info('Intersecting polygons...')
    new_polys, max_val = polystacker.infer_location(polys, demo=True)
    logging.info('Polygon intersection complete. Took %.2f seconds.' % (time.clock() - start))

    pointarr = []
    for c in new_polys:
        pointarr.append(c)

    point = []
    if twt['geo'] is not None:
        point.append(twt['geo']['coordinates'])

    polyplotter.polyplot(pointarr, point)

    pool.close()
    pool.join()

    return new_polys, max_val, twt


# setup the indicators
logging.info("Setting up indicators...")
inds = dict()
inds['ms'] = indicators.MessageIndicator(config)
inds['tz'] = indicators.TZIndicator(config)
inds['to'] = indicators.TZOffsetIndicator(config)
inds['lf'] = indicators.LocFieldIndicator(config)
inds['co'] = indicators.CoordinateIndicator(config)
inds['ws'] = indicators.WebsiteIndicator(config)
# inds['tg'] = indicators.GeotagIndicator(config)
logging.info("Setup indicators.")

# connect to the MongoDB
logging.info("Connecting to MongoDB...")
client = MongoClient(config.get("mongo", "address"), config.getint("mongo", "port"))
logging.info("Connected to MongoDB")

# select the database and collection based off config
try:
    db = client[config.get("mongo", "database")]
    col = db[config.get("mongo", "collection")]
except NoOptionError:
    logging.critical("Cannot connect to MongoDB database and collection. Config incorrect?")
    sys.exit()

root = tk.Tk()
app = Application(process_tweet, inds, master=root)
root.geometry("350x300+300+300")
app.db = db
root.wm_title("MI Demo")
app.mainloop()
