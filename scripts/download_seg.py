from pymongo import MongoClient
import datetime

clientrem = MongoClient()
dbrem = clientrem.twitter

cursor = dbrem.tweets.find({'timestamp_obj': {
    '$gte': datetime.datetime(2015, 12, 8, 16),
    '$lte': datetime.datetime(2015, 12, 27, 16)
}})

dbloc = clientrem.twitter

count = 0
for doc in cursor:
    dbloc.inftweets.insert_one(doc)

    count += 1
    if count % 100 == 0:
        print (count, "inserted...")

print ("Done.")
