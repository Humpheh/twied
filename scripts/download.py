
from pymongo import MongoClient
import datetime

clientrem = MongoClient(host="192.168.0.10")
dbrem = clientrem.twitter

cursor = dbrem.tweets.find({'timestamp_obj': {
    '$gte': datetime.datetime(2015, 12, 8, 16),
    '$lte': datetime.datetime(2015, 12, 27, 16)
}})

clientlocal = MongoClient()
dbloc = clientlocal.twitter

count = 0
for doc in cursor:
    dbloc.tweets.insert_one(doc)

    count += 1
    if count % 10 == 0:
        print (count, "inserted...")

print ("Done.")
