import numpy as np
from Polygon import Polygon
from Polygon.Utils import pointList
from PIL import Image, ImageDraw

show = False
scale = 4
width = 360 * scale
height = 180 * scale


def infer_location(polys):
    for i in polys:
        img = Image.new('1' if show else 'L', (width, height), 0)
        for poly in i:
            polygon = [((p[0] + 180) * scale, (-p[1] + 90) * scale) for p in poly]
            ImageDraw.Draw(img).polygon(polygon, outline=1, fill=1)

        try:
            mask += np.array(img)
        except NameError:
            mask = np.array(img)

    import matplotlib.pyplot as plt
    plt.matshow(mask, fignum=100)

    plt.show()

    top_positions = np.argwhere(mask == np.amax(mask)).squeeze()
    top_positions = [((p[1] / scale) - 180, -((p[0] / scale) - 90)) for p in top_positions]

    print(top_positions)
    out_poly = Polygon()
    h_step = 0.5/scale
    for pos in top_positions:
        out_poly.addContour([
            (pos[0] - h_step, pos[1] - h_step),
            (pos[0] + h_step, pos[1] - h_step),
            (pos[0] + h_step, pos[1] + h_step),
            (pos[0] - h_step, pos[1] + h_step)
        ])

    out_poly.simplify()

    return out_poly