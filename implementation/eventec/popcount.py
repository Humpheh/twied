import numpy as np
import math


class PopMap:
    def __init__(self, filename='glds15ag.asc'):
        d = np.genfromtxt(filename, max_rows=6, usecols=[1])

        self.settings = {
            'ncols': int(d[0]),
            'nrows': int(d[1]),
            'xllcorner': int(d[2]),
            'yllcorner': int(d[3]),
            'cellsize': float(d[4]),
            'NODATA_value': int(d[5])
        }

        self.data = np.loadtxt(filename, dtype=float, skiprows=6)
        print(self.data.shape)

    def get_cell(self, lon, lat):
        clat = abs(lat - self.settings['xllcorner']) / self.settings['cellsize']
        clon = abs(lon - self.settings['yllcorner']) / self.settings['cellsize']

        return round(clat), self.settings['nrows'] - round(clon)

    def get_population(self, lon, lat):
        cellat, cellon = self.get_cell(lon, lat)
        return self.data[cellon, cellat]

    def get_ll(self, clat, clon):
        lat = (clat * self.settings['cellsize']) + self.settings['xllcorner']
        lon = ((self.settings['nrows'] - clon) * self.settings['cellsize']) + self.settings['yllcorner']

        return lat, lon

    def get_reqfunc_uk(self, mediancount, mincount):
        ukdata = self.data[600:850, 4025:4400]
        ukvals = ukdata[ukdata != self.settings['NODATA_value']]

        x1 = np.min(ukvals)
        x2 = np.median(ukvals)

        y1 = mincount
        y2 = mediancount

        a = (y1 - y2) / np.log(x1 / x2)
        b = np.exp(((y2 * np.log(x1)) - (y1 * np.log(x2)))/(y1 - y2))

        return lambda x: math.ceil(a * np.log(x * b)) if x > 0 else mincount