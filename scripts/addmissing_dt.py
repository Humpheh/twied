from pymongo import MongoClient
import datetime

client = MongoClient()
db = client.twitter

cursor = db.tweets.find({'timestamp_obj':None})

count = 0
for doc in cursor:
    dt = datetime.datetime.utcfromtimestamp( float(doc['timestamp_ms']) / 1000 )
    db.tweets.update_one(
        {"_id": doc['_id']},
        {
            "$set": {
                "timestamp_obj": dt
            }
        }
    )
    count += 1
    print (count, "Updated", doc['_id'], dt)
