from pymongo import MongoClient
import datetime

client = MongoClient()
db = client.twitter

limit = int(input("Enter a limit # of posts > "))

cursor = db.tweets.aggregate([{
    "$group": {
        "_id": "$user.screen_name",
        "count": { "$sum": 1 }
    }}]
)

big = []
count = [0 for i in range(0, 100000)]
for doc in cursor:
    count[int(doc['count'])] += 1

    if int(doc['count']) > limit:
        big.append(doc)

big.sort(key=lambda x: int(x['count']), reverse=True)

import csv
with open('topposters.csv', 'w', newline='') as csvfile:
    topposters = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)

    for i in big:
        topposters.writerow([i['_id'], int(i['count'])])
        #print (str(i).encode('utf-8'))

"""
import matplotlib.pyplot as plt
import numpy as np

plt.plot(count)
plt.xscale('log')
plt.show()
"""
