from pymongo import MongoClient
import datetime
import csv

client = MongoClient()
db = client.twitter

cursor = db.tweets.find()

counts = {}

c = 0
d = 0
for doc in cursor:
    for ht in doc['entities']['hashtags']:
        try:
            counts[ht['text']] += 1
        except:
            counts[ht['text']] = 1

        c += 1
        if c % 10000 == 0:
            print ("Processed", c, "hashtags,", d, "documents.")
    d += 1

print ("Counted hashtags")

# convert from dict to list
countlist = []
for key, value in counts.items():
    countlist.append((key, value))

print ("Sorting hashtags...")
countlist.sort(key=lambda x: x[1], reverse=True)

print ("Outputting to files...")
with open('hashtagcount.csv', 'w', newline='', encoding='utf-8') as csvfile:
    topposters = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)

    for i in countlist:
        name = i[0]
        topposters.writerow([name, i[1]])
