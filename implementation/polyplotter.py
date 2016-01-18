from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle

def add_poly(coords, m):
    xy = []
    for i in coords:
        xy.append(m(i[0], i[1]))
    poly = Polygon(xy, facecolor='red', alpha=0.4)
    plt.gca().add_patch(poly)

def add_point(coords, m):
    xy = m(coords[0], coords[1])
    point = Circle(xy, radius=5000, facecolor='red', alpha=0.4)
    plt.gca().add_patch(point)

def polyplot(polygons, points):
    m = Basemap(projection='robin',lon_0=0)
    m.drawcoastlines()
    m.drawmapboundary()

    for poly in polygons:
        add_poly(poly, m)

    for point in points:
        add_point(point, m)

    plt.show()