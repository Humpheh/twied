from pymongo import MongoClient
import datetime
import csv

client = MongoClient()
db = client.twitter

# load users above limit
usernames = {}
with open('topposters.csv') as csvfile:
    reader = csv.reader(csvfile)
    for r in reader:
        usernames[r[0]] = r[1]

cursor = db.tweets.find()

countsnone = 0
countsremoved = 0
countsloc = 0
for doc in cursor:
    if doc['user']['screen_name'] in usernames:
        countsremoved += 1
    elif doc['user']['location'] == None:
        countsnone += 1
    else:
        countsloc += 1

    if (countsloc + countsnone + countsremoved) % 10000 == 0:
        print ("Processed:", (countsloc + countsnone + countsremoved))

    #print (str(doc['user']['location']).encode('utf-8'))
    #print (str(doc).encode('utf-8'))

print ("No location field:", countsnone)
print ("Removed from set: ", countsremoved)
print ("Location field:   ", countsloc)
