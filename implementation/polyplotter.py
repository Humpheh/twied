from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import logging
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

    poly = Polygon(list(zip(X, Y)), facecolor='black', alpha=0.2)
    pt = plt.gca().add_patch(poly)
    pt2, = plt.plot(X,Y,**kwargs)
    return pt2, pt


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


def plotevents(ed):
    # Set up formatting for the movie files
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)

    #m = Basemap(projection='robin', lon_0=59, lat_0=-12, lon_1=50, lat_1=4.2)
    m = Basemap(projection='merc', lat_0=53.458736, lon_0=-2.2,
        resolution='l', area_thresh = 1000.0,
        urcrnrlat=58.869587, urcrnrlon=4.186178,
        llcrnrlat=48.949979, llcrnrlon=-12.359231) # lat, lon
    m.drawcoastlines()
    m.drawmapboundary()

    torem = []

    ims = []
    for framid in range(350):
        yield
        logging.info("Drawing frame %i" % framid)

        #for x in torem:
       #     x.remove()
        torem = []

        clusters, unclustered, radius = ed.get_clusters(), ed.get_unclustered_points(), ed.c_manager.radius
        for c in clusters:
            for p in c.get_points():
                x, y = m(p[0], p[1])
                b, = m.plot(x, y, 'b.')
                torem.append(b)

            for x in c.centres:
                # point = Circle(xy2, radius=2000, facecolor='red', alpha=0.4)
                # plt.gca().add_patch(point)
                b = equi(m, x[0], x[1], radius, color='red', alpha=0.4)
                torem += b
                xy2 = m(x[0], x[1])
                b, = m.plot(xy2[0], xy2[1], 'g.')
                torem.append(b)

        for p in unclustered:
            x, y = m(p[0], p[1])
            b, = m.plot(x, y, 'r.')
            torem.append(b)

        txt = plt.text(-1, 0.2, "%i - %s" % (framid, ed.c_manager.lasttime), fontsize=10)
        torem.append(txt)

        #totimg = torem[0]
        #for x in range(1, len(torem)):
        #    totimg += torem[x]
        ims.append(torem)


    im_ani = animation.ArtistAnimation(plt.gcf(), ims, interval=50, repeat_delay=3000, blit=True)
    im_ani.save('im.mp4', writer=writer, dpi=200)
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