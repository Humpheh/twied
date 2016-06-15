from geopy.distance import vincenty

from random import randint


def geometric_mean(points):
    """
    Function which calculates the geometric mean from a list of points using
    the vincenty distance.

    :param points: List of points to find the geometric mean of.
    :return: The geometric mean of the points.
    """
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

    if len(distances) == 0:
        return None

    return distances[randint(0, len(distances)-1)]
