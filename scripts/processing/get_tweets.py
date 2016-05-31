from pymongo import MongoClient
from pprint import pprint

client = MongoClient(host="144.173.8.46")
db = client.twitter

cursor = db.tweets.find()

for doc in cursor:
    # doc is the tweet object
    pprint(doc)
    input(">")
