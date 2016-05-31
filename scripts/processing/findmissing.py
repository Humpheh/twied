from pymongo import MongoClient
import datetime

client = MongoClient()
db = client.twitter

cursor = db.tweets.find()

last = None
for doc in cursor:
    if not last == None:
        if doc['timestamp_obj'] - last['timestamp_obj'] > datetime.timedelta(hours=1):
            print ("Min:", last['_id'], last['id'], last['timestamp_obj'])
            print ("Max:", doc['_id'], doc['id'], doc['timestamp_obj'])
            print ("")
            
    last = doc
