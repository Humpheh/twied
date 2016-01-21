import numpy as np
import logging
from Polygon import Polygon
from Polygon.Utils import pointList
from PIL import Image, ImageDraw

scale = 4
width = 360 * scale
height = 180 * scale


def infer_location(polys):
    logging.info("Stacking polygons...")
    for i in polys:
        poly_mask = None
        for poly in i:
            img = Image.new('L', (width, height), 0)
            polygon = [((p[0] + 180) * scale, (-p[1] + 90) * scale) for p in poly[0]]
            ImageDraw.Draw(img).polygon(polygon, outline=1, fill=1)
            if poly_mask is None:
                poly_mask = np.array(img) * poly[1]
            else:
                new_mask = np.array(img) * poly[1]
                poly_mask = np.maximum(poly_mask, new_mask)

        if poly_mask is not None:
            try:
                mask += poly_mask
            except NameError:
                mask = poly_mask

    logging.info("Polygons stacked.")

    if np.count_nonzero(mask) == 0:
        return []

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