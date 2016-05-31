from pymongo import MongoClient
import datetime

client = MongoClient()
db = client.twitter

"""[{
    "$project": {
        "y": {
            "$year": "$timestamp_obj"
        },
        "m": {
            "$month": "$timestamp_obj"
        },
        "d": {
            "$dayOfMonth": "$timestamp_obj"
        }
    }
},
{
    "$group": {
        "_id": {
            "year": "$y",
            "month": "$m",
            "day": "$d"
        },
        "count": {
            "$sum": 1
        }
    }
},
{
    "$sort": {
        "_id.year": -1,
        "_id.month": 1,
        "_id.day": 1
    }
}]"""

cursor = db.tweets.aggregate(
    [{
        "$project": {
            "y": {
                "$year": "$timestamp_obj"
            },
            "m": {
                "$month": "$timestamp_obj"
            },
            "d": {
                "$dayOfMonth": "$timestamp_obj"
            },
            "h": {
                "$hour": "$timestamp_obj"
            }
        }
    },
    {
        "$group": {
            "_id": {
                "year": "$y",
                "month": "$m",
                "day": "$d",
                "hour": "$h"
            },
            "count": {
                "$sum": 1
            }
        }
    },
    {
        "$sort": {
            "_id.year": -1,
            "_id.month": 1,
            "_id.day": 1,
            "_id.hour": 1
        }
    }]
)

hours = [[] for i in range(24)]
counts = {}
earliest, latest = None, None

for doc in cursor:
    d = doc['_id']
    time = datetime.datetime(int(d['year']), int(d['month']), int(d['day']), int(d['hour']))

    counts[time] = doc['count']

    if earliest == None or time < earliest: earliest = time
    if latest == None or time > latest: latest = time

    hours[int(d['hour'])].append(int(doc['count']))
    print (str(doc).encode('utf-8'))

for i in range(0, len(hours)):
    hours[i] = sum(hours[i]) / len(hours[i])

starttime = earliest
sortedcounts = []
sortedhours = []
while not starttime >= latest:
    try:
        sortedcounts.append((counts[starttime], hours[starttime.hour]))
    except:
        sortedcounts.append((0, hours[starttime.hour]))
    starttime += datetime.timedelta(hours=1)

print (len(sortedcounts))

import matplotlib.pyplot as plt
import numpy as np

plt.plot(sortedcounts)
plt.show()
