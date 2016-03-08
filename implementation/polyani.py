import logging

import numpy as np
from multiind.polystacker import plot_area
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def plotevents_count(tweets):
    # Set up formatting for the movie files
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)

    p1 = (-12, 63)
    p2 = (5, 47)

    ims = []
    lastx = None
    for framid in range(500):#350):
        yield
        logging.info("Drawing frame %i" % framid)

        torem = []

        polys = []
        for t in tweets['twts']:
            p = eval(t['locinf']['mi']['test']['poly'])
            polys.append([(x, 1) for x in p])
        x, _, _ = plot_area(polys, 10, p1, p2)

        if lastx is not None:
            x = x * 0.04 + lastx * 0.96

        lastx = x

        torem.append(plt.imshow(x, interpolation='none'))

        txt = plt.text(-1, -3, "%i" % framid, fontsize=10)
        torem.append(txt)
        ims.append(torem)

    im_ani = animation.ArtistAnimation(plt.gcf(), ims, interval=50, repeat_delay=3000, blit=True)
    im_ani.save('im2.mp4', writer=writer, dpi=200)
    plt.show()


def plotevents(ed):
    # Set up formatting for the movie files
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)

    p1 = (-12, 63)
    p2 = (5, 47)

    ims = []
    for framid in range(100):#350):
        yield
        logging.info("Drawing frame %i" % framid)

        torem = []

        clusters, unclustered = ed.get_clusters(), ed.get_unclustered()
        tweets = unclustered
        for c in clusters:
            tweets += c._tweets

        polys = []
        for t in tweets:
            p = eval(t['locinf']['mi']['test']['poly'])
            polys.append([(x, 1) for x in p])
        x, _, _ = plot_area(polys, 10, p1, p2)
        torem.append(plt.imshow(x, interpolation='none'))

        txt = plt.text(-1, -3, "%i - %s" % (framid, ed.c_manager.lasttime), fontsize=10)
        torem.append(txt)

        #totimg = torem[0]
        #for x in range(1, len(torem)):
        #    totimg += torem[x]
        ims.append(torem)


    im_ani = animation.ArtistAnimation(plt.gcf(), ims, interval=50, repeat_delay=3000, blit=True)
    im_ani.save('im.mp4', writer=writer, dpi=200)
    plt.show()


def plotevents2(ed):
    p1 = (-12, 63)
    p2 = (5, 47)
    framid = 0

    fig = plt.figure()

    orgdata, _, _ = plot_area([[([[0,0], [1,1]], 1)]], 10, p1, p2)
    im = plt.imshow(orgdata, cmap = 'gray', animated=True)
    txt = plt.text(-1, -3, "%i - %s" % (framid, ed.c_manager.lasttime), fontsize=10, animated=True)

    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)

    with writer.saving(fig, "writer_test.mp4", 100):
        for i in range(10):
            yield
            logging.info("Drawing frame %i" % framid)

            clusters, unclustered = ed.get_clusters(), ed.get_unclustered()
            tweets = unclustered
            for c in clusters:
                tweets += c._tweets

            polys = []
            for t in tweets:
                p = eval(t['locinf']['mi']['test']['poly'])
                polys.append([(x, 1) for x in p])
            x, _, _ = plot_area(polys, 10, p1, p2)
            im.set_array(x)
            txt.set_text("%i - %s" % (framid, ed.c_manager.lasttime))
            framid += 1
            fig.canvas.draw()
            writer.grab_frame()
    plt.show()