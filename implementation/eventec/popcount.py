import numpy as np
import math


class PopMap:
    """
    Provides access to the population map for choosing the required
    number of tweets to create a cluster.

    This uses the population map retrieved from the
    `SEDAC <http://sedac.ciesin.columbia.edu/data/collection/gpw-v3>`_
    data centre. The file should be an .asc ASCII file containing the
    population of each point on the planet.

    .. note:: while the :func:`get_reqfunc_uk` function is provided
        for the UK, there is no function for the rest of the world.
    """

    def __init__(self, filename='glds15ag.asc'):
        """
        Create a new PopMap instance.

        :param filename: The population file to load.
        :type filename: str
        """
        d = np.genfromtxt(filename, max_rows=6, usecols=[1])

        # Load the settings and save them in a dictionary.
        self.settings = {
            'ncols': int(d[0]),
            'nrows': int(d[1]),
            'xllcorner': int(d[2]),
            'yllcorner': int(d[3]),
            'cellsize': float(d[4]),
            'NODATA_value': int(d[5])
        }

        # Load the population data
        self.data = np.loadtxt(filename, dtype=float, skiprows=6)

    def get_cell(self, lon, lat):
        """
        Translates a lat, lon coordinate into the coordinates of the population
        on the population grid.

        :param lon: Longitude of the coordinate.
        :type lon: float
        :param lat: Latitude of the coordinate.
        :type lat: float
        :return: The indexes of the population in the grid.
        :rtype: Tuple of the (x, y) grid coordinate in the population grid.

        .. seealso:: :func:`get_ll` performs the reverse of this method.
        """
        clat = abs(lat - self.settings['xllcorner']) / self.settings['cellsize']
        clon = abs(lon - self.settings['yllcorner']) / self.settings['cellsize']

        return round(clat), self.settings['nrows'] - round(clon)

    def get_population(self, lon, lat):
        """
        Gets the population at a lon, lat coordinate.

        :param lon: Longitude of the coordinate.
        :type lon: float
        :param lat: Latitude of the coordinate.
        :type lat: float
        :return: The population at the coordinate.
        :type: float
        """
        cellat, cellon = self.get_cell(lon, lat)
        return self.data[cellon, cellat]

    def get_ll(self, clat, clon):
        """
        Translates a cell_lat, cell_lon coordinate back into global
        lat, lon coordinates. Note that this will not return the exact
        value that was used when creating the cell coordinates.

        :param clat: The x coordinate of the cell.
        :type clat: integer
        :param clon: The y coordinate of the cell.
        :type clon: integer
        :return: The lat, lon position of the centre of the grid cell.
        :rtype: tuple

        .. seealso:: :func:`get_cell` performs the reverse of this method.
        """
        lat = (clat * self.settings['cellsize']) + self.settings['xllcorner']
        lon = ((self.settings['nrows'] - clon) * self.settings['cellsize']) + self.settings['yllcorner']

        return lat, lon

    def get_reqfunc_uk(self, mediancount, mincount):
        """
        Calculates and returns a function for finding the required number
        of tweets to initialise a cluster within the UK.

        Method returns a lambda function which takes a population value
        and returns the number of tweets required to start the cluster.
        The function is a logarithmic function which will return a
        minimum value at the lowest population densities within the UK
        and a median value at places with median population densities.
        The function levels off for larger population values.

        :param mediancount: The median count to return at median population
            densities within the UK.
        :param mincount: The minimum count to return at the minimum
            population densities within the UK.
        :return: lambda function which takes a population and returns the
            required number of tweets.
        """
        ukdata = self.data[600:850, 4025:4400]
        ukvals = ukdata[ukdata != self.settings['NODATA_value']]

        x1 = np.min(ukvals)
        x2 = np.median(ukvals)

        y1 = mincount
        y2 = mediancount

        a = (y1 - y2) / np.log(x1 / x2)
        b = np.exp(((y2 * np.log(x1)) - (y1 * np.log(x2)))/(y1 - y2))

        return lambda x: math.ceil(a * np.log(x * b)) if x > 0 else mincount
