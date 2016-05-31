from pymongo import MongoClient
import datetime

client = MongoClient()
db = client.twitter

cursor = db.tweets.find({'geo':{'$ne':None}, 'geo.type':'Point'})

lats = []
lons = []


from mpl_toolkits.basemap import Basemap
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

fig = plt.figure(figsize=(14,7))
ax = fig.add_subplot(111, frame_on=False)
map = Basemap(projection='robin',
              lat_0=0, lon_0=0)
              #width=500000, height=300000,
              #llcrnrlon=-130.476394,
              #llcrnrlat=25.891242,
              #urcrnrlon=-62.009597,
              #urcrnrlat=55.336887)
              #resolution='l', area_thresh=1000.0)

#map.drawcoastlines()
#map.drawcountries()
map.fillcontinents(color='#CCCCCC', zorder=1)
map.drawmapboundary()

#map.drawmeridians(np.arange(0, 360, 30))
#map.drawparallels(np.arange(-90, 90, 30))

lats = []
lons = []

count = 0
for doc in cursor:
    lats.append(doc['geo']['coordinates'][1])
    lons.append(doc['geo']['coordinates'][0])

    x,y = map(lats[-1], lons[-1])
    map.plot(x, y, 'o', markersize=0.1, color='red', alpha=0.4)
    #print (lats[-1], lons[-1])
    count += 1
    if count % 100 == 0:
        print ("Processed", count)

#a, b = map(lons, lats)
#map.hexbin(np.array(b), np.array(a), gridsize=50, bins='log', cmap=plt.get_cmap('Blues'), mincnt=1)

smallprint = ax.text(
    1.03, 0,
    'Test',
    ha='right', va='bottom',
    size=8,
    color='#555555',
    transform=ax.transAxes)

plt.title("Test")
plt.tight_layout()

try:
    plt.savefig('test.png', dpi=200, alpha=True)
except IOError:
    print("Could not save file to path.")

plt.show()
