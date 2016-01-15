from pymongo import MongoClient
import numpy as np
import datetime

client = MongoClient()
db = client.twitter

cursor = db.tweets.aggregate(
    [{
        "$project": {
            "y": { "$year": "$timestamp_obj"},
            "m": { "$month": "$timestamp_obj"},
            "d": { "$dayOfMonth": "$timestamp_obj" },
            "h": { "$hour": "$timestamp_obj" }
        }
    },
    {
        "$group": {
            "_id": { "year": "$y", "month": "$m", "day": "$d", "hour": "$h" },
            "count": { "$sum": 1 }
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
        sortedcounts.append(counts[starttime])
        sortedhours.append(hours[starttime.hour])
    except:
        sortedcounts.append(0)
        sortedhours.append(0)

    starttime += datetime.timedelta(hours=1)

N = len(sortedcounts)
# sample spacing
T = 1.0 / 100.0

yf = np.fft.fft(sortedcounts) # fft computing and normalization
xf = np.linspace(0.0, 1.0/(2.0*T), N/2)

yf[0] = 0

import matplotlib.pyplot as plt

fig, ax = plt.subplots(4, 1)

ax[0].plot(sortedcounts)
ax[0].set_xlabel('Time')
ax[0].set_ylabel('Count')

ax[1].plot(xf, 2.0/N * np.abs(yf[:N/2])) # plotting the spectrum

print(yf)
for i in range(0, 27):
    yf[i] = 0

for i in range(28, len(yf)-1):
    yf[i] = 0

ax[2].plot(xf, 2.0/N * np.abs(yf[:N/2]), 'rx') # plotting the spectrum

ixf = np.fft.ifft(yf)
ax[3].plot(ixf)
ax[3].plot(sortedcounts)
ax[3].plot(sortedhours)
ax[3].set_xlabel('Time')
ax[3].set_ylabel('Count')

plt.show()
