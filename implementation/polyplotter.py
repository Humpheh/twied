from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle

def shoot(lon, lat, azimuth, maxdist=None):
    """Shooter Function
    Original javascript on http://williams.best.vwh.net/gccalc.htm
    Translated to python by Thomas Lecocq
    """
    glat1 = lat * np.pi / 180.
    glon1 = lon * np.pi / 180.
    s = maxdist / 1.852
    faz = azimuth * np.pi / 180.

    EPS= 0.00000000005
    if ((np.abs(np.cos(glat1))<EPS) and not (np.abs(np.sin(faz))<EPS)):
        print("Only N-S courses are meaningful, starting at a pole!")
        return

    a=6378.13/1.852
    f=1/298.257223563
    r = 1 - f
    tu = r * np.tan(glat1)
    sf = np.sin(faz)
    cf = np.cos(faz)
    if (cf==0):
        b=0.
    else:
        b=2. * np.arctan2 (tu, cf)

    cu = 1. / np.sqrt(1 + tu * tu)
    su = tu * cu
    sa = cu * sf
    c2a = 1 - sa * sa
    x = 1. + np.sqrt(1. + c2a * (1. / (r * r) - 1.))
    x = (x - 2.) / x
    c = 1. - x
    c = (x * x / 4. + 1.) / c
    d = (0.375 * x * x - 1.) * x
    tu = s / (r * a * c)
    y = tu
    c = y + 1
    while (np.abs (y - c) > EPS):

        sy = np.sin(y)
        cy = np.cos(y)
        cz = np.cos(b + y)
        e = 2. * cz * cz - 1.
        c = y
        x = e * cy
        y = e + e - 1.
        y = (((sy * sy * 4. - 3.) * y * cz * d / 6. + x) *
              d / 4. - cz) * sy * d + tu

    b = cu * cy * cf - su * sy
    c = r * np.sqrt(sa * sa + b * b)
    d = su * cy + cu * sy * cf
    glat2 = (np.arctan2(d, c) + np.pi) % (2*np.pi) - np.pi
    c = cu * cy - su * sy * cf
    x = np.arctan2(sy * sf, c)
    c = ((-3. * c2a + 4.) * f + 4.) * c2a * f / 16.
    d = ((e * cy * c + cz) * sy * c + y) * sa
    glon2 = ((glon1 + x - (1. - c) * d * f + np.pi) % (2*np.pi)) - np.pi

    baz = (np.arctan2(sa, b) + np.pi) % (2 * np.pi)

    glon2 *= 180./np.pi
    glat2 *= 180./np.pi
    baz *= 180./np.pi

    return (glon2, glat2, baz)


def equi(m, centerlon, centerlat, radius, *args, **kwargs):
    glon1 = centerlon
    glat1 = centerlat
    X = []
    Y = []
    for azimuth in range(0, 360):
        glon2, glat2, baz = shoot(glon1, glat1, azimuth, radius)
        X.append(glon2)
        Y.append(glat2)
    X.append(X[0])
    Y.append(Y[0])

    #m.plot(X,Y,**kwargs) #Should work, but doesn't...
    X,Y = m(X,Y)
    plt.plot(X,Y,**kwargs)


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


def plotevents(clusters, unclustered):
    m = Basemap(projection='robin', lon_0=0)
    m.drawcoastlines()
    m.drawmapboundary()

    for c in clusters:
        for p in c.get_points():
            print('Clustered:', p)
            x, y = m(p[0], p[1])
            m.plot(x, y, 'bo')

        for x in c.centres:
            print('Centre:', x)
            # point = Circle(xy2, radius=2000, facecolor='red', alpha=0.4)
            # plt.gca().add_patch(point)
            equi(m, x[0], x[1], 100, color='red', alpha=0.4)
            xy2 = m(x[0], x[1])
            m.plot(xy2[0], xy2[1], 'go')

    for p in unclustered:
        print('Unclustered:', p)
        x, y = m(p[0], p[1])
        m.plot(x, y, 'ro')

    plt.show()


def d_polyplot(polyold, polynew):
    fig = plt.figure()
    ax = fig.add_subplot(211)
    ax.set_title("Before")
    m1 = Basemap(projection='robin', lon_0=0)
    m1.drawcoastlines()
    m1.drawmapboundary()
    for poly in polyold:
        add_poly(poly, m1)

    ax = fig.add_subplot(212)
    ax.set_title("Unioned")
    m2 = Basemap(projection='robin', lon_0=0)
    m2.drawcoastlines()
    m2.drawmapboundary()
    for poly in polynew:
        add_poly(poly, m2)

    plt.show()