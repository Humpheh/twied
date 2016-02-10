from geopy.distance import vincenty

from random import randint

"""from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from operator import itemgetter
"""


def geometric_mean(points):
    distances = []
    ad = []
    for x in points:
        dsum = sum([vincenty(x, y).km for y in points])

        row = [x, round(dsum, 5)]
        if distances == [] or distances[0][1] == dsum:
            distances.append(row)
        elif distances[0][1] > dsum:
            distances = [row]
        ad.append(row)

    print (ad)

    if len(distances) == 0:
        return None

    return distances[randint(0, len(distances)-1)]

"""m = Basemap(projection='robin', lon_0=0)
m.drawcoastlines()
m.drawmapboundary()
for coords in points:
    xy = m(coords[1], coords[0])
    point = Circle(xy, radius=5000, facecolor='red', alpha=0.4)
    plt.gca().add_patch(point)

xy = m(minpoint[1], minpoint[0])
point = Circle(xy, radius=5000, facecolor='blue', alpha=0.4)
plt.gca().add_patch(point)

plt.show()"""