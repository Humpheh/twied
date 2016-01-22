import numpy as np
from Polygon import Polygon
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import logging


# polys, (-180, -90), (180, 90)

def coord2grid(p, scale, offset):
    return (p[0] - offset[0]) * scale, (-p[1] + offset[1]) * scale


def grid2coord(p, scale, offset):
    return (p[1] / scale) + offset[0], -((p[0] / scale) - offset[1])


def plot_area(polys, scale=1, p1=(-180, 90), p2=(180, -90)):
    # get the drawing info from the points
    width = int((p2[0] - p1[0]) * scale)
    height = int((p1[1] - p2[1]) * scale)
    offset = (p1[0], p1[1])

    mask = None
    # loop through each of the polygons and add the weight to the mask
    for i in polys:
        poly_mask = None
        for poly in i:
            img = Image.new('L', (width, height), 0)

            # offset the polygon coordinates and draw to the image
            polygon = [coord2grid(p, scale, offset) for p in poly[0]]
            ImageDraw.Draw(img).polygon(polygon, outline=1, fill=1)

            # add the mask to the indicator mask - replace old if weight is higher
            new_mask = np.array(img, dtype=np.float_) * poly[1]
            poly_mask = np.maximum(poly_mask, new_mask) if poly_mask is not None else new_mask

        if poly_mask is not None:
            if mask is None:
                mask = poly_mask
            else:
                mask += poly_mask

    return mask, scale, offset


def generate_polygon(coords, scale):
    out_poly = Polygon()
    h_step = 0.5/scale
    for pos in coords:
        out_poly.addContour([
            (pos[0] - h_step, pos[1] - h_step),
            (pos[0] + h_step, pos[1] - h_step),
            (pos[0] + h_step, pos[1] + h_step),
            (pos[0] - h_step, pos[1] + h_step)
        ])

    out_poly.simplify()
    return out_poly


def find_bounds(coords, border):
    c_min = [180, -90]
    c_max = [-180, 90]
    for i in coords:
        c_min = (min([i[0], c_min[0]]), max([i[1], c_min[1]]))
        c_max = (max([i[0], c_max[0]]), min([i[1], c_max[1]]))
    c_min = (c_min[0] - border, c_min[1] + border)
    c_max = (c_max[0] + border, c_max[1] - border)
    return c_min, c_max


def get_highest(mask, scale, offset):
    top_positions = np.argwhere(mask == np.amax(mask)).squeeze()
    return [grid2coord(p, scale, offset) for p in top_positions]


def infer_location(polys):
    logging.info("Intersecting and finding area...")

    # generate rough outline
    mask, scale, offset = plot_area(polys, 1)

    logging.info("Intersected polygons.")

    # if grid is all zeros, there is no valid point to infer
    if np.count_nonzero(mask) == 0:
        logging.info("No location found.")
        return []

    # show diagram
    plt.matshow(mask, fignum=100)
    plt.show()

    # find the coordinates of the highest places
    top_positions = get_highest(mask, scale, offset)

    # find the area around the highest area to generate higher resolution grid for
    border = 2
    c_min, c_max = find_bounds(top_positions, border)
    logging.info("Zoom area:", c_min, c_max)

    # create a finer area around the polygon
    mask2, scale2, offset2 = plot_area(polys, 2, c_min, c_max)
    plt.matshow(mask2, fignum=100)
    plt.show()

    # get the highest positions for the zoomed in area
    top_positions_foc = get_highest(mask2, scale2, offset2)

    # generate a polygon around the points
    out_poly = generate_polygon(top_positions_foc, scale2)

    return out_poly
