from geopy.distance import vincenty
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from operator import itemgetter


def geometric_mean(points):
    distances = []
    for x in points:
        dsum = sum([vincenty(x, y).km for y in points])
        distances.append([x, dsum])

    minarg = min(distances, key=itemgetter(1))
    minpoint = minarg[0]

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

    return minarg